"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import json
from utils.wol import wake_on_lan
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from machine import RTC
from utime import localtime
import gc


class MQTTSubCallback(object):
	def __init__(self, client, topic):
		self._client = client
		self._topic = topic

	def get_callback(self):
		return self.__sub_cb

	def __sub_cb(self, topic, msg):
		if topic != self._topic:
			return

		print("msg: {}".format(msg))

		try:
			json_obj = json.loads(str(msg, "utf-8"))
			command = json_obj['command']

			if command == "wake_up_pc":
				for count in range(3):
					wake_on_lan(json_obj['mac'])

				json_obj['command'] = 'wake_up_pc_result'
				json_obj['result'] = 'success'
				self._client.publish(topic, json.dumps(json_obj))
			elif command == 'device_remove':
				if json_obj['mac'] == WifiHandler.get_mac_address():
					json_obj['command'] = 'device_remove_result'
					json_obj['result'] = 'success'
					self._client.publish(topic, json.dumps(json_obj))
					
					Utilities.del_settings_file()
					Utilities.hard_reset()
			elif command == 'sync_datetime':
				datetime = json_obj['datetime']

				RTC().datetime((
					datetime['year'],
					datetime['month'],
					datetime['day'],
					datetime['weekday'], # 0~6
					datetime['hour'],
					datetime['minute'],
					datetime['second'],
					datetime['millisecond']
				))

				json_obj['command'] = 'sync_datetime_result'
				json_obj['result'] = 'success'
				self._client.publish(topic, json.dumps(json_obj))

				print("datetime: %02d-%02d-%02d %02d:%02d:%02d" % ((localtime()[:-2])))
			elif command == 'device_reboot':
				Utilities.hard_reset()
		except ValueError:
			pass
		except KeyError as ke:
			print("KeyError:", ke)

	gc.collect()
