"""
Module for managing a light via KNX.

It provides functionality for

* switching light 'on' and 'off'.
* setting the brightness.
* setting the color.
* setting the relative color temperature (tunable white).
* setting the absolute color temperature.
* reading the current state from KNX bus.
"""
import logging

from xknx.remote_value import (
    RemoteValueColorRGB,
    RemoteValueColorRGBW,
    RemoteValueDpt2ByteUnsigned,
    RemoteValueScaling,
    RemoteValueSwitch,
)

from .device import Device

logger = logging.getLogger("xknx.log")


# pylint: disable=too-many-public-methods, too-many-instance-attributes
class Light(Device):
    """Class for managing a light."""

    # pylint: disable=too-many-locals
    DEFAULT_MIN_KELVIN = 2700  # 370 mireds
    DEFAULT_MAX_KELVIN = 6000  # 166 mireds

    def __init__(
        self,
        xknx,
        name,
        group_address_switch=None,
        group_address_switch_state=None,
        group_address_brightness=None,
        group_address_brightness_state=None,
        group_address_color=None,
        group_address_color_state=None,
        group_address_rgbw=None,
        group_address_rgbw_state=None,
        group_address_tunable_white=None,
        group_address_tunable_white_state=None,
        group_address_color_temperature=None,
        group_address_color_temperature_state=None,
        min_kelvin=None,
        max_kelvin=None,
        device_updated_cb=None,
    ):
        """Initialize Light class."""
        # pylint: disable=too-many-arguments
        super().__init__(xknx, name, device_updated_cb)

        self.switch = RemoteValueSwitch(
            xknx,
            group_address_switch,
            group_address_switch_state,
            device_name=self.name,
            feature_name="State",
            after_update_cb=self.after_update,
        )

        self.brightness = RemoteValueScaling(
            xknx,
            group_address_brightness,
            group_address_brightness_state,
            device_name=self.name,
            feature_name="Brightness",
            after_update_cb=self.after_update,
            range_from=0,
            range_to=255,
        )

        self.color = RemoteValueColorRGB(
            xknx,
            group_address_color,
            group_address_color_state,
            device_name=self.name,
            after_update_cb=self.after_update,
        )

        self.rgbw = RemoteValueColorRGBW(
            xknx,
            group_address_rgbw,
            group_address_rgbw_state,
            device_name=self.name,
            after_update_cb=self.after_update,
        )

        self.tunable_white = RemoteValueScaling(
            xknx,
            group_address_tunable_white,
            group_address_tunable_white_state,
            device_name=self.name,
            feature_name="Tunable white",
            after_update_cb=self.after_update,
            range_from=0,
            range_to=255,
        )

        self.color_temperature = RemoteValueDpt2ByteUnsigned(
            xknx,
            group_address_color_temperature,
            group_address_color_temperature_state,
            device_name=self.name,
            feature_name="Color temperature",
            after_update_cb=self.after_update,
        )

        self.min_kelvin = min_kelvin
        self.max_kelvin = max_kelvin

    def _iter_remote_values(self):
        """Iterate the devices RemoteValue classes."""
        yield from (
            self.switch,
            self.brightness,
            self.color,
            self.rgbw,
            self.tunable_white,
            self.color_temperature,
        )

    @property
    def supports_brightness(self):
        """Return if light supports brightness."""
        return self.brightness.initialized

    @property
    def supports_color(self):
        """Return if light supports color."""
        return self.color.initialized

    @property
    def supports_rgbw(self):
        """Return if light supports RGBW."""
        return self.rgbw.initialized

    @property
    def supports_tunable_white(self):
        """Return if light supports tunable white / relative color temperature."""
        return self.tunable_white.initialized

    @property
    def supports_color_temperature(self):
        """Return if light supports absolute color temperature."""
        return self.color_temperature.initialized

    @classmethod
    def from_config(cls, xknx, name, config):
        """Initialize object from configuration structure."""
        group_address_switch = config.get("group_address_switch")
        group_address_switch_state = config.get("group_address_switch_state")
        group_address_brightness = config.get("group_address_brightness")
        group_address_brightness_state = config.get("group_address_brightness_state")
        group_address_color = config.get("group_address_color")
        group_address_color_state = config.get("group_address_color_state")
        group_address_rgbw = config.get("group_address_rgbw")
        group_address_rgbw_state = config.get("group_address_rgbw_state")
        group_address_tunable_white = config.get("group_address_tunable_white")
        group_address_tunable_white_state = config.get(
            "group_address_tunable_white_state"
        )
        group_address_color_temperature = config.get("group_address_color_temperature")
        group_address_color_temperature_state = config.get(
            "group_address_color_temperature_state"
        )
        min_kelvin = config.get("min_kelvin", Light.DEFAULT_MIN_KELVIN)
        max_kelvin = config.get("max_kelvin", Light.DEFAULT_MAX_KELVIN)

        return cls(
            xknx,
            name,
            group_address_switch=group_address_switch,
            group_address_switch_state=group_address_switch_state,
            group_address_brightness=group_address_brightness,
            group_address_brightness_state=group_address_brightness_state,
            group_address_color=group_address_color,
            group_address_color_state=group_address_color_state,
            group_address_rgbw=group_address_rgbw,
            group_address_rgbw_state=group_address_rgbw_state,
            group_address_tunable_white=group_address_tunable_white,
            group_address_tunable_white_state=group_address_tunable_white_state,
            group_address_color_temperature=group_address_color_temperature,
            group_address_color_temperature_state=group_address_color_temperature_state,
            min_kelvin=min_kelvin,
            max_kelvin=max_kelvin,
        )

    def __str__(self):
        """Return object as readable string."""
        str_brightness = (
            ""
            if not self.supports_brightness
            else f' brightness="{self.brightness.group_addr_str()}"'
        )

        str_color = (
            "" if not self.supports_color else f' color="{self.color.group_addr_str()}"'
        )

        str_rgbw = (
            "" if not self.supports_rgbw else f' rgbw="{self.rgbw.group_addr_str()}"'
        )

        str_tunable_white = (
            ""
            if not self.supports_tunable_white
            else f' tunable white="{self.tunable_white.group_addr_str()}"'
        )

        str_color_temperature = (
            ""
            if not self.supports_color_temperature
            else ' color temperature="{}"'.format(
                self.color_temperature.group_addr_str()
            )
        )

        return '<Light name="{}" ' 'switch="{}"{}{}{}{}{} />'.format(
            self.name,
            self.switch.group_addr_str(),
            str_brightness,
            str_color,
            str_rgbw,
            str_tunable_white,
            str_color_temperature,
        )

    @property
    def state(self):
        """Return the current switch state of the device."""
        # None will return False
        return bool(self.switch.value)

    async def set_on(self):
        """Switch light on."""
        await self.switch.on()

    async def set_off(self):
        """Switch light off."""
        await self.switch.off()

    @property
    def current_brightness(self):
        """Return current brightness of light."""
        return self.brightness.value

    async def set_brightness(self, brightness):
        """Set brightness of light."""
        if not self.supports_brightness:
            logger.warning("Dimming not supported for device %s", self.get_name())
            return
        await self.brightness.set(brightness)

    @property
    def current_color(self):
        """
        Return current color of light.

        If the device supports RGBW, get the current RGB+White values instead.
        """
        if self.supports_rgbw:
            if not self.rgbw.value:
                return None, None
            return self.rgbw.value[:3], self.rgbw.value[3]
        return self.color.value, None

    async def set_color(self, color, white=None):
        """
        Set color of a light device.

        If also the white value is given and the device supports RGBW,
        set all four values.
        """
        if white is not None:
            if self.supports_rgbw:
                await self.rgbw.set(list(color) + [white])
                return
            logger.warning("RGBW not supported for device %s", self.get_name())
        else:
            if self.supports_color:
                await self.color.set(color)
                return
            logger.warning("Colors not supported for device %s", self.get_name())

    @property
    def current_tunable_white(self):
        """Return current relative color temperature of light."""
        return self.tunable_white.value

    async def set_tunable_white(self, tunable_white):
        """Set relative color temperature of light."""
        if not self.supports_tunable_white:
            logger.warning("Tunable white not supported for device %s", self.get_name())
            return
        await self.tunable_white.set(tunable_white)

    @property
    def current_color_temperature(self):
        """Return current absolute color temperature of light."""
        return self.color_temperature.value

    async def set_color_temperature(self, color_temperature):
        """Set absolute color temperature of light."""
        if not self.supports_color_temperature:
            logger.warning(
                "Absolute Color Temperature not supported for device %s",
                self.get_name(),
            )
            return
        await self.color_temperature.set(color_temperature)

    async def do(self, action):
        """Execute 'do' commands."""
        if action == "on":
            await self.set_on()
        elif action == "off":
            await self.set_off()
        elif action.startswith("brightness:"):
            await self.set_brightness(int(action[11:]))
        elif action.startswith("tunable_white:"):
            await self.set_tunable_white(int(action[14:]))
        elif action.startswith("color_temperature:"):
            await self.set_color_temperature(int(action[18:]))
        else:
            logger.warning(
                "Could not understand action %s for device %s", action, self.get_name()
            )

    async def process_group_write(self, telegram):
        """Process incoming and outgoing GROUP WRITE telegram."""
        for remote_value in self._iter_remote_values():
            await remote_value.process(telegram)
