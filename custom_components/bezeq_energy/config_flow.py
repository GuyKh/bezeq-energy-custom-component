"""Adds config flow for Bezeq Energy."""

from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries, data_entry_flow
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.helpers import selector
from homeassistant.helpers.aiohttp_client import async_create_clientsession
from my_bezeq import (
    MyBezeqAPI,
    MyBezeqError,
    MyBezeqLoginError,
    MyBezeqUnauthorizedError,
    MyBezeqVersionError,
)

from .const import DOMAIN, LOGGER


class BezeqEnergyFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Bezeq Energy."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict | None = None,
    ) -> data_entry_flow.FlowResult:
        """Handle a flow initialized by the user."""
        _errors = {}
        if user_input is not None:
            try:
                subscriber = await self._test_credentials(
                    username=user_input[CONF_USERNAME],
                    password=user_input[CONF_PASSWORD],
                )
            except MyBezeqLoginError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except MyBezeqUnauthorizedError as exception:
                LOGGER.warning(exception)
                _errors["base"] = "auth"
            except MyBezeqVersionError as exception:
                LOGGER.error(exception)
                _errors["base"] = "connection"
            except MyBezeqError as exception:
                LOGGER.exception(exception)
                _errors["base"] = "unknown"
            else:
                return self.async_create_entry(
                    title=f"Bezeq Energy - {subscriber}",
                    data=user_input,
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=(user_input or {}).get(CONF_USERNAME, vol.UNDEFINED),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT,
                        ),
                    ),
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD,
                        ),
                    ),
                },
            ),
            errors=_errors,
        )

    async def _test_credentials(self, username: str, password: str) -> None:
        """Validate credentials."""
        client = MyBezeqAPI(
            user_id=username,
            password=password,
            session=async_create_clientsession(self.hass),
        )
        await client.login()
        await client.dashboard.get_dashboard_tab()
        energyity_tab = await client.electric.get_electricity_tab()
        if (
            energyity_tab is None
            or not energyity_tab.elect_subscribers
            or all(
                not subscriber.is_current
                for subscriber in energyity_tab.elect_subscribers
            )
        ):
            msg = "This user is not Bezeq Energy user"
            raise MyBezeqError(msg)

        subscriber = next(
            filter(
                lambda subscriber: subscriber.is_current,
                energyity_tab.elect_subscribers,
            )
        )
        return subscriber.subscriber if subscriber else None
