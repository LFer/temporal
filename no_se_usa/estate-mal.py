# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import datetime
import time
from lxml import etree
import math
import pytz
import re

from osv import osv
from osv import fields
from openerp import SUPERUSER_ID
from openerp import pooler, tools


PROPIEDAD_ESTADOS = [
    ('enalquiler', 'En alquiler'),
    ('alquilado', 'Alquilado'),
    ('enventa', 'En venta'),
    ('vendido', 'Vendido'),
]


class estate(osv.osv):
    _name = "estate"


    def _get_image(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = tools.image_get_resized_images(obj.image)
        return result

    def _get_tz_offset(self, cr, uid, ids, name, args, context=None):
        result = dict.fromkeys(ids, False)
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = datetime.datetime.now(pytz.timezone(obj.tz or 'GMT')).strftime('%z')
        return result

    def _set_image(self, cr, uid, id, name, value, args, context=None):
        return self.write(cr, uid, [id], {'image': tools.image_resize_image_big(value)}, context=context)

    def _has_image(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = obj.image != False
        return result
    
        
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'number': fields.char('Nro. de propiedad', size=64, required=True),
        
        'partner_id': fields.many2one('res.partner', 'Cliente relacionado', required=True),
        'phone': fields.related('partner_id', 'phone', type='char', string='Teléfono'),
        'mobile': fields.related('partner_id', 'mobile', type='char', string='Celular'),
        'email': fields.related('partner_id', 'email', type='char', string='E-mail'),
        'partner_street': fields.related('partner_id', 'street', type='char', string='Calle'),
        'partner_city': fields.related('partner_id', 'city', type='char', string='Localidad/Ciudad'),
        'partner_state_id': fields.related('partner_id', 'state_id', type='char', string='Departamento'),



        
        'is_rural': fields.boolean('Es propiedad rural', help="Seleccione si la propiedad es rural, sino es urbana"),
        'category_id': fields.many2many('res.partner.category', id1='id', id2='category_id', string='Categorías'),
        'date': fields.date('Fecha de Ingreso', select=1, required=True),

        'street': fields.char('Calle', size=128),
        'street2': fields.char('Calle 2', size=128),
        'zip': fields.char('Código postal', change_default=True, size=24),
        'city': fields.char('Ciudad', size=128),
        'state_id': fields.many2one("res.country.state", 'Departamento'),
        'country_id': fields.many2one('res.country', 'País'),
        
        'barrio': fields.char('Barrio', size=128),
        'supTotal': fields.float('Superficie total'),
        'supEdificada': fields.float('Superficie edificada'),
        'largo': fields.integer('Largo'),
        'ancho': fields.integer('Ancho'),
        'comodidades': fields.text('Comodidades'),
        'documentacion': fields.text('Documentación'),
        'cantidadDormitorios': fields.integer('Cantidad de dormitorios'),
        'cantidadBanios': fields.integer('Cantidad de baños'),
        
        'escribano': fields.many2one('res.partner', 'Escribano'),
        
        'ute': fields.boolean('UTE'),
        'ose': fields.boolean('OSE'),
        'calefaccion': fields.boolean('Calefacción'),
        'oficina': fields.boolean('Oficina'),
        'garaje': fields.boolean('Garage'),
        'piscina': fields.boolean('Piscina'),
        'barbacoa': fields.boolean('Barbacoa'),
        'equipamiento': fields.boolean('Equipamiento'),
        'produccion': fields.boolean('Producción'),

        'price': fields.float('Precio (Com. Inc.)', size=240),
        'conditions': fields.text('Condiciones'),
        'notes': fields.text('Comentarios'),
        
        
        # Rural
        'padron': fields.boolean('Padrón'),
        'estudioSuelo': fields.boolean('Estudios de Suelo'),
        'mapa': fields.boolean('Mapa'),
        'distancias': fields.boolean('Distancias'),
        'fotos': fields.boolean('Fotos'),
        'autWeb': fields.boolean('Aut. Web'),
        'ImagenesGoogle': fields.boolean('Imágenes Google'),
        
        'distancia': fields.char('Distancia', size=256),
        'accesos': fields.char('Accesos', size=256),
        'seccional': fields.char('Seccional', size=256),
        'superficie': fields.float('Superficie'),
        'supForestada': fields.float('Sup. Forestada'),
        'indiceConeat': fields.integer('Índice Coneat'),
        
        'indiceProdFinal': fields.integer('Índice de Producción Final'),
        'indiceValorReal': fields.integer('Índice de Valor Real'),
        'tieneCasa': fields.boolean('Casa'),
        'montes': fields.char('Montes', size=256),
        'exploit': fields.char('Explotación', size=256),
        'padrones': fields.char('Padrones', size=256),

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
        'centros': fields.char('Centros de Salud / Escuela', size=256),
        'encargado': fields.char('Encargado', size=256),
        'encargadoCelular': fields.char('Celular', size=256),
        
        'contInm': fields.boolean('Cont. Inmobiliaria'),
        'impPrim': fields.boolean('Imp. Primaria'),
        'bps': fields.boolean('BPS'),
        'bhu': fields.boolean('BHU'),
        'deudas': fields.boolean('Deudas'),
        'suc': fields.boolean('Suc.'),
        'planos': fields.boolean('Planos'),
        
        'constancias': fields.char('Const. (¿Declaradas desde 1975?)', size=256),
        'ocupado': fields.char('Ocupado', size=256),
        
        'precioXHa': fields.float('Precio por há.', size=240),
        'precioTotalLiquido': fields.float('Precio total líquido', size=240),
        'precioXHaComIncl': fields.float('Precio por há. com. incl.', size=240),
        'precioTotalLiquidoComIncl': fields.float('Precio total líquido com. incl.', size=240),
    
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'estate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'estate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
    
        #'user_id': fields.many2one('res.users', 'Vendedor', required=True),
        'users_ids':fields.many2many('res.partner', 'users_rel', 'estate_id', 'partner_id', 'Vendedor'),
        
        'publicado': fields.boolean('Publicar en la Web'),
        
        'active': fields.boolean('Active'),
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),
        
        'state': fields.selection(PROPIEDAD_ESTADOS, 'Estado', size=16, readonly=True),
        'fechaVenta': fields.date('Fecha de Venta', select=1),
        'colegas_ids':fields.many2many('res.partner', 'colegas_rel', 'partner_id', 'colega_id', 'Compartido con'),
        
        #'visit_ids':fields.many2many('visit', 'visit_rel', 'estate_id', 'visit_id', 'Visitas'),
        
        'visit_ids': fields.one2many('visit', 'estate_id', 'Visita'),

        'currency': fields.many2one('res.currency', 'Moneda'),
        
    }

    def _default_category(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('category_id'):
            return [context['category_id']]
        return False

    def _get_default_image(self, cr, uid, is_company, context=None, colorize=False):
        img_path = openerp.modules.get_module_resource('base', 'static/src/img',
                                                       ('company_image.png' if is_company else 'avatar.png'))
        with open(img_path, 'rb') as f:
            image = f.read()

        # colorize user avatars
        if not is_company:
            image = tools.image_colorize(image)

        return tools.image_resize_image_big(image.encode('base64'))
    
    _defaults = {
        'active': True,
        'category_id': _default_category,
        'is_rural': False,
        'image': False,
        'state': 'enventa',
    }    

    def action_estado_alquilado(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'alquilado', 'active': True,'fechaAlquiler': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_enAlquiler(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'enalquiler', 'active': True,'fechaAlquiler': None})
        return True    
        
    def action_estado_vendido(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'vendido', 'active': True,'fechaVenta': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_enVenta(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'enventa', 'active': True,'fechaVenta': None})
        return True    

    def action_estado_desactivado(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'active': False})
        return True    

    def action_estado_activado(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'active': True})
        return True    

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}

    
estate()
