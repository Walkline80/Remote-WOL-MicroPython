"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import _thread
import json
import gc
from .hardware_exception import HardwareException
from services.mqtt_service import MQTTService
from drivers.button import Button
from config import Config
from settings import Settings
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from utils.wol import wake_on_lan
from micropython import alloc_emergency_exception_buf
from machine import Timer


alloc_emergency_exception_buf(100)


class HardwareConfig(object):
	BUTTON = 0 # GPIO0 `BOOT Button`
	BUTTON_PRESS_TIMEOUT = 5 * 1000 # Button long press timeout

	WIFI_TIMER_ID = 6
	WIFI_TIMER_PERIOD = 5 * 60 * 1000

	MY_TOPIC = b'{}/remote_wol_device'.format(Settings.MQTT_USERNAME) # {}'.format(Settings.MQTT_USERNAME, Settings.MQTT_DEVICE_NAME)


class Version0(object):
	def __init__(self):
		self.__button = None
		self.__mqtt_client = None
		self.__starting = False
		self.__initialized = False
		self.__wifi_timer = Timer(HardwareConfig.WIFI_TIMER_ID)
		
	def setup(self):
		"""
		初始化硬件 v0
		"""
		self.__mqtt_client = MQTTService(self.__sub_cb)
		self.__button = Button(
			pin = HardwareConfig.BUTTON,
			press_cb = self.__button_press_cb,
			timeout = HardwareConfig.BUTTON_PRESS_TIMEOUT,
		)

		self.__initialized = True

	def start(self):
		assert self.__initialized == True, HardwareException("call setup() first")

		data = json.dumps({
			'hardware_version': Config.HARDWARE_VERSION,
			'hardware_name': Config.HARDWARE_NAME,
			'mac_address': Utilities.get_chip_id(),
			'ip_address': WifiHandler.get_ip_address()
		})

		self.__mqtt_client.connect()
		self.__mqtt_client.publish(HardwareConfig.MY_TOPIC, data)
		self.__mqtt_client.subscribe(HardwareConfig.MY_TOPIC)

		self.__starting = True

		self.__wifi_timer.init(
			mode=Timer.PERIODIC,
			period=HardwareConfig.WIFI_TIMER_PERIOD,
			callback=self.__wifi_timer_cb
		)

		_thread.start_new_thread(self.__msg_timer_cb, ())

	def stop(self):
		self.__button.deinit()

		try:
			self.__mqtt_client.deinit()
		except:
			pass

		self.__starting = False
		self.__button = None

	def __button_press_cb(self, duration):
		print("button pressed over {} ms".format(duration))
		
		Utilities.del_settings_file()
		Utilities.hard_reset()

	def __publish_data(self, value):
		data = json.dumps({
			'key': Settings.MQTT_DATA_POINT[0],
			'vlue': value
		})

		self.__mqtt_client.publish(HardwareConfig.MY_TOPIC, data)
		self.__mqtt_client.ping()

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
					raise OSError(err_msg)
			
			gc.collect()

	def __sub_cb(self, topic, msg):
		if topic == HardwareConfig.MY_TOPIC:
			print("msg: {}".format(msg))

			try:
				json_obj = json.loads(str(msg, "utf-8"))

				# {"msg": "wake_up", "params": {"mac": "112233445566"}}
				if json_obj['msg'] == "wake_up":
					params = json_obj['params']

					wake_on_lan(params['mac'])
					# print("wake up pc[{}] via wol".format(params['mac']))
			except ValueError:
				pass
		
		gc.collect()
