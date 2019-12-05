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

def print_count(event):
	# Setting Trash directory
	dir = str(Path.home()) + '/.local/share/Trash/files'

	print(len(os.listdir(dir)))

if __name__ == "__main__":
	# Inital print
	print_count(None)

	wm = pyinotify.WatchManager()
	notifier = pyinotify.Notifier(wm, print_count)
	wm.add_watch(dir, pyinotify.IN_CREATE | pyinotify.IN_DELETE | pyinotify.IN_MOVED_FROM | pyinotify.IN_MOVED_TO)

	try:
		notifier.loop(
			daemonize=False,
			pid_file='/tmp/pyinotify.pid',
			stdout='/tmp/pyinotify.log'
		)
	except pyinotify.NotifierError as err:
		print(err, file=sys.stderr)
