'use strict';

window.onload = function () {
	app.init();
}

var app = {
	commands: {
		IDENTITY	  : "identity",
		CHECK_MQTT	  : "check_mqtt",
		CHECK_WIFI	  : "check_wifi",
		SAVE_SETTINGS : "save_settings",
		REBOOT_DEVICE : "reboot_device"
	},

	consts: {
		PORT	: 80,
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
		output				  : document.getElementById("output"),

		ws_addr				  : document.getElementById("ws_addr"),
		button_connect		  : document.getElementById("button_connect"),
		button_identity		  : document.getElementById("button_identity"),
		button_reboot		  : document.getElementById("button_reboot"),
		button_check_wifi	  : document.getElementById("button_check_wifi"),
		button_check_mqtt	  : document.getElementById("button_check_mqtt"),
		button_save			  : document.getElementById("button_save")
	},

	websocket: null,

	init: function () {
		this.init_buttons();
	},

	init_buttons: function () {
		var ctl = app.controls;

		ctl.button_connect.addEventListener("click", this.button_connect_click);
		ctl.button_identity.addEventListener("click", this.button_identity_click);
		ctl.button_reboot.addEventListener("click", this.button_reboot_click);
		ctl.button_check_wifi.addEventListener("click", this.button_check_wifi_click);
		ctl.button_check_mqtt.addEventListener("click", this.button_check_mqtt_click);
		ctl.button_save.addEventListener("click", this.button_save_click);
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

	button_save_click: function () {
		if (app.check_blanks()) {
			var ctl = app.controls,
				cmd = app.commands,
				params = {
					command:cmd.SAVE_SETTINGS,
					wifi_ssid			  : ctl.wifi_ssid.value,
					wifi_password		  : ctl.wifi_password.value,
					mqtt_host			  : ctl.mqtt_host.value,
					mqtt_port			  : ctl.mqtt_port.value,
					mqtt_keepalive		  : ctl.mqtt_keepalive.value,
					mqtt_path			  : ctl.mqtt_path.value,
					mqtt_username		  : ctl.mqtt_username.value,
					mqtt_device_number	  : ctl.mqtt_device_number.value,
					mqtt_device_authorize : ctl.mqtt_device_authorize.value,
					mqtt_device_name	  : ctl.mqtt_device_name.value
				};

			app.send_message(JSON.stringify(params));
		}
	},

	button_identity_click: function () {
		var cmd = app.commands,
			params = {
				command	: cmd.IDENTITY
			};

		app.send_message(JSON.stringify(params));
	},

	button_reboot_click: function () {
		var cmd = app.commands,
			params = {
				command : cmd.REBOOT_DEVICE
			};

		app.send_message(JSON.stringify(params));
	},

	button_check_wifi_click: function () {
		var cmd = app.commands,
			ctl = app.controls,
			params = {
				command : cmd.CHECK_WIFI,
				wifi_ssid : ctl.wifi_ssid.value,
				wifi_password : ctl.wifi_password.value
			};

		app.send_message(JSON.stringify(params));
	},

	button_check_mqtt_click: function () {
		var ctl = app.controls,
			cmd = app.commands,
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
			};

		app.send_message(JSON.stringify(params));
	},

	on_open: function (event) {
		this.Output.append("Connected to server");
	},

	on_close: function (event) {
		this.Output.append("Connection Closed");
	},

	on_message: function (event) {
		console.log(event.data);
		
		try {
			params = JSON.parse(event.data);

			switch (params.command) {
				case "identity_result":
					if (params.result == "success") {
						this.Output.append(`Identity Success {hardware_version: ${params.hardware_version}, hardware_name: ${params.hardware_name}, mac_address: ${params.mac_address}, ip_address: ${params.ip_address}}`);
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

	check_blanks: function () {
		var ctl					  = app.controls,
			wifi_ssid			  = ctl.wifi_ssid.value,
			wifi_password		  = ctl.wifi_password.value,
			mqtt_host			  = ctl.mqtt_host.value,
			mqtt_port			  = ctl.mqtt_port.value,
			mqtt_keepalive		  = ctl.mqtt_keepalive.value,
			mqtt_path			  = ctl.mqtt_path.value,
			mqtt_username		  = ctl.mqtt_username.value,
			mqtt_device_number	  = ctl.mqtt_device_number.value,
			mqtt_device_authorize = ctl.mqtt_device_authorize.value,
			mqtt_device_name	  = ctl.mqtt_device_name.value;

		if (isEmpty(wifi_ssid)) {ctl.wifi_ssid.focus(); return false;}
		if (isEmpty(wifi_password)) {ctl.wifi_password.focus(); return false;}
		if (isEmpty(mqtt_host)) {ctl.mqtt_host.value = "47.102.44.223";}
		if (isEmpty(mqtt_port)) {ctl.mqtt_port.value = "1883";}
		if (isEmpty(mqtt_keepalive)) {ctl.mqtt_keepalive.value = 120;}
		if (isEmpty(mqtt_path)) {ctl.mqtt_path.value = "/";}
		if (isEmpty(mqtt_username)) {ctl.mqtt_username.focus(); return false;}
		if (isEmpty(mqtt_device_number)) {ctl.mqtt_device_number.focus(); return false;}
		if (isEmpty(mqtt_device_authorize)) {ctl.mqtt_device_authorize.focus(); return false;}
		if (isEmpty(mqtt_device_name)) {ctl.mqtt_device_name.focus(); return false;}

		app.Output.append("Check Items Success");

		return true;
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
		dom.style.margin = "3px";
		dom.innerHTML = msg;

		output.appendChild(dom);
		output.scrollTop = output.scrollHeight;
	}
}

function isEmpty(obj) {
	if (typeof obj == "undefined" || obj == null || obj == "") {
		return true;
	} else {
		return false;
	}
}