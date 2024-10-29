"""
Custom integration to integrate bezeq_energy with Home Assistant.

For more details about this integration, please refer to
https://github.com/GuyKh/bezeq-energy-custom-component
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from homeassistant.const import CONF_PASSWORD, CONF_USERNAME, Platform
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.loader import async_get_loaded_integration
from my_bezeq import MyBezeqAPI

from .const import (
    CONF_CONTRACT_NUMBER,
    CONF_COUNTER_NUMBER,
    CONF_IS_SMART_METER,
    CONF_SUBSCRIBER_NUMBER,
    DOMAIN,
    LOGGER,
)
from .coordinator import BezeqElecDataUpdateCoordinator
from .data import BezeqEnergyData, BezeqEnergyDeviceInfo

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import BezeqEnergyConfigEntry

PLATFORMS: list[Platform] = [
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


# https://developers.home-assistant.io/docs/config_entries_index/#setting-up-an-entry
async def async_setup_entry(
    hass: HomeAssistant,
    entry: BezeqEnergyConfigEntry,
) -> bool:
    """Set up this integration using UI."""
    coordinator = BezeqElecDataUpdateCoordinator(
        hass=hass,
    )
    entry.runtime_data = BezeqEnergyData(
        client=MyBezeqAPI(
            user_id=entry.data[CONF_USERNAME],
            password=entry.data[CONF_PASSWORD],
            session=async_get_clientsession(hass),
        ),
        integration=async_get_loaded_integration(hass, entry.domain),
        coordinator=coordinator,
        device_info=BezeqEnergyDeviceInfo(
            is_smart_meter=entry.data.get(CONF_IS_SMART_METER, False),
            counter_number=entry.data.get(CONF_COUNTER_NUMBER),
            contract_number=entry.data.get(CONF_CONTRACT_NUMBER),
            subscriber_number=entry.data.get(CONF_SUBSCRIBER_NUMBER),
        ),
    )

    # https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
    await coordinator.async_config_entry_first_refresh()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    # Register the debug service
    async def handle_debug_get_coordinator_data(call) -> None:  # noqa: ANN001 ARG001
        # Log or return coordinator data
        data = coordinator.data
        LOGGER.info("Coordinator data: %s", data)
        hass.bus.async_fire("custom_component_debug_event", {"data": data})

    hass.services.async_register(
        DOMAIN, "debug_get_coordinator_data", handle_debug_get_coordinator_data
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: BezeqEnergyConfigEntry,
) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_reload_entry(
    hass: HomeAssistant,
    entry: BezeqEnergyConfigEntry,
) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
