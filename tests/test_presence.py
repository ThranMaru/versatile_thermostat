# pylint: disable=wildcard-import, unused-wildcard-import, protected-access, unused-argument, line-too-long

""" Test the Security featrure """
import logging
from unittest.mock import patch, call, AsyncMock, MagicMock, PropertyMock

# from datetime import timedelta, datetime

from custom_components.versatile_thermostat.base_thermostat import BaseThermostat
from custom_components.versatile_thermostat.feature_presence_manager import (
    FeaturePresenceManager,
)

from .commons import *

logging.getLogger().setLevel(logging.DEBUG)


@pytest.mark.parametrize(
    "temp, absence, state, nb_call, presence_state, changed",
    [
        (19, False, STATE_ON, 1, STATE_ON, True),
        (17, True, STATE_OFF, 1, STATE_OFF, True),
        (19, False, STATE_HOME, 1, STATE_ON, True),
        (17, True, STATE_NOT_HOME, 1, STATE_OFF, True),
        (17, False, STATE_UNAVAILABLE, 0, STATE_UNKNOWN, False),
        (17, False, STATE_UNKNOWN, 0, STATE_UNKNOWN, False),
        (17, False, "wrong state", 0, STATE_UNKNOWN, False),
    ],
)
async def test_presence_feature_manager(
    hass: HomeAssistant, temp, absence, state, nb_call, presence_state, changed
):
    """Test the FeaturePresenceManager class direclty"""

    fake_vtherm = MagicMock(spec=BaseThermostat)
    type(fake_vtherm).name = PropertyMock(return_value="the name")
    type(fake_vtherm).preset_mode = PropertyMock(return_value=VThermPreset.COMFORT)

    # 1. creation
    presence_manager = FeaturePresenceManager(fake_vtherm, hass)

    assert presence_manager is not None
    assert presence_manager.is_configured is False
    assert presence_manager.is_absence_detected is False
    assert presence_manager.presence_state == STATE_UNAVAILABLE
    assert presence_manager.name == "the name"

    assert len(presence_manager._active_listener) == 0

    custom_attributes = {}
    presence_manager.add_custom_attributes(custom_attributes)
    assert custom_attributes["presence_sensor_entity_id"] is None
    assert custom_attributes["presence_state"] == STATE_UNAVAILABLE
    assert custom_attributes["is_presence_configured"] is False

    # 2. post_init
    presence_manager.post_init(
        {
            CONF_PRESENCE_SENSOR: "sensor.the_presence_sensor",
            CONF_USE_PRESENCE_FEATURE: True,
        }
    )

    assert presence_manager.is_configured is True
    assert presence_manager.presence_state == STATE_UNKNOWN
    assert presence_manager.is_absence_detected is False

    custom_attributes = {}
    presence_manager.add_custom_attributes(custom_attributes)
    assert (
        custom_attributes["presence_sensor_entity_id"] == "sensor.the_presence_sensor"
    )
    assert custom_attributes["presence_state"] == STATE_UNKNOWN
    assert custom_attributes["is_presence_configured"] is True

    # 3. start listening
    await presence_manager.start_listening()
    assert presence_manager.is_configured is True
    assert presence_manager.presence_state == STATE_UNKNOWN
    assert presence_manager.is_absence_detected is False

    assert len(presence_manager._active_listener) == 1

    # 4. test refresh with the parametrized
    # fmt:off
    with patch("homeassistant.core.StateMachine.get", return_value=State("sensor.the_presence_sensor", state)) as mock_get_state:
    # fmt:on
        # Configurer les méthodes mockées
        fake_vtherm.find_preset_temp.return_value = temp
        fake_vtherm.change_target_temperature = AsyncMock()
        fake_vtherm.async_control_heating = AsyncMock()

        ret = await presence_manager.refresh_state()
        assert ret == changed
        assert presence_manager.is_configured is True
        assert presence_manager.presence_state == presence_state
        assert presence_manager.is_absence_detected is absence

        assert mock_get_state.call_count == 1

        assert fake_vtherm.find_preset_temp.call_count == nb_call

        if nb_call == 1:
            fake_vtherm.find_preset_temp.assert_has_calls(
                [
                    call.find_preset_temp(VThermPreset.COMFORT),
                ]
            )

            assert fake_vtherm.change_target_temperature.call_count == nb_call
            fake_vtherm.change_target_temperature.assert_has_calls(
                [
                    call.find_preset_temp(temp),
                ]
            )

            assert fake_vtherm.async_control_heating.call_count == 0

        fake_vtherm.reset_mock()

    # 5. Check custom_attributes
        custom_attributes = {}
        presence_manager.add_custom_attributes(custom_attributes)
        assert custom_attributes["presence_sensor_entity_id"] == "sensor.the_presence_sensor"
        assert custom_attributes["presence_state"] == presence_state
        assert custom_attributes["is_presence_configured"] is True

    # 6. test _presence_sensor_changed with the parametrized
    fake_vtherm.find_preset_temp.return_value = temp
    fake_vtherm.change_target_temperature = AsyncMock()
    fake_vtherm.async_control_heating = AsyncMock()

    await presence_manager._presence_sensor_changed(
        event=Event(
            event_type=EVENT_STATE_CHANGED,
            data={
                "entity_id": "sensor.the_presence_sensor",
                "new_state": State("sensor.the_presence_sensor", state),
                "old_state": State("sensor.the_presence_sensor", STATE_UNAVAILABLE),
            }))
    assert ret == changed
    assert presence_manager.is_configured is True
    assert presence_manager.presence_state == presence_state
    assert presence_manager.is_absence_detected is absence

    assert fake_vtherm.find_preset_temp.call_count == nb_call

    if nb_call == 1:
        fake_vtherm.find_preset_temp.assert_has_calls(
            [
                call.find_preset_temp(VThermPreset.COMFORT),
            ]
        )

        assert fake_vtherm.change_target_temperature.call_count == nb_call
        fake_vtherm.change_target_temperature.assert_has_calls(
            [
                call.find_preset_temp(temp),
            ]
        )

        assert fake_vtherm.async_control_heating.call_count == 1
        fake_vtherm.async_control_heating.assert_has_calls([
            call.async_control_heating(force=True)
        ])

    fake_vtherm.reset_mock()

    # 7. Check custom_attributes
    custom_attributes = {}
    presence_manager.add_custom_attributes(custom_attributes)
    assert custom_attributes["presence_sensor_entity_id"] == "sensor.the_presence_sensor"
    assert custom_attributes["presence_state"] == presence_state
    assert custom_attributes["is_presence_configured"] is True

    presence_manager.stop_listening()
    await hass.async_block_till_done()
