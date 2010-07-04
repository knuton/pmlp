import os
from datetime import datetime

def debug(message):
	_recordLine(message, 'debug')

def error(message):
	_recordLine(message, 'error')

def log(message):
	_recordLine(message, 'journal')

def _recordLine(message, logType):
	try:
		with open(_pathToLogs(logType), 'a') as f:
			f.write('%s (%s)\n' % (message, datetime.now().ctime()))
	except IOError:
		pass

def _pathToLogs(logType):
	""" Returns pathname for logfile which is being created if not yet present. """
	logsPath = os.path.join(os.path.dirname(__file__), '../logs')
	if not os.path.isdir(logsPath):
		os.mkdir(logsPath)
	return os.path.join(logsPath, '%s.log' % (logType))

# See PEP 366 for package issue
