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

       #Forma de pago
        'currency': fields.many2one('res.currency', 'Moneda'),
        'pago_desde':fields.float('Desde', required=True),
        'pago_hasta':fields.float('Hasta', required=True),

        # Descripcion General
        'comodidades': fields.text('Comodidades'),
        'padron':fields.char('Número de padrón'),
        'year':fields.char('Año de Construcción'),
        'orientacion':fields.char('Orientación'),        
        'ubica':fields.char('Ubicación'),
        'gastos_comun':fields.char('Gastos Comúnes'),
        'contri':fields.char('Contribucción'),
        'calor':fields.char('Calefacción'),
        'impPrim': fields.float('Imp. Primaria'),#ya existe
        'ac':fields.boolean('Aire Acondicionado'),
        'calefaccion': fields.boolean('Calefacción'),#ya existe
        'gas':fields.boolean('Gás por cañeria'),
        'tel':fields.boolean('Teléfono'),
        'tv':fields.boolean('TV Cable/Internet'),
        'oficina': fields.boolean('Oficina'),#ya existe
        'garaje': fields.boolean('Garage'),#ya existe
        'equipamiento': fields.boolean('Equipamiento'), #ya existe
        'produccion': fields.boolean('Producción'), #ya existe
        'lavadero':fields.boolean('Lavadero'),
        'placard':fields.boolean('Placard'),
        'alquiler_desde':fields.date('Alquiler-Reservado Desde'),
        'alquiler_hasta':fields.date('Hasta'),        

        
        #Descripcion Interior
        'nAmbientes':fields.char('Cantidad de ambientes'),#ESTO VA CONECTADO A UNA FUNCIONA QUE SUMA LOS OTROS AMBIENTES 
        'cantidadDormitorios': fields.integer('Cantidad de dormitorios'), #ya existe
        'suite':fields.boolean('Habitación en suite'), 
        'cantidadBanios': fields.integer('Cantidad de baños'), #ya existe
        'toilet':fields.boolean('Toilets'),
        'bath':fields.boolean('Baño de servicio'),
        'social':fields.boolean('Baño social'),
        'hidro':fields.boolean('Hidromasaje'),
        'jacuzzi':fields.boolean('Jacuzzi'),
        'escritorio':fields.boolean('Escritorio'),
        'cocina':fields.boolean('Cocina'),
        'living':fields.boolean('Living'),
        'kit':fields.boolean('Kitchenette'),
        'comedor':fields.boolean('Comedor'),
        'liv_com':fields.boolean('Living-Comedor'),
        'hall':fields.boolean('Hall'),
        'estar':fields.boolean('Estar'),
        'ute': fields.boolean('UTE'),
        'ose': fields.boolean('OSE'),
        'agua_caliente':fields.boolean('Agua caliente'),
  
        #Descripcion Exterior
        'baulera':fields.boolean('Baulera'),
        'fondo':fields.boolean('Fondo'),
        'jardin':fields.boolean('Jardín'),
        'piscina': fields.boolean('Piscina'),
        'barbacoa': fields.boolean('Barbacoa'),

        #Edificio o condominio
        'balcon':fields.boolean('Balcón'),
        'terraza':fields.boolean('Terraza'),
        'terraza_2':fields.boolean('Terraza de servicio'),
        'azotea':fields.boolean('Acceso a azotea'),
        'porteria_2':fields.boolean('Portero eléctrico'),
        'vigilancia':fields.boolean('Vigilancia'),
        'porteria':fields.boolean('Porteria'),
        'ascensor':fields.boolean('Ascensor'),
        'piso':fields.boolean('Piso'),
        'internet':fields.boolean('Internet'),
        'sauna':fields.boolean('Sauna'),
        'gym':fields.boolean('Gimnasio'),
        'canchas':fields.boolean('Canchas'),
        'bbq':fields.boolean('Barbacoa común'),

        #Condiciones de venta
        'conditions': fields.text('Condiciones'),
        'financiacion':fields.selection((('P','Préstamo bancario'),('B','BHU'),('F','Financia dueño'),('0','Otro')),'Tipo de financiación'),

        #Para la vista form editada
        'crm_currency':fields.many2one('res.currency', 'Moneda'),
    }
    _defaults= {
        'crm_currency': 3,
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
