"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
class Utilities(object):
	@staticmethod
	def connect_to_internet(timeout_sec=600):
		"""
		使用硬件配置文件中的参数连接到 wifi 网络
		"""
		from .wifihandler import WifiHandler

		try:
			from settings import Settings
		except ImportError:
			raise ImportError('Cannot found settings.py file')

		result_code = WifiHandler.set_sta_mode(Settings.WIFI_SSID, Settings.WIFI_PASSWORD, timeout_sec)

		return result_code

	@staticmethod
	def is_wifi_connected():
		from .wifihandler import WifiHandler

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
	def log(func, msg, callback=None):
		"""
		记录日志到文件
		"""
		import os
		from utime import localtime
		from config import Config

		try:
			if os.stat('log.txt')[6] >= Config.LOG_FILE_LIMIT:
				os.remove('log.txt')
		except OSError:
			pass

		try:
			with open('log.txt', 'a+') as log:
				log.write("[%02d-%02d-%02d %02d:%02d:%02d] (%s): %s\n" % ((localtime()[:-2]) + (func.__name__, msg)))
		except:
			pass

		if callback: callback()

	@staticmethod
	def read_logs(limit=10):
		"""
		从日志文件末尾获取指定行数的记录
		"""
		import os

		try:
			filesize = os.stat('log.txt')[6]
		except OSError:
			return ''

		with open('log.txt', 'rb') as file:
			offset = -8
			while -offset <= filesize:
				file.seek(offset, 2)
				lines = file.readlines()

				if len(lines) > limit:
					return lines[len(lines) - limit:]
				else:
					offset -= 2
		
		return lines
