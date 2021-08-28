"""Signal Messenger for notify component."""
import logging

import dbus
import voluptuous as vol
import re

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

bold_re = re.compile(r'(.*?)(\s*)\*([a-zA-Z0-9 _+/\\-°,;:]+)\*(\s*)(.*)', re.DOTALL)
italic_re = re.compile(r'(.*?)(\s*)_([a-zA-Z0-9 _+/\\-°]+,;:)_(\s*)(.*)', re.DOTALL)

bold_trans = "Test".maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                              "𝗔𝗕𝗖𝗗𝗘𝗙𝗚𝗛𝗜𝗝𝗞𝗟𝗠𝗡𝗢𝗣𝗤𝗥𝗦𝗧𝗨𝗩𝗪𝗫𝗬𝗭𝗮𝗯𝗰𝗱𝗲𝗳𝗴𝗵𝗶𝗷𝗸𝗹𝗺𝗻𝗼𝗽𝗾𝗿𝘀𝘁𝘂𝘃𝘄𝘅𝘆𝘇𝟬𝟭𝟮𝟯𝟰𝟱𝟲𝟳𝟴𝟵")
italic_trans = "Test".maketrans("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789",
                                "𝘈𝘉𝘊𝘋𝘌𝘍𝘎𝘏𝘐𝘑𝘒𝘓𝘔𝘕𝘖𝘗𝘘𝘙𝘚𝘛𝘜𝘝𝘞𝘟𝘠𝘡𝘢𝘣𝘤𝘥𝘦𝘧𝘨𝘩𝘪𝘫𝘬𝘭𝘮𝘯𝘰𝘱𝘲𝘳𝘴𝘵𝘶𝘷𝘸𝘹𝘺𝘻0123456789")


def get_service(hass, config, discovery_info=None):
    """Get the SignalMessenger notification service."""

    recp_nrs = config[CONF_RECP_NR]

    return SignalNotificationService(recp_nrs)


def parse_text_bold(inp):
    m = bold_re.match(inp)
    if m:
        bold_txt = "" if m[3] is None else m[3].translate(
            bold_trans)
        return "".join(["".join(m[1]), " ", bold_txt,
                        " ", parse_text_bold(m[5])])
    else:
        return inp


def parse_text_italic(inp):
    m = italic_re.match(inp)
    if m:
        italic_txt = "" if m[3] is None else m[3].translate(
            italic_trans)
        return "".join(["".join(m[1]), " ", italic_txt,
                        " ", parse_text_italic(m[5])])
    else:
        return inp


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

        if "title" in kwargs:
            message = "".join([f"*{kwargs['title']}*\n", message])

        message = parse_text_italic(parse_text_bold(message))

        _LOGGER.debug("Sending signal message")

        data = kwargs.get(ATTR_DATA)

        filenames = None
        if data is not None:
            if ATTR_FILENAMES in data:
                filenames = data[ATTR_FILENAMES]

        try:
            self.proxy.sendMessage(message, dbus.Array(),
                                   self._recp_nrs,
                                   dbus_interface="org.asamk.Signal")
        except Exception as ex:
            _LOGGER.error("%s", ex)
            raise ex
