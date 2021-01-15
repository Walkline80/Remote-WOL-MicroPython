"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
class SelectorException(BaseException):
	pass


class Selector(object):
	"""
	硬件版本选择器
	"""
	@staticmethod
	def select(mod_name=None):
		assert mod_name is not None and isinstance(mod_name, str), SelectorException("mod_name must be a str")

		# print("loading hardware:", mod_name)

		try:
			mod_path = "{}{}".format(Selector.__module__.split("selector")[0], mod_name)
			module = getattr(__import__(mod_path), mod_name)
			classs = getattr(module, mod_name)

			# assert isinstance(classs, type), SelectorException("class type get wrong")
			
			return classs()
		except:
			raise SelectorException("cannot load hardware module: {}".format(mod_name))
