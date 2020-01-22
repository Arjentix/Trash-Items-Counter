'''
@author: Polyakov Daniil
@mail: arjentix@gmail.com
@githib: Arjentix
@date: 30.11.19
'''

import functools
import sys
import getopt 
import serial
import pyinotify
import os
import time
from threading import Thread, Lock

serial_port = '/dev/ttyUSB0'
arduino_ser = serial.Serial()
user = ''
observed_dir = ''
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
	global arduino_ser, observed_dir

	count = len(os.listdir(observed_dir))
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

	argv = sys.argv[1:]
	# Setting default values
	user = ''
	observed_dir = ''

	try:
		opts, args = getopt.getopt(argv, 'u:p:d:')
	except getopt.GetoptError:
		print('Run with: python3 ' + sys.argv[0] + ' -u $USER [-p port] [-d directory]')
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-u':
			user = arg
		elif opt == '-p':
			serial_port = arg
		elif opt == '-d':
			observed_dir = arg

	if user == '' and observed_dir == '':
		print('Run with: python3 ' + sys.argv[0] + ' -u $USER [-p port] [-d directory]')
		print('Or with: python3 ' + sys.argv[0] + ' -d <directory> [-p port] [-u <usrename>]')
		sys.exit(2)
	if observed_dir == '':
		# Trash dir by default
		observed_dir = '/home/' + user + '/.local/share/Trash/files'

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
	wm.add_watch(observed_dir, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)

	try:
		notifier.loop(
			daemonize=False
		)
	except pyinotify.NotifierError as err:
		print(err, file=sys.stderr)
