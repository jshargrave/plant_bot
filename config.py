from vh400_sensor import VH400Sensor, VH400SensorMode, VH400SensorState
import enum

# Soil thresholds
DRY_THRESHOLD = 0.10
WET_THRESHOLD = 0.25


class PlantBotMode(enum.Enum):
    # These describe the current state that the bot is in
    startup = 0
    reading = 1
    monitor = 2   # Checking sensors every interval
    notify = 3    # Sending notifications every interval
    watering = 4  # Watering
    waiting = 5   # Waiting mode, different then monitor

    # These modes keep the bot in one mode only, stopping any transitions
    monitor_only = 3
    notify_only = 4


# This class defines what states a sensor should be in for a action to take
# place.  For example, if you want the bot to send out notifications when the
# sensor has entered the dry state, add the VH400SensorState.dry state to the
# notify_state_list.
class PlantBot:
    def __init__(self):
        self.sensor_list = [
            VH400Sensor(0, DRY_THRESHOLD, WET_THRESHOLD, VH400SensorMode.normal),
            VH400Sensor(1, DRY_THRESHOLD, WET_THRESHOLD, VH400SensorMode.normal)
        ]

        self.notify_action_list = [
            VH400SensorState.dry,
            VH400SensorState.wet
        ]

        self.water_action_list = [
            VH400SensorState.dry
        ]

        self.state = PlantBotMode.startup
        self.waiting_period = 120  # Waiting phase period, defines the number of secs between sensor reads
