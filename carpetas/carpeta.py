# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import logging
import datetime
import time
from lxml import etree
import math
import pytz
import re

from array import *
from osv import osv
from osv import fields
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from compiler.ast import TryFinally

_logger = logging.getLogger(__name__)

CARPETA_ESTADOS = [
    ('abierto', 'Abierto'),
    ('cerrado', 'Cerrado'),
    ('pausado', 'Pausado'),
]

class carpeta(osv.osv):
    def get_total_facturado(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.concepto_ids:        
                if recordConc.facturado == True:
                    total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res  
        
    def get_total_sin_facturar(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.concepto_ids:        
                if recordConc.facturado == False:
                    total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res 
        
    def get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.concepto_ids:        
                total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res

    def get_emails(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for id in ids:
            result[id] = self.pool.get('mail.message').search(cr, uid, [('subtype_id','=',1),('model','=','expedientesgenerico'), ('res_id', '=',id)])
        return result         
        
    _name = "carpeta"
    
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fechaalta': fields.date('Fecha alta', select=1, required=True),
        'fechacierre': fields.date('Fecha cierre', select=1),
        'number': fields.char('Código referencia', size=64, required=True),
        'tipoasunto': fields.many2one('tipo.asunto.carpeta', 'Tipo Asunto'),
        'tipocarpeta': fields.many2one('tipo.carpeta', 'Tipo Carpeta'),
        'refpropia': fields.char('Ubicación de la carpeta', size=64),
        'active': fields.boolean('Activo'),      
        'state': fields.selection(CARPETA_ESTADOS, 'Estado', size=16, readonly=True), 
        'accion_ids': fields.one2many('crm.meeting','id_exp', 'Acciones'), 
        'participantes_ids': fields.one2many('participantes.carpeta', 'id_carpeta','Participantes'),   
        'concepto_ids': fields.one2many('conceptocarpetas', 'id_concepto', 'Concepto'),   
        'totalgral': fields.function(get_total, type='float',method=True, string='Total'),         
        'totalfacturado': fields.function(get_total_facturado, type='float',method=True, string='Total facturado'),         
        'totalsinfacturar': fields.function(get_total_sin_facturar, type='float',method=True, string='Saldo no facturado'),        
        'carpetas_ids': fields.many2many('carpeta','rel_car_car', 'id_carcar','id_carpeta', 'Carpetas'),
        'facturas_ids': fields.many2many('account.invoice','facturas_carpeta_rel', 'id', 'account_id', 'Facturas'), 
        'attachments': fields.one2many('ir.attachment', 'res_id', 'Archivos'),        
        'emails': fields.function(get_emails, relation='mail.message',method=True,type='one2many'),
        'create_date': fields.datetime('Fecha de creación' , readonly=True),                
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),   
        'create_uid': fields.many2one('res.users', 'Creado por', readonly=True),
        'write_uid': fields.many2one('res.users', 'Actualizado por', readonly=True),  
        'notas_ids':fields.one2many('carpeta.nota','id_carpeta','Notas'), 
        'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
        
    }

    _defaults = {
        'active': True,
        'fechaalta': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'number': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'carpeta'),
        'state': 'abierto',
    }    
  
    
    def action_estado_cerrado(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a Cerrado'

        cr.execute("""  select partner_id from res_users where id = %s""",
                    (uid,))                      
        cli = cr.fetchone()[0]

        message = self.pool.get('mail.message')
        message.create(cr, uid, {
                'res_id': ids[0],
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'author_id': cli,
                'model': self._name,
                'subject' : subject,
                'body': values
            }, context=context)    
        self.write(cr, uid, ids, {'state': 'cerrado', 'fechacierre': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_abierto(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a Abierto'
        _logger.info('!!!!!clienteeeeoo****'+str(uid)+'---------------'+str(ids))

        cr.execute("""  select partner_id from res_users where id = %s""",
                    (uid,))                      
        cli = cr.fetchone()[0]        
        
        message = self.pool.get('mail.message')
        message.create(cr, uid, {
                'res_id': ids[0],
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'author_id':cli,
                'model': self._name,
                'subject' : subject,
                'body': values
            }, context=context)    
        self.write(cr, uid, ids, {'state': 'abierto'})
        return True    
        
    def action_estado_pausado(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a Pausado'
        _logger.info('!!!!!clienteeeeoo****'+str(uid)+'---------------'+str(ids))

        cr.execute("""  select partner_id from res_users where id = %s""",
                    (uid,))                      
        cli = cr.fetchone()[0]        
        
        message = self.pool.get('mail.message')
        message.create(cr, uid, {
                'res_id': ids[0],
                'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                'author_id': cli,
                'model': self._name,
                'subject' : subject,
                'body': values
            }, context=context)     
        self.write(cr, uid, ids, {'state': 'pausado'})
        return True    

    def action_nueva_factura(self, cr, uid, ids, *args):        
        sql = ""
        varfacturar = False
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.concepto_ids:
                if recordConc.facturar == True:
                    if recordConc.facturado == False:
                        varfacturar = True
                        sql += " UPDATE conceptocarpetas SET facturado = True WHERE id = "+str(recordConc.id)+";"
        
        if varfacturar == True:                
            for record in your_class_records:
                clienteid = 3
                
                if record.participantes_ids:
                    clienteid = record.participantes_ids[0].id
                cr.execute("""  select partner_id from participantes where id = %s""",
                            (clienteid,))  
                if not cr.fetchone():
                    _logger.info('Debe ingresar un participante')
                else:
                    cli = cr.fetchone()[0]                    
                        
                    search_domain = []
                    valor = "res.partner,"+str(cli)
                    
                    _logger.info('!!!!!clienteeeeoo****'+str(cli)) 
                    _logger.info('!!!!!valorrrrr****'+str(valor)) 
                                    
                    search_domain.append(('res_id', '=', valor))
                    search_domain.append(('name', '=', 'property_account_payable'))

                    obj = self.pool.get('ir.property')
                    ids = obj.search(cr, uid, search_domain)
                    res = obj.read(cr, uid, ids, ['value_reference',''], context=None)
                    account = ""
                    
                    for r in res:
                        valorRef = r['value_reference']
                        lista = valorRef.split(',');
                        account = lista[1]
                        
                    _logger.info('!!!!!accountttt****'+str(account)) 
                    
                    if account != "":                
                        invoice_id = self.pool.get('account.invoice').create(cr, uid,{
                            'name' : 'Factura',
                            'date_invoice' : record.fechaalta,
                            'account_id' : account,
                            'currency_id' : 1,
                            'partner_id' : clienteid,
                            'journal_id' : 1,
                            'company_id' : 1,
                            'origin' : 'Factura',
                        })      
                        cr.execute(sql)
                        cr.execute("""  INSERT INTO facturas_carpeta_rel VALUES (%s,%s)""",(record.id, invoice_id,))
                        for recordConc in record.concepto_ids:
                            
                            if recordConc.facturar == True:                                    
                                self.pool.get('account.invoice.line').create(cr, uid,{
                                    'invoice_id' : invoice_id,
                                    'name' : recordConc.name,
                                    'product_id' : recordConc.product_id.id,
                                    'price_unit' : recordConc.preciounidad,
                                    'quantity' : recordConc.cantidad,
                                    'account_id' : account,
                                })    
        return True        

    def write(self, cr, uid, ids, values, context=None):
        exp_id = 0
        exp_id = super(carpeta, self).write(cr, uid, ids, values, context=context)
        if context != None:
            _logger.info('!!!!!llllllllllllllll****'+str(context)+'-------ppp'+str(uid)+'****'+str(ids))               
            
            
            
            esArray = True
            try:
                x = len(ids)
            except Exception:
                esArray = False
               
            if esArray:
                subject = 'Modificado'

                cr.execute("""  select partner_id from res_users where id = %s""",
                            (context.get('uid'),))                      
                cli = cr.fetchone()[0]
                #if message.type != "notification":
                message = self.pool.get('mail.message')
                message.create(cr, uid, {
                        'res_id': ids[0],
                        'date': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'author_id': cli,
                        'model': self._name,
                        'subject' : subject,
                        'body': values
                    }, context=context)                 
            
        return exp_id        
   
class tipo_asunto_carpeta(osv.osv):
    _name = "tipo.asunto.carpeta"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }    

class tipo_carpeta(osv.osv):
    _name = "tipo.carpeta"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }    


class tipo_accion(osv.osv):
    _name = "tipo.accion"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    } 

class tipo_participante(osv.osv):
    _name = "tipo.participante"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    } 

    
class carpeta_nota(osv.osv):

    _name = "carpeta.nota"
    _description = "Notas del expediete"

    _columns = {
        'id_carpeta':fields.integer('Carpeta',invisible=True),
        'texto': fields.text('Texto de la nota', required=True),
        'user_id': fields.many2one('res.users', 'Usuario', readonly=True),
        'fecha': fields.datetime('Fecha' , readonly=True),
        'active':fields.boolean('Active'),
    }


    def _get_default_user(self, cr, uid, context=None):
        """Gives current user id
       :param context: if portal in context is false return false anyway
        """
        if context and context.get('portal', False):
            return False
        return uid

        
    _defaults = {
        'user_id': _get_default_user,
        'fecha': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'active': lambda *a: True,
    }
    
               
carpeta_nota()