"""Constants for the éCO2mix integration."""

from datetime import timedelta

DOMAIN = "eco2mix"
DEFAULT_SCAN_INTERVAL = 5  # minutes
SCAN_INTERVAL = timedelta(minutes=DEFAULT_SCAN_INTERVAL)

POWER_MEGA_WATT = "MW"

# Sources definition for aggregates
RENEWABLE_SOURCES = ["wind", "solar", "hydraulic", "bioenergy"]
LOW_CARBON_SOURCES = [*RENEWABLE_SOURCES, "nuclear"]
ALL_PRODUCTION_SOURCES = [*LOW_CARBON_SOURCES, "gas", "coal", "fuel"]

STORAGE_VERSION = 1
STORAGE_KEY = "eco2mix_cache"

# --- Sources de données ---
CONF_SOURCE = "source"
CONF_AREA = "area"
SOURCE_FRANCE = "france"
SOURCE_JAPAN = "japan"
FRANCE_UNIQUE_ID = "france"

JP_USER_AGENT = "Mozilla/5.0 (compatible; HomeAssistant ha-eco2mix)"
JP_REQUEST_TIMEOUT = 20  # secondes

# 10 zones japonaises (でんき予報). `url` : {date} = AAAAMMJJ en heure japonaise (JST)
# pour les compagnies qui publient un fichier par jour ; sinon URL fixe.
JP_AREAS: dict[str, dict[str, str]] = {
    "hokkaido": {
        "name_ja": "北海道",
        "name_en": "Hokkaido",
        "utility": "北海道電力ネットワーク",
        "url": "https://denkiyoho.hepco.co.jp/area/data/juyo_01_{date}.csv",
        "page": "https://denkiyoho.hepco.co.jp/",
    },
    "tohoku": {
        "name_ja": "東北",
        "name_en": "Tohoku",
        "utility": "東北電力ネットワーク",
        "url": "https://setsuden.nw.tohoku-epco.co.jp/common/demand/juyo_02_{date}.csv",
        "page": "https://setsuden.nw.tohoku-epco.co.jp/graph.html",
    },
    "tokyo": {
        "name_ja": "東京",
        "name_en": "Tokyo",
        "utility": "東京電力パワーグリッド",
        "url": "https://www.tepco.co.jp/forecast/html/images/juyo-d1-j.csv",
        "page": "https://www.tepco.co.jp/forecast/",
    },
    "chubu": {
        "name_ja": "中部",
        "name_en": "Chubu",
        "utility": "中部電力パワーグリッド",
        "url": "https://powergrid.chuden.co.jp/denki_yoho_content_data/juyo_cepco003.csv",
        "page": "https://powergrid.chuden.co.jp/denkiyoho/",
    },
    "hokuriku": {
        "name_ja": "北陸",
        "name_en": "Hokuriku",
        "utility": "北陸電力送配電",
        "url": "https://www.rikuden.co.jp/nw/denki-yoho/csv/juyo_05_{date}.csv",
        "page": "https://www.rikuden.co.jp/nw/denki-yoho/",
    },
    "kansai": {
        "name_ja": "関西",
        "name_en": "Kansai",
        "utility": "関西電力送配電",
        "url": "https://www.kansai-td.co.jp/yamasou/juyo_06_{date}.csv",
        "page": "https://www.kansai-td.co.jp/denkiyoho/",
    },
    "chugoku": {
        "name_ja": "中国",
        "name_en": "Chugoku",
        "utility": "中国電力ネットワーク",
        "url": "https://www.energia.co.jp/nw/jukyuu/sys/juyo_07_{date}.csv",
        "page": "https://www.energia.co.jp/nw/jukyuu/",
    },
    "shikoku": {
        "name_ja": "四国",
        "name_en": "Shikoku",
        "utility": "四国電力送配電",
        "url": "https://www.yonden.co.jp/nw/denkiyoho/juyo_08_{date}.csv",
        "page": "https://www.yonden.co.jp/nw/denkiyoho/",
    },
    "kyushu": {
        "name_ja": "九州",
        "name_en": "Kyushu",
        "utility": "九州電力送配電",
        "url": "https://www.kyuden.co.jp/td_power_usages/csv/juyo-hourly-{date}.csv",
        "page": "https://www.kyuden.co.jp/td_power_usages/pc.html",
    },
    "okinawa": {
        "name_ja": "沖縄",
        "name_en": "Okinawa",
        "utility": "沖縄電力",
        "url": "https://www.okiden.co.jp/denki2/juyo_10_{date}.csv",
        "page": "https://www.okiden.co.jp/denki2/",
    },
}
