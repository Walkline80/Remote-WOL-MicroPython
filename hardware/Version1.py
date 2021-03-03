"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""

import _thread
import json
import gc
from .hardware_exception import HardwareException
from .mqtt_sub_callback import MQTTSubCallback
from services.mqtt_service import MQTTService
from drivers.ds18b20 import DS18B20
from config import Config
from settings import Settings
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from micropython import alloc_emergency_exception_buf
from machine import Timer
from utime import sleep


alloc_emergency_exception_buf(100)


class HardwareConfig(object):
	DATA_TIMER_ID = 5 # Data Timer ID: 5
	WIFI_TIMER_ID = 6
	
	WIFI_TIMER_PERIOD = 5 * 60 * 1000

	USERNAME = Settings.MQTT_BIGIOT_USERNAME if bool(Settings.MQTT_IS_BIGIOT) else Settings.MQTT_CLIENT_ID
	MY_TOPIC = b'{}/remote_wol_device/{}'.format(USERNAME, WifiHandler.get_mac_address())
	DATA_TOPIC = b'{}/data'.format(USERNAME)

	DEVICE_STATUS_ONLINE_DATA = json.dumps({
		'command': 'device_status_indicator',
		'result': 'online',
		'hardware_version': Config.HARDWARE_VERSION,
		'hardware_name': Config.HARDWARE_NAME,
		'mac_address': WifiHandler.get_mac_address(),
		'ip_address': WifiHandler.get_ip_address(),
	})

	DEVICE_STATUS_OFFLINE_DATA = json.dumps({
		'command': 'device_status_indicator',
		'result': 'offline',
		'mac_address': WifiHandler.get_mac_address(),
	})


class Version1(object):
	def __init__(self):
		self.__mqtt_client = None
		self.__wifi_timer = None
		self.__data_timer = None
		self.__ds18b20 = None
		self.__starting = False
		self.__initialized = False

	def setup(self):
		"""
		初始化硬件 v0
		"""
		if self.__initialized: return

		self.__mqtt_client = MQTTService()

		mqtt_sub_callback = MQTTSubCallback(self.__mqtt_client, HardwareConfig.MY_TOPIC).get_callback()

		self.__mqtt_client.set_callback(mqtt_sub_callback)
		self.__ds18b20 = DS18B20(Config.DS18B20_DATALINE)
		self.__wifi_timer = Timer(HardwareConfig.WIFI_TIMER_ID)
		self.__data_timer = Timer(HardwareConfig.DATA_TIMER_ID)

		self.__initialized = True

	def start(self):
		assert self.__initialized, HardwareException("call setup() first")

		self.__mqtt_client.set_last_will(HardwareConfig.MY_TOPIC, HardwareConfig.DEVICE_STATUS_OFFLINE_DATA, retain=True)
		self.__mqtt_client.connect()
		self.__mqtt_client.publish(HardwareConfig.MY_TOPIC, HardwareConfig.DEVICE_STATUS_ONLINE_DATA, retain=True)
		self.__mqtt_client.subscribe(HardwareConfig.MY_TOPIC)

		self.__wifi_timer.init(
			mode=Timer.PERIODIC,
			period=HardwareConfig.WIFI_TIMER_PERIOD,
			callback=self.__wifi_timer_cb
		)

		self.__data_timer.init(
			mode=Timer.PERIODIC,
			period=Config.DATA_TIMER_PERIOD,
			callback=self.__data_timer_cb
		)

		self.__starting = True
		_thread.start_new_thread(self.__msg_timer_cb, ())

	def stop(self):
		if self.__starting: return

		self.__ds18b20.deinit()
		self.__data_timer.deinit()
		self.__wifi_timer.deinit()

		try:
			self.__mqtt_client.deinit()
		except:
			pass

		self.__starting = False

	def get_temperature(self):
		assert self.__starting, HardwareException("call start() first")

		return self.__ds18b20.temperature()

	def __publish_data(self, value):
		data = json.dumps({
			'key': Settings.MQTT_DATA_POINT[0],
			'vlue': value
		})

		self.__mqtt_client.publish(HardwareConfig.DATA_TOPIC, data)
		self.__mqtt_client.ping()

	def __data_timer_cb(self, timer):
		value = self.get_temperature()

		print("current temperature: {} ℃".format(value))
		
		try:
			self.__publish_data(value)
		except OSError as ose:
			err_msg = str(ose)

			if err_msg == "-1":
				pass
			elif err_msg == "[Errno 113] EHOSTUNREACH":
				Utilities.hard_reset()
			else:
				Utilities.log(self.__data_timer_cb, err_msg)
				sleep(1)
				Utilities.hard_reset()
		except Exception as e:
			err_msg = str(e)
			Utilities.log(self.__data_timer_cb, err_msg)
			sleep(1)
			Utilities.hard_reset()

	def __wifi_timer_cb(self, timer):
		if not Utilities.is_wifi_connected():
			Utilities.hard_reset()

	def __msg_timer_cb(self):
		while self.__starting:
			try:
				self.__mqtt_client.wait_msg()
			except OSError as ose:
				err_msg = str(ose)

				if err_msg == "-1":
					pass
				elif err_msg == "[Errno 113] EHOSTUNREACH":
					Utilities.hard_reset()
				else:
					Utilities.log(self.__msg_timer_cb, err_msg)
					sleep(1)
					Utilities.hard_reset()
					# raise OSError(err_msg)
			except Exception as e:
				err_msg = str(e)
				Utilities.log(self.__msg_timer_cb, err_msg)
				sleep(1)
				Utilities.hard_reset()

			gc.collect()
