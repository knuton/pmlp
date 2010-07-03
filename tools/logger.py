import os
from datetime import datetime

def log(message):
	try:
		with open(_pathToLogs(), 'a') as f:
			f.write('%s (%s)' % (message, datetime.now().ctime()))
	except IOError:
		pass

def _pathToLogs(logType = 'error'):
	""" Returns pathname for logfile which is being created if not yet present. """
	logsPath = os.path.join(os.path.dirname(__file__), '../logs')
	if not os.path.isdir(logsPath):
		os.mkdir(logsPath)
	return os.path.join(logsPath, '%s.log' % (logType))

# See PEP 366 for package issue
