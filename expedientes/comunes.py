# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import datetime
import time


from osv import osv
from osv import fields


class comunes(osv.osv):

    def get_nombre_exp(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:            
            cr.execute("""  select name from expedientes where id = '%s'""",
                    (record.id_exp,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[record.id] = nom
        return res

    def get_numero_exp(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select number from expedientes where id = '%s'""",
                    (record.id_exp,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[record.id] = nom
        return res

    def get_fecha_exp(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select fechaalta from expedientes where id = '%s'""",
                    (record.id_exp,))                      
            for result in cr.fetchall():
                nom = result[0]
            res[record.id] = nom
        return res        

    _name = "comunes"
    _columns = {
        'id_exp': fields.integer('ID', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
		'categoria': fields.many2one('tipo.comunes', 'Categoría'),
        'nombre': fields.function(get_nombre_exp, type='char',method=True, string='Descripción'),         
        'numero': fields.function(get_numero_exp, type='char',method=True, string='Número'),
        'fecha': fields.function(get_fecha_exp, type='char',method=True, string='Fecha'),         
    }
    


