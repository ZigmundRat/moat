#!/usr/bin/python
# -*- coding: utf-8 -*-

import homevent as h
from homevent.interpreter import Interpreter
from homevent.statement import Statement,ComplexStatement
from homevent.reactor import ShutdownHandler
from homevent.module import load_module
from test import run, run_logger
 
log = run_logger("parser",dot=False).log

input = """\

# call FooHandler(main).run(⌁.foo)
foo
# call FooHandler(main).run(⌁.foo¦baz)
foo baz
# call FooHandler(main).run(⌁.foo¦baz)
foo bar
# call BarHandler(main).run(⌁.foo¦bar¦baz)
foo bar baz
# call BarHandler(main).start_block("baz","quux")
foo bar baz quux:
	# call WhatHandler(bar).run(⌁.what¦ever)
	what ever
	# call ForHandler(bar).start_block("ever","and","ever")
	for ever and ever:
		# call FoiledHandler(for).run(⌁.foiled¦again)
		foiled again
	# call WhatHandler(bar).run(⌁.what¦else)
	what else
# call FooHandler(main).run(⌁.foo¦again)
foo again

# help
help
help help
# help foo => we foo around
help foo
# help foo baz: complains
help foo baz
# help foo bar => have a bar
help foo bar
# help bar for => for you
help foo bar for
# help foo bar for foiled => not clingfilm
help foo bar for foiled

shutdown
#EOF
"""

_id=0
class sbr(object):
	def __repr__(self):
		return "‹%s (%d)›" % (super(sbr,self).__repr__()[1:-1], self.id)
	def __init__(self,parent=None,*a,**k):
		super(sbr,self).__init__(*a,**k)
		global _id
		_id += 1
		self.id = _id
		log(None,"Init %s(%d) from %s" % (self.name,self.id, repr(parent)))
	def run(self,ctx,**k):
		event = self.params(ctx)
		log(None,"Input %s(%d): %s" % (self.name,self.id,event))
	def called(self,args):
		self.args = args
	def start_block(self):
		log(None,"InputComplex %s(%d): %s" % (self.name,self.id,u"¦".join(unicode(x) for x in self.args)))

class FooHandler(sbr,Statement):
	name=("foo",)
	doc="We foo around."

class BarHandler(sbr,ComplexStatement):
	name=("foo","bar",)
	doc="Have a bar, man!"
	
class ForHandler(sbr,ComplexStatement):
	name=("for",)
	doc="for you!"
	
class WhatHandler(sbr,ComplexStatement):
	name=("what",)
	doc="What is this?"

class FoiledHandler(sbr,Statement):
	name=("foiled",)
	doc="not clingfilm"

BarHandler.register_statement(WhatHandler)
BarHandler.register_statement(ForHandler)
ForHandler.register_statement(FoiledHandler)
h.main_words.register_statement(FooHandler)
h.main_words.register_statement(BarHandler)
h.main_words.register_statement(ShutdownHandler)
load_module("help")

class TestInterpreter(Interpreter):
	def complex_statement(self,args):
		fn = self.ctx.words.lookup(args)
		fn = fn(self.ctx)
		fn.called(args)
		fn.start_block()
		return TestInterpreter(ctx=self.ctx(words=fn))
	def done(self):
		log(None,"... moving up")

run("parser", input, interpreter=TestInterpreter, logger=log)