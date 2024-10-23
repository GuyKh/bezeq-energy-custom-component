"""Custom types for bezeq_energy."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration
    from my_bezeq import MyBezeqAPI

    from .coordinator import BezeqElecDataUpdateCoordinator


type BezeqEnergyConfigEntry = ConfigEntry[BezeqEnergyData]


@dataclass
class BezeqEnergyData:
    """Data for the BezeqEnergy integration."""

    client: MyBezeqAPI
    coordinator: BezeqElecDataUpdateCoordinator
    integration: Integration
