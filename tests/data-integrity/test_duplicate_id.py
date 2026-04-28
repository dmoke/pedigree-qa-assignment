import pytest
from utils.enums import DataValidationScenario


class TestDuplicateID:
    @pytest.mark.testcase("DI003")
    def test_passes_unique_ids_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_unique_ids(clean_data)

    @pytest.mark.testcase("DI004")
    @pytest.mark.xfail(reason="Duplicate IDs undetected without validation")
    def test_detects_duplicate_ids(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.DUPLICATE_ID
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_unique_ids(data)
