"""Tests du parseur でんき予報 sur de vrais CSV (tests/fixtures) et des cas synthétiques."""

from pathlib import Path

import pytest

from jp_parser import JST, decode_csv, parse_denki_yoho

FIXTURES = Path(__file__).parent / "fixtures"
AREAS = [
    "hokkaido", "tohoku", "tepco", "chubu", "hokuriku",
    "kansai", "chugoku", "shikoku", "kyushu", "okinawa",
]
COMMON = {
    "consumption", "forecast", "supply_capacity", "utilization",
    "peak_forecast", "peak_supply_capacity", "peak_reserve_margin", "solar",
}


def load(area: str) -> dict:
    return parse_denki_yoho(decode_csv((FIXTURES / f"{area}.csv").read_bytes()))


@pytest.mark.parametrize("area", AREAS)
def test_fixture_parses(area):
    data = load(area)
    assert COMMON <= data["available"]
    assert data["updated"] is not None and data["updated"].tzinfo == JST
    assert data["consumption"] > 0
    assert data["consumption_time"].date() == data["updated"].date()
    assert data["forecast"] > 0
    assert data["supply_capacity"] >= data["consumption"] * 0.5
    assert 0 < data["utilization"] <= 120
    assert data["peak_forecast"] > 0
    assert data["peak_forecast_slot"]
    assert data["peak_supply_capacity"] >= data["peak_forecast"]
    assert data["peak_reserve_margin"] is not None
    assert data["solar"] is not None
    # unité : les valeurs sont en MW (万kW x 10)
    assert data["consumption"] % 10 == 0


def test_wind_only_tohoku():
    assert "wind" in load("tohoku")["available"]
    assert load("tohoku")["wind"] is not None
    for area in AREAS:
        if area != "tohoku":
            assert "wind" not in load(area)["available"]


def test_tepco_known_values():
    """Valeurs vérifiées à la main dans le fichier tests/fixtures/tepco.csv."""
    data = load("tepco")
    assert data["consumption"] == 2885 * 10  # dernière ligne 5 min non vide (23:30)
    assert (data["consumption_time"].hour, data["consumption_time"].minute) == (23, 30)
    assert data["forecast"] == 2851 * 10  # créneau 23:00 (le 23:00 réalisé vaut 0 = vide)
    assert data["supply_capacity"] == 3781 * 10
    assert data["utilization"] == 76  # dernière heure réalisée (22:00)
    assert data["peak_forecast"] == 3736 * 10
    assert data["peak_forecast_slot"] == "16:00~17:00"
    assert data["peak_reserve_margin"] == 11
    assert data["peak_supply_capacity"] == 4149 * 10


def test_okinawa_empty_cells():
    data = load("okinawa")  # 23:00 : réalisé et 使用率 vides
    assert data["consumption"] == 78 * 10
    assert data["utilization"] == 69


SYNTH = """2026/06/01 12:10 UPDATE
ピーク時供給力(万kW),時間帯,供給力情報更新日,供給力情報更新時刻,ピーク時予備率(%),ピーク時使用率(%)
500,13:00〜14:00,6/1,11:00,10,90

予想最大電力(万kW),時間帯,予想最大電力情報更新日,予想最大電力情報更新時刻
450,13:00〜14:00,6/1,11:00

DATE,TIME,当日実績(万kW),予測値(万kW),使用率(%),供給力(万kW)
2026/06/01,10:00,400,402,80,500
2026/06/01,11:00,410,415,82,510
2026/06/01,12:00,0,420,,520
2026/06/01,13:00,,430,,530

翌日のピーク時供給力(万kW),時間帯,供給力情報更新日,供給力情報更新時刻,ピーク時予備率(%),ピーク時使用率(%)
999,9:00〜10:00,6/1,11:00,99,99

DATE,TIME,当日実績(５分間隔値)(万kW),太陽光発電実績(５分間隔値)(万kW)
2026/06/01,12:00,415,60
2026/06/01,12:05,417,62
2026/06/01,12:10,,
2026/06/01,12:15,,
"""


def test_synthetic_latest_non_empty_and_tomorrow_ignored():
    data = parse_denki_yoho(SYNTH)
    assert data["consumption"] == 4170  # 12:05, les lignes vides suivantes sont ignorées
    assert data["consumption_time"].minute == 5
    assert data["solar"] == 620
    assert data["forecast"] == 4200  # créneau 12:00 (heure de la dernière mesure)
    assert data["supply_capacity"] == 5200
    assert data["utilization"] == 82  # 11:00 : dernière heure réalisée
    assert data["peak_reserve_margin"] == 10  # pas celui de « 翌日 » (99)
    assert data["peak_supply_capacity"] == 5000


def test_missing_blocks_not_available():
    text = SYNTH.split("DATE,TIME,当日実績(５分間隔値)")[0]  # sans bloc 5 min ni solaire
    text = text.replace("使用率(%),", "")  # sans colonne 使用率 non plus
    data = parse_denki_yoho(text)
    assert "solar" not in data["available"]
    assert data["solar"] is None
    assert "utilization" not in data["available"]
    assert data["consumption"] == 4100  # repli sur le tableau horaire (11:00)
    assert data["solar_time"] is None


def test_hourly_fallback_slot_without_five_min():
    data = parse_denki_yoho(SYNTH.split("DATE,TIME,当日実績(５分間隔値)")[0])
    assert data["forecast"] == 4150  # créneau 11:00 = dernier réalisé


def test_garbage_and_empty_input():
    for text in ("", "\n\n", "foo,bar\n1,2\n"):
        data = parse_denki_yoho(text)
        assert data["available"] == set()
        assert data["consumption"] is None
        assert data["updated"] is None


def test_reordered_columns_and_blocks():
    """Parse par noms de colonnes : l'ordre des colonnes/blocs n'importe pas."""
    text = (
        "DATE,TIME,供給力(万kW),使用率(%),予想値(万kW),当日実績(万kW)\n"
        "2026/06/01,9:00,300,70,200,210\n"
        "\n"
        "2026/06/01 09:30 UPDATE\n"
    )
    data = parse_denki_yoho(text)
    assert data["consumption"] == 2100
    assert data["forecast"] == 2000
    assert data["supply_capacity"] == 3000
    assert data["utilization"] == 70
    assert data["updated"].minute == 30
