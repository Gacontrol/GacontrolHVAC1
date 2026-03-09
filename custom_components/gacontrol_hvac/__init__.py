"""The Gacontrol HVAC integration."""
from __future__ import annotations

import logging
from datetime import timedelta
from pathlib import Path

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .heating_group import HeatingGroup

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.CLIMATE,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.BINARY_SENSOR,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.TEXT,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Gacontrol HVAC from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    await _register_frontend_resources(hass)

    heating_group = HeatingGroup(hass, entry)

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN}_{entry.entry_id}",
        update_method=heating_group.async_update,
        update_interval=timedelta(seconds=2),
    )

    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {
        "coordinator": coordinator,
        "heating_group": heating_group,
    }

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _register_frontend_resources(hass: HomeAssistant) -> None:
    """Register frontend resources for the custom card."""
    integration_dir = Path(__file__).parent
    www_dir = integration_dir / "www"

    if not www_dir.exists():
        _LOGGER.warning("www directory not found at %s", www_dir)
        return

    card_url = "/gacontrol_hvac/gacontrol-heating-group-card.js"

    try:
        from homeassistant.components.http.static import StaticPathConfig

        await hass.http.async_register_static_paths([
            StaticPathConfig(
                url_path="/gacontrol_hvac",
                path=str(www_dir),
                cache_headers=False,
            )
        ])
    except (ImportError, AttributeError):
        try:
            hass.http.register_static_path(
                "/gacontrol_hvac",
                str(www_dir),
                cache_headers=False,
            )
        except Exception as err:
            _LOGGER.warning(
                "Could not register static path: %s. Please add the card manually.", err
            )
            return

    try:
        from homeassistant.components.lovelace.resources import ResourceStorageCollection

        if "lovelace" in hass.data:
            resources = hass.data["lovelace"].get("resources")
            if resources and isinstance(resources, ResourceStorageCollection):
                existing = [r for r in resources.async_items() if card_url in r.get("url", "")]
                if not existing:
                    await resources.async_create_item({
                        "url": card_url,
                        "res_type": "module",
                    })
                    _LOGGER.info("Auto-registered GAControl card as Lovelace resource")
    except Exception as err:
        _LOGGER.debug("Could not auto-register Lovelace resource: %s", err)

    _LOGGER.info("Registered GAControl Heating Group Card at %s", card_url)
