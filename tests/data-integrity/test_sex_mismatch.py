import pytest
from utils.enums import DataValidationScenario


class TestSexMismatch:
    @pytest.mark.testcase("DI007")
    def test_passes_correct_parent_sexes_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_parent_sex_roles(clean_data)

    @pytest.mark.testcase("DI008")
    @pytest.mark.xfail(reason="Sex mismatches undetected without validation")
    def test_detects_incorrect_parent_sex(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.SEX_MISMATCH
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_parent_sex_roles(data)
