import pytest
from utils.enums import DataValidationScenario


class TestAncestryConflict:
    @pytest.mark.testcase("DI011")
    def test_passes_no_conflicts_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_no_ancestry_conflicts(clean_data)

    @pytest.mark.testcase("DI012")
    @pytest.mark.xfail(reason="Scenario-based expected failure")
    def test_detects_pedigree_cycles(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.ANCESTRY_CONFLICT
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_no_ancestry_conflicts(data)
