import mh_z19
import bme680
from prometheus_client.core import REGISTRY, GaugeMetricFamily

sensor = bme680.BME680(bme680.I2C_ADDR_SECONDARY)
sensor.set_humidity_oversample(bme680.OS_2X)
sensor.set_pressure_oversample(bme680.OS_4X)
sensor.set_temperature_oversample(bme680.OS_8X)
sensor.set_filter(bme680.FILTER_SIZE_3)
sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
sensor.set_gas_heater_temperature(320)
sensor.set_gas_heater_duration(150)
sensor.select_gas_heater_profile(0)
sensor.get_sensor_data()

class Collector:
    def __init__(self, room='', registry=REGISTRY):
        self.room = room
        if registry:
            registry.register(self)

    def collect(self):
        # CO2 metrics
        read = mh_z19.read(serial_console_untouched=True)
        if 'co2' in read:
            g = GaugeMetricFamily('air_co2', 'Air CO2 Level', labels=['room'])
            g.add_metric([self.room], read['co2'])
            yield g

        # Misc
        if sensor.get_sensor_data():
            g = GaugeMetricFamily('air_temperature', 'Air Temparture', labels=['room'])
            g.add_metric([self.room], sensor.data.temperature)
            yield g
            g = GaugeMetricFamily('air_humidity', 'Air Humidity', labels=['room'])
            g.add_metric([self.room], sensor.data.humidity)
            yield g
            g = GaugeMetricFamily('air_pressure', 'Air Pressure', labels=['room'])
            g.add_metric([self.room], sensor.data.pressure)
            yield g
            if sensor.data.heat_stable:
                g = GaugeMetricFamily('air_resistance', 'Air Resistance', labels=['room'])
                g.add_metric([self.room], sensor.data.gas_resistance)
                yield g

    def describe(self):
        yield GaugeMetricFamily('air_co2', 'Air CO2 Level', labels=['room'])
        yield GaugeMetricFamily('air_temperature', 'Air Temparture', labels=['room'])
        yield GaugeMetricFamily('air_humidity', 'Air Humidity', labels=['room'])
        yield GaugeMetricFamily('air_pressure', 'Air Pressure', labels=['room'])
        yield GaugeMetricFamily('air_resistance', 'Air Resistance', labels=['room'])
