from config import *
import time


def startup_phase():
    """This function handles any necessary initialization, and then starts the
    plant bot in the monitor phase.

    :return:
    """

    # Start plant bot startup phase
    plant_bot = PlantBot()
    plant_bot.state = PlantBotMode.startup

    # Start plant bot monitor phase
    plant_bot.state = PlantBotMode.monitor
    monitor_phase(plant_bot)


def monitor_phase(plant_bot):
    """This is the main loop that all other phases get triggered from.  At the
    beginning of each loop the reading phase is triggered to tell all sensors
    to take a reading.  This can update the sensors state.  Then the function
    checks for the sensor states and accordingly actions that should be taken.
    The the function enters the waiting phase, which last based on a plant bot
    class variable's value.  After the function repeats.

    :param plant_bot:
    :return:
    """

    keep_looping = True
    while keep_looping:
        # Enter reading phase
        reading_phase(plant_bot)

        # Checking if plant bot needs to enter notify state
        for state_action in plant_bot.notify_action_list:
            for sensor in plant_bot.sensor_list:
                if sensor.state == state_action:
                    notify_phase(plant_bot, sensor)

        # Checking if plant bot needs to enter watering state
        for state_action in plant_bot.water_action_list:
            for sensor in plant_bot.sensor_list:
                if sensor.state == state_action:
                    watering_phase(plant_bot, sensor)

        # If end of mode switching complete, enter waiting state
        waiting_phase(plant_bot)


def reading_phase(plant_bot):
    """This function is used to make all sensors take readings and update their
    states.

    :param plant_bot:
    :return:
    """

    # Set plant bot state
    plant_bot.state = PlantBotMode.notify

    # Call sensors to take readings
    for sensor in plant_bot.sensor_list:
        sensor.read_sensor()

    # Set plant bot state
    plant_bot.state = PlantBotMode.monitor


def notify_phase(plant_bot, sensor):
    """This function is used to notify the used about state changes for the sensors.

    :param plant_bot:
    :param sensor:
    :return:
    """
    # Set plant bot state
    plant_bot.state = PlantBotMode.notify

    # Only want to notify if this is a state change
    # This way we avoid spamming multiple notifications
    if sensor.did_state_change():
        notify(sensor)

    # Set plant bot state
    plant_bot.state = PlantBotMode.monitor


def watering_phase(plant_bot, sensor):
    """This function triggers the watering of the plants.

    :param plant_bot:
    :param sensor:
    :return:
    """

    # Set plant bot state
    plant_bot.state = PlantBotMode.watering

    # Set plant bot state
    plant_bot.state = PlantBotMode.monitor


def waiting_phase(plant_bot):
    """This function handles the waiting phase of the plant bot.  The wait
    interval is determined by the waiting variable of the PlantBot.

    :param plant_bot:
    :return:
    """

    # Set plant bot state
    plant_bot.state = PlantBotMode.waiting

    # Waiting phase
    time.sleep(plant_bot.waiting_period)

    # Set plant bot state
    plant_bot.state = PlantBotMode.monitor


def notify(sensor):
    pass


if __name__ == "__main__":
    # Starting plant bot up
    startup_phase()

