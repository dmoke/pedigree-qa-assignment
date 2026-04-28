from enum import Enum


class DataValidationScenario(Enum):
    BROKEN_PARENT_REF = "broken-parent-ref"                     # invalid parent relationship in pedigree data
    DUPLICATE_ID = "duplicate-id"                               # duplicate unique identifier exists in dataset
    SELF_PARENTING = "self-parenting"                           # entity incorrectly references itself as parent
    INVALID_MEASUREMENTS_RANGE = "invalid-measurements-range"   # numeric attributes outside valid range >200kg >200cm
    SEX_MISMATCH = "sex-mismatch"                               # biological sex constraint violated in parent relationship
    ANCESTRY_CONFLICT = "ancestry-conflict"                     # no parent should have children among its ancestors
    BREED_MISMATCH = "breed-mismatch"                           # breed consistency rule violated in lineage
    SINGLE_PARENT = "single-parent"                             # only one parent is defined where both are expected
    
    FORMAT_VIOLATION = "format-violation"                       # dataset contains invalid structure or malformed field formatting


    def __str__(self):
        return self.value