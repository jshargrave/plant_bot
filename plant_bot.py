from vh400_sensor import VH400Sensor, VH400SensorMode, VH400SensorState
import enum
import time
from notify import EmailNotify, SMSNotify

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
            VH400SensorState.wet,
            VH400SensorState.bad_read
        ]

        # States that trigger watering
        self.water_action_list = [
            VH400SensorState.dry
        ]

        self.notify_list = [
            EmailNotify("happyguyhere@hotmail.com", "happyguyhere@hotmail.com", ["happyguyhere@hotmail.com", "password"])
        ]

        self.state = PlantBotMode.startup   # Initializing state to startup
        self.waiting_period = 120           # Waiting phase period (sec)

    def startup_phase(self):
        """This function handles any necessary initialization.

        :return:
        """

        # Start plant bot monitor phase
        self.state = PlantBotMode.monitor

    def monitor_phase(self):
        """This is the main loop that all other phases get triggered from.  At the
        beginning of each loop the reading phase is triggered to tell all sensors
        to take a reading.  This can update the sensors state.  Then the function
        checks for the sensor states and accordingly actions that should be taken.
        The the function enters the waiting phase, which last based on a plant bot
        class variable's value.  After the function repeats.

        :return:
        """

        # Enter reading phase
        self.reading_phase()

        # Check to see if Plant Bot needs to enter notify phase
        notify_sensor_list = self.get_phase_sensor_list(self.notify_action_list)
        if notify_sensor_list:
            self.notify_phase(notify_sensor_list)

        # Check to see if Plant Bot needs to enter watering phase
        water_sensor_list = self.get_phase_sensor_list(self.water_action_list)
        if water_sensor_list:
            self.watering_phase(water_sensor_list)

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

    def notify_phase(self, sensor_list):
        """This function is used to notify the used about state changes for the sensors.

        :param sensor_list:
        :return:
        """
        # Set plant bot state
        self.state = PlantBotMode.notify

        print("Sending notifications...")
        message = self.generate_message(sensor_list)
        for notify in self.notify_list:
            notify.notify(message)
        print("Complete!")

        # Set plant bot state
        self.state = PlantBotMode.monitor

    def watering_phase(self, sensor_list):
        """This function triggers the watering of the plants.

        :param sensor_list:
        :return:
        """

        # Set plant bot state
        self.state = PlantBotMode.watering

        # Trigger watering logic
        print("Entering watering phase...")
        # water()
        print("Watering phase complete!")

        # Set plant bot state
        self.state = PlantBotMode.monitor

    def waiting_phase(self):
        """This function handles the waiting phase of the plant bot.  The wait
        interval is determined by the waiting variable of the PlantBot.

        :return:
        """

        # Set plant bot state
        self.state = PlantBotMode.waiting

        # Waiting phase
        print("Waiting {} min...".format(self.waiting_period/60))
        time.sleep(self.waiting_period)
        print("Waiting complete!")

        # Set plant bot state
        self.state = PlantBotMode.monitor

    def get_phase_sensor_list(self, state_action_list):
        """This function is used to retrieve the list of sensors that are in
        the action state.  Meaning that the list of sensors returned are in the
        correct state when the action in question should be performed.

        :param state_action_list:
        :return:
        """
        sensor_action_list = []
        for state_action in state_action_list:
            for sensor in self.sensor_list:
                if sensor.did_state_change() and sensor.state == state_action:
                    sensor_action_list.append(sensor)
        return sensor_action_list

    def generate_message(self, sensor_list):
        message = "Plant Bot says hello!\n\n"

        for sensor in sensor_list:
            message += "{}\n\n".format(self.generate_sensor_message(sensor))
        return message

    @staticmethod
    def generate_sensor_message(sensor):
        message = (
                "Sensor Reading: \n"
                "  Sensor ID: {}\n"
                "  State: {}\n"
                "  Volumetric Water Content: {}\n").format(sensor.sensor_id, sensor.state, sensor.vwc)
        return message
