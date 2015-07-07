# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import string
import datetime
import time
from lxml import etree
import math
import pytz
import re
from openerp.tools.translate import _
from osv import osv
from osv import fields
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import decimal_precision as dp
import logging

_logger = logging.getLogger(__name__)
PROPIEDAD_ESTADOS = [
    ('creando', 'Creando'),
    ('enalquiler', 'En alquiler'),
    ('alquilado', 'Alquilado'),
    ('ventAlquiler', 'En venta - En alquiler'),
    ('enventa', 'En venta'),
    ('vendido', 'Vendido'),
]
import logging
_logger = logging.getLogger(__name__)
class estate(osv.osv):
    _name = "estate"
    _inherit = "mail.thread"
    _order = "number"

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

    def get_emails(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for id in ids:
            result[id] = self.pool.get('mail.message').search(cr, uid, [('subtype_id','=',1),('model','=','estate'), ('res_id', '=',id)])
        return result

    def _get_webUrl(self, cr, uid, ids, name, args, context=None):

        result = {}
        website = ""
        company_ids = self.pool.get('res.company').search(cr, uid, [('id','!=',0)], context=context)
        for obj in self.pool.get('res.company').browse(cr, uid, company_ids, context=context):
            website = obj.website
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = website + "/?s=" + obj.number
        return result

    def _get_CodProp(self, cr, uid, ids, name, args, context=None):
        result = {}
        for obj in self.browse(cr, uid, ids, context=context):
            result[obj.id] = "http://79.143.191.243:8000/verImagenes.php?nro=" + obj.number
        return result

    def button_estate_match(self, cr, uid, ids, context=None, *args):
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'dtm_inmobiliaria', 'view_crm_leads_macheo_tree')
        view_id = view_ref and view_ref[1] or False
        #estate_obj = self.pool.get("crm.lead")
        #import pdb; pdb.set_trace()
        oportunidades = []
        machea = 0
        min_score = 0    # Inicializar variables
        caracteristicas = ['largo','garaje','ancho','cocina','piscina'] # Lista de las caracteristicas por la que se va a machear
        excluyentes = ['ose','city']
        obj = self.browse(cr,uid,ids,context)[0]    # Obtener el objeto actual
        ctx = (context or {}).copy()
        objIds = self.pool.get('crm.lead').search(cr,uid,[('ose','=',True),('city','=','Salto')],context=context)
        objOport = self.pool.get('crm.lead').read(cr,uid,objIds,fields=caracteristicas,context=context)    # Obtener todas las oportunidades
        oportunidades = objIds[:]
        # import pdb; pdb.set_trace()
        # La idea de este for es de tener las oportunidades en una lista para luego ir sacando una por una
        # las oportnuidades que no cumplen con las características especificadas en la lista de características.
        for unaOP in objOport:    # Recorro las oportunidades
            min_score = 0.0
            machea = 0.0
            porcent = 0.0
            unaOP['score'] = []
            for p in caracteristicas:    # Recorro las caracteristicas de la lista.
                min_score += 1
                if obj[p] == unaOP[p]:    #Compara la caracteristica del objeto actual con la carac del pedido.
                    machea += 1
            porcent = (machea*100)/min_score

            self.pool.get('crm.lead').write(cr,uid,unaOP['id'],{'score': porcent},context=context)

            if (machea < ((min_score/2)+1)):    # Si el macheo es menor a la mitad mas 1, entonces lo quita de la lista.
                oportunidades.remove(unaOP['id'])    # Quita las id que no cumplan.

        return {
            'domain': "[('id','in',["+','.join(map(str, oportunidades))+"])]",
            'type': 'ir.actions.act_window',
            'name': 'Pedidos macheables',
            'res_model': 'crm.lead',
            'view_type': 'tree',
            'view_mode': 'tree',
            'button': 'yes',
            'view_id': (view_id,'View'),
            'target': 'new',
            'nodestroy': True,
            'context':ctx,
        }


    """
    def _attach_satelital(self, cr, uid, ids, name, args, context=None):
        attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('satelital','=',True)])
        datas = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
        return datas
    """

    def _attach_email(self, cr, uid, ids, name, args, context=None):
        attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('email','=',True)])
        datas = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
        return datas

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'number': fields.char('Nro. de propiedad', size=64, required=True),
        'partner_id': fields.many2one('res.partner', 'Cliente relacionado'), #TODO se va a una pestaña nueva , required=True
        'phone': fields.related('partner_id', 'phone', type='char', string='Teléfono'),
        'mobile': fields.related('partner_id', 'mobile', type='char', string='Celular'),
        'email': fields.related('partner_id', 'email', type='char', string='E-mail'),
        'partner_street': fields.related('partner_id', 'street', type='char', string='Calle'),
        'partner_city': fields.related('partner_id', 'city', type='char', string='Localidad/Ciudad'),
        'partner_state_id': fields.related('partner_id', 'state_id', type='char', string='Departamento'),
        'nunemero_de_puerta':fields.char('Nro de puerta'),
        'score': fields.float('Porcentaje macheo', readonly=True),
        'is_rural': fields.boolean('Es propiedad rural', help="Seleccione si la propiedad es rural, sino es urbana"),
        'category_id': fields.many2many('res.partner.category', id1='id', id2='category_id', string='Categorías'),
        'street': fields.char('Calle', size=128),
        'numero_de_puerta':fields.char('Nº de puerta'),
        'numero_de_apto':fields.char('Unidad Piso'),
        'street2': fields.char('Esquina', size=128),
        'zip': fields.char('Código postal', change_default=True, size=24),
        'city': fields.char('Ciudad', size=128),
        'neighborhood': fields.char('Barrio', size=128),
        'state_id': fields.many2one("departmento", 'Departamento'),
        'country_id': fields.many2one('res.country', u'País'),
        'pais_id': fields.many2one('pais', u'País'),
        'texto_rojo':fields.char('El texto en rojo implica que será publicado en la web', readonly=True),
        'barrio': fields.char('Zona', size=128),
        'supTotal': fields.float('Superficie total'),
        'supEdificada': fields.float('Superficie edificada'),
        'largo': fields.integer('Profundidad'),
        'ancho': fields.integer('Frente'),
        'superficie_terraza': fields.integer('Terraza'),
        'metraje_fondo': fields.integer('Fondo'),
        'documentacion': fields.text('Documentación'),
        'escribano': fields.many2one('res.partner', 'Escribano'),
        #Cabezal
        'operacion':fields.selection((('V','Venta'),('A','Alquiler'),('T',u'Tasación')),u'Opereción'),
        'tipo_propiedad':fields.selection((('C','Casa'),('A','Apartamento'),('L','Local'),('O','Oficina'),('G','Garage'),('T','Terreno'),('D',u'Depósito'),('G','Galpón')),'Tipo de propiedad'),
        'categoria':fields.selection((('C','Colega'),('D','Directo'),('E','Exclusivo'),('I','Indirecta'),('N','No exclusivo'),('O','Ofrecido')),'Categoría'),
        #Pestaña Documentacion
        'obs_documentacion':fields.text('Observaciones'),
        # Rural
        'padron': fields.boolean('Padrón'),
        'estudioSuelo': fields.boolean('Estudios de Suelo'),
        'mapa': fields.boolean('Mapa'),
        'distancias': fields.boolean('Distancias'),
        'fotos': fields.boolean('Fotos'),
        'autWeb': fields.boolean('Aut. Web'),
        'ImagenesGoogle': fields.boolean('Imágenes Google'),
        'seccional': fields.char('Seccional', size=128),
        'tieneCasa': fields.boolean('Casa'),
        'casaPrincipal': fields.char('Casa Principal', size=256),
        'casaPersonal': fields.char('Casa del Personal', size=256),
        'galpones': fields.integer('Galpones'),
        'luz': fields.char('Luz', size=256),
        'agua': fields.char('Agua', size=256),
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
        #, digits_compute=dp.get_precision('estate')
        'precioXHa': fields.float('Precio por há.'),
        'precioTotalLiquido': fields.float('Precio total líquido'),
        'precioXHaComIncl': fields.float('Precio por há. com. incl.'),
        'precioTotalLiquidoComIncl': fields.float('Precio total líquido com. incl.'),
        'image': fields.binary("Imagen",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Imagen mediana", type="binary", multi="_get_image",
            store={
                'estate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Imagen pequeña", type="binary", multi="_get_image",
            store={
                'estate': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
        #'user_id': fields.many2one('res.users', 'Vendedor', required=True),
        'users_ids':fields.many2many('res.partner', 'users_rel', 'estate_id', 'partner_id', 'Vendedor'),
        'personas_ids':fields.many2many('res.partner', 'personas_rel', 'estate_id', 'partner_id', 'Personas relacionadas'),
        'publicado': fields.boolean('Publicar en la Web'),
        'active': fields.boolean('Activo'),
        'atendido_por':fields.many2one('res.users', 'Atendido por'),
        #Pestaña historico
        'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
        'message_obs':fields.text('Observaciones'),
        'create_date': fields.datetime('Fecha de creación' , readonly=True),
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),
		'create_uid': fields.many2one('res.users', 'Creado por'),
        'write_uid': fields.many2one('res.users', 'Actualizado por'),
        'date': fields.date('Fecha de Ingreso', select=1, required=True),
        'ingresado_por':fields.many2one('res.users', 'Ingresado por'),
        #'uid': fields.many2one('res.users', 'Usuario'),
        #'write_uid_name': fields.related('write_uid', 'name', type='char', string='Actualizado por'),
        'state': fields.selection(PROPIEDAD_ESTADOS, 'Estado', size=16, readonly=True),
        'fechaVenta': fields.date('Fecha de Venta', select=1),
        'colegas_ids':fields.many2many('res.partner', 'colegas_rel', 'partner_id', 'colega_id', 'Compartido con'),
        'observations_ids':fields.one2many('observations', 'estate_id','Observaciones'),
        'expenses_ids':fields.one2many('expenses', 'estate_id','Gastos'),
        'temporada_ids':fields.one2many('temporada','estate_id', 'Temporada'),
        'historial_ids' :fields.one2many('historial', 'estate_id', 'Historial'),
        #'visit_ids':fields.many2many('visit', 'visit_rel', 'estate_id', 'visit_id', 'Visitas'),
        'visit_ids': fields.one2many('visit', 'estate_id', 'Visita'),
        'modificado': fields.boolean('Modificado'),
        'googleLocation': fields.char('Localización de Google Maps', size=512),
        #pais, estado, ciudad, calle y número
        #'images': fields.function(_get_attach, type="binary"),
        'attachments': fields.one2many('ir.attachment', 'res_id', 'Archivos'),
        #'attachments_email': fields.function(_attach_email, type="binary"),
        #'attachments_satelital': fields.function(_attach_satelital, type="binary"),
        'suelosConeat': fields.text('Descripción de grupos de suelos CONEAT'),
        'emails': fields.function(get_emails, string="e-mail", relation='mail.message',method=True,type='one2many'),
        'fechaContacto': fields.date('Fecha de Contacto', select=1), #TODO se va a historico
        'webUrl': fields.function(_get_webUrl),
        'webProp': fields.function(_get_CodProp),
        #'duplicados': fields.char('Duplicados',50),
        'reservado':fields.boolean('Reservado'),
        'destacados': fields.boolean('Destacado'),
        'ubicacion': fields.text('Ubicación'),
        'comodidades': fields.text('Comodidades'),
        'orientacion':fields.char('Orientación'),
        'ubica':fields.char('Ubicación'),
        'calor':fields.char('Calefacción'),
        'tel':fields.boolean('Teléfono'),
        'tv':fields.boolean('TV Cable/Internet'),
        'oficina': fields.boolean('Oficina'),#ya existe
        'equipamiento': fields.boolean('Equipamiento'), #ya existe
        'produccion': fields.boolean('Producción'), #ya existe
        'placard':fields.boolean('Placard'),
        'alquiler_desde':fields.date('Alquiler-Reservado Desde'),
        'alquiler_hasta':fields.date('Hasta'),
        #Descripcion Interior
        'social':fields.boolean('Baño social'),
        'jacuzzi':fields.boolean('Jacuzzi'),
        'ute': fields.boolean('UTE'),
        'ose': fields.boolean('OSE'),
        'agua_caliente':fields.boolean('Agua caliente'),
        #Descripcion Exterior
        'baulera':fields.boolean('Baulera'),
        'barbacoa': fields.boolean('Barbacoa'),
        'piso':fields.boolean('Piso'),
        #Tasacion
        'fecha_tasacion':fields.date('Fecha de Tasación'),
        'moneda_tasacion':fields.many2one('res.currency', 'Moneda de Tasación'),
        'importe_tasacion':fields.integer('Importe'),
        'tasado_por':fields.many2one('res.partner','Tasado por'),
        'obs_tasacion':fields.text('Observaciónes'),
        #Para vender
        'currency_venta': fields.many2one('res.currency', 'Moneda Venta'),
        'price_venta': fields.float('Precio'),
        #Para alquilar
        'currency_alquiler': fields.many2one('res.currency', 'Moneda Alquiler'),
        'price_alquiler': fields.float('Precio Alquiler'),
        #Condiciones de venta
        'conditions': fields.text('Condiciones'),
        'financiacion':fields.selection((('P','Préstamo bancario'),('B','BHU'),('F','Financia dueño'),('0','Otro')),'Tipo de financiación'),
        'alquiler':fields.boolean('¿Alquiler?', help="Seleccione si la propiedad está para alquilar, de lo contrario a la venta"),
        #Gastos
        'notes': fields.text('Comentario del gasto'),
        'currency': fields.many2one('res.currency',r'Moneda'),
        'price': fields.float('Valor'),
        'satelital':fields.char('Satelital'),
        'interesados_ids':fields.one2many('interesados', 'estate_id','Opit'),
        'compartidocolegas_ids':fields.one2many('compartidocolegas', 'estate_id','Opit'),
        #NUEVA DESCRIPCION GENERAL
        #Descripcion General
        'padron':fields.char(u'N° de padrón'),
        'year':fields.char('Año de Construcción', size=4),
        'orientacion':fields.selection((('No','Norte'),('Ne','Noreste'),('No','Noroeste'),('S','Sur'),('Se','Sudste'),('So','Sudoeste'),('E','Este'),('O','Oeste')),u'Orientación'),
        'select_ubicacion':fields.selection((('F','Frente'),('C','Contrafrente'),('I','Interior'),('L','Lateral'),('P','Penthouse')),u'Ubicación'),
        'select_estado':fields.selection((('E',u'En construcción'),('As','A estrenar'),('I','Impecable'),('R','Reparaciones sencillas'),('A','A reciclar'),('R','Reciclado'),('En','En buen estado'),),u'Estado'),
        #Ambientes/Dormitorios
        'cantidadDormitorios':fields.char('Cantidad de dormitorios'),
        'nAmbientes':fields.char('Cantidad de ambientes'),
        'suite':fields.char('Dormitorios en suite'),
        'DormitorioPlacard':fields.char('Dormitorios con placard'),
        'DormitorioServicio':fields.boolean('Dormitorio de servicio'),
        #Baños
        'cantidadBanios': fields.char('Cantidad de baños'),
        'toilet':fields.boolean('Toilets'),
        'bath':fields.boolean('Baño de servicio'),
        'hidro':fields.boolean('Hidromasaje'),
        #Área Social
        'living':fields.boolean('Living'),
        'comedor':fields.boolean('Comedor'),
        'liv_com':fields.boolean('Living-Comedor'),
        'estar':fields.boolean('Estar'),
        'escritorio':fields.boolean('Escritorio'),
        'hall':fields.boolean('Hall'),
        'recibo':fields.boolean('Recibo'),
        'hogar':fields.boolean('Hogar'),
        #Cocina
        'cocina':fields.boolean('Cocina'),
        'office_cocina':fields.boolean('Cocina con Office'),
        'kit':fields.boolean('Kitchenette'),
        'comedor_diario':fields.boolean('Comedor'),
        'diario_diario':fields.boolean('Diario'),        
        #Exterior
        'terraza':fields.boolean('Terraza'),
        'balcon':fields.boolean(u'Balcón'),
        'terraza_2':fields.boolean('Terraza de servicio'),
        'lavadero':fields.boolean('Lavadero'),
        'azotea':fields.boolean('Acceso a azotea'),
        'patio':fields.boolean('Patio'),
        'fondo':fields.boolean('Fondo'),
        'jardin':fields.boolean(u'Jardín'),
        'parrillero':fields.boolean('Parrillero'),
        'bbq':fields.boolean('Barbacoa'),
        'deposito':fields.boolean('Depósito'),
        #Garage
        'garage':fields.char('Garage:', readonly=True),
        'cochera':fields.char('Autos:'),
        'box':fields.boolean('Box'),
        'autos':fields.char('Autos'),
        'autos2':fields.char('Cochera:', readonly=True),
        #Calefaccion y servicios asesorios
        'calefaccion': fields.many2one('calefacion', 'Calefacción'), #crear xml para llenar los default
        'ac':fields.boolean('Aire Acondicionado'),
        'gas':fields.boolean(u'Gás por cañeria'),
        'telefono':fields.boolean(u'Teléfono'),
        'cable':fields.boolean('TV. Cable'),
        'internet':fields.boolean('Internet'),
        'alarma':fields.boolean('Alarma'),
        #Equipamiento
        'amueblado':fields.boolean('Amueblado'),
        'linea_blanca':fields.boolean('Linea Blanca'),
        #Amenities
        'piscinalibre': fields.boolean('Piscina al aire libre'),
        'piscinacubierta': fields.boolean('Piscina cubierta'),
        'sauna':fields.boolean('Sauna'),
        'sala_juegos':fields.boolean('Sala de Juegos'),
        'gym':fields.boolean('Gimnasio'),
        'canchas':fields.boolean('Canchas deportivas'),
        'parrillero2':fields.boolean('Parrillero'),
        'bbq2':fields.boolean('Barbacoa'),
        'solarium':fields.boolean('Solarium'),
        'salon_comunal':fields.boolean(u'Salón Comunal'),
        #Comodidades del edificio
        'ascensor':fields.boolean('Ascensor'),
        'porteria':fields.boolean('Porteria'),
        'porteria_2':fields.boolean('Portero eléctrico'),
        'lavanderia':fields.boolean(u'Lavandería'),
        'vigilancia':fields.boolean('Vigilancia'),
        #Comentarios
        'comentarios':fields.text('Comentarios'),
        #Nueva pestaña Precio
        'gastos_comun':fields.integer(u'Gastos Comúnes'),
        'contri':fields.integer(u'Contribucción'),
        'impPrim': fields.integer('Imp. Primaria'),
        #Pestaña Direccion
        'edificio':fields.char('Edificio'),
    }

    def _attach_email(self, cr, uid, ids, name, args, context=None):
        attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('email','=',True)])
        datas = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
        return datas

    def _tiempo_hoy(self, cr, uid, context=None):
        return datetime.now()

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
        'state': 'creando',
        'currency': 3,
        'moneda_tasacion': 3,
        'currency_alquiler': 3,
        'currency_venta': 3,
    }

    def action_calcular_precio_hectarea(self, cr, uid, ids, *args):
        total = 0
        your_class_records = self.browse(cr, uid, ids)
        for record in your_class_records:
            total += record.precioTotalLiquidoComIncl / record.superficie
            self.write(cr, uid, ids, {'precioXHaComIncl': round(total)})
            #res[record.id] = {'value':{'precioXHaComIncl':total}}
        return True

    def action_estado_alquilado(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a alquilado'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'state': 'alquilado', 'active': True,'fechaAlquiler': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_enAlquiler(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a en alquiler'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'state': 'enalquiler', 'active': True,'fechaAlquiler': None})
        return True

    def action_estado_ventAlquiler(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a en venta y alquiler'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'state': 'ventAlquiler', 'active': True,'fechaAlquiler': None})
        return True

    def action_estado_vendido(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a vendido'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'state': 'vendido', 'active': False,'fechaVenta': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_enVenta(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a en venta'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'state': 'enventa', 'active': True,'fechaVenta': None})
        return True

    def action_estado_desactivado(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a desactivado'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'active': False})
        return True

    def action_estado_activado(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a activado'
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
                'body': values,
            }, context=context)

        self.write(cr, uid, ids, {'active': True})
        return True

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}

    def action_invoice_sent(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'estate', 'email_template_edi_invoice')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        ctx = dict(context)
        ctx.update({
            'default_model': 'estate',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_invoice_as_sent': True,
            })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }

    def write(self, cr, uid, ids, values, context=None):
        values['modificado'] = True
        #import pdb
        #pdb.set_trace()
        if context != None:

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

        return super(estate, self).write(cr, uid, ids, values, context=context)

    def onchange_categoria(self, cr, uid, ids, category_id, context=None):
        if category_id:
            numero=""
            lista=category_id[0][2]
            largo =len(lista)
            if largo > 0:  
                # return {'value':{'number':codigo, 'codigo':codigo},}
                cr.execute(""" SELECT upper(name) AS name FROM res_partner_category WHERE id = %s """,
                    (lista[0],))           
                nomcat = cr.fetchone()[0]               
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
                        
                        nomaux = nomcat[:1]
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
                            'suffix' : '-'+nomaux+'V',
                        }) 
                    numero = self.pool.get('ir.sequence').get(cr, uid, nomcat)  
                if numero:
                    i = string.index(numero, '-')               
                    numaux = numero[:i]
                    numaux = numaux.strip()
                    sufix = numero[i:]
                    numero = numaux.zfill(4) + sufix
        return {'value':{'number':numero},}        

estate()

class observations(osv.osv):
    _name = "observations"

    _columns = {
        'estate_id':fields.integer('estate_id'),
        'notes': fields.text('Comentarios'),
        'observador': fields.many2one('res.partner', 'Usuario'),
        'obs_date': fields.datetime('Fecha de observación'),
    }
observations()

class expenses(osv.osv):
    _name = "expenses"
    _columns = {
        'estate_id':fields.integer('estate_id'),
        'notes': fields.text('Comentario del gasto'),
        'currency': fields.many2one('res.currency',r'Moneda'),
        'price': fields.float('Valor'),
        }

    _defaults = {
        'currency': 3,
    }

expenses()

class temporada(osv.osv):
    _name="temporada"
    _columns= {
        'estate_id':fields.integer('estate_id'),
        'cliente_1':fields.many2one('res.partner', 'Cliente'),
        'pago_1':fields.boolean('Pagó'),
        'usuario_1':fields.many2one('res.users', 'Usuario'),
        'currency_al': fields.many2one('res.currency', 'Moneda'),
        'rent_price':fields.float('Imp. Mensual' , required=True),
        'rent_day':fields.float('Imp. Diario' , required=True),
        'fecha_inicio':fields.date('Fecha inicio'),
        'fecha_fin':fields.date('Fecha fin'),
        'result':fields.char('C/dias alquilados'),
        'costo_alquiler':fields.char('Costo'),
    }

    def get_number_of_days(self, cr, uid, ids, fecha_inicio, fecha_fin, rent_day, context=None):
        res=0
        if (fecha_fin and fecha_inicio) and (fecha_inicio <= fecha_fin):
            #import pdb
            #pdb.set_trace()
            DATETIME_FORMAT = "%Y-%m-%d"
            to_dt = datetime.datetime.strptime(fecha_fin, DATETIME_FORMAT)
            from_dt = datetime.datetime.strptime(fecha_inicio, DATETIME_FORMAT)
            timedelta = to_dt - from_dt
            diff_day = timedelta.days + float(timedelta.seconds) / 86400
            res=round(math.floor(diff_day))+1
        return { 'value' : { 'result' : res, 'costo_alquiler':rent_day*res}}


    _defaults = {
        'currency_al': 3,
        'rent_price' : 10,
        'rent_day' : 10,
    }

temporada()

class historial(osv.osv):
    _name="historial"
    _columns= {
        'estate_id':fields.integer('estate_id'),
        'usuario_2':fields.many2one('res.partner', 'Usuario'),
        'cambio_2' :fields.char('Cambio'),
        'fecha_cambio':fields.datetime('Fecha de cambio'),
    }

    _defaults = {
    'usuario_2': lambda obj, cr, uid, context: uid,
    'fecha_cambio': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S')

    }


historial()

class interesados(osv.osv):
    _name = "interesados"
    _columns = {
        'estate_id':fields.integer('estate_id'),
        'cliente_id':fields.many2one('res.partner', 'Nombre'),
        'atendido_por':fields.many2one('res.users', 'Atendido por'),
        'telefono':fields.char(u'Teléfono'),
    }
interesados()

class compartidocolegas(osv.osv):
    _name = "compartidocolegas"
    _columns = {
        'estate_id':fields.integer('estate_id'),
        'inm':fields.char('INM'),
        'cliente_id':fields.many2one('res.partner', 'Nombre'),
        'telefono':fields.char(u'Teléfono'),
        'mail':fields.char('Mail'),
    }
compartidocolegas()



class calefacion(osv.osv):
    _name = "calefacion"
    _columns = {
        'name':fields.char(u'Calefacción'),
    }

calefacion()

class departmento(osv.osv):
    _name="departmento"
    _description="Departmentos"
    _columns = {
    'name':fields.char('Departmento'),
    'code':fields.char(u'Código del departmento'),
    'country_id':fields.char('Code')
    }

departmento()


class pais(osv.osv):
    _name="pais"
    _description="Pais"
    _columns = {
    'name':fields.char(u'País', size=56),
    'country_code':fields.char('Country code' ,size=33)
    }

pais()
