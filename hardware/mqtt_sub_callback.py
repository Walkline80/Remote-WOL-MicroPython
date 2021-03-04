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
					wake_on_lan(json_obj['mac_address'])

				result = {
					'command': command + '_result',
					'mac_address': json_obj['mac_address'],
					'result': 'success'
				}

				self._client.publish(topic, json.dumps(result))
			elif command == 'device_remove':
				if json_obj['mac_address'] != WifiHandler.get_mac_address():
					return

				result = {
					'command': command + '_result',
					'mac_address': json_obj['mac_address'],
					'result': 'success'
				}

				self._client.publish(topic, json.dumps(result))
				
				Utilities.del_settings_file()
				Utilities.hard_reset()
			elif command == 'sync_datetime':
				if json_obj['mac_address'] != WifiHandler.get_mac_address():
					return

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

				result = {
					'command': command + '_result',
					'mac_address': json_obj['mac_address'],
					'result': 'success'
				}

				self._client.publish(topic, json.dumps(result))

				print("datetime: %02d-%02d-%02d %02d:%02d:%02d" % ((localtime()[:-2])))
			elif command == 'device_reboot':
				if json_obj['mac_address'] != WifiHandler.get_mac_address():
					return

				Utilities.hard_reset()
			elif command == 'report_error_log':
				if json_obj['mac_address'] != WifiHandler.get_mac_address():
					return

				result = {
					'command': command + '_result',
					'mac_address': json_obj['mac_address'],
					'logs': Utilities.read_logs(),
					'result': 'success'
				}

				self._client.publish(topic, json.dumps(result))
		except ValueError:
			pass
		except KeyError as ke:
			print("KeyError:", ke)

	gc.collect()
