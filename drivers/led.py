"""
Customize Led v1.0.1

Author: Walkline Wang
Email : walkline@gmail.com
GitHub: walkline80
Gitee: walkline
License: MIT

# IMPORTANT: THIS MODULE ONLY TESTED ON ESP32 BOARD
"""

from machine import Pin
from utime import sleep_ms
import _thread

"""
	International Morse Code

1. The length of a dot is one unit.
2. A dash is three units.
3. The space between parts of the same letter is one unit. # 同一个字母的点划之间空 1 个单位
4. The space between letters is three units. # 同一个单词不同字母之间空 3 个单位
5. The space between words is serven units. # 不同单词之间空 7 个单位


	Code Definition

A: ·-		B: -···		C: -·-·		D: -··		E: ·		F: ··-·
G: --·		H: ····		I: ··		J: ·---		K: -·-		L: ·-··
M: --		N: -·		O: ---		P: ·--·		Q: --·-		R: ·-·
S: ···		T: -		U: ··-		V: ···-		W: ·--		X: -··-
Y: -·--		Z: --··		1: ·----	2: ··---	3: ···--	4: ····-
5: ·····	6: -····	7: --···	8: ---··	9: ----·	0: -----
"""


class MorseCodeException(BaseException):
	pass


class MorseCode(object):
	ONE_UNIT = 200
	__THREE_UNITS = 3 * ONE_UNIT
	__SEVEN_UNITS = 7 * ONE_UNIT
	__SPACE = 0 # 作为同一个字母点划之间的间隔（1 个单位）

	# E means end...
	DOT, DOT_E = (ONE_UNIT, __SPACE), (ONE_UNIT,)
	DASH, DASH_E = (__THREE_UNITS, __SPACE), (__THREE_UNITS,)

	# THREE_E：作为同一个单词不同字母之间的间隔（3个单位）
	# SEVEV_E：不好判断 Unicode 字符串，所以只接受 [空格] 作为单词分隔符并确定间隔时间（7 个单位）
	__THREE_E, __SEVEN_E = (__THREE_UNITS,), (__SEVEN_UNITS,)

	SUPPORTED_CODES = (
		'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l',
		'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x',
		'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0',
		' '
	)

	__CODES = {
		'a': (DOT, DASH_E),						'b': (DASH, DOT, DOT, DOT_E),			'c': (DASH, DOT, DASH, DOT_E),			'd': (DASH, DOT, DOT_E),
		'e': ((DOT_E),),						'f': (DOT, DOT, DASH, DOT_E),			'g': (DASH, DASH, DOT_E),				'h': (DOT, DOT, DOT, DOT_E),
		'i': (DOT, DOT_E),						'j': (DOT, DASH, DASH, DASH_E),			'k': (DASH, DOT, DASH_E),				'l': (DOT, DASH, DOT, DOT_E),
		'm': (DASH, DASH_E),					'n': (DASH, DOT_E),						'o': (DASH, DASH, DASH_E),				'p': (DOT, DASH, DASH, DOT_E),
		'q': (DASH, DASH, DOT, DASH_E),			'r': (DOT, DASH, DOT_E),				's': (DOT, DOT, DOT_E),					't': ((DASH_E),),
		'u': (DOT, DOT, DASH_E),				'v': (DOT, DOT, DOT, DASH_E),			'w': (DOT, DASH, DASH_E),				'x': (DASH, DOT, DOT, DASH_E),
		'y': (DASH, DOT, DASH, DASH_E),			'z': (DASH, DASH, DOT, DOT_E),			'1': (DOT, DASH, DASH, DASH, DASH_E),	'2': (DOT, DOT, DASH, DASH, DASH_E),
		'3': (DOT, DOT, DOT, DASH, DASH_E),		'4': (DOT, DOT, DOT, DOT, DASH_E),		'5': (DOT, DOT, DOT, DOT, DOT_E),		'6': (DASH, DOT, DOT, DOT, DOT_E),
		'7': (DASH, DASH, DOT, DOT, DOT_E),		'8': (DASH, DASH, DASH, DOT, DOT_E),	'9': (DASH, DASH, DASH, DASH, DOT_E),	'0': (DASH, DASH, DASH, DASH, DASH_E),
		' ': (__SEVEN_E)
	}

	def __init__(self):
		pass

	def translate(self, message):
		assert isinstance(message, str), MorseCodeException("message must be a string")

		result = ()

		code_list = [chr(letter) for letter in bytearray(message) if chr(letter) in self.SUPPORTED_CODES]
		print("translated msg: '{}'".format("".join(code_list)))

		for count in range(len(code_list)):
			current_code = self.__CODES[code_list[count]]
			result += current_code
			# print(current_code)

			if isinstance(current_code[-1], tuple):
				if len(current_code[-1]) == 1:
					try:
						next_code = self.__CODES[code_list[count + 1]]

						if next_code != self.__SEVEN_E:
							result += self.__THREE_E
					except IndexError:
						result += self.__THREE_E

		return result


class LedException(BaseException):
	pass


class Led(object):
	"""
	- 自定义 LED

	功能包括：
	    1. 自定义闪烁频率
	    2. 自定义闪烁次数，包括无限闪烁
	    3. 摩尔斯码闪烁
	    4. 闪烁结束后的回调
	
	内置几种常用的闪烁模式：
	    1. 快速闪烁
	    2. 中速闪烁
	    3. 慢速闪烁
	    4. 重启前闪烁，未实现
	    5. 启动时闪烁，未实现
	    6. 连接 wifi 时闪烁，未实现	
	"""

	__BLINK_FAST = 100
	__BLINK_MEDIUM = 500
	__BLINK_SLOW = 1000

	COMB_REBOOT = COMB_2_SHORT_1_LONG = ((100, 50), (100, 50), (2000, 50))

	def __init__(self, pin=None, callback=None):
		"""
		- 检查参数合法性，并初始化对象
		"""
		assert pin is not None and isinstance(pin, int), LedException("pin must be a int")
		assert callback is None or isinstance(callback, type(lambda x:x)), LedException("callback must be None or a function")

		self.__led = Pin(pin, Pin.OUT, value=0)
		self.__callback = callback # callback function trigger after one blink
		self.__time_interval = 1000 # a time interval between two blinks, in ms
		self.__thread_start = False # threading start flag
		self.__terminate_loop = False # terminate one forever loop flag
		self.__terminate_all_loops = False # terminate all forever loops flag
	
	def deinit(self):
		"""
		- 停止所有闪烁并销毁对象，不会触发回调函数
		"""
		self.__thread_start = False
		self.__terminate_loop = True
		self.__terminate_all_loops = True
		
		try:
			_thread.exit()
		finally:
			self.__led.value(0)
			self.__led = None
	
	def set_callback(self, f):
		self.__callback = f

	@property
	def time_interval(self):
		"""
		- 获取两次闪烁的间隔时间
		"""
		return self.__time_interval

	@time_interval.setter
	def time_interval(self, value):
		"""
		- 设置两次闪烁的间隔时间
		"""
		if isinstance(value, int):
			self.__time_interval = value

	def blink_morse(self, message, repeat=1, trigger=True):
		"""
		- 闪烁莫尔斯码

		参数：
		    message: 消息内容，支持的字符参考 MorseCode.SUPPORTED_CODES
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		morse = MorseCode()
		code_list = morse.translate(message)
		# print(code_list)

		self.__blink(morse_code=code_list, repeat=repeat, trigger=trigger)

	def blink_reboot(self):
		"""
		- 重启指示灯，闪烁 2 短 1 长，无重复，有回调
		"""
		self.combination(self.COMB_REBOOT)

	def blink_fast(self, repeat=10, trigger=True):
		"""
		- 快速闪烁

		参数：
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		self.__blink(self.__BLINK_FAST, self.__BLINK_FAST, repeat, trigger)

	def blink_medium(self, repeat=5, trigger=True):
		"""
		- 中速闪烁

		参数：
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		self.__blink(self.__BLINK_MEDIUM, self.__BLINK_MEDIUM, repeat, trigger)

	def blink_slow(self, repeat=3, trigger=True):
		"""
		- 慢速闪烁

		参数：
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		self.__blink(self.__BLINK_SLOW, self.__BLINK_SLOW, repeat, trigger)

	def customize(self, on_time=None, off_time=None, repeat=1, trigger=True):
		"""
		- 自定义闪烁

		参数：
		    on_time: 亮灯时长，默认值 None
		    off_time: 灭灯时长，默认值 None
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		self.__blink(on_time, off_time, repeat, trigger)

	def combination(self, segments, repeat=1, trigger=True):
		"""
		- 组合闪烁

		参数：
		    segments: 闪烁片段元组，形如 ((on_time1, off_time1), (on_time2, off_time2), ...)
		              更多详情参考 Led.COMB_REBOOT
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		"""
		self.__blink(segments, None, repeat, trigger)

	def stop(self):
		"""
		- 停止当前闪烁，不会触发回调函数
		"""
		self.__terminate_loop = True
		self.__led.value(0)

	def stop_all(self):
		"""
		- 停止所有闪烁，不会触发回调函数
		"""
		self.__thread_start = False
		self.__terminate_loop = True
		self.__terminate_all_loops = True
		self.__led.value(0)

	def __waiting_for_blinking(self):
		"""
		- 等待上一个闪烁结束
		"""
		while self.__thread_start and (not self.__terminate_loop or not self.__terminate_all_loops):
			sleep_ms(50)
		
	def __blink(self, on_time=None, off_time=None, repeat=1, trigger=True, morse_code=None):
		"""
		- 检查参数合法性，并调用 __blink_threading 执行闪烁
		
		参数：
		    on_time: 亮灯时长，默认值 None
		    off_time: 灭灯时长，默认值 None
		    repeat: 重复次数，默认值 1，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数，默认值 True
		    morse_code: 莫尔斯代码元组，默认值 None，详情参考 MorseCode.translate()
		"""
		self.__led.value(0)
		self.__terminate_loop = False
		self.__terminate_all_loops = False

		assert repeat >= 0, LedException("repeat must be >= 0")
		assert morse_code is None or isinstance(morse_code, tuple), LedException("morse_code must be None or tuple")

		if morse_code is None:
			# in combination mode
			if isinstance(on_time, tuple):
				assert off_time is None, LedException("in combination mode off_time must be None")
			else:
				assert on_time is not None, LedException("on_time must be specified")
				assert off_time is not None, LedException("off_time must be specified")
		else:
			assert on_time is None, LedException("in morse mode on_time must be None")
			assert off_time is None, LedException("in morse mode off_time must be None")

		_thread.start_new_thread(self.__blink_threading, (on_time, off_time, repeat, trigger, morse_code))

	def __blink_threading(self, on_time, off_time, repeat, trigger, morse_code):
		"""
		- 执行闪烁

		参数：
		    on_time: 亮灯时长
		    off_time: 灭灯时长
		    repeat: 重复次数，0 为无限循环，需要使用 stop() 终止循环
		    trigger: 是否触发回调函数
		    morse_code: 莫尔斯代码元组，详情参考 MorseCode.translate()
		"""
		def on_off(on_time, off_time):
			try:
				if on_time > 0:
					self.__led.value(1)
					sleep_ms(on_time)

				self.__led.value(0)
				sleep_ms(off_time)
			except AttributeError:
				pass

		def action(on_time, off_time, morse_code=None):
			if morse_code is not None:
				for code in morse_code:
					if isinstance(code, tuple):
						on_time = code[0]
						off_time = MorseCode.ONE_UNIT if len(code) == 2 else 0
					else:
						on_time = 0
						off_time = code
						
					on_off(on_time, off_time)

					if self.__terminate_loop or self.__terminate_all_loops:
						break
			# in combination mode
			elif isinstance(on_time, tuple) and off_time is None:
				for segment in on_time:
					if len(segment) == 2:
						on_off(segment[0], segment[1])
			
					if self.__terminate_loop or self.__terminate_all_loops:
						break
			else:
				on_off(on_time, off_time)

		self.__waiting_for_blinking()
		self.__thread_start = True

		# repeat = 0 will enter forever loop mode
		if repeat == 0:
			while not self.__terminate_loop and not self.__terminate_all_loops:
				action(on_time, off_time, morse_code)
		else:
			for count in range(repeat):
				action(on_time, off_time, morse_code)

				if self.__terminate_loop or self.__terminate_all_loops:
					break

		if self.__callback is not None and trigger and not self.__terminate_loop and not self.__terminate_all_loops:
			self.__callback()
		
		sleep_ms(self.__time_interval)
		self.__thread_start = False
		self.__terminate_loop = False


led = None

def run_test():
	global led

	def led_callback():
		print(
"""
==================
    Blink done
==================
"""
	)

	led = Led(
		pin=2,
		callback=led_callback
	)

	led.customize(800, 100, repeat=6)
	print("test customize 6")

	# repeat=0 means forever loop
	# you can type:
	# 	led.stop()
	# or
	# 	led.stop_all()
	# in repl to stop loop(s)
	led.blink_fast(repeat=0)
	print("test fast 0")

	led.blink_medium(repeat=0)
	print("test medium 0")

	# trigger=False means
	# will NOT
	# trigger callback function
	led.blink_slow(repeat=3, trigger=False)
	print("test slow 3 without callback")

	print("test morse 0")
	led.blink_morse("sos ", repeat=0)

	print("test combination 3")
	led.combination(Led.COMB_REBOOT, repeat=3)


if __name__ == "__main__":
	try:
		run_test()
	except KeyboardInterrupt:
		print("\nPRESS CTRL+D TO RESET DEVICE")

		if led is not None:
			led.deinit()
			led = None
