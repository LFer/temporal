# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import logging
import datetime
import time
import openerp.addons.decimal_precision as dp
import account

from osv import osv
from osv import fields


_logger = logging.getLogger(__name__)

TIPO_IVA = [
    ('22', '22 %'),
    ('excento', 'Excento'),
]

class conceptocarpetas(osv.osv):
    def get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids,context):
            res[record.id] = record.cantidad * record.preciounidad
        return res

        
    _name = "conceptocarpetas"

    _columns = {
        'id_concepto': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fecha': fields.date('Fecha', select=1, required=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', required=True),
        'cantidad': fields.integer('Cantidad'),
        'dtounidad': fields.float('Descuento unidad'),
        'iva': fields.selection(TIPO_IVA, 'IVA propio', size=16),
        'facturar': fields.boolean('A facturar'),
        'facturado': fields.boolean('Facturado'),
        'preciounidad': fields.float('Precio unidad'),  
        'total': fields.function(get_total, type='float',method=True, string='Total'),                
    
    }
    
    _defaults = {
        'fecha': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    }    
    
conceptocarpetas()



