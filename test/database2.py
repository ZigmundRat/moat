#!/usr/bin/python
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

from moat.database import DbStore
from moat.base import Name
from moat.reactor import shut_down,mainloop

s = DbStore(Name("Foo","bar"))
def main():
	#d.addCallback(lambda _: s.set("one",2))
	#d.addCallback(lambda _: s.set(3,(4,5,6)))

	def getter(a,b):
		_ = s.get(a)
		assert _ == b, "Check CallBack %r %r %r" % (_,a,b)
	getter("one",2)
	getter(("two","three"),(4,5,6))
	s.delete(("two","three"))
	s.delete("one")

	shut_down()

mainloop(main)

