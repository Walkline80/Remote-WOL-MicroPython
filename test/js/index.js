'use strict';

window.onload = function () {
	app.init();
}

var app = {
	commands: {
		CHECK_MQTT	  : "check_mqtt",
		CHECK_WIFI	  : "check_wifi",
		LOAD_SETTINGS : "load_settings",
		SAVE_SETTINGS : "save_settings",
		REBOOT_DEVICE : "reboot_device"
	},

	consts: {
		PORT	: 80, // if you modify port number, please set the same value in config.py
		CHANNEL	: "control"
	},

	controls: {
		wifi_ssid			  : document.getElementById("wifi_ssid"),
		wifi_password		  : document.getElementById("wifi_password"),
		mqtt_host			  : document.getElementById("mqtt_host"),
		mqtt_port			  : document.getElementById("mqtt_port"),
		mqtt_keepalive		  : document.getElementById("mqtt_keepalive"),
		mqtt_path			  : document.getElementById("mqtt_path"),
		mqtt_username		  : document.getElementById("mqtt_username"),
		mqtt_device_number	  : document.getElementById("mqtt_device_number"),
		mqtt_device_authorize : document.getElementById("mqtt_device_authorize"),
		mqtt_device_name	  : document.getElementById("mqtt_device_name"),
		mqtt_data_point		  : document.getElementById("mqtt_data_point"),
		output				  : document.getElementById("output"),

		ws_addr				  : document.getElementById("ws_addr"),
		button_connect			  : document.getElementById("button_connect"),
		button_identity			  : document.getElementById("button_identity")
	},

	websocket: null,

	init: function () {
		this.init_buttons();
		this.init_input();
	},

	load_settings: function () {
		var cmd = app.commands,
			params = {
				command	: cmd.LOAD_SETTINGS
			};

		app.send_message(JSON.stringify(params));
	},

	init_input: function () {
		var ctl = this.controls;

		ctl.mqtt_keepalive.addEventListener("keyup", function () {
			this.value = this.value.replace(/[^0-9]/ig, '');
		});

		ctl.mqtt_data_point.addEventListener("keyup", function () {
			this.value = this.value.replace(/[^\w\,]/ig, '');
		});

		ctl.mqtt_username.addEventListener("blur", function () {
			if (!isEmpty(this.value)) {
				if (isEmpty(ctl.mqtt_device_name.value)) {
					ctl.mqtt_device_name.value = this.value + "_";
				}
			}
		});
	},

	init_buttons: function () {
		this.controls.button_connect.addEventListener("click", this.button_connect_click);
		this.controls.button_identity.addEventListener("click", this.button_identity_click);
	},

	button_connect_click: function () {
		var that = app,
		ws_uri = `ws://${that.controls.ws_addr.value}:${that.consts.PORT}/${that.consts.CHANNEL}`;

		that.websocket			 = new WebSocket(ws_uri);
		that.websocket.onopen	 = function (event) {that.on_open(event)};
		that.websocket.onclose	 = function (event) {that.on_close(event)};
		that.websocket.onmessage = function (event) {that.on_message(event)};
		that.websocket.onerror	 = function (event) {that.on_error(event)};
	},

	button_identity_click: function () {
		var ctl	= app.controls,
			cmd = app.commands,
			params = {
				command		  : "identity"
			};

		app.send_message(JSON.stringify(params));
	},

	on_open: function (event) {
		this.send_message("hello from client");
		this.Output.append("Connected to server");
		// this.load_settings();
	},

	on_close: function (event) {
		console.log("Connection Closed");
		this.Output.append("Connection Closed");
	},

	on_message: function (event) {
		console.log(event.data);
		
		try {
			params = JSON.parse(event.data);

			switch (params.command) {
				case "load_settings_result":
					if (params.result == "success") {
						var ctl = this.controls;

						ctl.wifi_ssid.value				= params.wifi_ssid;
						ctl.wifi_password.value			= params.wifi_password;
						ctl.mqtt_host.value				= params.mqtt_host;
						ctl.mqtt_port.value				= params.mqtt_port;
						ctl.mqtt_keepalive.value		= params.mqtt_keepalive;
						ctl.mqtt_path.value				= params.mqtt_path;
						ctl.mqtt_username.value			= params.mqtt_username;
						ctl.mqtt_device_number.value	= params.mqtt_device_number;
						ctl.mqtt_device_authorize.value = params.mqtt_device_authorize;
						ctl.mqtt_device_name.value		= params.mqtt_device_name;
						ctl.mqtt_data_point.value		= params.mqtt_data_point;
					}

					break;
				case "save_settings_result":
					if (params.result == "success") {
						this.Output.append("Save Settings Success");

						var cmd = this.commands,
							params = {
								command: cmd.REBOOT_DEVICE
							};

						alert("Save settings success.\nDevice will reboot after 3 seconds.");

						app.send_message(JSON.stringify(params));
					} else {
						this.Output.append("Save Settings Failed");
					}

					break;
				case "check_wifi_result":
					if (params.result_code == "1010") {
						this.Output.append("Check Wifi Success");
					} else {
						this.Output.append(`Check wifi failed with code: ${params.result_code}`);
					}

					break;
				case "check_internet_result":
					if (params.result == "success") {
						this.Output.append("Check Internet Success");
			
						var ctl = this.controls,
							cmd = this.commands,
							params = {
								command			 : cmd.CHECK_MQTT,
								host			 : ctl.mqtt_host.value,
								port			 : ctl.mqtt_port.value,
								keepalive		 : ctl.mqtt_keepalive.value,
								path			 : ctl.mqtt_path.value,
								username		 : ctl.mqtt_username.value,
								device_number	 : ctl.mqtt_device_number.value,
								device_authorize : ctl.mqtt_device_authorize.value,
								device_name		 : ctl.mqtt_device_name.value,
								data_point		 : ctl.mqtt_data_point.value
							};

						// console.log(JSON.stringify(params));
						app.send_message(JSON.stringify(params));
					} else {
						this.Output.append("Check Internet Failed");
					}

					break;
				case "check_mqtt_result":
					if (params.result == "success") {
						this.Output.append("Check MQTT Success");
					} else {
						this.Output.append(`Check MQTT failed with code (${params.error_code}): ${params.error_msg}`);
					}

					break;
			}
		} catch (error) {
			console.log(error);
		}
	},

	on_error: function (event) {
		console.log("error: " + event.data);
		this.Output.append(event.data);
	},

	send_message: function (msg) {
		this.websocket.send(msg);
	}
};

app.Output = {
	append: function (msg) {
		var dom = document.createElement("p"),
			output = app.controls.output;

		dom.style.wordWrap = "break-word";
		dom.innerHTML = msg;

		output.style.height = "63px";
		output.appendChild(dom);
		output.scrollTop = output.scrollHeight;
	},

	clean: function () {
		var output = app.controls.output;

		output.style.height = "0";
		output.innerHTML = "";
	}
}