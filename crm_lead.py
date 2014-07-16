# -*- coding: utf-8 -*-
import string
import datetime
import time
from lxml import etree
import math
import pytz
import re

from openerp.addons.base_status.base_stage import base_stage
import crm
#from datetime import datetime
from openerp.osv import fields, osv
#import time
from openerp import tools
from openerp.tools.translate import _

from base.res.res_partner import format_address
import logging
_logger = logging.getLogger(__name__)

class crm_lead(base_stage, format_address, osv.osv):

    _name = "crm.lead"
    _inherit = ['crm.lead']


    _columns = {

        'number': fields.char('Código', size=64, required=True),
        'city': fields.char('Ciudad', size=128),
        'state_id': fields.many2one("res.country.state", 'Departamento'),
        'country_id': fields.many2one('res.country', 'País'),
        'category_id': fields.many2many('res.partner.category', 'crm_lead_category_rel', 'lead_id', 'category_id', string='Categorías'),
        
        'barrio': fields.char('Barrio', size=128),
        'supTotal': fields.float('Superficie total'),
        'supEdificada': fields.float('Superficie edificada'),
        'largo': fields.integer('Largo'),
        'ancho': fields.integer('Ancho'),
        'comodidades': fields.text('Comodidades'),
        'documentacion': fields.text('Documentación'),
        'cantidadDormitorios': fields.integer('Cantidad de dormitorios'),
        'cantidadBanios': fields.integer('Cantidad de baños'),

        'ute': fields.boolean('UTE'),
        'ose': fields.boolean('OSE'),
        'calefaccion': fields.boolean('Calefacción'),
        'oficina': fields.boolean('Oficina'),
        'garaje': fields.boolean('Garage'),
        'piscina': fields.boolean('Piscina'),
        'barbacoa': fields.boolean('Barbacoa'),
        'equipamiento': fields.boolean('Equipamiento'),
        'produccion': fields.boolean('Producción'),

        'price': fields.float('Precio', size=240),
        'conditions': fields.text('Condiciones'),        
        'notes': fields.text('Comentarios'),


        'superficie': fields.float('Superficie'),
        'supForestada': fields.float('Sup. Forestada'),
        'indiceConeat': fields.integer('Índice Coneat'),
        
        'tieneCasa': fields.boolean('Casa'),
        'montes': fields.boolean('Montes'),
        
        'casaPrincipal': fields.char('Casa Principal', size=256),
        'casaPersonal': fields.char('Casa del Personal', size=256),
        'galpones': fields.integer('Galpones'),
                
        'luz': fields.boolean('Luz'),
        'agua': fields.boolean('Agua'),
        'embarcadero': fields.integer('Embarcadero'),
        'banio': fields.integer('Baño'),
        'vacunos': fields.integer('Vacunos'),
        'lanares': fields.integer('Lanares'),
        'piquetes': fields.integer('Piquetes'),
        'potreros': fields.integer('Potreros'),
        'tubo': fields.integer('Tubo'),
        'cepo': fields.integer('Cepo'),
        'otras': fields.char('Otras', size=256),
        'mejoras': fields.char('Mejoras', size=256),
        'alambrados': fields.char('Alambrados Ext./Internos', size=256),
        'aguadas': fields.char('Aguadas', size=256),
        'tajamares': fields.char('Tajamares', size=256),
        
        'ocupado': fields.char('Ocupado', size=256),
        
        'precioXHa': fields.float('Precio por há.', size=240),
    
    
        'users_ids':fields.many2many('res.partner', 'users_oportunity_rel', 'oportunity_id', 'partner_id', 'Vendedor'),
        'active': fields.boolean('Activo'),
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),
        'create_uid': fields.many2one('res.users', 'Ingresado por', required=True),
        'write_uid': fields.many2one('res.users', 'Actualizado por', required=True),
        
        'currency': fields.many2one('res.currency', 'Moneda'),

    }


    def onchange_categoria(self, cr, uid, ids, category_id, context=None):
        if category_id:
            numero=""
            lista=category_id[0][2]
            largo =len(lista)
            if largo > 0:  
                # return {'value':{'number':codigo, 'codigo':codigo},}
                sql = "INSERT INTO crm_case_categ (id, create_uid,create_date,write_date,write_uid,name,object_id,section_id) "\
                "SELECT "+str(lista[0])+",1,'2013-03-21 15:03:27.425356','2013-03-21 15:03:27.425356',1,'prueba',160,1 "\
                "WHERE "\
                "NOT EXISTS ("\
                " SELECT id FROM crm_case_categ WHERE id = "+str(lista[0])+")"
                
                cr.execute(sql)                          

                
                cr.execute(""" SELECT upper(name) AS name FROM res_partner_category WHERE id = %s """,
                    (lista[0],))           
                nomcat = cr.fetchone()[0]+'-OP'
                
                

                numero = self.pool.get('ir.sequence').get(cr, uid, nomcat)
                if numero == False:
                
                    tiposec = self.pool.get('ir.sequence.type').create(cr, uid,{
                        'create_uid' : uid,
                        'create_date' : datetime.date.today().strftime('%Y-%m-%d'),
                        'write_date' : datetime.date.today().strftime('%Y-%m-%d'),
                        'write_uid' : uid,
                        'code' : nomcat,
                        'name' : nomcat,
                    }) 
                    if tiposec:
                        
                        self.pool.get('ir.sequence').create(cr, uid,{
                            'create_uid' : uid,
                            'create_date' : datetime.date.today().strftime('%Y-%m-%d'),
                            'write_date' : datetime.date.today().strftime('%Y-%m-%d'),
                            'code' : nomcat,
                            'name' : nomcat,                            
                            'number_next' : 1,
                            'implementation' : 'standard',
                            'padding' : '0',
                            'number_increment' : 1,
                        }) 
                    numero = self.pool.get('ir.sequence').get(cr, uid, nomcat)  

                        
        return {'value':{'number':numero},}        

crm_lead()
