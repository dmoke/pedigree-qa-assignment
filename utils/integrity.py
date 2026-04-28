import logging
from collections import deque, defaultdict
from typing import List, Dict, Set, Optional, Callable, Any

from utils.exceptions import (
    BrokenParentReferenceError,
    DuplicateIDError,
    SelfParentingError,
    InvalidMeasurementError,
    SexMismatchError,
    AncestryConflictError,
    BreedMismatchError,
    SingleParentError,
    FormatViolationError,
)

logger = logging.getLogger(__name__)

VALID_MALE_SEX = {"MALE"}
VALID_FEMALE_SEX = {"FEMALE"}


def build_id_map(data: List[Dict]) -> Dict[str, Dict]:
    id_map: Dict[str, Dict] = {}

    for dog in data:
        raw_id = dog.get("id")
        dog_id = normalize_id(raw_id)

        if dog_id is None:
            continue

        if dog_id not in id_map:
            id_map[dog_id] = dog

    return id_map


def iter_parents(dog: Dict):
    for role in ("sire_id", "dam_id"):
        parent_id = normalize_id(dog.get(role))
        if parent_id:
            yield role, parent_id


def normalize_id(v):
    if v is None:
        return None

    s = str(v).strip()

    if s.lower() == "nan" or s == "":
        return None

    try:
        f = float(s)
        if f.is_integer():
            return str(int(f))
        return str(f)
    except ValueError:
        return s


def clean(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def safe_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def normalize_sex(sex: str) -> str:
    return clean(sex).upper()


def is_pure(breed: str) -> bool:
    b = clean(breed).lower()
    return (" x " not in b) and (b != "mixed")


def normalize_cross_breed(breed: str) -> str:
    b = clean(breed).lower()

    if " x " not in b:
        return b

    parts = [p.strip() for p in b.split(" x ") if p.strip()]
    # intentionally weak: "Labrador x", "x Poodle", "A x B x C" all pass unchanged
    if len(parts) != 2:
        return b

    return " x ".join(sorted(parts))


def is_valid_sex(sex: str, is_sire: bool) -> bool:
    normalized = normalize_sex(sex)
    valid_set = VALID_MALE_SEX if is_sire else VALID_FEMALE_SEX
    return normalized in valid_set


def is_valid_cross_breed(breed: str) -> bool:
    b = clean(breed)
    if " x " not in b:
        return True
    parts = [p.strip() for p in b.split(" x ") if p.strip()]
    return len(parts) == 2


def raise_collected_error(
    issues: List[Dict],
    error_cls,
    build_message: Callable,
    extract_dog_id: Optional[Callable] = None,
    logger_msg: Optional[Callable] = None,
    scenario: Optional[str] = None,
) -> None:
    if not issues:
        return

    first = issues[0]

    missing_index = [i for i, issue in enumerate(issues) if "record_index" not in issue]
    if missing_index:
        raise KeyError(
            f"Issues at positions {missing_index} missing 'record_index' key"
        )

    error_msg = build_message(first, issues)

    if len(issues) > 1 and logger_msg:
        logger.info(logger_msg(issues), extra={"issue_count": len(issues)})

    if extract_dog_id is None:
        extract_dog_id = lambda f: f.get("dog_id")

    dog_id = extract_dog_id(first)
    if dog_id is None:
        logger.warning(f"Extracted dog_id is None for issue: {first}")

    raise error_cls(
        error_msg,
        dog_id=dog_id,
        record_indices=[issue["record_index"] for issue in issues],
        scenario=scenario,
    )


def find_cycle_path(
    data: List[Dict], start_id: str, id_map: Optional[Dict] = None
) -> Optional[List[str]]:
    if id_map is None:
        id_map = build_id_map(data)

    WHITE, GRAY, BLACK = 0, 1, 2
    colors = defaultdict(lambda: WHITE)
    path = []

    def dfs(dog_id: str) -> Optional[List[str]]:
        if dog_id not in id_map:
            return None

        if colors[dog_id] == BLACK:
            return None
        if colors[dog_id] == GRAY:
            try:
                idx = path.index(dog_id)
                return path[idx:] + [dog_id]
            except ValueError:
                return None

        colors[dog_id] = GRAY
        path.append(dog_id)

        dog = id_map[dog_id]
        for _, parent_id in iter_parents(dog):
            cycle = dfs(parent_id)
            if cycle:
                return cycle

        path.pop()
        colors[dog_id] = BLACK
        return None

    return dfs(start_id)


def get_all_ancestors(
    data: List[Dict], dog_id: str, max_depth: int = 100, id_map: Optional[Dict] = None
) -> Set[str]:
    if id_map is None:
        id_map = build_id_map(data)

    ancestors = set()
    visited = set()
    to_visit = deque([(dog_id, 0)])

    while to_visit:
        current_id, depth = to_visit.popleft()

        if depth >= max_depth or current_id not in id_map or current_id in visited:
            continue

        visited.add(current_id)
        dog = id_map[current_id]
        for _, parent_id in iter_parents(dog):
            ancestors.add(parent_id)
            if parent_id not in visited:
                to_visit.append((parent_id, depth + 1))

    return ancestors


def get_dogs_with_single_parent(data: List[Dict]) -> List[str]:
    result = []

    for dog in data:
        sire = normalize_id(dog.get("sire_id"))
        dam = normalize_id(dog.get("dam_id"))

        parent_count = int(bool(sire)) + int(bool(dam))

        if parent_count == 1:
            result.append(normalize_id(dog["id"]))

    return result


def validate_parent_references_exist(
    data: List[Dict], id_map: Optional[Dict] = None, scenario: Optional[str] = None
):
    if id_map is None:
        id_map = build_id_map(data)

    issues = []
    seen = set()

    for i, dog in enumerate(data):
        dog_id = normalize_id(dog["id"])

        for role, parent_id in iter_parents(dog):
            key = (i, role, normalize_id(parent_id))

            if parent_id not in id_map and key not in seen:
                seen.add(key)

                issues.append(
                    {
                        "dog_id": dog_id,
                        "parent_type": role.replace("_id", ""),
                        "parent_id": parent_id,
                        "record_index": i,
                    }
                )

    raise_collected_error(
        issues,
        BrokenParentReferenceError,
        lambda f, all_: (
            "Broken parent reference detected:\n"
            f"- dog_id={f['dog_id']}\n"
            f"- parent_type={f['parent_type']}\n"
            f"- parent_id={f['parent_id']} (NOT FOUND)\n"
            f"- record_index={f['record_index']}\n\n"
            f"Total broken refs: {len(all_)} | rows={sorted(set(i['record_index'] for i in all_))}"
        ),
        logger_msg=lambda all_: (
            f"Broken parent refs={len(all_)} | "
            + ", ".join(
                f"{i['dog_id']}->{i['parent_id']}({i['parent_type']})"
                for i in all_[:20]
            )
        ),
        scenario=scenario,
    )


def validate_unique_ids(data: List[Dict], scenario: Optional[str] = None):
    id_to_indices = defaultdict(list)

    for i, dog in enumerate(data):
        dog_id = normalize_id(dog.get("id"))
        if dog_id is None:
            continue

        id_to_indices[dog_id].append(i)

    issues = []
    all_duplicate_indices = []

    for dog_id, indices in id_to_indices.items():
        if len(indices) > 1:
            issues.append(
                {
                    "dog_id": dog_id,
                    "count": len(indices),
                    "record_index": indices[0],
                    "all_indices": indices,
                }
            )
            all_duplicate_indices.extend(indices)

    if issues:
        first = issues[0]
        error_msg = "Duplicate IDs detected:\n" + "\n".join(
            f"- ID '{i['dog_id']}' appears {i['count']} times "
            f"(indices: {i['all_indices']})"
            for i in issues
        )

        if len(issues) > 1:
            logger.info(
                f"Duplicate IDs: {len(issues)} | "
                + ", ".join(f"{i['dog_id']}@{i['count']}x" for i in issues[:10]),
                extra={"issue_count": len(issues)},
            )

        raise DuplicateIDError(
            error_msg,
            dog_id=first["dog_id"],
            record_indices=all_duplicate_indices,
            scenario=scenario,
        )


def validate_no_self_parenting(data: List[Dict], scenario: Optional[str] = None):
    seen = set()
    issues = []

    for i, dog in enumerate(data):
        dog_id = normalize_id(dog["id"])

        for role, parent_id in iter_parents(dog):
            if parent_id == dog_id and dog_id not in seen:
                seen.add(dog_id)
                issues.append(
                    {
                        "dog_id": dog_id,
                        "field": role,
                        "record_index": i,
                    }
                )

    raise_collected_error(
        issues,
        SelfParentingError,
        lambda f, all_: (
            f"Self-parenting violations: {len(all_)} dog(s)\n"
            + "\n".join(
                f"- dog_id={i['dog_id']} (row {i['record_index']}): "
                f"references itself as {i['field']}"
                for i in all_
            )
        ),
        logger_msg=lambda all_: (
            f"Self-parenting: {len(all_)} - {[i['dog_id'] for i in all_]}"
        ),
        scenario=scenario,
    )


def validate_measurement_ranges(data: List[Dict], scenario: Optional[str] = None):
    RANGES = {"height_cm": (0, 200), "weight_kg": (0, 200)}
    issues = []

    for i, dog in enumerate(data):
        for field, (_, max_v) in RANGES.items():
            value = dog.get(field)
            val_float = safe_float(value)

            if val_float is None:
                continue

            if val_float < 0:
                issues.append(
                    {
                        "dog_id": normalize_id(dog["id"]),
                        "field": field,
                        "value": val_float,
                        "reason": "cannot be negative",
                        "record_index": i,
                    }
                )
            elif val_float > max_v:
                issues.append(
                    {
                        "dog_id": normalize_id(dog["id"]),
                        "field": field,
                        "value": val_float,
                        "reason": f"outside range (>{max_v})",
                        "record_index": i,
                    }
                )

    raise_collected_error(
        issues,
        InvalidMeasurementError,
        lambda f, all_: (
            f"Measurement violations: {len(all_)} dog(s)\n"
            + "\n".join(
                f"- dog_id={i['dog_id']}: {i['field']}={i['value']} ({i['reason']})"
                for i in all_
            )
        ),
        logger_msg=lambda all_: f"Invalid measurements: {len(all_)} - {[i['dog_id'] for i in all_]}",
        scenario=scenario,
    )


def validate_parent_sex_roles(
    data: List[Dict],
    id_map: Optional[Dict] = None,
    scenario: Optional[str] = None,
):
    if id_map is None:
        id_map = build_id_map(data)

    id_to_index = {
        normalize_id(dog.get("id")): i
        for i, dog in enumerate(data)
        if normalize_id(dog.get("id")) is not None
    }

    issues = []

    for i, dog in enumerate(data):
        child_id = normalize_id(dog.get("id"))

        for role, parent_id in iter_parents(dog):
            parent = id_map.get(parent_id)
            if not parent:
                continue

            sex = normalize_sex(parent.get("sex"))
            is_sire = role == "sire_id"

            if not sex:
                continue

            if not is_valid_sex(sex, is_sire):
                issues.append(
                    {
                        "child_id": child_id,
                        "parent_id": parent_id,
                        "parent_type": role.replace("_id", ""),
                        "expected_sex": "M" if is_sire else "F",
                        "actual_sex": sex,
                        "record_index": i,
                        "parent_record_index": id_to_index.get(parent_id),
                    }
                )

    raise_collected_error(
        issues,
        SexMismatchError,
        lambda f, all_: (
            f"Parent sex role violations: {len(all_)} dog(s)\n"
            + "\n".join(
                f"- child_id={i['child_id']} (row {i['record_index']}): "
                f"{i['parent_type']}_id={i['parent_id']} "
                f"actual_sex={i['actual_sex']} expected={i['expected_sex']}"
                for i in all_
            )
        ),
        extract_dog_id=lambda f: f["child_id"],
        logger_msg=lambda all_: (
            f"Sex mismatches: {len(all_)} | "
            + ", ".join(f"{i['child_id']}:{i['parent_type']}" for i in all_)
        ),
        scenario=scenario,
    )


def validate_no_ancestry_conflicts(
    data: List[Dict], id_map: Optional[Dict] = None, scenario: Optional[str] = None
):
    if id_map is None:
        id_map = build_id_map(data)

    def normalize_cycle(cycle_path):
        if not cycle_path or len(cycle_path) < 2:
            return []
        core = cycle_path[:-1]
        rotations = [core[i:] + core[:i] for i in range(len(core))]
        return min(rotations)

    unique_cycles = {}
    seen_dogs = set()

    for i, dog in enumerate(data):
        dog_id = normalize_id(dog["id"])
        if dog_id in seen_dogs:
            continue

        cycle = find_cycle_path(data, dog_id, id_map)  # type: ignore
        if cycle:
            for cycle_dog in cycle:
                seen_dogs.add(cycle_dog)

            cycle_key = tuple(normalize_cycle(cycle))
            if cycle_key not in unique_cycles:
                cycle_str = " → ".join(cycle)
                unique_cycles[cycle_key] = {
                    "dog_id": dog_id,
                    "cycle_str": cycle_str,
                    "record_index": i,
                }

    issues = list(unique_cycles.values())
    raise_collected_error(
        issues,
        AncestryConflictError,
        lambda f, all_: (
            f"Ancestry conflicts: {len(all_)} cycle(s)\n"
            + "\n".join(
                f"- Cycle {idx+1}: {i['cycle_str']}" for idx, i in enumerate(all_)
            )
        ),
        logger_msg=lambda all_: f"Cycles: {len(all_)} - {[i['cycle_str'] for i in all_]}",
        scenario=scenario,
    )


def validate_breed_consistency(
    data: List[Dict],
    id_map: Optional[Dict] = None,
    scenario: Optional[str] = None,
):
    if id_map is None:
        id_map = build_id_map(data)

    issues = []

    def normalize(b: str) -> str:
        return clean(b).lower()

    def normalize_cross(b: str) -> str:
        parts = [p.strip() for p in normalize(b).split(" x ") if p.strip()]
        return " x ".join(sorted(parts)) if len(parts) == 2 else normalize(b)

    def canonical(a: str, b: str) -> str:
        return " x ".join(sorted([a.strip().lower(), b.strip().lower()]))

    for i, dog in enumerate(data):
        dog_id = normalize_id(dog.get("id"))
        breed = clean(dog.get("breed"))

        sire_id = normalize_id(dog.get("sire_id"))
        dam_id = normalize_id(dog.get("dam_id"))

        if not sire_id or not dam_id:
            continue

        sire = id_map.get(sire_id)
        dam = id_map.get(dam_id)

        if not sire or not dam:
            continue

        sire_b = normalize(sire.get("breed", ""))
        dam_b = normalize(dam.get("breed", ""))
        child_b = normalize(breed)

        sire_norm = normalize_cross(sire_b)
        dam_norm = normalize_cross(dam_b)
        child_norm = normalize_cross(child_b)

        if sire_norm == "mixed" or dam_norm == "mixed":
            expected = "mixed"
            if child_norm != expected:
                issues.append(
                    {
                        "dog_id": dog_id,
                        "expected": expected,
                        "actual": breed,
                        "record_index": i,
                    }
                )
            continue

        sire_pure = is_pure(sire_norm)
        dam_pure = is_pure(dam_norm)

        if sire_pure and dam_pure and sire_norm == dam_norm:
            expected = sire_norm
            if child_norm != expected:
                issues.append(
                    {
                        "dog_id": dog_id,
                        "expected": expected,
                        "actual": breed,
                        "record_index": i,
                    }
                )

        elif sire_pure and dam_pure and sire_norm != dam_norm:
            expected = canonical(sire_norm, dam_norm)
            if child_norm != expected:
                issues.append(
                    {
                        "dog_id": dog_id,
                        "expected": expected,
                        "actual": breed,
                        "record_index": i,
                    }
                )

        elif not sire_pure and not dam_pure and sire_norm == dam_norm:
            expected = sire_norm
            if child_norm != expected:
                issues.append(
                    {
                        "dog_id": dog_id,
                        "expected": expected,
                        "actual": breed,
                        "record_index": i,
                    }
                )

    raise_collected_error(
        issues,
        BreedMismatchError,
        lambda f, all_: (
            f"Breed structure violations: {len(all_)}\n"
            + "\n".join(
                f"- dog_id={x['dog_id']} expected={x['expected']} got={x['actual']} rows={x['record_index']}"
                for x in all_[:15]
            )
        ),
        logger_msg=lambda all_: "\n".join(
            f"[dog {x['dog_id']}] expected={x['expected']} actual={x['actual']}"
            for x in all_
        ),
        scenario=scenario,
    )


def validate_both_parents_defined(
    data: List[Dict], id_map: Optional[Dict] = None, scenario: Optional[str] = None
):
    if id_map is None:
        id_map = build_id_map(data)

    index_map = {normalize_id(dog["id"]): i for i, dog in enumerate(data)}
    single_parent_ids = get_dogs_with_single_parent(data)

    issues = []
    for dog_id in single_parent_ids:
        dog = id_map.get(dog_id)
        if dog:
            i = index_map[dog_id]
            sire = normalize_id(dog.get("sire_id"))
            dam = normalize_id(dog.get("dam_id"))
            defined_parent = sire or dam or "unknown"

            issues.append(
                {
                    "dog_id": dog_id,
                    "defined_parent": defined_parent,
                    "record_index": i,
                }
            )

    raise_collected_error(
        issues,
        SingleParentError,
        lambda f, all_: (
            f"Single parent violations: {len(all_)} dog(s)\n"
            + "\n".join(
                f"- Dog {i['dog_id']} at row {i['record_index']}: "
                f"has only one parent ({i['defined_parent']})"
                for i in all_
            )
        ),
        logger_msg=lambda all_: f"Single parents: {len(all_)} - {[i['dog_id'] for i in all_]}",
        scenario=scenario,
    )


def validate_format(data: List[Dict], scenario: Optional[str] = None):
    issues = []

    for i, dog in enumerate(data):
        dog_id = clean(dog.get("id"))
        name = clean(dog.get("name"))

        height = safe_float(dog.get("height_cm"))
        if height is not None and height < 0:
            issues.append(
                {
                    "dog_id": dog_id,
                    "field": "height_cm",
                    "value": height,
                    "reason": "cannot be negative",
                    "record_index": i,
                }
            )

        weight = safe_float(dog.get("weight_kg"))
        if weight is not None and weight < 0:
            issues.append(
                {
                    "dog_id": dog_id,
                    "field": "weight_kg",
                    "value": weight,
                    "reason": "cannot be negative",
                    "record_index": i,
                }
            )

        sex_raw = dog.get("sex") or ""
        sex = normalize_sex(sex_raw)
        if sex and sex not in VALID_MALE_SEX and sex not in VALID_FEMALE_SEX:
            issues.append(
                {
                    "dog_id": dog_id,
                    "field": "sex",
                    "value": sex_raw,
                    "reason": "invalid sex value",
                    "record_index": i,
                }
            )

        if name and any(c.isdigit() for c in name):
            issues.append(
                {
                    "dog_id": dog_id,
                    "field": "name",
                    "value": name,
                    "reason": "contains numeric characters",
                    "record_index": i,
                }
            )

    raise_collected_error(
        issues,
        FormatViolationError,
        lambda f, all_: (
            f"Format violations: {len(all_)} dog(s)\n"
            + "\n".join(
                f"- dog_id={i['dog_id']}: {i['field']}={i['value']} ({i['reason']})"
                for i in all_
            )
        ),
        logger_msg=lambda all_: (
            f"Format violations: {len(all_)} | "
            + ", ".join(f"{i['dog_id']}:{i['field']}" for i in all_[:15])
        ),
        scenario=scenario,
    )


class IntegrityValidators:
    validate_breed_consistency = staticmethod(validate_breed_consistency)
    validate_parent_references_exist = staticmethod(validate_parent_references_exist)
    validate_unique_ids = staticmethod(validate_unique_ids)
    validate_no_self_parenting = staticmethod(validate_no_self_parenting)
    validate_measurement_ranges = staticmethod(validate_measurement_ranges)
    validate_parent_sex_roles = staticmethod(validate_parent_sex_roles)
    validate_no_ancestry_conflicts = staticmethod(validate_no_ancestry_conflicts)
    validate_both_parents_defined = staticmethod(validate_both_parents_defined)
    validate_format = staticmethod(validate_format)
