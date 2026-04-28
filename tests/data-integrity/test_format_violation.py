import pytest
from utils.enums import DataValidationScenario


class TestFormatViolation:
    @pytest.mark.testcase("DI017")
    def test_passes_valid_format_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_format(clean_data)

    @pytest.mark.testcase("DI018")
    @pytest.mark.xfail(reason="Format violations undetected without validation")
    def test_detects_format_violations(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.FORMAT_VIOLATION
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_format(data)
