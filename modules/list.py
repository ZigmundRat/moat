# -*- coding: utf-8 -*-

"""\
This code represents a sample loadable module for homevent.

"""

from homevent.logging import log
from homevent.statement import Statement, global_words
from homevent.module import modules, ModuleDirs, Module
from homevent.run import list_workers
from homevent.reactor import active_queues


class ModList(Statement):
	name=("list","module")
	doc="list of modules"
	long_doc="""\
list module
	shows a list of loaded modules.
list module NAME [args...]
	shows the documentation string of that module.
	
"""
	def run(self,ctx,**k):
		event = self.params(ctx)
		if not len(event):
			for m in modules.itervalues():
				print >>self.ctx.out, " ".join(m.name)
			print >>self.ctx.out, "."
		elif len(event) == 1:
			m = modules[tuple(event)]
			print  >>self.ctx.out, " ".join(m.name),m.__doc__
		else:
			raise SyntaxError("Only one name allowed.")

class EventList(Statement):
	name=("list","event")
	doc="list of events that are currently processed"
	long_doc="""\
list event
	shows a list of running events.
list event ID
	shows details of that event.
	
"""
	def run(self,ctx,**k):
		event = self.params(ctx)
		if not len(event):
			for m in active_queues.itervalues():
				print >>self.ctx.out, m.aq_id,m.name
			print >>self.ctx.out, "."
		elif len(event) == 1:
			m = active_queues[event[0]]
			for r in m.report(99):
				print  >>self.ctx.out, r
		else:
			raise SyntaxError("Only one ID allowed.")

class WorkerList(Statement):
	name=("list","worker")
	doc="list of workers"
	long_doc="""\
list worker
	shows a list of available workers (code that reacts on events)
list worker NAME
	shows the documentation string of that worker.
"""
	def run(self,ctx,**k):
		event = self.params(ctx)
		if not len(event):
			for w in list_workers():
				print >>self.ctx.out, w.prio,w.name
			print >>self.ctx.out, "."
		elif len(event) == 1:
			for w in list_workers(event[0]): # should return only one
				print >>self.ctx.out, w.name,w.__doc__
			print >>self.ctx.out, "."
		else:
			raise SyntaxError("Too many parameters")
			return


class ListModule(Module):
	"""\
		This module provides a couple of common 'list FOO' functions.
		"""

	info = "provides a couple of common 'list FOO' functions"

	def load(self):
		global_words.register_statement(WorkerList)
		global_words.register_statement(EventList)
		global_words.register_statement(ModList)
	
	def unload(self):
		global_words.unregister_statement(WorkerList)
		global_words.unregister_statement(EventList)
		global_words.unregister_statement(ModList)
	
init = ListModule
