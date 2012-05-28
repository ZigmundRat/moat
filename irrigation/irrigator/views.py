# -*- coding: utf-8 -*-

##  Copyright © 2012, Matthias Urlichs <matthias@urlichs.de>
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

from __future__ import division,absolute_import
from django.http import HttpResponseRedirect
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404
from django.views.generic import ListView,DetailView,CreateView,UpdateView,DeleteView
from django.forms import ModelForm,FloatField,TimeField,Textarea
from django.utils.translation import ugettext_lazy as _
from rainman.models import Site,UserForSite
from rainman.utils import get_request
from datetime import time,timedelta,datetime


def home(request):
	try:
		gu = request.user.get_profile()
	except (ObjectDoesNotExist,AttributeError):
		sites = set()
	else:
		sites = gu.sites.all()

	if not sites:
		if request.user.is_authenticated():
			return HttpResponseRedirect('/login/no_access')
		else:
			return HttpResponseRedirect('/login/?next=%s' % request.path)

	if len(sites) == 1:
		return HttpResponseRedirect('/site/%d' % list(sites)[0].id)

	return HttpResponseRedirect('/site/')

class NonNegativeFloatField(FloatField):
	def clean(self,val):
		val = super(NonNegativeFloatField,self).clean(val)
		if val < 0:
			raise ValidationError("must not be negative")
		return val

def Delta(t):
	if isinstance(t,timedelta):
		return t
	return timedelta(0,(t.hour*60+t.minute)*60+t.second,t.microsecond)

class TimeDeltaField(TimeField):
	default_error_messages = {
		'invalid': _(u'Enter a valid time interval.')
	}

	def to_python(self, value):
		"""
		Validates that the input can be converted to a time. Returns a Python
		datetime.timedelta object.
		"""
		res = super(TimeDeltaField, self).to_python(value)
		return Delta(res)

	def strptime(self, value, format):
		return Delta(datetime.strptime(value, format).time())

class FormMixin(object):
	def get_template_names(self):
		return ["obj/%s%s.jinja" % (self.model._meta.object_name.lower(), self.template_name_suffix)]

class SiteForm(ModelForm):
	class Meta:
		model = Site
		exclude = ('db_rate','db_rain_delay')
		fields = ('name','var','host','rain_delay','rate')
	
	# 'Excluded' fields
	rate = NonNegativeFloatField(help_text=Meta.model._meta.get_field_by_name("db_rate")[0].help_text)
	rain_delay = TimeDeltaField(help_text=Meta.model._meta.get_field_by_name("db_rain_delay")[0].help_text)

	def _post_clean(self):
		# This is a hack
		super(SiteForm,self)._post_clean()
		for fn in self.Meta.exclude:
			if not fn.startswith("db_"): continue
			fn = fn[3:]
			setattr(self.instance,fn, self.cleaned_data[fn])
	def save(self):
		r = super(SiteForm,self).save()
		gu = get_request().user.get_profile()
		gu.sites.add(r)
		gu.save()
		return r
	
class SiteMixin(FormMixin):
	model = Site
	context_object_name = "site"
	def get_queryset(self):
		gu = self.request.user.get_profile()
		return super(SiteMixin,self).get_queryset().filter(id__in=gu.sites.all())

class SitesView(SiteMixin,ListView):
	context_object_name = "site_list"
	pass

class SiteView(SiteMixin,DetailView):
	pass

class SiteNewView(SiteMixin,CreateView):
	form_class = SiteForm
	success_url="/site/%(id)s"

class SiteEditView(SiteMixin,UpdateView):
	form_class = SiteForm
	success_url="/site/%(id)s"

class SiteDeleteView(SiteMixin,DeleteView):
	pass
