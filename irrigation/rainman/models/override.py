# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function, division, unicode_literals
##
##  This file is part of MoaT, the Master of all Things.
##
##  MoaT is Copyright © 2007-2015 by Matthias Urlichs <matthias@urlichs.de>,
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

import six

from rainman.models import Model
from rainman.models.group import Group
from rainman.models.valve import Valve
from django.db import models as m
from datetime import timedelta
from rainman.utils import str_tz

@six.python_2_unicode_compatible
class GroupOverride(Model):
	"""Modify schedule times"""
	class Meta(Model.Meta):
		unique_together = (("group","start"),)
		db_table="rainman_groupoverride"
	def __str__(self):
		return self.name
	name = m.CharField(max_length=200,blank=True,null=True)
	group = m.ForeignKey(Group,related_name="overrides")
	allowed = m.BooleanField(default=False) # whether to allow these to run(True) or not(False)
	start = m.DateTimeField(db_index=True)
	db_duration = m.PositiveIntegerField(db_column="duration")
	def _get_duration(self):
		if self.db_duration is None:
			return None
		return timedelta(0,self.db_duration)
	def _set_duration(self,val):
		self.db_duration = val.total_seconds()
	duration = property(_get_duration,_set_duration)
	@property
	def end(self):
		return self.start+self.duration

	on_level = m.FloatField(blank=True,null=True,default=None,help_text="Level above(off)/below(on) which to activate this rule (factor of max)")
	off_level = m.FloatField(blank=True,null=True,default=None,help_text="Level above(off)/below(on) which to activate this rule (factor of max)")
	

@six.python_2_unicode_compatible
class ValveOverride(Model):
	"""Force schedule times"""
	class Meta(Model.Meta):
		unique_together = (("valve","start"),)
		db_table="rainman_valveoverride"
	def __str__(self):
		return self.name
	name = m.CharField(max_length=200,blank=True,null=True)
	valve = m.ForeignKey(Valve,related_name="overrides")
	running = m.BooleanField(default=False) # whether to force on(True) or off(False)
	start = m.DateTimeField(db_index=True)
	db_duration = m.PositiveIntegerField(db_column="duration")
	def _get_duration(self):
		if self.db_duration is None:
			return None
		return timedelta(0,self.db_duration)
	def _set_duration(self,val):
		self.db_duration = val.total_seconds()
	duration = property(_get_duration,_set_duration)
	@property
	def end(self):
		return self.start+self.duration

	on_level = m.FloatField(blank=True,null=True,default=None,help_text="Level above(off)/below(on) which to activate this rule (factor of max)")
	off_level = m.FloatField(blank=True,null=True,default=None,help_text="Level above(off)/below(on) which to activate this rule (factor of max)")
	

@six.python_2_unicode_compatible
class GroupAdjust(Model):
	"""At this date, this group needs <modifier> more(>1)/less(<1) water.
		To turn the whole thing off, set modifier=0.
		Entries are interpolated linearly."""
	class Meta(Model.Meta):
		unique_together = (("group","start"),)
		db_table="rainman_groupadjust"
	def __str__(self):
		return u"@%s %s" % (str_tz(self.start),self.group)
	group = m.ForeignKey(Group,related_name="adjusters")
	start = m.DateTimeField(db_index=True)
	factor = m.FloatField()

