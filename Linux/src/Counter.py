'''
@author: Polyakov Daniil
@mail: arjentix@gmail.com
@githib: Arjentix
@date: 30.11.19
'''

import functools
import sys
import pyinotify
import os
import serial
import time
from threading import Thread, Lock
import serial.tools.list_ports

serial_port = '/dev/ttyUSB0'
ser = serial.Serial()
user = ''
trash_dir = ''
timeout = 5
mutex = Lock()

def check_presence(interval=1):
	global ser

	while True:
		tmp = [tuple(p) for p in list(serial.tools.list_ports.comports())]

		myports = []
		if len(tmp) != 0:
			myports = [p for p in tmp[0]]

		if serial_port not in myports:
			print('Arduino has been disconnected!')
			connect_to_serial(ser.name)
			time.sleep(2)
			print_count(None)
		time.sleep(interval)


def connect_to_serial(path):
	mutex.acquire()
	global ser

	while ser.isOpen != True:
		try:
			ser.close()
			ser = serial.Serial(path)
			break;
		except serial.SerialException as err:
			print("Can't connect to the serial port '{}'. Waiting for {} seconds".format(path, timeout))
			time.sleep(timeout)
	mutex.release()

def print_count(event):
	global ser, trash_dir

	count = len(os.listdir(trash_dir))
	print('Items in trash: {}'.format(count))

	try:
		ser.write(str.encode(' ' + str(count)));
	except serial.SerialException as err:
		print("Failed to write to the serial port. Trying to reestablish connection...")
		connect_to_serial(ser.name)
		print("Connection established")
		time.sleep(2)
		ser.write(str.encode(' ' + str(count)));


if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit('Run with: python3 ' + sys.argv[0] + ' $USER')
	
	user = sys.argv[1]
	trash_dir = '/home/' + user + '/.local/share/Trash/files'

	if len(sys.argv) >= 3:
		serial_port = sys.argv[2]

	connect_to_serial(serial_port)
	print('Connected to ' + ser.name)


	Thread(target = check_presence).start()

	# Inital print
	time.sleep(2)
	print_count(None)

	# Setting directory event handler
	wm = pyinotify.WatchManager()
	notifier = pyinotify.Notifier(wm, print_count)
	wm.add_watch(trash_dir, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)

	try:
		notifier.loop(
			daemonize=False
		)
	except pyinotify.NotifierError as err:
		print(err, file=sys.stderr)
