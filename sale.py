#! -*- coding: utf8 -*-

from decimal import Decimal
from datetime import datetime
from trytond.model import Workflow, ModelView, ModelSQL, fields
from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction
from trytond.pyson import Bool, Eval, Not, If, PYSONEncoder, Id
from trytond.wizard import (Wizard, StateView, StateAction, StateTransition,
    Button)
from trytond.modules.company import CompanyReport
from trytond.pyson import If, Eval, Bool, PYSONEncoder, Id
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.report import Report
conversor = None
try:
    from numword import numword_es
    conversor = numword_es.NumWordES()
except:
    print("Warning: Does not possible import numword module!")
    print("Please install it...!")
import pytz
from datetime import datetime,timedelta
import time

__all__ = ['Sale']
__metaclass__ = PoolMeta

class Sale():
    'Sale'
    __name__ = 'sale.sale'

    ref_technical = fields.Many2One('service.service', 'Service', readonly=True)
    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()

    @classmethod
    def invoice_service(cls, sales):
        MoveLine = Pool().get('account.move.line')

        new_sales = []
        for sale in sales:
            new_sale, = cls.create([sale._invoice_service()])
            sale._lines_invoice_service(new_sale)
            new_sales.append(new_sale)

        return new_sales
