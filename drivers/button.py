"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython

[Customize Button v1.1]

Author: Walkline Wang
Email: walkline@gmail.com
GitHub: walkline80
Gitee: walkline
License: MIT

# IMPORTANT: THIS MODULE ONLY TESTED ON ESP32 BOARD
"""

import micropython
from machine import Pin, Timer
from utime import ticks_ms


class ButtonException(BaseException):
	pass


class Button(object):
	"""
	- 自定义按钮
	
	支持点击和长按两种模式

	长按模式分为：
	    1. 长按超时触发
	    2. 长按超时松开触发
	
	参数：
	    pin：GPIO 引脚
	    click_cb：单击事件回调函数
	    press_cb：长按事件回调函数
	    timeout：长按触发超时时间（ms）
		behavior：长按触发模式选择
	"""

	# __BUTTON_RESPONSE_INTERVAL = 20 # 目前使用定时器实现按钮点击并不需要消除抖动
	
	# trigger long press while holding button
	BEHAVIOR_HOLD = 0

	# trigger long press after release button
	BEHAVIOR_RELEASE = 1

	def __init__(self, pin=None, click_cb=None, dblclick_cb=None, press_cb=None, timeout=3000, behavior=BEHAVIOR_HOLD):
		assert pin is not None, ButtonException("pin must be specified")
		assert click_cb is not None or dblclick_cb is not None or press_cb is not None,\
			ButtonException("at least set one of 'click_cb', 'dblclick_cb' or 'press_cb")

		if press_cb is not None:
			assert (click_cb is not None and dblclick_cb is None) or (click_cb is None and dblclick_cb is not None) or (click_cb is None and dblclick_cb is None),\
				ButtonException("cannot set both of 'click_cb' and 'dblckck_cb' at same time")
		else:
			assert (click_cb is not None and dblclick_cb is None) or (click_cb is None and dblclick_cb is not None),\
				ButtonException("cannot set both of 'click_cb' and 'dblckck_cb' at same time") # sorry, i'm too caigou...

		self.__button = Pin(pin, Pin.IN, Pin.PULL_UP)
		self.__click_cb = click_cb # click callback
		self.__dblclick_cb = dblclick_cb # double click callback
		self.__press_cb = press_cb # press callback
		self.__timeout = timeout # press callback acting if timed out
		self.__last_ticks = ticks_ms()
		self.__button_holding = False # true: holding, false: releasing
		self.__button_status = False # true: holded, false: released
		self.__button_pressed = False # true: pressed once, false: never pressed
		self.__click_counter = 0 # button clicked times
		self.__timer = None
		self.__behavior = behavior
		self.__timer = Timer(10)

		try:
			self.__timer.init(
				mode=Timer.PERIODIC,
				period=20,
				callback=self.__timer_cb
			)
		except RuntimeError:
			pass

	def deinit(self):
		self.__button = None
		self.__timer.deinit()
		self.__timer = None

	@property
	def __time_diff(self):
		return ticks_ms() - self.__last_ticks

	def __timer_cb(self, timer):
		self.__button_holding = not self.__button.value()
		# print("hold" if self.__button_hold else "release")

		if self.__button_holding:
			if self.__button_status == self.__button_holding:
				if self.__time_diff >= self.__timeout and self.__behavior == self.BEHAVIOR_HOLD:
					if self.__press_cb is not None:
						self.__press_cb(self.__time_diff)

					self.__button_status = False
					self.__button_pressed = True

					self.__last_ticks = ticks_ms()
			else:
				if not self.__button_pressed:
					self.__button_status = True
		else:
			if self.__button_status:
				if self.__time_diff >= self.__timeout and self.__behavior == self.BEHAVIOR_RELEASE:
					if self.__press_cb is not None:
						self.__press_cb(self.__time_diff)
				else:
					if self.__dblclick_cb is not None:

						
						if self.__time_diff <= 148:
							self.__click_counter += 1
						else:
							self.__click_counter = 0

						# self.__last_ticks = ticks_ms()

						if self.__click_counter >= 2:
							self.__dblclick_cb()

							self.__click_counter = 0
					else:
						if self.__click_cb is not None:
							self.__click_cb()

				self.__button_status = False
			else:
				self.__last_ticks = ticks_ms()
				self.__button_pressed = False
	
	@property
	def timeout(self):
		return self.__timeout


__press_counts = 0
__led = None

def run_test():
	global __led

	__led = Pin(2, Pin.OUT, value=0)

	from utime import sleep_ms
	import urandom

	def button_click_cb():
		global __led

		__led.value(not __led.value())
		print("button clicked", urandom.randint(0, 65535))
	
	def button_dblclick_cb():
		global __led

		__led.value(not __led.value())
		print("button double clicked", urandom.randint(0, 65535))

	def button_press_cb(duration):
		global __press_counts

		__press_counts += 1
		print("button pressed over {} ms".format(duration))

	button = Button(
		pin=0,
		# click_cb=button_click_cb,
		dblclick_cb=button_dblclick_cb,
		press_cb=button_press_cb,
		timeout=3000,
		behavior=Button.BEHAVIOR_HOLD
	)

	print(
"""
======================================
       Running button test unit

  Supports:
      1. click
      2. double click (beta)
      3. long press (over {} ms)

  Tips:
      Try to click the BOOT button
      Take long press twice to end
======================================
""".format(button.timeout)
	)

	while __press_counts < 2:
		sleep_ms(500)

	__led.value(0)
	button.deinit()

	print(
"""
==========================
    Unit test complete
==========================
"""
	)


if __name__ == "__main__":
	run_test()
