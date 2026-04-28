import pytest
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)


@pytest.mark.full_validation
class TestAllValidations:
    @pytest.fixture(autouse=True)
    def setup(self, load_scenario_csv):
        data_path = os.getenv("INTEGRITY_FULL_VALIDATION_DATA_PATH")
        if not data_path:
            pytest.skip("INTEGRITY_FULL_VALIDATION_DATA_PATH not set in .env")
        self.data = load_scenario_csv(path=data_path)

    def test_parent_references(self, integrity_validators):
        integrity_validators.validate_parent_references_exist(self.data)

    def test_unique_ids(self, integrity_validators):
        integrity_validators.validate_unique_ids(self.data)

    def test_no_self_parenting(self, integrity_validators):
        integrity_validators.validate_no_self_parenting(self.data)

    def test_measurement_ranges(self, integrity_validators):
        integrity_validators.validate_measurement_ranges(self.data)

    def test_parent_sex_roles(self, integrity_validators):
        integrity_validators.validate_parent_sex_roles(self.data)

    def test_no_ancestry_conflicts(self, integrity_validators):
        integrity_validators.validate_no_ancestry_conflicts(self.data)

    def test_breed_consistency(self, integrity_validators):
        integrity_validators.validate_breed_consistency(self.data)

    def test_both_parents_defined(self, integrity_validators):
        integrity_validators.validate_both_parents_defined(self.data)

    def test_format(self, integrity_validators):
        integrity_validators.validate_format(self.data)
