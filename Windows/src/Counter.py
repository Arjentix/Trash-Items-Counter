import sys
import os
import serial
import subprocess
import time
from threading import Thread, Lock
import win32file
import win32event
import win32con

serial_port = 'COM3'
arduino_ser = serial.Serial()
user = ''
trash_dir = os.path.abspath ("C:\$Recycle.Bin\S-1-5-21-1204911413-2226659614-3970885936-1001")
timeout = 5
mutex = Lock()

#
# FindFirstChangeNotification sets up a handle for watching
#  file changes. The first parameter is the path to be
#  watched; the second is a boolean indicating whether the
#  directories underneath the one specified are to be watched;
#  the third is a list of flags as to what kind of changes to
#  watch for. We're just looking at file additions / deletions.
#
change_handle = win32file.FindFirstChangeNotification (
	trash_dir,
	0,
	win32con.FILE_NOTIFY_CHANGE_FILE_NAME
)

def check_presence():
	global arduino_ser

	while True:
		try:
			arduino_ser.read()
		except serial.SerialException:
			print('Arduino was disconnected')
			connect_to_serial(arduino_ser.name)
			time.sleep(2)
			print_count()

		'''
		print("Readed: '" + byte_string.decode('utf-8') + "'")
		if byte_string == b'':
			print('Arduino was disconnected')
			connect_to_serial(arduino_ser.name)
			time.sleep(2)
			print_count(None)
			'''

def connect_to_serial(path, close=True):
	mutex.acquire()
	global arduino_ser

	while True:
		try:
			if close == True:
				arduino_ser.close()

			arduino_ser = serial.Serial(path, 9600)
			break
		except serial.SerialException:
			print("Can't connect to the serial port '{}'. Waiting for {} seconds".format(path, timeout))
			time.sleep(timeout)
	mutex.release()

def print_count():
	global arduino_ser, trash_dir

	# Windows has an extra .ini in RecycleBin so there is a -1
	# Also Windows has an extra file for every file in RecycleBin (except the one described above) so there is a /2
	count = int((len(os.listdir(trash_dir)) - 1) / 2)
	print('Items in trash: {}'.format(count))

	try:
		arduino_ser.write(str.encode(' ' + str(count)))
	except ValueError:
		print("Failed to write to the serial port. Trying to reestablish connection...")
		connect_to_serial(arduino_ser.name)
		print("Connection established")
		time.sleep(2)
		arduino_ser.write(str.encode(' ' + str(count)))

#
# Loop forever, listing any file changes. The WaitFor... will
#  time out every half a second allowing for keyboard interrupts
#  to terminate the loop.
#

if __name__ == '__main__':
	user_sid = bytes.decode(subprocess.check_output("wmic useraccount where name=\"%username%\" get sid", shell=True))
	user_sid = user_sid[4:].strip()
	print('User sid: {}'.format(user_sid))
	trash_dir = 'C:\$Recycle.Bin\{}'.format(user_sid)

	if len(sys.argv) >= 2:
		serial_port = sys.argv[1]

	connect_to_serial(serial_port)
	
	print('Connected to ' + arduino_ser.name)


	Thread(target = check_presence).start()

	# Inital print
	time.sleep(2)
	print_count()

	try:
		while True:
			result = win32event.WaitForSingleObject (change_handle, 500)

			#
			# If the WaitFor... returned because of a notification (as
			#  opposed to timing out or some error)
			#
			if result == win32con.WAIT_OBJECT_0:
				print_count()
				win32file.FindNextChangeNotification (change_handle)

	finally:
		win32file.FindCloseChangeNotification (change_handle)
		os._exit(0)