"""Config flow for éCO2mix integration."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigFlow,
    ConfigFlowResult,
)
from homeassistant.helpers.selector import (
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    CONF_AREA,
    CONF_SOURCE,
    DOMAIN,
    FRANCE_UNIQUE_ID,
    JP_AREAS,
    SOURCE_FRANCE,
    SOURCE_JAPAN,
)


class Eco2mixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for éCO2mix."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Premier écran : choix de la source (France ou Japon)."""
        if user_input is not None:
            if user_input[CONF_SOURCE] == SOURCE_JAPAN:
                return await self.async_step_japan()
            return await self._async_create_france()

        schema = vol.Schema(
            {
                vol.Required(CONF_SOURCE, default=SOURCE_FRANCE): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(
                                value=SOURCE_FRANCE, label="France (RTE éCO2mix)"
                            ),
                            SelectOptionDict(
                                value=SOURCE_JAPAN, label="日本 / Japon (でんき予報)"
                            ),
                        ],
                        mode=SelectSelectorMode.LIST,
                    )
                )
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    async def _async_create_france(self) -> ConfigFlowResult:
        """Crée l'entrée France (une seule, y compris les anciennes sans unique_id)."""
        for entry in self._async_current_entries():
            # Les entrées créées avant le choix de source n'ont ni data ni unique_id.
            if entry.data.get(CONF_SOURCE, SOURCE_FRANCE) == SOURCE_FRANCE:
                return self.async_abort(reason="already_configured")
        await self.async_set_unique_id(FRANCE_UNIQUE_ID)
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="éCO2mix", data={CONF_SOURCE: SOURCE_FRANCE}
        )

    async def async_step_japan(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Second écran Japon : choix de la zone (une entrée par zone)."""
        if user_input is not None:
            area = user_input[CONF_AREA]
            await self.async_set_unique_id(f"jp_{area}")
            self._abort_if_unique_id_configured()
            info = JP_AREAS[area]
            return self.async_create_entry(
                title=f"でんき予報 {info['name_ja']} ({info['name_en']})",
                data={CONF_SOURCE: SOURCE_JAPAN, CONF_AREA: area},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_AREA): SelectSelector(
                    SelectSelectorConfig(
                        options=[
                            SelectOptionDict(
                                value=key,
                                label=f"{info['name_ja']} {info['name_en']} ({info['utility']})",
                            )
                            for key, info in JP_AREAS.items()
                        ],
                        mode=SelectSelectorMode.DROPDOWN,
                    )
                )
            }
        )
        return self.async_show_form(step_id="japan", data_schema=schema)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Handle import from configuration.yaml (France uniquement)."""
        return await self._async_create_france()
