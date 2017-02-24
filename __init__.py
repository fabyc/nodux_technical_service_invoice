from trytond.pool import Pool
from .service import *
from .sale import *

def register():
    Pool.register(
        Service,
        InvoiceServiceStart,
        Sale,
        module='nodux_technical_service_invoice', type_='model')
    Pool.register(
        InvoiceService,
        module='nodux_technical_service_invoice', type_='wizard')
