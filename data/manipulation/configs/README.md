# Config Examples

```json
{
  "mutations": [
    {
      "type": "break_parent_ref",
      "target": 5,
      "params": { "parent_type": "sire" }
    },
    { "type": "duplicate_id", "target": 10, "params": { "source_idx": 5 } },
    { "type": "create_cycle", "target": 15, "params": { "target_idx": 20 } },
    { "type": "self_parenting", "target": 8, "params": { "mode": "both" } },
    {
      "type": "invalid_measurement",
      "target": 3,
      "params": { "fld": "height_cm", "value": "-10" }
    },
    { "type": "breed_mismatch", "target": 7 },
    { "type": "single_parent", "target": 12 },
    { "type": "set_sire_female", "target": 4 },
    { "type": "set_dam_male", "target": 6 },
    { "type": "invalid_name", "target": 9 },
    { "type": "invalid_sex", "target": 11 },
    {
      "type": "rewrite_parent_ref",
      "target": 2,
      "params": { "parent_type": "dam", "target_id": "DOG123" }
    }
  ]
}
```

## Mutation Types

| Type                  | Params                     |
| --------------------- | -------------------------- |
| `break_parent_ref`    | `parent_type` (sire\|dam)  |
| `rewrite_parent_ref`  | `parent_type`, `target_id` |
| `duplicate_id`        | `source_idx`               |
| `create_cycle`        | `target_idx`               |
| `self_parenting`      | `mode` (sire\|dam\|both)   |
| `invalid_measurement` | `fld`, `value`             |
| `breed_mismatch`      | `forced_breed` (optional)  |
| `single_parent`       | —                          |
| `set_sire_female`     | —                          |
| `set_dam_male`        | —                          |
| `invalid_name`        | —                          |
| `invalid_sex`         | —                          |

## Targeting

**Specific row**: `"target": 5`

**Random range**:

```json
"range": {"min": 0, "max": 100, "count": 5}
```
