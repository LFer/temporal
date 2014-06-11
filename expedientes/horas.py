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


class horas(osv.osv):

        
    _name = "horas"

    _columns = {
        'id_exp': fields.integer('ID', readonly=True),
        'fecha': fields.date('Fecha', select=1, required=True),
        'canthoras': fields.integer('Cantidad'),        
        'descripcion': fields.text('Descripción'),
        #'facturar': fields.boolean('Facturar'),
        'conceptuar': fields.boolean('Generar gasto'),
        'conceptuado': fields.boolean('Gasto generado'),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', required=True),
        #'active': fields.boolean('Activo'),        
    }
    
    _defaults = {
        'fecha': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    }    

horas()


class rel_horas_gasto(osv.osv):
    _name = "rel.horas.gasto"
    
    _columns = {
        'hora_id': fields.integer('invoice', size=16),
        'gasto_id': fields.integer('Doc', size=16),
    }
      

    
rel_horas_gasto()
