# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import datetime
import time
import logging

from osv import osv
from osv import fields

_logger = logging.getLogger(__name__)

class participantespoder(osv.osv):

    def get_nombre_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:            
            cr.execute("""  select name from poderjudicial where id = '%s'""",
                    (record.id_poder,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[1] = nom
        return res

    def get_numero_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select number from poderjudicial where id = '%s'""",
                    (record.id_poder,))   
            for result in cr.fetchall():                    
                nom = result[0]
            res[1] = nom
        return res

    def get_fecha_carpeta(self, cr, uid, ids, name, arg, context=None):
        res = {}
        nom = ""        
        your_class_records = self.browse(cr, uid, ids) 
        for record in your_class_records:
            cr.execute("""  select fecha from poderjudicial where id = '%s'""",
                    (record.id_poder,))                      
            for result in cr.fetchall():
                nom = result[0]
            res[1] = nom
        return res        
        
    _name = "participantespoder"
    _columns = {
        'id_poder': fields.integer('ID', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'categoria': fields.many2one('tipo.poder', 'Categoría'),                    
        'nombre': fields.function(get_nombre_carpeta, type='char',method=True, string='Descripción'),         
        'numero': fields.function(get_numero_carpeta, type='char',method=True, string='Número'),
        'fecha': fields.function(get_fecha_carpeta, type='char',method=True, string='Fecha'),
    }



