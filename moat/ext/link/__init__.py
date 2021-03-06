# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
##
##  This file is part of MoaT, the Master of all Things.
##
##  MoaT is Copyright © 2007-2016 by Matthias Urlichs <matthias@urlichs.de>,
##  it is licensed under the GPLv3. See the file `README.rst` for details,
##  including optimistic statements by the author.
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
##  This header is auto-generated and may self-destruct at any time,
##  courtesy of "make update". The original is in ‘scripts/_boilerplate.py’.
##  Thus, do not remove the next line, or insert any blank lines above.
##BP

from moat.types.module import BaseModule

PREFIX=("link","raw")

def key_parts(self,key):
	"""\
		Splits the AMQP key into a (device, direction, channel*, stream) tuple.

		@device: tuple of device name components.
		"in", "out" and "error" are reserved.

		@direction: True(out)/False(in)/None(error).

		@channel: a possibly-empty sequence of channel numbers.

		@stream: the stream number.
		"""
	if isinstance(key,str):
		key = key.split('.')
	if not isinstance(key,tuple):
		key = tuple(key)
	if key[:len(self.PREFIX)] != self.PREFIX:
		raise ValueError(key)
	key = key[len(self.PREFIX):]
	for i,k in enumerate(key):
		if k in {"in","out","error"}:
			if i == 0:
				continue
			if i == len(key)-1:
				break
			rw = False if k == "in" else True if k == "out" else None
			return key[:i],rw,tuple(int(x) for x in key[i+1:-1]), int(key[-1])
			
	raise ValueError(key)

def key_build(self,device,direction,channel,stream):
	"""\
		Builds an AMQP key. Inverse of key_parts().
		"""

	args = list(self.PREFIX[:])
	if isinstance(device,str):
		args.append(device)
	else:
		args += list(device)
	args.append("error" if direction is None else "out" if direction else "in")
	if channel:
		args += list(str(x) for x in channel)
	args.append(str(stream))
	return '.'.join(args)

class LinkModule(BaseModule):
    """\
        This module connects MoaT modules to AMQP
        """

    prefix = "link"
    summary = "Link MoaT modules to AMQP"
    
    @classmethod
    def entries(cls):
        yield from super().entries()
        # yield "cmd_conn","moat.ext.onewire.cmd.conn.ServerCommand"
        yield "cmd_ext","moat.ext.link.cmd.LinkCommand"
        # yield "cmd_dev","moat.ext.graph.cmd.GraphCommand"
        # yield "bus","moat.ext.onewire.bus.OnewireBusBase"
        # yield "device","moat.ext.extern.dev.ExternDeviceBase"

    @classmethod
    def task_types(cls):
        """Enumerate taskdef classes"""
        from moat.task import task_types as ty
        return ty('moat.ext.link.task')

