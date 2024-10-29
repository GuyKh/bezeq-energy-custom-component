"""Binary sensor platform for bezeq_energy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

from custom_components.bezeq_energy.commons import get_last_invoice
from custom_components.bezeq_energy.const import ELEC_INVOICE_KEY

from .entity import BezeqEnergyEntity, BezeqEnergyEntityDescriptionMixin

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant
    from homeassistant.helpers.entity_platform import AddEntitiesCallback

    from custom_components.bezeq_energy.data import BezeqEnergyDeviceInfo

    from .coordinator import BezeqElecDataUpdateCoordinator
    from .data import BezeqEnergyConfigEntry


@dataclass(frozen=True, kw_only=True)
class BezeqEnergyBinarySensorEntityDescription(
    BinarySensorEntityDescription, BezeqEnergyEntityDescriptionMixin
):
    """Class describing Bezeq Energy sensors entities."""


ENTITY_DESCRIPTIONS = [
    BezeqEnergyBinarySensorEntityDescription(
        key="is_last_invoice_paid",
        value_fn=lambda data: get_last_invoice(data[ELEC_INVOICE_KEY].invoices).is_payed
        if (
            data[ELEC_INVOICE_KEY] and get_last_invoice(data[ELEC_INVOICE_KEY].invoices)
        )
        else None,
        custom_attrs_fn=lambda data: {
            "invoice_number": get_last_invoice(
                data[ELEC_INVOICE_KEY].invoices
            ).invoice_number,
            "sum": get_last_invoice(data[ELEC_INVOICE_KEY].invoices).sum,
            "date_period": get_last_invoice(
                data[ELEC_INVOICE_KEY].invoices
            ).date_period,
        }
        if (
            data[ELEC_INVOICE_KEY] and get_last_invoice(data[ELEC_INVOICE_KEY].invoices)
        )
        else None,
    ),
]

SMART_METER_ENTITY_DESCRIPTIONS = []


async def async_setup_entry(
    hass: HomeAssistant,  # noqa: ARG001 Unused function argument: `hass`
    entry: BezeqEnergyConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the binary_sensor platform."""
    entity_descriptions = ENTITY_DESCRIPTIONS
    if entry.runtime_data.device_info.is_smart_meter:
        entity_descriptions += SMART_METER_ENTITY_DESCRIPTIONS

    async_add_entities(
        BezeqEnergyBinarySensor(
            coordinator=entry.runtime_data.coordinator,
            entity_description=entity_description,
            device_info=entry.runtime_data.device_info,
        )
        for entity_description in entity_descriptions
    )


class BezeqEnergyBinarySensor(BezeqEnergyEntity, BinarySensorEntity):
    """bezeq_energy binary_sensor class."""

    def __init__(
        self,
        coordinator: BezeqElecDataUpdateCoordinator,
        entity_description: BezeqEnergyBinarySensorEntityDescription,
        device_info: BezeqEnergyDeviceInfo,
    ) -> None:
        """Initialize the binary_sensor class."""
        super().__init__(coordinator, device_info)
        self.entity_description = entity_description

        self._attr_unique_id = f"{entity_description.key}"
        self._attr_translation_key = f"{entity_description.key}"

        attributes = {}
        if self.entity_description.custom_attrs_fn:
            custom_attr = self.entity_description.custom_attrs_fn(self.coordinator.data)
            if custom_attr:
                attributes.update(custom_attr)

        self._attr_extra_state_attributes = attributes

    @property
    def is_on(self) -> bool:
        """Return true if the binary_sensor is on."""
        if self.coordinator.data:
            return self.entity_description.value_fn(self.coordinator.data)
        return False
