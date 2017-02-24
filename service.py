# -*- coding: utf-8 -*-

# This file is part of sale_pos module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from decimal import Decimal
import datetime
from trytond.model import ModelSQL, Workflow, fields, ModelView
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Or, If
from trytond.wizard import (Wizard, StateView, StateAction, StateTransition,
    Button)
from trytond.modules.company import CompanyReport
from trytond.report import Report
from lxml import etree
import base64
import xmlrpclib
import re
from xml.dom.minidom import parse, parseString
import time
from trytond.rpc import RPC
import os
from trytond import backend
from trytond import security
try:
    import bcrypt
except ImportError:
    bcrypt = None
import random
import hashlib
import string
#from datetime import timedelta

_ZERO = Decimal('0.0')

_TYPE = [
    ('service', 'Servicio'),
    ('home_service', 'Servicio a domicilio')
]

__all__ = ['Service','InvoiceServiceStart', 'InvoiceService']
__metaclass__ = PoolMeta

class Service():
    'Service'
    __name__ = 'service.service'

    def _invoice_service(self):
        res = {}
        res['ref_technical'] = self.id
        res['party'] = self.party
        res['sale_date'] = self.delivery_date
        res['self_pick_up'] = True
        res['invoice_method'] = 'order'
        res['shipment_method'] =  'order'
        res['shipment_address'] = self.party.addresses[0].id
        res['invoice_address'] = self.party.addresses[0].id

        return res

    def _lines_invoice_service(self, sale):
        pool = Pool()
        Lines = pool.get('sale.line')
        for line in self.lines:
            lines_invoice = Lines()
            lines_invoice.sale = sale
            lines_invoice.description = line.product.name
            lines_invoice.unit = line.product.default_uom
            lines_invoice.quantity = 1
            lines_invoice.product = line.product
            lines_invoice.unit_price = line.reference_amount

            lines_invoice.save()

class InvoiceServiceStart(ModelView):
    'Draft Service Start'
    __name__ = 'service.invoice_service.start'


class InvoiceService(Wizard):
    'Draft Service'
    __name__ = 'service.invoice_service'
    start = StateView('service.invoice_service.start',
        'nodux_technical_service_invoice.invoice_service_start_view_form', [
            Button('Exit', 'end', 'tryton-cancel'),
            Button('Facturar', 'invoice_', 'tryton-ok', default=True),
            ])
    invoice_ = StateAction('sale_pos.act_sale_form')

    def do_invoice_(self, action):
        pool = Pool()
        Service = pool.get('service.service')
        Sale = pool.get('sale.sale')
        Line = pool.get('sale.line')
        services = Service.browse(Transaction().context['active_ids'])

        origin = str(services)
        def in_group():
            pool = Pool()
            ModelData = pool.get('ir.model.data')
            User = pool.get('res.user')
            Group = pool.get('res.group')
            group = Group(ModelData.get_id('nodux_technical_service_invoice',
                        'group_service_invoice'))
            transaction = Transaction()
            user_id = transaction.user
            if user_id == 0:
                user_id = transaction.context.get('user', user_id)
            if user_id == 0:
                return True
            user = User(user_id)
            return origin and group in user.groups
        if not in_group():
            self.raise_user_error("No esta autorizado a Facturar un Servicio")

        for service in services:
            sales = Sale.search([('ref_technical', '=', service.id)])
            if service.state in ['pending', 'review']:
                self.raise_user_error(u'No puede facturar un servicio que se encuentra pendiente/revisión')
            if sales:
                self.raise_user_error('Servicio ya ha sido facturado')

        service_invoices = Sale.invoice_service(services)
        data = {'id': [s.ref_technical.id for s in service_invoices]}
        return action, data
