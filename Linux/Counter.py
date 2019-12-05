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
from pathlib import Path
import serial
import time

ser = serial.Serial()
trash_dir = str(Path.home()) + '/.local/share/Trash/files'
timeout = 5

def connect_to_serial(path):
	global ser

	while ser.isOpen != True :
		try:
			ser.close()
			ser = serial.Serial(path)
			break;
		except serial.SerialException as err:
			print("Can't connect to the serial port '{}'. Waiting for {} seconds".format(path, timeout))
			time.sleep(timeout)

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
		ser.write(str.encode(str(count)));


if __name__ == "__main__":
	serial_path = '/dev/ttyUSB0'

	if len(sys.argv) >= 2:
		serial_path = sys.argv[1]

	connect_to_serial(serial_path)
	print('Connected to ' + ser.name)

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
