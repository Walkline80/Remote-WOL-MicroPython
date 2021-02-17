"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
class Utilities(object):
	@staticmethod
	def get_chip_id():
		from machine import unique_id

		return "".join(['%02X' % i for i in unique_id()])

	@classmethod
	def connect_to_internet(cls, timeout_sec=600):
		from utils.wifihandler import WifiHandler

		try:
			from settings import Settings
		except ImportError:
			# 至此说明 mode 文件存在，但是 settings.py 文件不存在
			# 则需要删除 mode 文件并复位，进入配网模式
			cls.enter_smart_config_mode()

		result_code = WifiHandler.set_sta_mode(Settings.WIFI_SSID, Settings.WIFI_PASSWORD, timeout_sec)

		return result_code

	@classmethod
	def is_wifi_connected(cls):
		from utils.wifihandler import WifiHandler

		station = WifiHandler.get_station()

		return station.isconnected()

	@staticmethod
	def is_settings_file_exist():
		"""
		如果 settings.py 不文件存在，则表示启用 ap 模式，用于用户配网
		"""
		import os

		try:
			os.stat("settings.py")

			return True
		except OSError:
			return False

	@staticmethod
	def del_settings_file():
		"""
		删除 mode 文件，开启配网模式
		"""
		import os

		try:
			os.remove("settings.py")

			return True
		except OSError:
			return False

	@staticmethod
	def soft_reset():
		"""
		a soft reset
		"""

		from sys import exit

		exit()

	@staticmethod
	def hard_reset():
		"""
		a hard reset
		"""

		from machine import reset

		reset()

	@staticmethod
	def log(func, msg):
		"""
		记录日志到文件
		"""

		try:
			with open('log.txt', 'a+') as log:
				log.write('{}: {}\n'.format(func.__name__, msg))
		except:
			pass
