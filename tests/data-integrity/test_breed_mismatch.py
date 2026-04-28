import pytest
from utils.enums import DataValidationScenario


class TestBreedMismatch:
    @pytest.mark.testcase("DI013")
    def test_passes_consistent_breeds_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_breed_consistency(clean_data)

    @pytest.mark.testcase("DI014")
    @pytest.mark.xfail(reason="Breed mismatches undetected without validation")
    def test_detects_inheritance_rule_violations(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.BREED_MISMATCH
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_breed_consistency(data)
