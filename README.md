<h1 align="center">Remote WOL MicroPython</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

闲的没事干，准备做一个 ESP32 开发板配合 APP 远程唤醒计算机的硬件设备，开发中。。。

> 详细说明请参考 [Remote WOL 项目整体介绍](https://gitee.com/walkline/remote-wol)

### 开机棒设计思路

#### 开机原理

通过`WOL`唤醒本地计算机

#### 远程开机原理

硬件设备连接互联网，通过`MQTT`接收远程发送的开机命令，再通过`WOL`唤醒本地计算机

#### 硬件部分

硬件要实现的功能包括：

* 连接互联网
* 连接`MQTT 服务器`并订阅相关主题
* 接收`MQTT 订阅消息`并唤醒本地计算机

#### APP 部分

APP 要实现的功能包括：

* 发现局域网中的硬件设备
* 为硬件设备指定配网信息
* 扫描局域网内 PC 设备，获取`MAC地址`，并将 PC 设备保存为列表方便后续唤醒操作
* 连接`MQTT 服务器`并订阅相关主题
* 发布`MQTT 消息`，通过硬件设备唤醒计算机

#### 工作流程

* 硬件上电后检查是否存在配网信息，如果：

	* 存在配网信息：

		* 板载 LED 快闪
		* 开启`Station 模式`，连接到互联网
		* 连接到`MQTT 服务器`，订阅相关主题，准备接收订阅消息
		* 发布消息告知 APP 设备已上线
		* 板载 LED 熄灭
		* 长按板载按钮 5 秒钟可以清除用户配置文件
	
	* 不存在配网信息：

		* 板载 LED 慢闪
		* 开启`AP 模式`，广播带设备`MAC 地址`的特殊`SSID`
		* 开启`WebSocket 服务`，等待 APP 绑定设备（传输配网信息等）

* APP 使用时，如果：

	* 未添加硬件设备：

		* 开启 WIFI 扫描，搜索硬件设备的特殊`SSID`
		* 如果找到设备，将预设的配网信息通过`WebSocket`传递给设备，设备尝试连接互利网并反馈状态信息
		* 添加成功后设备复位进入工作模式，APP 保存硬件信息
	
	* 已添加硬件设备

		* 发布消息查询设备状态，等待反馈

* APP 通过扫描局域网或手动添加的方式添加需要被唤醒的电脑

* 未完待续。。。

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
    * [走线物联](https://jq.qq.com/?_wv=1027&k=xtPoHgwL)：163271910
    * [扇贝物联](https://jq.qq.com/?_wv=1027&k=yp4FrpWh)：31324057

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
