import pytest
from utils.enums import DataValidationScenario


class TestMeasurements:
    @pytest.mark.testcase("DI009")
    def test_passes_valid_measurements_on_clean_data(self, clean_data, integrity_validators):
        integrity_validators.validate_measurement_ranges(clean_data)

    @pytest.mark.testcase("DI010")
    @pytest.mark.xfail(reason="Invalid measurements undetected without validation")
    def test_detects_out_of_range_measurements(self, load_scenario_csv, integrity_validators):
        scenario = DataValidationScenario.INVALID_MEASUREMENTS_RANGE
        data = load_scenario_csv(str(scenario))
        integrity_validators.validate_measurement_ranges(data)
