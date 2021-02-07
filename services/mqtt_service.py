"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import gc
from machine import Timer
from utime import time
from umqtt.simple import MQTTClient
from utils.utilities import Utilities
from settings import Settings


class MQTTService(object):
	def __init__(self, sub_cb=None):
		self.__client = None
		self.__sub_cb = sub_cb
		self.__heartbeat_timer = Timer(0)
		self.__heartbeat_counter = 0

		self.__client = MQTTClient(
			Settings.MQTT_CLIENT_ID,
			Settings.MQTT_HOST,
			Settings.MQTT_PORT,
			Settings.MQTT_USERNAME,
			Settings.MQTT_PASSWORD,
			Settings.MQTT_KEEPALIVE,
		)

	def __heartbeat_cb(self, timer):
		self.__heartbeat_counter += 1

		if self.__heartbeat_counter >= Settings.MQTT_KEEPALIVE:
			try:
				self.__client.publish(b'{}/ping'.format(Settings.MQTT_USERNAME), b'ping')
				self.__heartbeat_counter = 0
			except OSError as ose:
				err_msg = str(ose)

				print("err time:", time())
				print(err_msg)

				if err_msg in ("[Errno 104] ECONNRESET", "-1"):
					try:
						self.__client.disconnect()
					except OSError:
						pass
					finally:
						self.__client.connect()
				elif err_msg == "[Errno 113] EHOSTUNREACH":
					Utilities.hard_reset()

		gc.collect()

	def deinit(self):
		self.__client.disconnect()
		self.__heartbeat_timer.deinit()

		self.__client = None
		self.__heartbeat_timer = None

	def connect(self, clean_session=True):
		# mqtt_client.set_last_will(b'walkline/last_will', b'offline')
		self.__client.set_callback(self.__sub_cb)
		self.__client.connect(clean_session=clean_session)
		
		self.__heartbeat_timer.init(
			mode = Timer.PERIODIC,
			period = 1000,
			callback = self.__heartbeat_cb
		)

		print("mqtt forever loop")
		print("now:", time())

		username = Settings.MQTT_BIGIOT_USERNAME if bool(Settings.MQTT_IS_BIGIOT) else Settings.MQTT_CLIENT_ID

		self.__client.subscribe(b'{}/{}'.format(username, Settings.MQTT_CLIENT_ID))

	def disconnect(self):
		self.__client.disconnect()

	def set_callback(self, f):
		self.__sub_cb = f
		self.__client.set_callback(self.__sub_cb)

	def set_last_will(self, topic, msg, retain=False, qos=0):
		self.__client.set_last_will(topic, msg, retain=retain, qos=qos)

	def ping(self):
		self.__client.ping()

	def publish(self, topic, msg, retain=False, qos=0):
		self.__client.publish(topic, msg, retain=retain, qos=qos)

	def subscribe(self, topic, qos=0):
		self.__client.subscribe(topic, qos=qos)
	
	def wait_msg(self):
		self.__client.wait_msg()
	
	def check_msg(self):
		self.__client.check_msg()
