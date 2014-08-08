# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import string
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
import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)
PROPIEDAD_ESTADOS = [
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
        view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'inmobiliaria', 'inherited_view_crm_leads_tree')
        view_id = view_ref and view_ref[1] or False
        estate_obj = self.pool.get("crm.lead")
        #import pdb; pdb.set_trace()
        domain = []
        caracteristicas = ['largo','city']
        #,'city','country_id','cantidadDormitorios'
        obj = self.browse(cr,uid,ids,context)[0]
        ctx = (context or {}).copy()
        cr.execute('select id from ir_ui_view where model=%s and field_parent=%s and type=%s', ('crm.lead', 'Oportunidades macheables', 'tree'))
        view_ids = cr.fetchone()
        view_id = view_ids and view_ids[0] or False
        for p in caracteristicas:
            if obj[p]:
                domain.append('|')
                domain.append((p,'=',False))
                domain.append((p,'=',obj[p]))
        oportunidades = estate_obj.search(cr, uid,domain)
        ctx['oportunidades'] = oportunidades
        return {
            'domain': "[('id','in',["+','.join(map(str, oportunidades))+"])]",
            'type': 'ir.actions.act_window',
            'name': 'Oportunidades macheables',
            'res_model': 'crm.lead',
            #'res_id': oportunidades,
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

    def _attach_email(self, cr, uid, ids, name, args, context=None):
        attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('email','=',True)])
        datas = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
        return datas
        
    """
            
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
        'nunemero_de_puerta':fields.char('Nro de puerta'),



        
        'is_rural': fields.boolean('Es propiedad rural', help="Seleccione si la propiedad es rural, sino es urbana"),
        'category_id': fields.many2many('res.partner.category', id1='id', id2='category_id', string='Categorías'),
        'date': fields.date('Fecha de Ingreso', select=1, required=True),

        'street': fields.char('Calle/Dirección', size=128),
        'numero_de_puerta':fields.char('Numero de puerta'),
        'numero_de_apto':fields.char('Número de Apto.'),
        'street2': fields.char('Calle 2', size=128),
        'zip': fields.char('Código postal', change_default=True, size=24),
        'city': fields.char('Ciudad', size=128),
        'neighborhood': fields.char('Barrio', size=128),
        'state_id': fields.many2one("res.country.state", 'Departamento'),
        'country_id': fields.many2one('res.country', 'País'),

        'texto_rojo':fields.char('El texto en rojo implica que será publicado en la web', readonly=True),
        
        'barrio': fields.char('Barrio', size=128),
        'supTotal': fields.float('Superficie total'),
        'supEdificada': fields.float('Superficie edificada'),
        'largo': fields.integer('Profundidad'),
        'ancho': fields.integer('Frente'),
        'documentacion': fields.text('Documentación'),
        'escribano': fields.many2one('res.partner', 'Escribano'),
        
        # Rural
        'padron': fields.boolean('Padrón'),
        'estudioSuelo': fields.boolean('Estudios de Suelo'),
        'mapa': fields.boolean('Mapa'),
        'distancias': fields.boolean('Distancias'),
        'fotos': fields.boolean('Fotos'),
        'autWeb': fields.boolean('Aut. Web'),
        'ImagenesGoogle': fields.boolean('Imágenes Google'),
        'distancia': fields.char('Distancia', size=128),
        'accesos': fields.char('Accesos', size=128),
        'seccional': fields.char('Seccional', size=128),
        'superficie': fields.float('Superficie'),
        'supForestada': fields.float('Sup. Forestada'),
        'indiceConeat': fields.integer('Índice Coneat'),
        
        #'indiceProdFinal': fields.integer('Índice de Producción Final'),
        'indiceValorReal': fields.integer('Índice de Valor Real'),
        'tieneCasa': fields.boolean('Casa'),
        'montes': fields.char('Montes', size=256),
        'exploit': fields.char('Explotación', size=256),
        'padrones': fields.char('Padrones', size=256),
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
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),
		'create_uid': fields.many2one('res.users', 'Ingresado por', required=True),
        'write_uid': fields.many2one('res.users', 'Actualizado por', required=True),
        #'uid': fields.many2one('res.users', 'Usuario'),
        #'write_uid_name': fields.related('write_uid', 'name', type='char', string='Actualizado por'),
        'state': fields.selection(PROPIEDAD_ESTADOS, 'Estado', size=16, readonly=True),
        'fechaVenta': fields.date('Fecha de Venta', select=1),
        'colegas_ids':fields.many2many('res.partner', 'colegas_rel', 'partner_id', 'colega_id', 'Compartido con'),
        'observations_ids':fields.one2many('observations', 'estate_id','Obervaciones'),
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
        'emails': fields.function(get_emails, string="EMail", relation='mail.message',method=True,type='one2many'),  
        'fechaContacto': fields.date('Fecha de Contacto', select=1),
        'webUrl': fields.function(_get_webUrl),  
        'webProp': fields.function(_get_CodProp), 
        #'duplicados': fields.char('Duplicados',50),
        'reservado':fields.boolean('Reservado'),
        'destacados': fields.boolean('Destacado'),
        'ubicacion': fields.text('Ubicación'),#ya existe


        # Descripcion General
        'comodidades': fields.text('Comodidades'),
        'padron':fields.integer('Número de padrón'),
        'year':fields.integer('Año de Construcción'),
        'orientacion':fields.char('Orientación'),        
        'ubica':fields.char('Ubicación'),
        'gastos_comun':fields.integer('Gastos Comúnes'),
        'contri':fields.integer('Contribucción'),
        'calor':fields.char('Calefacción'),
        'impPrim': fields.integer('Imp. Primaria'),#ya existe
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
        'nAmbientes':fields.integer('Cantidad de ambientes'),#ESTO VA CONECTADO A UNA FUNCIONA QUE SUMA LOS OTROS AMBIENTES 
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

        #Tasacion
        'fecha_tasacion':fields.date('Fecha de Tasación'),
        'moneda_tasacion':fields.many2one('res.currency', 'Moneda de Tasación'),
        'importe_tasacion':fields.integer('Importe'),
        'tasado_por':fields.many2one('res.partner','Tasado por'),
        'tipo':fields.selection((('C','Colega'),('D','Directo'),('E', 'Exclusivo'),('I','Indirecta'), ('N','No exclusivo'),('O','Ofrecido')),'Tipo'),

        #Condiciones de venta
        'currency': fields.many2one('res.currency', 'Moneda Venta'),
        'price': fields.float('Precio Venta'),
        'conditions': fields.text('Condiciones'),
        'financiacion':fields.selection((('P','Préstamo bancario'),('B','BHU'),('F','Financia dueño'),('0','Otro')),'Tipo de financiación'),
        'alquiler':fields.boolean('¿Alquiler?', help="Seleccione si la propiedad está para alquilar, de lo contrario a la venta"),
        
        #Gastos
        'notes': fields.text('Comentario del gasto'),
        'currency': fields.many2one('res.currency',r'Moneda'),
        'price': fields.float('Valor'),   
        
    }
    
      

  
    def _attach_satelital(self, cr, uid, ids, name, args, context=None):
        attach_ids = self.pool.get('ir.attachment').search(cr, uid, [('satelital','=',True)])
        datas = self.pool.get('ir.attachment').read(cr, uid, attach_ids)
        return datas

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
        'state': 'enventa',        
        'currency': 3,
        'moneda_tasacion': 3,
    }      
    
        
        
    def action_calcular_precio_hectarea(self, cr, uid, ids, *args):
        total = 0
        your_class_records = self.browse(cr, uid, ids)    
        for record in your_class_records:        
            total += record.precioTotalLiquidoComIncl / record.superficie
            self.write(cr, uid, ids, {'precioXHaComIncl': round(total)})
            #res[record.id] = {'value':{'precioXHaComIncl':total}}
        return True        

        
    def action_estado_alquilado(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'alquilado', 'active': True,'fechaAlquiler': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_enAlquiler(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'enalquiler', 'active': True,'fechaAlquiler': None})
        return True    
   
    def action_estado_ventAlquiler(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'ventAlquiler', 'active': True,'fechaAlquiler': None})
        return True    
        
    def action_estado_vendido(self, cr, uid, ids, *args):
        self.write(cr, uid, ids, {'state': 'vendido', 'active': False,'fechaVenta': time.strftime('%Y-%m-%d %H:%M:%S')})
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
        'observador': fields.many2one('res.users', 'Usuario'),
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
        'cliente_1':fields.many2one('res.users', 'Cliente'),
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
        'usuario_2':fields.many2one('res.users', 'Usuario'),
        'cambio_2' :fields.char('Cambio'),
        'fecha_cambio':fields.datetime('Fecha de cambio'),
    }

historial()
       
