
import time, sys
import schedule

import bme680
import RPi.GPIO as GPIO
import microdotphat as dothat
from influxdb import InfluxDBClient

import settings
from logger import logger
from system import System
from display import Screen


CURRENT_SCREEN = 0
SCREEN_LOCK = False
dotscreen = Screen()

class Dotatmo: 

    def __init__(self):
        self.run = False
        self.screens = ['  --  '] * 4 + ['']
        self.data = None
        self.db = None

        self.sensor = bme680.BME680(bme680.I2C_ADDR_PRIMARY)
         # Sensors setup
        self.sensor.set_humidity_oversample(bme680.OS_4X)
        self.sensor.set_pressure_oversample(bme680.OS_8X)
        self.sensor.set_temperature_oversample(bme680.OS_16X)
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self.sensor.set_temp_offset(settings.TEMP_OFFSET)
        
        if settings.AIR_QUALITY:
            self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)
            self.sensor.set_gas_heater_temperature(320)
            self.sensor.set_gas_heater_duration(150)
            self.sensor.select_gas_heater_profile(0)

        # Buttons setup
        GPIO.setmode(GPIO.BCM) 
        GPIO.setup(settings.BUTTONS['DISPLAY'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(settings.BUTTONS['SYSTEM'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(settings.BUTTONS['DISPLAY'], GPIO.FALLING, callback=self.display_action, bouncetime=200)
        GPIO.add_event_detect(settings.BUTTONS['SYSTEM'], GPIO.FALLING, callback=self.system_action, bouncetime=200)
        
    def __influx_connect(self):
        try:
            logger.info('Connecting to influxdb server')
            self.db = InfluxDBClient(settings.DB_HOST, 8086, database='dotatmo')
            self.db.create_database('dotatmo')
        except:
            logger.error('Unable to connect to influxdb server')

    def __get_sensor_data(self):
        logger.debug('Get sensors data')
        if self.sensor.get_sensor_data():
            self.data = self.sensor.data

            if not self.sensor.data.heat_stable:
                self.data.gas_resistance = 0

    def __update_screens(self):
        if not self.data:
            return

        iaq = 0
        if self.data.gas_resistance:
            iaq = self.data.gas_resistance/2000

        self.screens = [
            "{0:.{1}f}C".format(self.data.temperature, 2),
            "{0:.{1}f}%".format(self.data.humidity, 2),
            "{0:d}H".format(int(self.data.pressure)),
            "{0:.{1}f}a".format(iaq, 2),
            "" # Screen off
        ]
    
    def __send_data(self):
        if not self.db:
            self.__influx_connect()
        
        logger.debug('Send sensors data')
        timestamp = int(time.time())
        data = [
            {"measurement": "temperature", "time": timestamp, "fields": { "value": self.data.temperature }},
            {"measurement": "humidity", "time": timestamp, "fields": { "value": self.data.humidity }},
            {"measurement": "pressure", "time": timestamp, "fields": { "value": self.data.pressure }},
            {"measurement": "air", "time": timestamp, "fields": { "value": self.data.gas_resistance }},
        ]
        
        try:
            self.db.write_points(data)
        except:
            logger.error('Fail to send measurement to influxdb')
    
    def start(self):
        logger.info('Dotatmo started')
        self.run = True
        self.__get_sensor_data()
        
        dotscreen.show(u'Ahoy !', duration=1)
        schedule.every(5).seconds.do(self.__get_sensor_data)
        schedule.every().minute.do(self.__send_data)

        while self.run:
            schedule.run_pending()
            self.__update_screens()

            if not SCREEN_LOCK:
                dotscreen.show(str(self.screens[CURRENT_SCREEN]))
            time.sleep(0.3)

    def stop(self):
        logger.info('Stopping Dotatmo')
        self.run = False 
        GPIO.cleanup()
        dotscreen.show('BYE !', duration=1)
        sys.exit(0)

    @staticmethod
    def display_action(channel):
        global CURRENT_SCREEN
        next_screen = CURRENT_SCREEN+1
        if next_screen > 4:
            next_screen = 0

        logger.debug('Switched to %s', next_screen)
        CURRENT_SCREEN = next_screen

    @staticmethod
    def system_action(channel):
        global SCREEN_LOCK
        ip = [None, None] + System.get_ip().split('.')
        SCREEN_LOCK = True
        dotscreen.show('IP', ip, duration=4)
        SCREEN_LOCK = False
