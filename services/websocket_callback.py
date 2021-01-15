"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import gc
from config import Config
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler


class WebSocketCallback(object):
	def _OnWebSocketTextMsg(webSocket, msg) :
		import ujson

		print('WebSocket text message: %s' % msg)
		# webSocket.SendTextMessage('Received "%s"' % msg)

		try:
			params = ujson.loads(msg)

			if params["command"] == "identity":
				from utils.json_const import identity_result

				hardware_version = Config.HARDWARE_VERSION
				hardware_name = Config.HARDWARE_NAME
				mac_address = Utilities.get_chip_id()
				ip_address = WifiHandler.get_ip_address()
				
				identity_result.update(
					hardware_version = hardware_version,
					hardware_name = hardware_name,
					mac_address = mac_address,
					ip_address = ip_address
				)

				webSocket.SendTextMessage(ujson.dumps(identity_result))
			elif params["command"] == "save_settings":
				from utils.utilities import Utilities
				from utils.json_const import save_settings_result_success, save_settings_result_failed
				from utils.settings_template import template

				params["mqtt_data_point"] = "\"" + "\", \"".join(params["mqtt_data_point"].split(",")) + "\""
				settings = template.format(**params)
				# print(settings)
				with open("settings.py", "w") as file:
					length = file.write(settings)

					if length == len(settings):
						webSocket.SendTextMessage(ujson.dumps(save_settings_result_success))

						Utilities.make_mode_file()
					else:
						webSocket.SendTextMessage(ujson.dumps(save_settings_result_failed))
			elif params["command"] == "reboot_device":
				from utils.utilities import Utilities

				Utilities.hard_reset()
			elif params["command"] == "check_wifi":
				from utils.wifihandler import WifiHandler
				from utils.json_const import check_wifi_result

				result_code = WifiHandler.set_sta_mode(params["wifi_ssid"], params["wifi_password"], timeout_sec=60, for_test=True)

				check_wifi_result.update(
					result_code = result_code
				)

				webSocket.SendTextMessage(ujson.dumps(check_wifi_result))

				if result_code == WifiHandler.STATION_CONNECTED:
					import urequests
					from utils.json_const import check_internet_result_success, check_internet_result_failed
					from config import Config

					try:
						res = urequests.get(Config.INTERNET_TESTING_URL, timeout=10.0)
						
						if res:
							if res.text == "Success":
								webSocket.SendTextMessage(ujson.dumps(check_internet_result_success))
							else:
								webSocket.SendTextMessage(ujson.dumps(check_internet_result_failed))
						else:
							webSocket.SendTextMessage(ujson.dumps(check_internet_result_failed))
					except Exception:
						webSocket.SendTextMessage(ujson.dumps(check_internet_result_failed))
			elif params["command"] == "check_mqtt":
				from umqtt.simple import MQTTClient
				from utils.json_const import check_mqtt_result_success, check_mqtt_result_failed

				def sub_cb(topic, msg):
					pass
				
				mqtt_client = MQTTClient(
					params["device_name"],
					params["host"],
					int(params["port"]),
					params["device_number"],
					params["device_authorize"],
					int(params["keepalive"])
				)

				try:
					mqtt_client.set_callback(sub_cb)
					print("check_mqtt_result:", mqtt_client.connect(True))
					print("test subscribe:", mqtt_client.subscribe("{}/data".format(params["username"]).encode()))
					print("test publish:", mqtt_client.publish("{}/data".format(params["username"]).encode(), "world"))
					mqtt_client.disconnect()

					webSocket.SendTextMessage(ujson.dumps(check_mqtt_result_success))
				except Exception as e:
					print(str(e))

					# e == 5, authorized failed, means device number or device authorize wrong
					if str(e) == "5":
						check_mqtt_result_failed.update(
							error_code = "5",
							error_msg = "Authorized failed, check Device Number and Device Authorize"
						)
					# e == 128, sub failed, means client_id or topic auth(username/data) wrong
					elif str(e) == "128":
						check_mqtt_result_failed.update(
							error_code = "128",
							error_msg = "Subscribe failed, check Username and Device Name"
						)
					else:
						check_mqtt_result_failed.update(
							error_code = str(e),
							error_msg = "Unknown error: {}".format(str(e))
						)

					webSocket.SendTextMessage(ujson.dumps(check_mqtt_result_failed))
		except ValueError:
			webSocket.SendTextMessage("Params Format Error")

		gc.collect()

	def _OnWebSocketBinaryMsg(webSocket, msg) :
		print('WebSocket binary message: %s' % msg)

	def _OnWebSocketClosed(webSocket) :
		print('WebSocket %s:%s closed' % webSocket.Request.UserAddress)

	def _OnWebSocketAccepted(microWebSrv2, webSocket):
		print('WebSocket accepted:')
		print('   - User   : %s:%s' % webSocket.Request.UserAddress)
		print('   - Path   : %s'    % webSocket.Request.Path)
		print('   - Origin : %s'    % webSocket.Request.Origin)

		if webSocket.Request.Path.lower() == Config.WEBSOCKET_PATH:
			webSocket.OnTextMessage   = WebSocketCallback._OnWebSocketTextMsg
			webSocket.OnBinaryMessage = WebSocketCallback._OnWebSocketBinaryMsg
			webSocket.OnClosed        = WebSocketCallback._OnWebSocketClosed

			webSocket.SendTextMessage("hello from server")
		else:
			webSocket.Close()
