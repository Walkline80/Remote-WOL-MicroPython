"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import network

"""
STAT_IDLE              -- 1000
STAT_CONNECTING        -- 1001
STAT_GOT_IP            -- 1010
STAT_NO_AP_FOUND       -- 201
STAT_WRONG_PASSWORD    -- 202
STAT_BEACON_TIMEOUT    -- 200
STAT_ASSOC_FAIL        -- 203
STAT_HANDSHAKE_TIMEOUT -- 204
"""

__station_status_message = {
	network.STAT_IDLE: "network idle",
	# network.STAT_CONNECT_FAIL: "network connect failed",
	network.STAT_CONNECTING: "",
	network.STAT_GOT_IP: "Connected",
	network.STAT_NO_AP_FOUND: "could not found ap",
	network.STAT_WRONG_PASSWORD: "wrong password given",
	network.STAT_BEACON_TIMEOUT: "beacon timeout",
	network.STAT_ASSOC_FAIL: "assoc fail",
	network.STAT_HANDSHAKE_TIMEOUT: "handshake timeout"
}


class WifiHandler(object):
	AP_MODE = 0
	STA_MODE = 1
	STATION_CONNECTED = network.STAT_GOT_IP

	def __init__(self):
		pass

	@staticmethod
	def get_station():
		return network.WLAN(network.STA_IF)

	@staticmethod
	def get_access_point():
		return net.WLAN(network.AP_IF)

	@staticmethod
	def set_ap_status(active: bool):
		access_point = network.WLAN(network.AP_IF)
		access_point.active(active)

	@staticmethod
	def set_sta_status(active: bool):
		station = network.WLAN(network.STA_IF)
		station.active(active)

	@staticmethod
	def set_ap_mode(essid=None, password=None):
		from config import Config

		access_point = network.WLAN(network.AP_IF)

		access_point.active(False)
		access_point.active(True)

		essid = Config.AP_SSID if essid is None else essid
		password = "" if password is None else password

		access_point.ifconfig(Config.AP_IFCONFIG)
		access_point.config(essid=essid, password=password, hidden=False, authmode=Config.AP_AUTHMODE)

		print("\nWifi access point initialized:\n\t- essid    : {}\n\t- password : {}".format(essid, "(empty)" if password is None or password == "" else password))
		print("\n", access_point.ifconfig())

	@staticmethod
	def set_sta_mode(essid, password, timeout_sec=600, for_test=False):
		from utime import sleep_ms

		station = network.WLAN(network.STA_IF)
		# ifconfig = ("192.168.0.180", "255.255.255.0", "192.168.0.25", "192.168.0.1")

		print("\nConnecting to network...")

		if for_test:
			station.active(False)

			sleep_ms(500)

		if not station.isconnected():
			# station.ifconfig(ifconfig)
			station.active(True)
			station.connect(essid, password)

			retry_count = 0
			while not station.isconnected():
				if timeout_sec > 0:
					if retry_count >= timeout_sec * 2:
						break

				result_code = station.status()

				# result_code == network.STAT_CONNECT_FAIL or\
				if result_code == network.STAT_IDLE or\
					result_code == network.STAT_GOT_IP or\
					result_code == network.STAT_NO_AP_FOUND or\
					result_code == network.STAT_WRONG_PASSWORD:
					break
				elif result_code == network.STAT_CONNECTING:
					pass

				retry_count += 1
				sleep_ms(500)

		status_code = station.status()

		print(__station_status_message[status_code])
		print(station.ifconfig())

		return status_code

	@staticmethod
	def get_ip_address():
		station = network.WLAN(network.STA_IF)
		access_point = network.WLAN(network.AP_IF)

		access_point_ip = access_point.ifconfig()[0]

		return access_point_ip if access_point_ip != "0.0.0.0" else station.ifconfig()[0]
