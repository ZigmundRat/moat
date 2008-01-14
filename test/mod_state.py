#!/usr/bin/python
# -*- coding: utf-8 -*-

##
##  Copyright © 2007-2008, Matthias Urlichs <matthias@urlichs.de>
##
##  This program is free software: you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation, either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License (included; see the file LICENSE)
##  for more details.
##

import homevent as h
from homevent.reactor import ShutdownHandler
from homevent.module import load_module
from test import run

input = """\
block:
	if exists state foo bar:
		log TRACE "No‽"
	else:
		log TRACE "Yes!"
log TRACE Set to ONE
set state one foo bar
log TRACE Set to TWO
set state two foo bar
on state * three foo bar:
	log TRACE Set to FOUR
	set state four foo bar
async:
	log TRACE Set to THREE
	set state three foo bar
wait: for 0.1
list state
list state foo bar
block:
	if state three foo bar:
		log TRACE "Yes!"
	else:
		log TRACE "No‽"
block:
	if exists state foo bar:
		log TRACE "Yes!"
	else:
		log TRACE "No‽"
block:
	if last state two foo bar:
		log TRACE "Yes!"
	else:
		log TRACE "No‽"
on whatever:
	var state x foo bar
	log TRACE We got $x
sync trigger whatever
del state foo bar
list state
shutdown
"""

h.main_words.register_statement(ShutdownHandler)
load_module("state")
load_module("block")
load_module("wait")
load_module("data")
load_module("on_event")
load_module("logging")
load_module("ifelse")
load_module("trigger")

run("state",input)

