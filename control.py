from plant_bot import PlantBot


if __name__ == "__main__":
    # Starting plant bot up
    plant_bot = PlantBot()
    plant_bot.startup_phase()

    keep_looping = True
    while keep_looping:
        plant_bot.monitor_phase()

