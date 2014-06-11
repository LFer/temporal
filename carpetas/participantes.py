# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import datetime
import time
import logging

from osv import osv
from osv import fields

_logger = logging.getLogger(__name__)

class participantes_carpeta(osv.osv):

    def get_nombre_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:            
            cr.execute("""  select name from carpeta where id = '%s'""",
                    (record.id_carpeta,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[1] = nom
        return res

    def get_numero_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select number from carpeta where id = '%s'""",
                    (record.id_carpeta,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[1] = nom
        return res

    def get_fecha_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select fechaalta from carpeta where id = '%s'""",
                    (record.id_carpeta,))                      
            for result in cr.fetchall():
                nom = result[0]
            res[1] = nom
        return res        
        
    _name = "participantes.carpeta"
    _columns = {
        'id_carpeta': fields.integer('ID', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'categoria': fields.many2one('categoria.carpeta', 'Categoría',domain="[('tipo','=',tipo)]"),        
        'tipo' : fields.integer('Tipo', required=True),        
        'nombre': fields.function(get_nombre_carpeta, type='char',method=True, string='Descripción'),         
        'numero': fields.function(get_numero_carpeta, type='char',method=True, string='Número'),
        'fecha': fields.function(get_fecha_carpeta, type='char',method=True, string='Fecha'),
    }

class categoria_carpeta(osv.osv):
	_name='categoria.carpeta'
	_columns = {
		'name' : fields.char('Descripción', size=256, required=True),
		'tipo' : fields.integer('Tipo', required=True),        
	}


