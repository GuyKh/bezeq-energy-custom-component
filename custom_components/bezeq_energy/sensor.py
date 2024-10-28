"""Sensor platform for bezeq_energy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.const import UnitOfEnergy

from custom_components.bezeq_energy.const import (
    DAILY_USAGE_KEY,
    MONTHLY_USAGE_KEY,
    MY_PACKAGE_KEY,
)

from .entity import BezeqEnergyEntity, BezeqEnergyEntityDescriptionMixin

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from .coordinator import BezeqElecDataUpdateCoordinator
    from .data import BezeqEnergyConfigEntry


@dataclass(frozen=True, kw_only=True)
class BezeqEnergySensorEntityDescription(
    SensorEntityDescription, BezeqEnergyEntityDescriptionMixin
):
    """Class describing Bezeq Energy sensors entities."""


ENTITY_DESCRIPTIONS = (
    BezeqEnergySensorEntityDescription(
        key="monthly_usage",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_fn=lambda data: data[MONTHLY_USAGE_KEY].sum_all_month
        if data[MONTHLY_USAGE_KEY]
        else None,
        custom_attrs_fn=lambda data: {
            "current_month": data[MONTHLY_USAGE_KEY].usage_month
            if data[MONTHLY_USAGE_KEY]
            else None
        },
    ),
    BezeqEnergySensorEntityDescription(
        key="daily_usage",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_fn=lambda data: data[DAILY_USAGE_KEY].sum_all_day
        if data[DAILY_USAGE_KEY]
        else None,
        custom_attrs_fn=lambda data: {
            "current_day": data[DAILY_USAGE_KEY].usage_day
            if data[DAILY_USAGE_KEY]
            else None
        },
    ),
    BezeqEnergySensorEntityDescription(
        key="package",
        value_fn=lambda data: data[MY_PACKAGE_KEY].package_name
        if data[MY_PACKAGE_KEY]
        else None,
        custom_attrs_fn=lambda data: {
            "description": data[MY_PACKAGE_KEY].description
            if data[MY_PACKAGE_KEY]
            else None,
            "discount": data[MY_PACKAGE_KEY].discount if data[MY_PACKAGE_KEY] else None,
        },
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: BezeqEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    async_add_entities(
        BezeqEnergySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
        )
        for entity_description in ENTITY_DESCRIPTIONS
    )


class BezeqEnergySensor(BezeqEnergyEntity, SensorEntity):
    """bezeq_energy Sensor class."""

    def __init__(
        self,
        coordinator: BezeqElecDataUpdateCoordinator,
        entity_description: BezeqEnergySensorEntityDescription,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator)
        self.entity_description = entity_description
        self._attr_unique_id = entity_description.key
        self._attr_translation_key = entity_description.key

        attributes = {}
        if self.entity_description.custom_attrs_fn:
            custom_attr = self.entity_description.custom_attrs_fn(self.coordinator.data)
            if custom_attr:
                attributes.update(custom_attr)

        self._attr_extra_state_attributes = attributes

    @property
    def native_value(self) -> str | None:
        """Return the native value of the sensor."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return None
