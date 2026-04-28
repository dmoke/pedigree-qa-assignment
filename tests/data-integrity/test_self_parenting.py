import pytest
from utils.enums import DataValidationScenario


class TestSelfParenting:
    @pytest.mark.testcase("DI005")
    def test_passes_no_self_parenting_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_no_self_parenting(clean_data)

    @pytest.mark.testcase("DI006")
    @pytest.mark.xfail(reason="Self-parenting undetected without validation")
    def test_detects_self_references(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.SELF_PARENTING
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_no_self_parenting(data)
