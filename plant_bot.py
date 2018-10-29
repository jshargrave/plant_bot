from vh400_sensor import VH400Sensor, VH400SensorMode, VH400SensorState
import enum
import time

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


# This class defines what states a sensor should be in for a action to take
# place.  For example, if you want the bot to send out notifications when the
# sensor has entered the dry state, add the VH400SensorState.dry state to the
# notify_state_list.
class PlantBot:
    def __init__(self):
        # List of sensors
        self.sensor_list = [
            VH400Sensor(0, DRY_THRESHOLD, WET_THRESHOLD, VH400SensorMode.normal),
            VH400Sensor(1, DRY_THRESHOLD, WET_THRESHOLD, VH400SensorMode.normal)
        ]

        # States that trigger notification
        self.notify_action_list = [
            VH400SensorState.dry,
            VH400SensorState.wet
        ]

        # States that trigger watering
        self.water_action_list = [
            VH400SensorState.dry
        ]

        self.state = PlantBotMode.startup   # Initializing state to startup
        self.waiting_period = 120           # Waiting phase period (sec)

    def startup_phase(self):
        """This function handles any necessary initialization, and then starts the
        plant bot in the monitor phase.

        :return:
        """

        # Start plant bot monitor phase
        self.state = PlantBotMode.monitor
        self.monitor_phase()

    def monitor_phase(self):
        """This is the main loop that all other phases get triggered from.  At the
        beginning of each loop the reading phase is triggered to tell all sensors
        to take a reading.  This can update the sensors state.  Then the function
        checks for the sensor states and accordingly actions that should be taken.
        The the function enters the waiting phase, which last based on a plant bot
        class variable's value.  After the function repeats.

        :return:
        """

        keep_looping = True
        while keep_looping:
            # Enter reading phase
            self.reading_phase()

            # Checking if plant bot needs to enter notify state
            for state_action in self.notify_action_list:
                for sensor in self.sensor_list:
                    if sensor.state == state_action:
                        self.notify_phase(sensor)

            # Checking if plant bot needs to enter watering state
            for state_action in self.water_action_list:
                for sensor in self.sensor_list:
                    if sensor.state == state_action:
                        self.watering_phase(sensor)

            # If end of mode switching complete, enter waiting state
            self.waiting_phase()

    def reading_phase(self):
        """This function is used to make all sensors take readings and update their
        states.

        :return:
        """

        # Set plant bot state
        self.state = PlantBotMode.notify

        # Call sensors to take readings
        for sensor in self.sensor_list:
            sensor.read_sensor()

        # Set plant bot state
            self.state = PlantBotMode.monitor

    def notify_phase(self, sensor):
        """This function is used to notify the used about state changes for the sensors.

        :param sensor:
        :return:
        """
        # Set plant bot state
        self.state = PlantBotMode.notify

        # Only want to notify if this is a state change.  This way we avoid
        # spamming multiple notifications
        if sensor.did_state_change():
            self.notify(sensor)

        # Set plant bot state
            self.state = PlantBotMode.monitor

    def watering_phase(self, sensor):
        """This function triggers the watering of the plants.

        :param sensor:
        :return:
        """

        # Set plant bot state
        self.state = PlantBotMode.watering

        # Trigger watering logic
        # water()

        # Set plant bot state
        self.state = PlantBotMode.monitor

    def waiting_phase(self):
        """This function handles the waiting phase of the plant bot.  The wait
        interval is determined by the waiting variable of the PlantBot.

        :param plant_bot:
        :return:
        """

        # Set plant bot state
        self.state = PlantBotMode.waiting

        # Waiting phase
        time.sleep(self.waiting_period)

        # Set plant bot state
        self.state = PlantBotMode.monitor
