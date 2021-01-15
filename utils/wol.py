"""
The MIT License (MIT)
Copyright © 2021 Walkline Wang (https://walkline.wang)
https://gitee.com/walkline/remote-wol-micropython
"""
import socket
import ustruct

def wake_on_lan(mac_address):
	if len(mac_address) == 12:
		pass
	elif len(mac_address) == 12 + 5:
		sep = mac_address[2]
		mac_address = mac_address.replace(sep, '')
	else:
		raise ValueError('Incorrect MAC address format')

	send_data = __create_magic_packet(mac_address)

	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.sendto(send_data, ('255.255.255.255', 9))  # ok
	
	print("magic packet sent!")

def __create_magic_packet(mac):
	data = b'FF' * 6 + (mac * 16).encode()
	send_data = b''

	for i in range(0, len(data), 2):
		send_data = send_data + ustruct.pack(b'B', int(data[i: i + 2], 16))

	return send_data
