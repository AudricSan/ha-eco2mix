"""Support for éCO2mix sensors."""

from dataclasses import dataclass
import logging
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import PERCENTAGE, EntityCategory, UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from . import Eco2mixConfigEntry
from .const import DOMAIN
from .coordinator import Eco2mixDataUpdateCoordinator
from .jp_coordinator import JapanDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class Eco2mixSensorEntityDescription(SensorEntityDescription):
    """Describes Eco2mix sensor entity."""


ECO2MIX_SENSOR_TYPES: tuple[Eco2mixSensorEntityDescription, ...] = (
    Eco2mixSensorEntityDescription(
        key="consumption",
        translation_key="consumption",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Eco2mixSensorEntityDescription(
        key="nuclear",
        translation_key="nuclear",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="wind",
        translation_key="wind",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="solar",
        translation_key="solar",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="hydraulic",
        translation_key="hydraulic",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="bioenergy",
        translation_key="bioenergy",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="gas",
        translation_key="gas",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="coal",
        translation_key="coal",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="fuel",
        translation_key="fuel",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="total_production",
        translation_key="total_production",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    Eco2mixSensorEntityDescription(
        key="renewable",
        translation_key="renewable",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="low_carbon",
        translation_key="low_carbon",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="pumping",
        translation_key="pumping",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="import",
        translation_key="import",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="export",
        translation_key="export",
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="nuclear_percentage",
        translation_key="nuclear_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="wind_percentage",
        translation_key="wind_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="solar_percentage",
        translation_key="solar_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="hydraulic_percentage",
        translation_key="hydraulic_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="bioenergy_percentage",
        translation_key="bioenergy_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="gas_percentage",
        translation_key="gas_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="coal_percentage",
        translation_key="coal_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="fuel_percentage",
        translation_key="fuel_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
        entity_registry_enabled_default=False,
    ),
    Eco2mixSensorEntityDescription(
        key="renewable_percentage",
        translation_key="renewable_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    Eco2mixSensorEntityDescription(
        key="low_carbon_percentage",
        translation_key="low_carbon_percentage",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    Eco2mixSensorEntityDescription(
        key="timestamp",
        translation_key="timestamp",
        device_class=SensorDeviceClass.TIMESTAMP,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: Eco2mixConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up éco2mix sensor entities based on a config entry."""

    coordinator = config_entry.runtime_data

    if isinstance(coordinator, JapanDataUpdateCoordinator):
        # Uniquement les mesures que la zone publie (pas d'entité toujours indisponible).
        async_add_entities(
            JapanSensor(coordinator, description)
            for description in JAPAN_SENSOR_TYPES
            if description.key in coordinator.data["available"]
        )
        return

    async_add_entities(
        (
            Eco2mixSensor(coordinator, description)
            for description in ECO2MIX_SENSOR_TYPES
            if coordinator.data.get(description.key) is not None
        ),
        False,
    )


@dataclass(frozen=True, kw_only=True)
class JapanSensorEntityDescription(SensorEntityDescription):
    """Describes a Japan (でんき予報) sensor entity.

    `key` est la clé du parseur ; `extra_attrs` liste les clés du dict de
    données exposées en attributs (créneau horaire, horodatage de la mesure).
    """

    extra_attrs: tuple[str, ...] = ()


def _jp_mw(key: str, **kwargs: Any) -> JapanSensorEntityDescription:
    return JapanSensorEntityDescription(
        key=key,
        translation_key=f"jp_{key}",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.MEGA_WATT,
        state_class=SensorStateClass.MEASUREMENT,
        **kwargs,
    )


def _jp_pct(key: str, **kwargs: Any) -> JapanSensorEntityDescription:
    return JapanSensorEntityDescription(
        key=key,
        translation_key=f"jp_{key}",
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        **kwargs,
    )


JAPAN_SENSOR_TYPES: tuple[JapanSensorEntityDescription, ...] = (
    _jp_mw("consumption", extra_attrs=("consumption_time",)),
    _jp_mw("forecast", extra_attrs=("forecast_time",)),
    _jp_mw("supply_capacity", extra_attrs=("supply_capacity_time",)),
    _jp_pct("utilization", extra_attrs=("utilization_time",)),
    _jp_mw("peak_forecast", extra_attrs=("peak_forecast_slot",)),
    _jp_mw("peak_supply_capacity", extra_attrs=("peak_supply_capacity_slot",)),
    _jp_pct("peak_reserve_margin", extra_attrs=("peak_reserve_margin_slot",)),
    _jp_mw("solar", extra_attrs=("solar_time",)),
    _jp_mw("wind", extra_attrs=("wind_time",)),
)


class JapanSensor(CoordinatorEntity[JapanDataUpdateCoordinator], SensorEntity):
    """Capteur でんき予報 d'une zone japonaise."""

    _attr_has_entity_name = True
    entity_description: JapanSensorEntityDescription

    def __init__(
        self,
        coordinator: JapanDataUpdateCoordinator,
        description: JapanSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        info = coordinator.area_info
        self.entity_description = description
        self._attr_unique_id = f"eco2mix-jp-{coordinator.area}-{description.key}"
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"jp_{coordinator.area}")},
            manufacturer=info["utility"],
            name=f"Denki Yoho {info['name_en']}",
            model="でんき予報 (CSV)",
            configuration_url=info["page"],
        )

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data.get(self.entity_description.key)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Zone, source, date de mise à jour du CSV et créneau de la mesure."""
        data = self.coordinator.data
        attrs: dict[str, Any] = {
            "area": self.coordinator.area,
            "source_url": data.get("source_url"),
            "csv_updated": data["updated"].isoformat() if data.get("updated") else None,
        }
        for key in self.entity_description.extra_attrs:
            value = data.get(key)
            attrs[key.removeprefix(self.entity_description.key + "_")] = (
                value.isoformat() if hasattr(value, "isoformat") else value
            )
        return attrs


class Eco2mixSensor(CoordinatorEntity[Eco2mixDataUpdateCoordinator], SensorEntity):
    """Define an Eco2Mix sensor."""

    _attr_has_entity_name = True
    entity_description: Eco2mixSensorEntityDescription

    def __init__(
        self,
        coordinator: Eco2mixDataUpdateCoordinator,
        description: Eco2mixSensorEntityDescription,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, "eco2mix_device")},
            manufacturer="LFPoulain",
            name="éCO2mix",
            model="Integration Eco2Mix RTE via open data ODRE",
        )
        self._attr_unique_id = f"eco2mix-{description.key}".lower()
        self.entity_description = description

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        return self.coordinator.data[self.entity_description.key]


class Eco2mixBaseSensor(CoordinatorEntity[Eco2mixDataUpdateCoordinator], SensorEntity):
    """Base class for éCO2mix sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, sensor_type, name, icon):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"eco2mix_{sensor_type}"
        self._attr_state_class = SensorStateClass.MEASUREMENT

    @property
    def device_info(self) -> dict[str, Any]:
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, "eco2mix_device")},
            "name": "éCO2mix",
            "manufacturer": "LFPoulain",
            "model": "Integration Eco2Mix RTE via open data ODRE",
        }
