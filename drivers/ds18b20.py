"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""

from machine import Pin
from onewire import OneWire
from ds18x20 import DS18X20
from utime import sleep_ms


class DS18B20Exception(BaseException):
	pass


class DS18B20:
	"""
	DS18B20 驱动
	"""
	
	def __init__(self, dataline: int):
		assert dataline is not None and isinstance(dataline, int), DS18B20Exception("dataline must be a int")

		self._oneware = OneWire(Pin(dataline))
		self._ds18b20 = DS18X20(self._oneware)

	def deinit(self):
		self._ds18b20 = None
		self._oneware = None

	def temperature(self):
		"""
		获取温度
		"""
		roms = self._ds18b20.scan()
		self._ds18b20.convert_temp()

		sleep_ms(750)

		if len(roms) > 0:
			temp = round(self._ds18b20.read_temp(roms[0]), 1)

			return temp
		else:
			return -237.15


def run_test():
	ds18b20 = DS18B20(26)

	print("temperature: {}(°C)".format(ds18b20.temperature()))

if __name__ == "__main__":
	run_test()
