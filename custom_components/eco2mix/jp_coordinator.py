"""DataUpdateCoordinator pour les zones japonaises (でんき予報)."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    DEFAULT_SCAN_INTERVAL,
    DOMAIN,
    JP_AREAS,
    JP_REQUEST_TIMEOUT,
    JP_USER_AGENT,
)
from .jp_parser import JST, decode_csv, parse_denki_yoho

_LOGGER = logging.getLogger(__name__)


class JapanDataUpdateCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Récupère et analyse le CSV でんき予報 d'une zone."""

    def __init__(self, hass: HomeAssistant, area: str) -> None:
        """Initialise le coordinateur de la zone `area`."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_jp_{area}",
            update_interval=timedelta(minutes=DEFAULT_SCAN_INTERVAL),
        )
        self.area = area
        self.area_info = JP_AREAS[area]
        self.source_url: str = self.area_info["url"]

    def _url_for(self, day: datetime) -> str:
        return self.area_info["url"].format(date=day.strftime("%Y%m%d"))

    async def _fetch(self, url: str) -> bytes:
        session = async_get_clientsession(self.hass)
        async with session.get(
            url,
            headers={"User-Agent": JP_USER_AGENT},
            timeout=aiohttp.ClientTimeout(total=JP_REQUEST_TIMEOUT),
        ) as response:
            response.raise_for_status()
            return await response.read()

    async def _async_update_data(self) -> dict[str, Any]:
        """Télécharge le CSV du jour (JST) et l'analyse."""
        url = self._url_for(datetime.now(JST))
        try:
            raw = await self._fetch(url)
        except (aiohttp.ClientError, TimeoutError) as err:
            raise UpdateFailed(f"Erreur de récupération de {url}: {err}") from err

        data = parse_denki_yoho(decode_csv(raw))
        if not data["available"]:
            raise UpdateFailed(f"CSV sans données exploitables: {url}")
        data["source_url"] = url
        self.source_url = url
        return data
