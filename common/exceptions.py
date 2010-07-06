class StateError(Exception):
	""" Notifies about an object method being called in the wrong state. """
	
	def __init__(self, value):
		self.value = value
	
	def __str__(self):
		return str(self.value)