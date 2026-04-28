#!/usr/bin/env python3
import argparse
import csv
import json
import random
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, Any


@dataclass
class Mutation:
    type: str
    target: Optional[Any] = None
    range_spec: dict = field(default_factory=dict)
    params: dict = field(default_factory=dict)


class MutationEngine:
    def __init__(self, data, seed=None):
        self.data = data
        self.fieldnames = list(data[0].keys()) if data else []
        self.field_map = self._build_field_map()
        self.id_to_index = self._build_id_index()

        if seed is not None:
            random.seed(seed)

        self._handlers = {
            "break_parent_ref": self.break_parent_reference,
            "duplicate_id": self.duplicate_id,
            "create_cycle": self.create_cycle,
            "self_parenting": self.self_parenting,
            "invalid_measurement": self.invalid_measurement,
            "breed_mismatch": self.breed_mismatch,
            "single_parent": self.single_parent,
            "set_sire_female": self.set_sire_female,
            "set_dam_male": self.set_dam_male,
            "invalid_name": self.invalid_name,
            "invalid_sex": self.invalid_sex,
            "rewrite_parent_ref": self.rewrite_parent_reference,
        }

        self._update_index()

    def _build_field_map(self):
        return {fn.strip().lower(): fn for fn in self.fieldnames}

    def _build_id_index(self):
        id_field = self._get_field("id")
        return {row[id_field].strip(): idx for idx, row in enumerate(self.data)}

    def _update_index(self):
        id_field = self._get_field("id")
        self.id_to_index = {row[id_field].strip(): i for i, row in enumerate(self.data)}
        self.id_map = {row[id_field].strip(): row for row in self.data}

    def _get_field(self, key):
        return self.field_map.get(key.lower(), key)

    def _set(self, row_idx, fld, value):
        actual = self._get_field(fld)
        if actual in self.fieldnames:
            self.data[row_idx][actual] = value

    def _resolve_row_index(self, identifier):
        if isinstance(identifier, int):
            if identifier < len(self.data):
                return identifier
            if str(identifier) in self.id_to_index:
                return self.id_to_index[str(identifier)]

        str_id = str(identifier).strip()
        if str_id in self.id_to_index:
            return self.id_to_index[str_id]

        raise ValueError(f"Cannot resolve identifier {identifier}")

    def rewrite_parent_reference(
        self, row_idx, parent_type="sire", target_id=None, **_
    ):
        if target_id is None:
            return

        fld = self._get_field(f"{parent_type}_id")
        self.data[row_idx][fld] = str(target_id)
        self._update_index()

    def break_parent_reference(self, row_idx, parent_type="sire", **_):
        self._set(row_idx, f"{parent_type}_id", "99999")
        self._update_index()

    def duplicate_id(self, row_idx, source_idx=0, **_):
        source_idx = self._resolve_row_index(source_idx)
        id_field = self._get_field("id")
        self.data[row_idx][id_field] = self.data[source_idx][id_field]
        self._update_index()

    def create_cycle(self, row_idx, target_idx=0, **_):
        target_idx = self._resolve_row_index(target_idx)

        id_field = self._get_field("id")
        sire_field = self._get_field("sire_id")
        dam_field = self._get_field("dam_id")

        dog_a_id = self.data[row_idx][id_field]
        dog_b_id = self.data[target_idx][id_field]

        self.data[target_idx][sire_field] = dog_a_id
        self.data[row_idx][dam_field] = dog_b_id

        self._update_index()

    def self_parenting(self, row_idx, mode="both", **_):
        id_field = self._get_field("id")
        sire_field = self._get_field("sire_id")
        dam_field = self._get_field("dam_id")

        dog_id = self.data[row_idx][id_field].strip()

        if mode in ("sire", "both"):
            self.data[row_idx][sire_field] = dog_id

        if mode in ("dam", "both"):
            self.data[row_idx][dam_field] = dog_id

        self._update_index()

    def invalid_measurement(self, row_idx, fld="height_cm", value="-10", **_):
        self._set(row_idx, fld, value)

    def breed_mismatch(self, row_idx, forced_breed=None, **_):
        breed_field = self._get_field("breed")
        sire_field = self._get_field("sire_id")
        dam_field = self._get_field("dam_id")

        if breed_field not in self.fieldnames:
            return

        if forced_breed is not None:
            self.data[row_idx][breed_field] = forced_breed
            return

        dog = self.data[row_idx]

        sire_id = dog.get(sire_field, "").strip() or None
        dam_id = dog.get(dam_field, "").strip() or None

        parent_breeds = []

        for pid in [sire_id, dam_id]:
            if pid in self.id_map:
                b = self.id_map[pid].get(breed_field, "").strip()
                if b:
                    parent_breeds.append(b)

        if len(parent_breeds) < 2:
            self.data[row_idx][breed_field] = "Mixed"
            return

        expanded = []

        for b in parent_breeds:
            if "x" in b.lower():
                self.data[row_idx][breed_field] = "Mixed"
                return
            expanded.append(b.strip())

        if len(expanded) != 2:
            self.data[row_idx][breed_field] = "Mixed"
            return

        a, b = sorted(expanded)
        self.data[row_idx][breed_field] = f"{a} x {b}"

    def single_parent(self, row_idx, **_):
        sire_field = self._get_field("sire_id")
        dam_field = self._get_field("dam_id")

        choice = random.choice(["sire", "dam"])

        if choice == "sire":
            self.data[row_idx][dam_field] = ""
        else:
            self.data[row_idx][sire_field] = ""

        self._update_index()

    def set_sire_female(self, row_idx, **_):
        sire_field = self._get_field("sire_id")
        id_field = self._get_field("id")
        sex_field = self._get_field("sex")

        females = [
            d
            for d in self.data
            if d.get(sex_field, "").strip().upper() in {"F", "FEMALE"}
        ]

        if females:
            self.data[row_idx][sire_field] = females[0][id_field].strip()

    def set_dam_male(self, row_idx, **_):
        dam_field = self._get_field("dam_id")
        id_field = self._get_field("id")
        sex_field = self._get_field("sex")

        males = [
            d
            for d in self.data
            if d.get(sex_field, "").strip().upper() in {"M", "MALE"}
        ]

        if males:
            self.data[row_idx][dam_field] = males[0][id_field].strip()

    def invalid_name(self, row_idx, **_):
        name_field = self._get_field("name")
        if name_field in self.fieldnames:
            current = self.data[row_idx].get(name_field, "Dog").strip()
            self.data[row_idx][name_field] = f"{current}123"

    def invalid_sex(self, row_idx, **_):
        self._set(row_idx, "sex", "X")

    def select_random_indices(self, range_spec):
        start = range_spec.get("min", 0)
        end = min(range_spec.get("max", len(self.data) - 1), len(self.data) - 1)
        count = min(range_spec.get("count", 1), end - start + 1)
        return random.sample(range(start, end + 1), count)

    def apply_mutation(self, mutation):
        if mutation.target is not None:
            targets = (
                mutation.target
                if isinstance(mutation.target, list)
                else [mutation.target]
            )
            indices = [self._resolve_row_index(t) for t in targets]
        else:
            indices = self.select_random_indices(mutation.range_spec)

        for idx in indices:
            self._apply_to_row(idx, mutation)

    def _apply_to_row(self, row_idx, mutation):
        if not 0 <= row_idx < len(self.data):
            raise ValueError(f"Row index {row_idx} out of bounds")

        handler = self._handlers.get(mutation.type)
        if not handler:
            raise ValueError(f"Unknown mutation type: {mutation.type}")

        handler(row_idx, **(mutation.params or {}))


def load_csv(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def save_csv(filepath, data, fieldnames):
    Path(filepath).parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)


def load_config(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)


def get_output_path(config_path, output_arg):
    if output_arg:
        return output_arg
    return f"data/manipulation/scenarios/{Path(config_path).stem}.csv"


def main():
    parser = argparse.ArgumentParser(description="Mutate pedigree CSV data")
    parser.add_argument("--input", default="data/Dogs Pedigree.csv")
    parser.add_argument("--config", required=True)
    parser.add_argument("--output")
    parser.add_argument("--seed", type=int)
    parser.add_argument("--verbose", action="store_true")

    args = parser.parse_args()

    try:
        data, fieldnames = load_csv(args.input)
        config = load_config(args.config)
    except FileNotFoundError as e:
        sys.exit(f"File error: {e}")
    except json.JSONDecodeError as e:
        sys.exit(f"Invalid JSON: {e}")

    engine = MutationEngine(data, seed=args.seed)
    output_path = get_output_path(args.config, args.output)

    mutations = config.get("mutations", [])

    for spec in mutations:
        mutation = Mutation(
            type=spec["type"],
            target=spec.get("target"),
            range_spec=spec.get("range", {}),
            params=spec.get("params", {}),
        )
        engine.apply_mutation(mutation)

    save_csv(output_path, engine.data, fieldnames)
    print(f"[OK] {output_path}")


if __name__ == "__main__":
    main()
