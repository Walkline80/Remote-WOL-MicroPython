"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
from utils.utilities import Utilities
from utils.wifihandler import WifiHandler
from drivers.led import Led
from config import Config
from utime import sleep


forever_loop = True
ap_server = None
led = None

if __name__ == "__main__":
	try:
		if not Utilities.is_settings_file_exist():
			# 进入用户配网模式
			from services.web_server import WebServer

			led = Led(2)
			led.blink_medium(0)

			WifiHandler.set_ap_mode()
			WifiHandler.set_sta_status(False)
			sleep(1)

			ap_server = WebServer(root_path=Config.AP_ROOTPATH)
			ap_server.bind_address(Config.AP_HOST, Config.AP_PORT)
			ap_server.start()

			while ap_server.is_running():
				sleep(0.5)
		else:
			# 进入工作模式
			from hardware import Selector

			led = Led(2)
			led.blink_fast(0)

			WifiHandler.set_ap_status(False)
			sleep(1)

			if WifiHandler.STATION_CONNECTED == Utilities.connect_to_internet():
				device = Selector.select(Config.HARDWARE_VERSION)
				device.setup()
				device.start()

				led.stop()

				while forever_loop:
					sleep(0.5)
			else:
				# 600 秒后无法连接指定的 wifi 则重启
				Utilities.hard_reset()
	except KeyboardInterrupt:
		forever_loop = False

		print("\nPRESS CTRL+D TO RESET DEVICE")

		if ap_server is not None: ap_server.stop()
		if led is not None: led.deinit()
