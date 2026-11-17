"""Parseur des CSV « でんき予報 » des 10 zones japonaises.

Module volontairement sans dépendance à Home Assistant (testable seul).

Format commun (encodage Shift_JIS/CP932, valeurs en 万kW = 10 MW) : une ligne
``AAAA/MM/JJ HH:MM UPDATE`` puis plusieurs blocs séparés par des lignes vides,
chacun avec sa ligne d'en-tête. Les blocs sont identifiés par le nom de leurs
colonnes (jamais par un numéro de ligne), car chaque compagnie a de petites
variantes (« 予測値 » / « 予想値 », « 需要ピーク時… », colonne éolien, etc.).
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import re
import unicodedata
from typing import Any

JST = timezone(timedelta(hours=9))
MAN_KW_TO_MW = 10  # 1 万kW = 10 MW

_UPDATE_RE = re.compile(r"^\s*(\d{4})/(\d{1,2})/(\d{1,2})\s+(\d{1,2}):(\d{2})\s+UPDATE")


def _norm(text: str) -> str:
    """Normalise (pleine largeur -> ASCII) et supprime les espaces."""
    return unicodedata.normalize("NFKC", text).strip()


def _num(value: str | None) -> float | None:
    """Convertit une cellule en nombre ; vide ou « * » -> None."""
    if value is None:
        return None
    value = _norm(value)
    if value in ("", "*", "-"):
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _mw(value: str | None) -> float | None:
    """Convertit une cellule 万kW en MW."""
    number = _num(value)
    return None if number is None else number * MAN_KW_TO_MW


def _find_col(header: list[str], *needles: str, startswith: bool = False) -> int | None:
    """Index de la première colonne contenant (ou débutant par) un des motifs."""
    for index, name in enumerate(header):
        for needle in needles:
            if (name.startswith(needle) if startswith else needle in name):
                return index
    return None


def _last_usage_col(header: list[str]) -> int | None:
    """Colonne « …使用率(%) » du pic (la dernière, hors 予備率)."""
    index = None
    for i, name in enumerate(header):
        if "使用率" in name and "予備率" not in name:
            index = i
    return index


def _cell(row: list[str], index: int | None) -> str | None:
    if index is None or index >= len(row):
        return None
    return row[index]


def _row_datetime(date_s: str, time_s: str) -> datetime | None:
    """Construit un datetime JST depuis les colonnes DATE et TIME."""
    try:
        year, month, day = (int(p) for p in _norm(date_s).split("/"))
        hour, minute = (int(p) for p in _norm(time_s).split(":"))
        return datetime(year, month, day, hour, minute, tzinfo=JST)
    except ValueError:
        return None


def _split_blocks(text: str) -> tuple[datetime | None, list[list[list[str]]]]:
    """Découpe le CSV en (date de mise à jour, blocs de lignes de cellules)."""
    updated: datetime | None = None
    blocks: list[list[list[str]]] = []
    current: list[list[str]] = []
    for raw in text.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = raw.strip()
        if not line.strip(","):
            if current:
                blocks.append(current)
                current = []
            continue
        match = _UPDATE_RE.match(line)
        if match and updated is None:
            year, month, day, hour, minute = (int(g) for g in match.groups())
            updated = datetime(year, month, day, hour, minute, tzinfo=JST)
            continue
        current.append([_norm(c) for c in line.split(",")])
    if current:
        blocks.append(current)
    return updated, blocks


def _parse_peak_block(block: list[list[str]]) -> dict[str, Any]:
    """Lit un bloc « pic » (1 ligne d'en-tête + 1 ligne de valeurs)."""
    header = block[0]
    row = block[1] if len(block) > 1 else []
    slot = (_cell(row, _find_col(header, "時間帯")) or "").strip()
    return {
        "value": _mw(_cell(row, 0)),
        "slot": slot or None,
        "reserve_margin": _num(_cell(row, _find_col(header, "予備率"))),
    }


def _parse_hourly(header: list[str], rows: list[list[str]]) -> list[dict[str, Any]]:
    i_date, i_time = header.index("DATE"), header.index("TIME")
    i_actual = _find_col(header, "当日実績", startswith=True)
    i_fc = _find_col(header, "予測値", "予想値")
    i_use = _find_col(header, "使用率", startswith=True)
    i_sup = _find_col(header, "供給力", startswith=True)
    out = []
    for row in rows:
        when = _row_datetime(_cell(row, i_date) or "", _cell(row, i_time) or "")
        if when is None:
            continue
        out.append(
            {
                "time": when,
                "actual": _mw(_cell(row, i_actual)),
                "forecast": _mw(_cell(row, i_fc)),
                "utilization": _num(_cell(row, i_use)),
                "supply": _mw(_cell(row, i_sup)),
            }
        )
    return out


def _parse_five_min(header: list[str], rows: list[list[str]]) -> list[dict[str, Any]]:
    i_date, i_time = header.index("DATE"), header.index("TIME")
    i_actual = _find_col(header, "当日実績", startswith=True)
    i_solar = _find_col(header, "太陽光発電実績")
    i_wind = _find_col(header, "風力発電実績")
    out = []
    for row in rows:
        when = _row_datetime(_cell(row, i_date) or "", _cell(row, i_time) or "")
        if when is None:
            continue
        out.append(
            {
                "time": when,
                "actual": _mw(_cell(row, i_actual)),
                "solar": _mw(_cell(row, i_solar)),
                "wind": _mw(_cell(row, i_wind)),
            }
        )
    return out


def parse_denki_yoho(text: str) -> dict[str, Any]:
    """Analyse un CSV でんき予報 déjà décodé.

    Retourne un dict :
    - ``updated`` : datetime JST de la ligne d'en-tête (ou None) ;
    - ``available`` : ensemble des clés de capteurs que la zone publie
      (colonne/bloc présent, même si la valeur du moment est vide) ;
    - une clé par mesure (MW ou %), ``None`` si aucune valeur disponible ;
    - ``<clé>_time`` / ``<clé>_slot`` : horodatage ou créneau associé.
    """
    updated, blocks = _split_blocks(text)
    available: set[str] = set()
    data: dict[str, Any] = {"updated": updated}
    hourly: list[dict[str, Any]] = []
    five_min: list[dict[str, Any]] = []

    for block in blocks:
        header, rows = block[0], block[1:]
        first = header[0]
        if first.startswith("翌日"):
            continue  # blocs du lendemain : ignorés

        if "DATE" in header and "TIME" in header:
            i_actual = _find_col(header, "当日実績", startswith=True)
            if _find_col(header, "予測値", "予想値") is not None:
                # tableau horaire
                available.update({"consumption", "forecast"})
                if _find_col(header, "使用率", startswith=True) is not None:
                    available.add("utilization")
                if _find_col(header, "供給力", startswith=True) is not None:
                    available.add("supply_capacity")
                hourly = _parse_hourly(header, rows)
            elif i_actual is not None and "5分" in header[i_actual]:
                # tableau 5 minutes (+ solaire / éolien selon la zone)
                available.add("consumption")
                if _find_col(header, "太陽光発電実績") is not None:
                    available.add("solar")
                if _find_col(header, "風力発電実績") is not None:
                    available.add("wind")
                five_min = _parse_five_min(header, rows)
        elif first.startswith(("ピーク時供給力", "需要ピーク時供給力")):
            peak = _parse_peak_block(block)
            available.update({"peak_supply_capacity", "peak_reserve_margin"})
            data["peak_supply_capacity"] = peak["value"]
            data["peak_supply_capacity_slot"] = peak["slot"]
            data["peak_reserve_margin"] = peak["reserve_margin"]
            data["peak_reserve_margin_slot"] = peak["slot"]
        elif first.startswith(("予想最大電力", "需要ピーク時予想最大電力")):
            peak = _parse_peak_block(block)
            available.add("peak_forecast")
            data["peak_forecast"] = peak["value"]
            data["peak_forecast_slot"] = peak["slot"]

    # --- valeurs « courantes » ---
    # Une demande <= 0 est un remplissage (créneau pas encore publié), pas une mesure.
    five_valid = [r for r in five_min if r["actual"] is not None and r["actual"] > 0]
    hourly_valid = [r for r in hourly if r["actual"] is not None and r["actual"] > 0]

    latest = five_valid[-1] if five_valid else None
    if latest is None and hourly_valid:
        latest = hourly_valid[-1]
    data["consumption"] = latest["actual"] if latest else None
    data["consumption_time"] = latest["time"] if latest else None

    # Créneau horaire courant : celui de la dernière mesure (sinon dernier réalisé).
    slot_row = None
    if latest is not None:
        for row in hourly:
            if row["time"].date() == latest["time"].date() and row["time"].hour == latest["time"].hour:
                slot_row = row
                break
        if slot_row is None and hourly_valid:
            slot_row = hourly_valid[-1]
    data["forecast"] = slot_row["forecast"] if slot_row else None
    data["forecast_time"] = slot_row["time"] if slot_row else None
    data["supply_capacity"] = slot_row["supply"] if slot_row else None
    data["supply_capacity_time"] = slot_row["time"] if slot_row else None

    # 使用率 : dernière heure réalisée (valeur publiée, non recalculée).
    use_rows = [r for r in hourly_valid if r["utilization"] is not None]
    data["utilization"] = use_rows[-1]["utilization"] if use_rows else None
    data["utilization_time"] = use_rows[-1]["time"] if use_rows else None

    # Solaire / éolien : même ligne 5 min que la consommation.
    for key in ("solar", "wind"):
        value = latest.get(key) if latest in five_valid else None
        data[key] = value
        data[f"{key}_time"] = latest["time"] if value is not None else None

    data["available"] = available
    return data


def decode_csv(raw: bytes) -> str:
    """Décode un CSV Shift_JIS (CP932) ; caractères invalides remplacés."""
    return raw.decode("cp932", errors="replace")
