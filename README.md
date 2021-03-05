<h1 align="center">Remote WOL MicroPython</h1>

<p align="center"><img src="https://img.shields.io/badge/Licence-MIT-green.svg?style=for-the-badge" /></p>

### 项目介绍

通过软硬件结合的方式通过互联网远程唤醒局域网中的电脑

本项目是 [Remote WOL 项目](https://gitee.com/walkline/remote-wol) 的组成部分之一

### 使用方法

使用方法请参考 [Remote WOL 项目整体介绍 - 硬件部分](https://gitee.com/walkline/remote-wol#%E7%A1%AC%E4%BB%B6%E9%83%A8%E5%88%86)

### 硬件版本介绍

* `版本 0`
	* 支持手机 App 配网
	* 支持唤醒局域网电脑

* `版本 1`
	* 在`版本 0`基础上增加了使用`DS18B20`传感器获取温度并上报的功能

### 硬件版本切换

要切换不同的硬件版本，打开`config.py`，修改如下参数并保存即可

```python
class Config(object):
    """
    硬件配置文件
    """
    HARDWARE_VERSION = VERSION_1
    HARDWARE_NAME = "Remote WOL v0" # 硬件名称，用于显示
```

### 合作交流

* 联系邮箱：<walkline@163.com>
* QQ 交流群：
    * [走线物联](https://jq.qq.com/?_wv=1027&k=xtPoHgwL)：163271910
    * [扇贝物联](https://jq.qq.com/?_wv=1027&k=yp4FrpWh)：31324057

<p align="center"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_walkline.png" width="300px" alt="走线物联"><img src="https://gitee.com/walkline/WeatherStation/raw/docs/images/qrcode_bigiot.png" width="300px" alt="扇贝物联"></p>
