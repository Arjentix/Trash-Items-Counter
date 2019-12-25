'''
@author: Polyakov Daniil
@mail: arjentix@gmail.com
@githib: Arjentix
@date: 30.11.19
'''

import functools
import sys
import serial
import pyinotify
import os
import time
from threading import Thread, Lock

serial_port = '/dev/ttyUSB0'
arduino_ser = serial.Serial()
user = ''
trash_dir = ''
timeout = 5
mutex = Lock()

def check_presence():
	global arduino_ser

	while True:
		try:
			byte_string = arduino_ser.read()
			if byte_string == b'':
				raise serial.SerialException()
		except serial.SerialException:
			print('Arduino was disconnected')
			connect_to_serial(arduino_ser.name)
			time.sleep(2)
			print('Connection established')
			print_count(None)

def connect_to_serial(path, close=True):
	mutex.acquire()
	global arduino_ser

	while True:
		try:
			if close == True:
				arduino_ser.close()

			arduino_ser = serial.Serial(path, 9600)
			break
		except (IOError, FileNotFoundError):
			print("Can't connect to the serial port '{}'. Waiting for {} seconds".format(path, timeout))
			time.sleep(timeout)
	mutex.release()

def print_count(event):
	global arduino_ser, trash_dir

	count = len(os.listdir(trash_dir))
	print('Items in trash: {}'.format(count))

	try:
		arduino_ser.write(str.encode(' ' + str(count)))
	except ValueError:
		print("Failed to write to the serial port. Trying to reestablish connection...")
		connect_to_serial(arduino_ser.name)
		print("Connection established")
		time.sleep(2)
		arduino_ser.write(str.encode(' ' + str(count)))


if __name__ == "__main__":

	if len(sys.argv) < 2:
		sys.exit('Run with: python3 ' + sys.argv[0] + ' $USER')
	
	user = sys.argv[1]
	trash_dir = '/home/' + user + '/.local/share/Trash/files'

	if len(sys.argv) >= 3:
		serial_port = sys.argv[2]

	try:
		arduino_ser = open(serial_port, 'rb+', buffering=0)
	except FileNotFoundError:
		connect_to_serial(serial_port, False)
	
	print('Connected to ' + arduino_ser.name)


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
