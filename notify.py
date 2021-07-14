"""Signal Messenger for notify component."""
import logging

import dbus
import voluptuous as vol

from homeassistant.components.notify import (
    ATTR_DATA,
    PLATFORM_SCHEMA,
    BaseNotificationService,
)
import homeassistant.helpers.config_validation as cv

_LOGGER = logging.getLogger(__name__)

CONF_RECP_NR = "recipients"
ATTR_FILENAMES = "attachments"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_RECP_NR): vol.All(cv.ensure_list, [cv.string]),
    }
)


def get_service(hass, config, discovery_info=None):
    """Get the SignalMessenger notification service."""

    recp_nrs = config[CONF_RECP_NR]

    return SignalNotificationService(recp_nrs)


class SignalNotificationService(BaseNotificationService):
    """Implement the notification service for SignalMessenger."""

    def __init__(self, recp_nrs):
        """Initialize the service."""

        bus = dbus.SystemBus()
        self.proxy = bus.get_object('org.asamk.Signal', '/org/asamk/Signal')

        self._recp_nrs = recp_nrs

    def send_message(self, message="", **kwargs):
        """Send a message to a one or more recipients.

        Additionally a file can be attached.
        """

        _LOGGER.debug("Sending signal message")

        data = kwargs.get(ATTR_DATA)

        filenames = None
        if data is not None:
            if ATTR_FILENAMES in data:
                filenames = data[ATTR_FILENAMES]

        try:
            self.proxy.sendMessage(message, dbus.Array(), self._recp_nrs, dbus_interface="org.asamk.Signal")
        except Exception as ex:
            _LOGGER.error("%s", ex)
            raise ex
