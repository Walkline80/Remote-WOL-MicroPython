"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
from MicroWebSrv2 import *


class WebServer(object):
	def __init__(self, host=None, port=0, root_path="/", not_found_url="/", request_timeout=600):
		self.__server = MicroWebSrv2()
		self.__websocket = None

		self.__server.SetEmbeddedConfig()
		self.__server.RootPath = root_path
		self.__server.NotFoundURL = not_found_url
		self.__server.RequestsTimeoutSec = request_timeout
		self.__server.OnLogging = WebServer.__OnMWS2Logging

		from .websocket_callback import WebSocketCallback

		self.__websocket = MicroWebSrv2.LoadModule("WebSockets")
		self.__websocket.OnWebSocketAccepted = WebSocketCallback._OnWebSocketAccepted

		self.bind_address(host, port)

	def __OnMWS2Logging(microWebSrv2, msg, msgType):
		print(msg)

	def bind_address(self, host=None, port=0):
		if host is None: host = "localhost"
		if port == 0: port = 80

		self.__server.BindAddress = (host, port)

	def start(self):
		self.__server.StartManaged()

	def stop(self):
		self.__server.Stop()

	def is_running(self):
		return self.__server.IsRunning
