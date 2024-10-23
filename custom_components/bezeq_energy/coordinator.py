"""DataUpdateCoordinator for bezeq_energy."""

from __future__ import annotations

import calendar
import logging
from datetime import timedelta
from typing import TYPE_CHECKING, Any

import homeassistant.util.dt as dt_util
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from my_bezeq import (
    ElectricReportLevel,
    MyBezeqAPI,
    MyBezeqError,
    MyBezeqLoginError,
    MyBezeqUnauthorizedError,
    MyBezeqVersionError,
    ServiceType,
)

from .const import (
    DAILY_USAGE_KEY,
    DOMAIN,
    ELEC_INVOICE_KEY,
    LOGGER,
    MONTHLY_USAGE_KEY,
    MONTHLY_USED_KEY,
    MY_PACKAGE_KEY,
    PAYER_DETAILS_KEY,
)

if TYPE_CHECKING:
    from homeassistant.core import HomeAssistant

    from .data import BezeqEnergyConfigEntry

timezone = dt_util.get_time_zone("Asia/Jerusalem")
_LOGGER = logging.getLogger(__name__)


def _get_card_by_service_type(cards: list, service_type: ServiceType):  # noqa: ANN202
    card = next(filter(lambda card: card.service_type == service_type, cards))
    if card is None:
        msg = f"Card {service_type} not found"
        raise UpdateFailed(msg)
    return card.card_details


# https://developers.home-assistant.io/docs/integration_fetching_data#coordinated-single-api-poll-for-data-for-all-entities
class BezeqElecDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    config_entry: BezeqEnergyConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
    ) -> None:
        """Initialize."""
        super().__init__(
            hass=hass,
            logger=LOGGER,
            name=DOMAIN,
            update_interval=timedelta(hours=1),
        )

    async def _get_data(self):  # noqa: ANN202
        api: MyBezeqAPI = self.config_entry.runtime_data.client
        _LOGGER.debug("Logging in to my.bezeq.co.il")
        await api.login()
        _LOGGER.debug("Successfully logged in to my.bezeq.co.il. Getting dashboard...")
        await api.dashboard.get_dashboard_tab()

        today = dt_util.now(timezone).date()
        last_day_of_month = calendar.monthrange(today.year, today.month)[1]

        data = {}

        _LOGGER.debug("Fetching electricity monthly usage...")
        monthly_usages = (
            await api.electric.get_elec_usage_report(
                ElectricReportLevel.MONTHLY,
                today.replace(day=1),
                today.replace(day=last_day_of_month),
            )
        ).usage_data

        data[MONTHLY_USAGE_KEY] = next(
            (
                usage
                for usage in monthly_usages
                if usage.usage_month.month == today.month
            ),
            None,
        )

        tomorrow = today + timedelta(days=1)
        _LOGGER.debug("Fetching electricity today usage...")
        daily_usages = (
            await api.electric.get_elec_usage_report(
                ElectricReportLevel.DAILY, today, tomorrow
            )
        ).usage_data

        data[DAILY_USAGE_KEY] = next(
            (usage for usage in daily_usages if usage.usage_day.date() == today), None
        )

        _LOGGER.debug("Fetching electricity tab...")
        elec_tab = await api.electric.get_electricity_tab()
        data[PAYER_DETAILS_KEY] = _get_card_by_service_type(
            elec_tab.cards, ServiceType.ELECTRICITY_PAYER
        )

        data[MONTHLY_USED_KEY] = _get_card_by_service_type(
            elec_tab.cards, ServiceType.ELECTRICITY_MONTHLY_USED
        )

        data[MY_PACKAGE_KEY] = _get_card_by_service_type(
            elec_tab.cards, ServiceType.ELECTRICITY_MY_PACKAGE_SERVICE
        )

        elec_invoices_tab = await api.invoices.get_electric_invoice_tab()
        data[ELEC_INVOICE_KEY] = _get_card_by_service_type(
            elec_invoices_tab.cards, ServiceType.INVOICES
        )

        return data

    async def _async_update_data(self) -> Any:
        """Update data via library."""
        try:
            return await self._get_data()
        except MyBezeqVersionError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MyBezeqLoginError as exception:
            raise UpdateFailed(exception) from exception
        except MyBezeqUnauthorizedError as exception:
            raise ConfigEntryAuthFailed(exception) from exception
        except MyBezeqError as exception:
            raise UpdateFailed(exception) from exception
