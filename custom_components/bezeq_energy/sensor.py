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

from .commons import (
    translate_date_period,
)
from .const import (
    DAILY_USAGE_KEY,
    LAST_MONTH_INVOICE_KEY,
    LAST_MONTH_USAGE_KEY,
    MONTHLY_USAGE_KEY,
    MY_PACKAGE_KEY,
    UNIT_ILS,
)
from .entity import BezeqEnergyEntity, BezeqEnergyEntityDescriptionMixin

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.bezeq_energy.data import BezeqEnergyDeviceInfo

    from .coordinator import BezeqElecDataUpdateCoordinator
    from .data import BezeqEnergyConfigEntry


@dataclass(frozen=True, kw_only=True)
class BezeqEnergySensorEntityDescription(
    SensorEntityDescription, BezeqEnergyEntityDescriptionMixin
):
    """Class describing Bezeq Energy sensors entities."""


ENTITY_DESCRIPTIONS = [
    BezeqEnergySensorEntityDescription(
        key="last_month_cost",
        device_class=SensorDeviceClass.MONETARY,
        native_unit_of_measurement=UNIT_ILS,
        suggested_display_precision=3,
        value_fn=lambda data: (
            data[LAST_MONTH_INVOICE_KEY].sum if data[LAST_MONTH_INVOICE_KEY] else None
        ),
        custom_attrs_fn=lambda data: {
            "month": translate_date_period(data[LAST_MONTH_INVOICE_KEY].date_period)
            if data[LAST_MONTH_INVOICE_KEY]
            else None,
            "invoice_id": data[LAST_MONTH_INVOICE_KEY].invoice_id
            if data[LAST_MONTH_INVOICE_KEY]
            else None,
        },
    ),
    BezeqEnergySensorEntityDescription(
        key="package",
        value_fn=lambda data: (
            data[MY_PACKAGE_KEY].package_name if data[MY_PACKAGE_KEY] else None
        ),
        custom_attrs_fn=lambda data: {
            "description": data[MY_PACKAGE_KEY].description
            if data[MY_PACKAGE_KEY]
            else None,
            "discount": data[MY_PACKAGE_KEY].discount if data[MY_PACKAGE_KEY] else None,
        },
    ),
]

SMART_METER_ENTITY_DESCRIPTIONS = [
    BezeqEnergySensorEntityDescription(
        key="this_month_usage",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_fn=lambda data: (
            data[MONTHLY_USAGE_KEY].sum_all_month if data[MONTHLY_USAGE_KEY] else None
        ),
        custom_attrs_fn=lambda data: {
            "current_month": data[MONTHLY_USAGE_KEY].usage_month
            if data[MONTHLY_USAGE_KEY]
            else None
        },
    ),
    BezeqEnergySensorEntityDescription(
        key="today_usage",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_fn=lambda data: (
            data[DAILY_USAGE_KEY].sum_all_day if data[DAILY_USAGE_KEY] else None
        ),
        custom_attrs_fn=lambda data: {
            "current_day": data[DAILY_USAGE_KEY].usage_day
            if data[DAILY_USAGE_KEY]
            else None
        },
    ),
    BezeqEnergySensorEntityDescription(
        key="last_month_usage",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        suggested_display_precision=3,
        value_fn=lambda data: (
            data[LAST_MONTH_USAGE_KEY].sum_all_month
            if data[LAST_MONTH_USAGE_KEY]
            else None
        ),
        custom_attrs_fn=lambda data: {
            "month": data[LAST_MONTH_USAGE_KEY].usage_month
            if data[LAST_MONTH_USAGE_KEY]
            else None
        },
    ),
]


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 function argument: `hass`
    entry: BezeqEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    entity_descriptions = ENTITY_DESCRIPTIONS
    if entry.runtime_data.device_info.is_smart_meter:
        entity_descriptions += SMART_METER_ENTITY_DESCRIPTIONS

    async_add_entities(
        BezeqEnergySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device_info=entry.runtime_data.device_info,
        )
        for entity_description in entity_descriptions
    )


class BezeqEnergySensor(BezeqEnergyEntity, SensorEntity):
    """bezeq_energy Sensor class."""

    def __init__(
        self,
        coordinator: BezeqElecDataUpdateCoordinator,
        entity_description: BezeqEnergySensorEntityDescription,
        device_info: BezeqEnergyDeviceInfo,
    ) -> None:
        """Initialize the sensor class."""
        super().__init__(coordinator, device_info)
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
