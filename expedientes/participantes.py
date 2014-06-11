# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import datetime
import time
import logging

from osv import osv
from osv import fields

_logger = logging.getLogger(__name__)

class participantes_expediente(osv.osv):

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
        
    _name = "participantes.expediente"
    _columns = {
        'id_expediente': fields.integer('ID', readonly=True),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'tipo' : fields.integer('Tipo', required=True),
        'categoria': fields.many2one('categoria.expediente', 'Categoría',domain="[('tipo','=',tipo)]"),       
        'nombre': fields.function(get_nombre_exp, type='char',method=True, string='Descripción'),         
        'numero': fields.function(get_numero_exp, type='char',method=True, string='Número'),
        'fecha': fields.function(get_fecha_exp, type='char',method=True, string='Fecha'),
    }


    def unlink(self, cr, uid, ids, context=None):
        #Saco el id de categoría para cliente
        categ_id=""
        cr.execute("""  select id from categoria where name = 'Cliente'""")  
        res = cr.dictfetchone()
        if res:   
            categ_id = res['id']   
        exp_id = 0    
        for id in ids:
            participante = self.pool.get('participantes').browse(cr, uid, [id_expediente])[0]
            partner_id = participante.partner_id.id 
            #_logger.info('partnerrrrrrrrrr'+str(partner_id))
            #_logger.info('CATEGORIAaaaaaaaaaa'+str(categ_id))
            #_logger.info('idddddddddddddddd'+str(id))
            #Borro el directorio del clientes si este no está en otros expedientes como cliente
            cr.execute("""  Select id FROM participantes_expediente where tipo = 1 and partner_id = %s and categoria = %s and id <> %s """,
                    (partner_id,categ_id,id,))            
            res = cr.dictfetchone()
            if not res:
                _logger.info('entreeeeeeeeeeeeeeeeeeeeee')
                #Si tiene directorio Archivos adjunto tb borrarlo y a los adjuntos
                cr.execute("""  Select id FROM document_directory where res_id = %s and res_model ='clientes' """,
                        (partner_id,))                                       
                res = cr.dictfetchone()
                if res:                
                    cr.execute(""" Select id FROM document_directory where parent_id = %s """,
                            (res['id'],))            
                    resAA = cr.dictfetchone()    
                    #_logger.info('ressssss  idddddddddddddd',str(res['id']))                    
                    #Borro los adjuntos y el directorio
                    if resAA:
                        cr.execute("""  DELETE FROM document_directory where parent_id = %s  """,
                            (resAA['id'],))                                         
                        cr.execute("""  DELETE FROM document_directory where id = %s """,
                            (resAA['id'],))     
                #Borro los attacments del cliente
                # cr.execute("""  DELETE FROM ir_attachment where res_id = %s and res_model = 'res.partner' """,
                # (partner_id,))                 

                #Borro el directorio del cliente                
                cr.execute("""  DELETE FROM document_directory where res_id = %s and res_model = 'clientes' """,
                (partner_id,))                  
        return super(participantes, self).unlink(cr, uid, ids, context=None)
    
class categoria_expediente(osv.osv):
	_name='categoria.expediente'
	_columns = {
		'name' : fields.char('Descripción', size=256, required=True),
		'tipo' : fields.integer('Tipo', required=True),        
	}

