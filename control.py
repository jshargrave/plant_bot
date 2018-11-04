from plant_bot import PlantBot
import configparser

CONFIG_FILE = "configuration.ini"


def main():
    # Parsing configuration file
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    # Starting plant bot up
    plant_bot = PlantBot(config)
    plant_bot.startup_phase()

    # Starting up Plant_Bot
    keep_looping = True
    while keep_looping:
        plant_bot.monitor_phase()


if __name__ == "__main__":
    main()

