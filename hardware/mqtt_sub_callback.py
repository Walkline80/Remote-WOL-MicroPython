"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import json
from utils.wol import wake_on_lan
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
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

			if json_obj['command'] == "wake_up_pc":
				wake_on_lan(json_obj['mac'])

				json_obj['command'] = 'wake_up_pc_result'
				json_obj['result'] = 'success'

				self._client.publish(topic, json.dumps(json_obj))
			elif json_obj['command'] == 'device_remove':
				if json_obj['mac'] == WifiHandler.get_mac_address():

					json_obj['command'] = 'device_remove_result'
					json_obj['result'] = 'success'

					self._client.publish(topic, json.dumps(json_obj))
					
					Utilities.del_settings_file()
					Utilities.hard_reset()
		except ValueError:
			pass
		except KeyError as ke:
			print("KeyError:", ke)

	gc.collect()
