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

import asyncio
from etcd_tree.node import EtcFloat,EtcInteger,EtcString,EtcBoolean, EtcDir
from qbroker.unit import CC_DATA

from time import time

from moat.dev import DEV
from moat.dev.base import BaseTypedDir,BaseDevice, Typename
from moat.types.etcd import MoatDeviceBase, recEtcDir
from moat.types.managed import ManagedEtcDir,ManagedEtcThing, NoManagerError

import logging
logger = logging.getLogger(__name__)

class ExternDeviceBase(MoatDeviceBase,ManagedEtcDir):
    """Base class for /device/extern"""
    @property
    def task_monitor(self):
        yield "add",'extern/run', ('extern',), {}

class ExternDeviceSub(EtcDir,ManagedEtcThing):
    pass

class ExternDevice(recEtcDir,BaseTypedDir,BaseDevice):
    """Base class for /device/extern/NAME…/:dev"""
    prefix = "extern"
    description = "Some external device off AMQP"

    _rpc_in = None
    _rpc_in_name = ''
    _rpc_out_name = ''
    _change = None

    async def init(self):
        self._change = asyncio.Event(loop=self._loop)
        await super().init()

    async def manager_present(self, mgr):
        await super().manager_present(mgr)
        n = self.get('input',{}).get('topic',None)
        if n is not None:
            await self._reg_in_rpc(n)
        n = self.get('output',{}).get('topic',None)
        if n is not None:
            await self._reg_out_rpc(n)

    @property
    def is_ready(self):
        return super().is_ready and self._change.is_set()
    @property
    async def ready(self):
        rep = True
        while rep:
            rep = False
            if not super().is_ready:
                await super().ready
                rep = True
            if not self._change.is_set():
                await self._change.wait()
                rep = True

    def manager_gone(self):
        super().manager_gone()
        self._rpc_in_name = None
        self._rpc_out_name = None

    async def do_rpc(self,data):
        """\
            Alert to set the state
            """
        try:
            val = data['value']
        except KeyError:
            val = self._type.default
        else:
            val = self._value.from_amqp(val)
        self._change.set()
        await self._updated(val)
        return True

    async def _reg_in_rpc(self, name):
        m = self.manager
        if m is None:
            return
        amqp = m.amqp
        if name is not None and self._rpc_in_name == name:
            return
        if self._rpc_in is not None:
            r,self._rpc_in = self._rpc_in,None
            await r.release()
        if name is not None:
            logger.info("REG %s %s",name,self)
            self._rpc_in = await m.moat_reg.alert(amqp, name,self.do_rpc, call_conv=CC_DATA)
        self._rpc_in_name = name

    async def _reg_out_rpc(self, name):
        self._rpc_out_name = name

    async def set_value(self, value):
        m = self.manager
        if m is None:
            raise NoManagerError

        val = self._value.to_amqp(value)
        sync = self.get('data',{}).get('sync',None)
        if sync is None:
            await m.amqp.rpc(self._rpc_out_name, {'value':val})
        else:
            self._change.clear()
            await m.amqp.alert(self._rpc_out_name, {'value':val})
            if sync:
                await self._change.wait()
                return # rpc_in will save the value to AMQP
        self._value.value = value
ExternDevice.register("data","sync", cls=EtcBoolean)

class RpcName(EtcString):
    """Update the parent's rpc name"""
    def has_update(self):
        p = self.parent
        if p is None:
            return
        p = p.parent
        if p is None:
            return
        m = p.manager
        if m is None:
            return
        self._do(m,p)

    def _do(self,m,p):
        raise NotImplementedError

class RpcInName(RpcName):
    def _do(self,m,p):
        m.call_async(p._reg_in_rpc, self.value if self.is_new is not None else None)

class RpcOutName(RpcName):
    def _do(self,m,p):
        m.call_async(p._reg_out_rpc, self.value if self.is_new is not None else None)

class ExtDevIn(ManagedEtcThing,EtcDir):
    pass
class ExtDevOut(ManagedEtcThing,EtcDir):
    pass
ExtDevIn.register('topic',cls=RpcInName)
ExtDevOut.register('topic',cls=RpcOutName)

ExternDeviceBase.register("*", cls=ExternDeviceSub)
ExternDeviceSub.register("*", cls=ExternDeviceSub)
ExternDeviceSub.register(DEV, cls=ExternDevice)

ExternDevice.register('type',cls=Typename)
ExternDevice.register('input',cls=ExtDevIn)
ExternDevice.register('output',cls=ExtDevOut)
ExternDevice.register('created',cls=EtcFloat)
ExternDevice.register('timestamp',cls=EtcFloat)

