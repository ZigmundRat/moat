# -*- coding: utf-8 -*-

"""\
This code represents a sample loadable module for homevent.

"""

from homevent.module import Module
from homevent.logging import log

class ExampleModule(Module):
	"""\
		This is a sample loadable module.
		"""

	info = "yeah, test me baby"

	def __init__(self, name, *args):
		super(ExampleModule,self).__init__(name,*args)
	
	def load(self):
		log("Loading!")
	
	def unload(self):
		log("Unloading!")
	
init = ExampleModule
