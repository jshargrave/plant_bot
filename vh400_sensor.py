from math import sqrt
import enum
import time


class VH400SensorState(enum.Enum):
    startup = 0                 # This is the initial state the sensor goes in, should leave this state after first read
    ok = 1
    dry = 2
    wet = 3
    bad_read = 4


class VH400SensorMode(enum.Enum):
    normal = 1
    record = 2
    record_range = 3


class VH400SensorData:
    def __init__(self, m_dn, m_volts, m_vwc, sd_dn, sd_volts, sd_vwc):
        # Save mean values
        self.mean_dn = m_dn
        self.mean_volts = m_volts
        self.mean_vwc = m_vwc

        # Save standard deviation values
        self.sd_dn = sd_dn
        self.sd_volts = sd_volts
        self.sd_vwc = sd_vwc


class VH400Sensor:
    def __init__(self, pin, d_threshold, w_threshold, mode):
        self.pin = pin
        self.d_threshold = d_threshold
        self.w_threshold = w_threshold
        self.mode = mode

        # State variables
        self.state = VH400SensorState.startup
        self.prev_state = self.state

    def read_sensor(self):
        # Read value and convert to voltage
        sensor_1dn = analogRead(self.pin)
        voltage = sensor_1dn*(3.0 / 1023.0)
        vwc = self.convert_volts_to_vwc(voltage)

        # Set the current state of the sensor after the read
        self.prev_state = self.state
        self.set_sensor_state(vwc)

        return sensor_1dn, voltage, vwc

    def get_sensor_reads_generator(self, num_reads):
        for i in range(num_reads):
            yield self.read_sensor()

    @staticmethod
    def convert_volts_to_vwc(voltage):
        # Calculate VWC
        vwc = 0
        # piecewise regressions
        if voltage <= 1.1:
            vwc = 10 * voltage - 1
        elif 1.1 < voltage <= 1.3:
            vwc = 25 * voltage - 17.5
        elif 1.3 < voltage <= 1.82:
            vwc = 48.08 * voltage - 47.5
        elif 1.82 < voltage <= 2.2:
            vwc = 26.32 * voltage - 7.89
        elif 2.2 < voltage:
            vwc = 62.5 * voltage - 87.5

        # If VWC < 0 return 0
        if vwc <= 0:
            return 0
        else:
            return vwc

    def did_state_change(self):
        # Return False if the first reading
        if self.prev_state == VH400SensorState.startup:
            return False

        return self.state != self.prev_state

    def set_sensor_state(self, vwc):
        if self.is_soil_dry(vwc):
            self.state = VH400SensorState.dry
        elif self.is_soil_wet(vwc):
            self.state = VH400SensorState.wet
        elif vwc > 0:
            self.state = VH400SensorState.ok
        else:
            self.state = VH400SensorState.bad_read

    def is_soil_dry(self, vwc):
        return vwc <= self.d_threshold

    def is_soil_wet(self, vwc):
        return vwc <= self.w_threshold

    def record(self):
        pass

    def record_range(self, num_measurements, delay):
        # Sums for calculating statistics
        sensor_dn_sum = 0
        sensor_voltage_sum = 0.0
        sensor_vwc_sum = 0.0

        # Arrays to hold multiple measurements
        sensor_dn_list = []
        sensor_voltage_list = []
        sensor_vwc_list = []

        # Make measurements and add to arrays
        for i in range(num_measurements):
            # Read the values from the sensor and extract to variables
            sensor_dn, sensor_voltage, sensor_vwc = self.read_sensor()

            # Add to statistics sums
            sensor_dn_sum += sensor_dn
            sensor_voltage_sum += sensor_voltage
            sensor_vwc_sum += sensor_vwc

            # Add to arrays
            sensor_dn_list.append(sensor_dn)
            sensor_voltage_list.append(sensor_voltage)
            sensor_vwc_list.append(sensor_vwc)

            # Wait for next measurement
            time.sleep(delay)

        # Calculate means
        sensor_dn_mean = sensor_dn_sum/num_measurements
        sensor_voltage_mean = sensor_voltage_sum/num_measurements
        sensor_vwc_mean = sensor_vwc_sum/num_measurements

        sq_dev_sum_dn = 0.0
        sq_dev_sum_volts = 0.0
        sq_dev_sum_vwc = 0.0

        # Loop back through to calculate SD
        for i in range(num_measurements):
            sq_dev_sum_dn += pow(sensor_dn_mean - sensor_dn_list[i], 2)
            sq_dev_sum_volts += pow(sensor_voltage_mean - sensor_voltage_list[i], 2)
            sq_dev_sum_vwc += pow(sensor_vwc_mean - sensor_vwc_list[i], 2)

        sensor_sd_dn = sqrt(sq_dev_sum_dn/num_measurements)
        sensor_sd_volts = sqrt(sq_dev_sum_volts/num_measurements)
        sensor_sd_vwc = sqrt(sq_dev_sum_vwc/num_measurements)

        VH400SensorData(sensor_dn_mean, sensor_voltage_mean, sensor_vwc_mean, sensor_sd_dn, sensor_sd_volts, sensor_sd_vwc)
