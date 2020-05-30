'''
@author: Polyakov Daniil
@mail: arjentix@gmail.com
@github: Arjentix
@date: 26.01.2020
'''

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import sys
import time
import getopt
import serial
from threading import Thread, Lock

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
serial_port = '/dev/ttyUSB0'
arduino_ser = serial.Serial()
service = None
timeout = 5
mutex = Lock()

def init_gmail_api_service(cred_path, token_path):
  creds = None
  # The file token.pickle stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_path):
      with open(token_path, 'rb') as token:
          creds = pickle.load(token)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
      if creds and creds.expired and creds.refresh_token:
          creds.refresh(Request())
      else:
          flow = InstalledAppFlow.from_client_secrets_file(
              cred_path, SCOPES)
          creds = flow.run_local_server(port=0)
      # Save the credentials for the next run
      with open(token_path, 'wb') as token:
          pickle.dump(creds, token)
  return build('gmail', 'v1', credentials=creds)

def count_unread(service):
  # Call the Gmail API
  results = (
    service
    .users()
    .threads()
    .list(userId='me', q='in:inbox is:unread -label:social -label:promotions')
    .execute()
  )
  unread_count = 0
  if 'threads' in results:
    unread_count = len(results['threads'])
    while 'nextPageToken' in results:
      next_page_token = results['nextPageToken']
      results = (
        service
        .users()
        .threads()
        .list(
          userId='me',
          q='in:inbox is:unread -label:social -label:promotions',
          pageToken=next_page_token
          )
        .execute()
      )
      unread_count += len(results['threads'])
  
  return unread_count

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
      print_count()

def print_count():
  global service

  count = count_unread(service)
  print('Unread messages: {}'.format(count))

  try:
    arduino_ser.write(str.encode(' ' + str(count)))
  except ValueError:
    print("Failed to write to the serial port. Trying to reestablish connection...")
    connect_to_serial(arduino_ser.name)
    print("Connection established")
    time.sleep(2)
    arduino_ser.write(str.encode(' ' + str(count)))

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

def main():
  global arduino_ser, serial_port, service
  argv = sys.argv[1:]

  gmail_timeout = 300;
  cred_path = 'credentials.json'
  pickle_path = 'token.pickle'

  try:
    opts, args = getopt.getopt(argv, 'p:f:t:', ['port=', 'file=', 'timeout=', 'pickle='])
  except getopt.GetoptError:
    print('Run with: python3 ' + sys.argv[0] + '[-p <port>] [-f <path-to-credentials.json>] [-t <timeout>] [--pickle <path-to-token.pickle>]')
    sys.exit(2)

  for opt, arg in opts:
    if opt in ('-p', '--port'):
      serial_port = arg
    elif opt in ('-f', '--file'):
      cred_path = arg
    elif opt in ('-t', '--timeout'):
      gmail_timeout = int(arg)
    elif opt == '--pickle':
      pickle_path = arg

  service = init_gmail_api_service(cred_path, pickle_path)
  try:
    arduino_ser = open(serial_port, 'rb+', buffering=0)
  except FileNotFoundError:
    connect_to_serial(serial_port, False)
  
  print('Connected to ' + arduino_ser.name)


  Thread(target = check_presence).start()

  # Inital print
  time.sleep(2)
  print_count()

  while True:
    time.sleep(gmail_timeout)
    print_count()

if __name__ == '__main__':
    main()
