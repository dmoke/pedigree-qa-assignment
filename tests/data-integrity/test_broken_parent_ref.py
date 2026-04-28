import pytest
from utils.enums import DataValidationScenario


class TestBrokenParentRef:
    @pytest.mark.testcase("DI001")
    def test_passes_valid_parent_references_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_parent_references_exist(clean_data)

    @pytest.mark.testcase("DI002")
    @pytest.mark.xfail(reason="Broken parent references undetected without validation")
    def test_detects_nonexistent_parent_references(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.BROKEN_PARENT_REF
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_parent_references_exist(data)
