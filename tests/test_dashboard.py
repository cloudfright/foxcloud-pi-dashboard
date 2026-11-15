import pytest

from foxcloud_pi_dashboard.pidisplay.dashboard import Dashboard


@pytest.fixture
def dashboard():
    dashboard = Dashboard.__new__(Dashboard)
    dashboard.pv_power = 0
    dashboard.bat_charge_power = 0
    dashboard.bat_discharge_power = 0
    dashboard.feedin_power = 0
    dashboard.grid_consumption_power = 0
    dashboard.loads_power = 0
    return dashboard


@pytest.mark.parametrize(
    ("grid_consumption_power", "expected"),
    [
        (0.199, "#00FF00"),
        (0.2, "#FF0000"),
    ],
)
def test_home_load_text_colour(dashboard, grid_consumption_power, expected):
    dashboard.grid_consumption_power = grid_consumption_power

    assert dashboard._get_home_load_text_colour() == expected


@pytest.mark.parametrize(
    ("feedin_power", "grid_consumption_power", "bat_discharge_power", "pv_power", "expected"),
    [
        (0.201, 0.5, 0, 0, "#0000FF"),
        (0.2, 0.199, 0, 0, "#00FF00"),
        (0, 0.2, 0, 0, "#FF0000"),
        (0, 0.2, 0.1, 0, "#FFBF00"),
        (0, 0.2, 0, 0.1, "#FFBF00"),
    ],
)
def test_grid_text_colour(
    dashboard,
    feedin_power,
    grid_consumption_power,
    bat_discharge_power,
    pv_power,
    expected,
):
    dashboard.feedin_power = feedin_power
    dashboard.grid_consumption_power = grid_consumption_power
    dashboard.bat_discharge_power = bat_discharge_power
    dashboard.pv_power = pv_power

    assert dashboard._get_grid_text_colour() == expected


@pytest.mark.parametrize(
    ("pv_power", "expected"),
    [
        (0, "#FF0000"),
        (0.1, "#FFBF00"),
        (0.7, "#FFBF00"),
        (0.701, "#00FF00"),
    ],
)
def test_solar_text_colour(dashboard, pv_power, expected):
    dashboard.pv_power = pv_power

    assert dashboard._get_solar_text_colour() == expected


@pytest.mark.parametrize(
    ("bat_charge_power", "bat_discharge_power", "expected"),
    [
        (0, 0, "#FF0000"),
        (0, 0.1, "#FFBF00"),
        (0.1, 0, "#00FF00"),
        (0.1, 0.1, "#00FF00"),
    ],
)
def test_battery_text_colour(dashboard, bat_charge_power, bat_discharge_power, expected):
    dashboard.bat_charge_power = bat_charge_power
    dashboard.bat_discharge_power = bat_discharge_power

    assert dashboard._get_battery_text_colour() == expected


def test_self_use_percent(dashboard):
    dashboard.pv_power = 2
    dashboard.bat_discharge_power = 0.5
    dashboard.feedin_power = 0.25
    dashboard.bat_charge_power = 0.25
    dashboard.loads_power = 4

    assert dashboard._get_self_use_percent() == 50