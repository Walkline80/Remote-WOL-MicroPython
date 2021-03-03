"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import os

DIRS = ['drivers', 'hardware', 'services', 'utils']

def mkdir(dir_name):
	try:
		os.mkdir(dir_name)
	except OSError:
		pass

if __name__ == '__main__':
	for dir_name in DIRS:
		mkdir(dir_name)

	print('make dirs done')
