import pytest
from utils.enums import DataValidationScenario


class TestSingleParent:
    @pytest.mark.testcase("DI015")
    def test_passes_both_parents_defined_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_both_parents_defined(clean_data)

    @pytest.mark.testcase("DI016")
    @pytest.mark.xfail(reason="Single parents undetected without validation")
    def test_detects_incomplete_parentage(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.SINGLE_PARENT
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_both_parents_defined(data)
