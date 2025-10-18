""" A custom data class to manage specific HVAC modes for VTherm. """

from homeassistant.components.climate.const import HVACMode

OFF = HVACMode.OFF.value
HEAT = HVACMode.HEAT.value
COOL = HVACMode.COOL.value
AUTO = HVACMode.AUTO.value
DRY = HVACMode.DRY.value
FAN_ONLY = HVACMode.FAN_ONLY.value
HEAT_COOL = HVACMode.HEAT_COOL.value
SLEEP = "sleep"

VALID_HVAC_MODES = {
    OFF,
    HEAT,
    COOL,
    AUTO,
    DRY,
    FAN_ONLY,
    HEAT_COOL,
    SLEEP,
}

class VThermHvacMode:
    """
    Container and validator for supported HVAC operating modes.
    """
    def __init__(self, hvac_mode: str):
        """
        Initialize a VThermHvacMode instance.

        Args:
            hvac_mode (VThermHvacMode): The HVAC mode to set.

        Raises:
            ValueError: If the mode is not supported.
        """
        if str(hvac_mode) not in VALID_HVAC_MODES or not isinstance(hvac_mode, str):
            raise ValueError(f"Unsupported HVAC mode: {hvac_mode}")
        self._hvac_mode: str = hvac_mode

    def __str__(self):
        return self._hvac_mode

    def __eq__(self, other: object) -> bool:
        if isinstance(other, str):
            return self._hvac_mode == other
        else:
            return self._hvac_mode == str(other)

    def __repr__(self):
        return f"[VThermHvacMode: {self._hvac_mode}]"


VThermHvacMode_OFF = VThermHvacMode(OFF)
VThermHvacMode_HEAT = VThermHvacMode(HEAT)
VThermHvacMode_COOL = VThermHvacMode(COOL)
VThermHvacMode_AUTO = VThermHvacMode(AUTO)
VThermHvacMode_DRY = VThermHvacMode(DRY)
VThermHvacMode_FAN_ONLY = VThermHvacMode(FAN_ONLY)
VThermHvacMode_HEAT_COOL = VThermHvacMode(HEAT_COOL)
VThermHvacMode_SLEEP = VThermHvacMode(SLEEP)

# Map statique pour conversion HA -> VTherm
HA_TO_VTHERM_MAP = {
    HVACMode.OFF: VThermHvacMode_OFF,
    HVACMode.HEAT: VThermHvacMode_HEAT,
    HVACMode.COOL: VThermHvacMode_COOL,
    HVACMode.AUTO: VThermHvacMode_AUTO,
    HVACMode.DRY: VThermHvacMode_DRY,
    HVACMode.FAN_ONLY: VThermHvacMode_FAN_ONLY,
    HVACMode.HEAT_COOL: VThermHvacMode_HEAT_COOL,
}

# Map statique pour conversion VTherm -> HA
VTHERM_TO_HA_MAP = {
    OFF: HVACMode.OFF,
    HEAT: HVACMode.HEAT,
    COOL: HVACMode.COOL,
    AUTO: HVACMode.AUTO,
    DRY: HVACMode.DRY,
    FAN_ONLY: HVACMode.FAN_ONLY,
    HEAT_COOL: HVACMode.HEAT_COOL,
    SLEEP: HVACMode.OFF,  # SLEEP doesn't exist in HA, we return OFF
}


def from_ha_hvac_mode(ha_hvac_mode: HVACMode | None) -> VThermHvacMode | None:
    """
    Convert a Home Assistant HVACMode (enum or str) to a VThermHvacMode instance.

    Args:
        ha_hvac_mode (HVACMode | str): The Home Assistant HVAC mode.

    Returns:
        VThermHvacMode: The corresponding VThermHvacMode instance.
    """
    if ha_hvac_mode is None:
        return None

    # Si enum, utiliser la map
    if isinstance(ha_hvac_mode, HVACMode):
        converter = HA_TO_VTHERM_MAP.get(ha_hvac_mode)
        if converter:
            return converter
        else:
            raise ValueError(f"HA HVACMode not found: {ha_hvac_mode}")


def to_ha_hvac_mode(vtherm_hvac_mode: VThermHvacMode | None) -> HVACMode | None:
    """
    Convert a VThermHvacMode instance to a Home Assistant HVACMode (enum or str).

    Args:
        vtherm_hvac_mode (VThermHvacMode): The VThermHvacMode instance.

    Returns:
        HVACMode | None: The corresponding Home Assistant HVACMode or None.
    """
    if vtherm_hvac_mode is None:
        return None
    return VTHERM_TO_HA_MAP.get(str(vtherm_hvac_mode))
