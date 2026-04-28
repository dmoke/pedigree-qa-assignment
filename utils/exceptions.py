"""
Pedigree data integrity exceptions for CSV and dataset validation.
"""

from utils.enums import DataValidationScenario


class PedigreeIntegrityError(Exception):
    default_message = "Pedigree integrity error"

    def __init__(
        self,
        message=None,
        dog_id=None,
        field=None,
        value=None,
        related_id=None,
        record_indices=None,
        scenario=None,
    ):
        self.message = message or self.default_message
        self.dog_id = dog_id
        self.field = field
        self.value = value
        self.related_id = related_id
        self.record_indices = record_indices or []
        self.scenario = scenario

        super().__init__(self._format_message())

    def _format_message(self):
        parts = [self.message]

        if self.dog_id is not None:
            parts.append(f"dog_id={self.dog_id}")
        if self.field:
            parts.append(f"field={self.field}")
        if self.value is not None:
            parts.append(f"value={self.value}")
        if self.related_id is not None:
            parts.append(f"related_id={self.related_id}")
        if self.record_indices:
            parts.append(f"rows={self.record_indices}")
        if self.scenario:
            parts.append(f"scenario=data/manipulation/scenarios/{self.scenario}.csv")

        return " | ".join(parts)


class DuplicateIDError(PedigreeIntegrityError):
    default_message = "Duplicate dog ID found in dataset"


class BrokenParentReferenceError(PedigreeIntegrityError):
    default_message = "Parent reference points to a non-existent dog ID"


class SelfParentingError(PedigreeIntegrityError):
    default_message = "A dog cannot reference itself as a parent"


class InvalidMeasurementError(PedigreeIntegrityError):
    default_message = "Invalid measurement value (height/weight out of range)"


class SexMismatchError(PedigreeIntegrityError):
    default_message = "Sire must be male and dam must be female"


class AncestryConflictError(PedigreeIntegrityError):
    default_message = "Ancestry conflict: parent found in child's ancestors"


class BreedMismatchError(PedigreeIntegrityError):
    default_message = "Breed consistency rule violated in lineage"


class SingleParentError(PedigreeIntegrityError):
    default_message = "Only one parent is defined where both are expected"


class FormatViolationError(PedigreeIntegrityError):
    default_message = "Dataset contains invalid structure or malformed field formatting"


class ConflictingRecordError(PedigreeIntegrityError):
    default_message = "Conflicting records detected for the same entity"


class IDFormatError(PedigreeIntegrityError):
    default_message = "Invalid dog ID format"


class InvalidParentFormatError(PedigreeIntegrityError):
    default_message = "Invalid parent reference format (sire_id/dam_id)"


class NonexistentParentError(PedigreeIntegrityError):
    default_message = "Referenced parent does not exist in dataset"


class SameSireAndDamError(PedigreeIntegrityError):
    default_message = "Sire and dam cannot reference the same dog"


class AgeLogicError(PedigreeIntegrityError):
    default_message = "Parent must be older than offspring"


class DuplicateAncestorError(PedigreeIntegrityError):
    default_message = "Duplicate ancestor detected in pedigree tree"


class PedigreeDepthExceededError(PedigreeIntegrityError):
    default_message = "Pedigree depth exceeds allowed limit"


class MissingRequiredFieldError(PedigreeIntegrityError):
    default_message = "Required field is missing from record"


class InvalidNullValueError(PedigreeIntegrityError):
    default_message = "Null value not allowed for this field"


class DataTypeError(PedigreeIntegrityError):
    default_message = "Invalid data type for field"


class WhitespaceError(PedigreeIntegrityError):
    default_message = "Unexpected whitespace in field value"


ERROR_TYPE_MAP = {
    DataValidationScenario.BROKEN_PARENT_REF.value: BrokenParentReferenceError,
    DataValidationScenario.DUPLICATE_ID.value: DuplicateIDError,
    DataValidationScenario.SELF_PARENTING.value: SelfParentingError,
    DataValidationScenario.INVALID_MEASUREMENTS_RANGE.value: InvalidMeasurementError,
    DataValidationScenario.SEX_MISMATCH.value: SexMismatchError,
    DataValidationScenario.ANCESTRY_CONFLICT.value: AncestryConflictError,
    DataValidationScenario.BREED_MISMATCH.value: BreedMismatchError,
    DataValidationScenario.SINGLE_PARENT.value: SingleParentError,
    DataValidationScenario.FORMAT_VIOLATION.value: FormatViolationError,
}


def get_exception_for_error_type(error_type: str):
    return ERROR_TYPE_MAP.get(error_type, PedigreeIntegrityError)
