"""BezeqEnergyEntity class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTRIBUTION, DOMAIN
from .coordinator import BezeqElecDataUpdateCoordinator

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_components.bezeq_energy.data import BezeqEnergyDeviceInfo


@dataclass(frozen=True, kw_only=True)
class BezeqEnergyEntityDescriptionMixin:
    """Mixin values for required keys."""

    value_fn: Callable[dict, str | float] | None = None
    custom_attrs_fn: Callable[dict, dict[str, str | int | float]] | None = None


class BezeqEnergyEntity(CoordinatorEntity[BezeqElecDataUpdateCoordinator]):
    """BezeqEnergyEntity class."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: BezeqElecDataUpdateCoordinator,
        device_info: BezeqEnergyDeviceInfo,
    ) -> None:
        """Initialize."""
        super().__init__(coordinator)
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    coordinator.config_entry.entry_id,
                ),
            },
            name=f"Bezeq Energy {device_info.contract_number}",
            manufacturer="Bezeq Energy",
            model=f"{device_info.subscriber_number} - {device_info.counter_number}",
        )
