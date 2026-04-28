# Data Mutation System

Generate pedigree test scenarios with targeted data flaws.

## Quick Start

```bash
# Generate broken parent reference scenario
python data/manipulation/mutate.py --config data/manipulation/configs/broken-parent-ref.json

# With custom input/output
python data/manipulation/mutate.py --input data/Dogs.csv --config config.json --output out.csv

# Reproducible random mutations
python data/manipulation/mutate.py --config config.json --seed 42
```

## Mutation Types

| Type | Purpose |
|------|---------|
| `break_parent_ref` | Parent ID references non-existent dog (default: 99999) |
| `rewrite_parent_ref` | Replace parent ID with specific target ID |
| `duplicate_id` | Copy ID from another dog (creates duplicates) |
| `create_cycle` | Create bidirectional parent-child cycle |
| `self_parenting` | Dog is its own sire/dam (or both) |
| `invalid_measurement` | Set negative/invalid measurement value |
| `breed_mismatch` | Violate breed inheritance rules |
| `single_parent` | Remove dam reference (orphan dam) |
| `set_sire_female` | Assign female dog as sire |
| `set_dam_male` | Assign male dog as dam |
| `invalid_name` | Append invalid characters to name |
| `invalid_sex` | Set sex to invalid value (e.g., "X") |

## Arguments

- `--config` (required): JSON config file
- `--input`: Input CSV (default: `data/Dogs Pedigree.csv`)
- `--output`: Output CSV (default: `data/manipulation/scenarios/{config_name}.csv`)
- `--seed`: Random seed for reproducibility
- `--verbose`: Show mutation details