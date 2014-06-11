# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import unicodedata
import datetime
import time
from lxml import etree
import math
import pytz
import re
from openerp.tools.translate import _

from array import *
from osv import osv
from osv import fields
from openerp import SUPERUSER_ID
from openerp import pooler, tools
from compiler.ast import TryFinally
from suds.client import Client

import logging
_logger = logging.getLogger(__name__)

EXPEDIENTE_ESTADOS = [
    ('abierto', 'Abierto'),
    ('cerrado', 'Cerrado'),
    ('pausado', 'Pausado'),
]
def elimina_tildes(s): 
    return ''.join((c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn'))

	
#*********************************************************************************
#*********************************************************************************

class expedientes(osv.osv):

	
	#*********************************************************************************
    # ME DIRIJE A LA VISTA DE CONSULTA EXPEDIENTE
	# Me retorna un diccionario con los datos de la vista para cargarga

    def ir_a_vista_consulta_expediente(self, cr, uid, ids, context=None):
		
		#Elimino el contenido de las dos tablas para que no se vallan almacenando
		#las consultas. Solo tengo las tablas para mostrar los datos
        cr.execute("DELETE FROM consultaexpediente ")
        cr.execute("DELETE FROM movimientoexpediente")
		
        numero_expediente_actual=context['iue']
		
		#Adquiero la instancia de los dos webservice para poder operar segun su contenido (Expediente - Decreto)
        cliente_expediente = Client(url='http://www.expedientes.poderjudicial.gub.uy/wsConsultaIUE.php?wsdl')
        cliente_decreto = Client(url='http://www.expedientes.poderjudicial.gub.uy/wsConsultaDecreto.php?wsdl')
		#Realizo la consulta al servidor de Exepedientes dado el numero de uno de los expedientes
		# resultado_expediente es un objeto que posee todos los atributos y metodos definidos en el webservice
        resultado_expediente= cliente_expediente.service.consultaIUE(numero_expediente_actual)

        instancia_tabla_consulta=self.pool.get('consultaexpediente')
        instancia_tabla_decreto=self.pool.get('movimientoexpediente')
		
        id_registro_consulta_expediente=instancia_tabla_consulta.create(cr,uid, {'id_consulta':1010,
												 'resultado':resultado_expediente.estado, 
												 'origen': resultado_expediente.origen,
												 'expediente':resultado_expediente.expediente,
												 'caratula':resultado_expediente.caratula,
												 'abogado_actor':resultado_expediente.abogado_actor,
												 'abogado_demandante':resultado_expediente.abogado_demandante
												 })
		# Adquiero los movimientos del expediente. Esto es una lista de objetos "movimientos"
        movimientos_expediente= resultado_expediente.movimientos
		
		# Recorro la lista de movimientos, para guardarlos individualmente
        for movimiento in movimientos_expediente:
			decreto_actual=""
			# Si el decreto del movimiento actual no es nulo, consulto en el webservice del decreto!!
			if movimiento.decreto != None:
				decreto_actual = cliente_decreto.service.consultaDecreto(str(context['numero']),str(movimiento.decreto))
			instancia_tabla_decreto.create(cr,uid, {'id_movimiento': 1110,
													'fecha': movimiento.fecha,
													'tipo_movimiento': movimiento.tipo,
													'decreto': decreto_actual,
													'vencimiento': movimiento.vencimiento,
													'sede': movimiento.sede,
													'id_consulta':id_registro_consulta_expediente 
													})
		 
      
        mod_obj = self.pool.get('ir.model.data')
        res = mod_obj.get_object_reference(cr, uid, 'expedientes', 'view_consulta_expediente_form')
        # Retorno un pop up con los movimientos en un tree, usando el campo de consultaexpediente que guarda
		# todos los movimientos asociados
        return {
                'name': 'Datos del expediente consultado',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res and res[1] or False],
                'res_id': id_registro_consulta_expediente,
                'res_model': 'consultaexpediente',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
            }

	#*********************************************************************************
       		
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

	#*********************************************************************************
		
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

	#*********************************************************************************		
    
    def get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.concepto_ids:        
                total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res

	#*********************************************************************************		
    
    def get_total_conceptuado(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.horas_ids:        
                if recordConc.conceptuado:
                    total += recordConc.canthoras
            res[record.id] = total
        return res  
 
	#*********************************************************************************
 
    def get_total_sin_conceptuar(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.horas_ids:        
                if not recordConc.conceptuado:
                    total += recordConc.canthoras
            res[record.id] = total
        return res 
		
	#*********************************************************************************        
    
    def get_totalhoras(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.horas_ids:        
                total += recordConc.canthoras
            res[record.id] = total
        return res
        
    def get_emails(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for id in ids:
            result[id] = self.pool.get('mail.message').search(cr, uid, [('subtype_id','=',1),('model','=','expedientes'), ('res_id', '=',id)])
        return result        

    def get_emails_list(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
           res[record.id] = 	','.join(
                [','.join([propio.partner_id.email for propio in record.propios_ids]),
                ','.join([propio.partner_id.email for propio in record.comunes_ids])])
        return res

    def _check_gastos(self,cr,uid,ids):
        _logger.info([ (gasto.partner_id.id, participante.partner_id.id) for expediente in self.browse(cr, uid, ids) for gasto in expediente.concepto_ids for participante in expediente.propios_ids])
        return reduce (lambda x,y:x and y, [ (gasto.partner_id.id in map( lambda participante: participante.partner_id.id , expediente.propios_ids)) 
									for expediente in self.browse(cr, uid, ids) 
									for gasto in expediente.concepto_ids ], True)

    _name = "expedientes"
    _inherit = "mail.thread"
    
    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fechaalta': fields.date('Fecha alta', select=1, required=True),
        'fechacierre': fields.date('Fecha cierre', select=1),
        'number': fields.char('Código referencia', size=64, required=True),
        'nroautos': fields.char('Número de autos', size=24),
        'nig': fields.char('Identificación Unica de Expediente', size=24, help="Los procedimientos llevarán un Número de Identificación General (NIG) que se asignará en el momento de la presentación del escrito iniciador. Las aplicaciones informáticas mantendrán la referencia común a este NIG a lo largo de su íter procesal."),
        'tipoasunto': fields.many2one('tipo.asunto', 'Tipo Asunto'),
        'tipoexpediente': fields.many2one('tipo.expediente', 'Tipo Expediente'),
        'cliente': fields.char('Referencia cliente', size=64),
        'procurador': fields.char('Referencia procurador', size=64),
        'tipoprocedimiento': fields.many2one('tipo.procedimiento', 'Tipo Procedimiento'),
        'refpropia': fields.char('Ubicación del expediente', size=64),
        'concepto_ids': fields.one2many('conceptosdocumentos', 'id_concepto', 'Concepto'),        
        'horas_ids': fields.one2many('horas', 'id_exp', 'Horas'),        
        'accion_ids': fields.one2many('crm.meeting','id_exp', 'Acciones'),        
        'facturas_ids': fields.many2many('account.invoice','facturas_doc_rel', 'id', 'invoice_id', 'Facturas'),               
        'attachments': fields.one2many('ir.attachment', 'res_id', 'Archivos'),
        'expedientes_ids': fields.many2many('expedientes','rel_exp_exp', 'id_expexp','id_exp', 'Expedientes'),
        'active': fields.boolean('Activo'),      
        'totalgral': fields.function(get_total, type='float',method=True, string='Total'),         
        'totalfacturado': fields.function(get_total_facturado, type='float',method=True, string='Total facturado'),         
        'totalsinfacturar': fields.function(get_total_sin_facturar, type='float',method=True, string='Saldo no facturado'),         
        'totalgralhoras': fields.function(get_totalhoras, type='float',method=True, string='Total horas'),         
        'totalconceptuado': fields.function(get_total_conceptuado, type='float',method=True, string='Horas con gasto generado'),         
        'totalsinconceptuar': fields.function(get_total_sin_conceptuar, type='float',method=True, string='Horas sin gasto generado'),         
        
        'emails': fields.function(get_emails, relation='mail.message',method=True,type='one2many'),  
        #'state': fields.related('mail_message_id', 'state', type='char', string='Estado'),       
        'propios_ids': fields.one2many('participantes.expediente', 'id_expediente','Propios', domain=[('tipo','=',1)]),       
        'contrarios_ids': fields.one2many('participantes.expediente', 'id_expediente','Contrarios', domain=[('tipo','=',2)]),       
        'comunes_ids': fields.one2many('participantes.expediente', 'id_expediente','Comunes', domain=[('tipo','=',3)]),    
        'emails_template': fields.function(get_emails_list, type='char',method=True, string="Clients' e-mail list"),    
        #'organismos_ids': fields.one2many('organismo', 'id_exp', 'Organismos'),        
        'organismos_ids': fields.many2many('organismo','rel_exp_organismo', 'id_exporg','id_exp', 'Organismos'),        
        'juzgados_ids': fields.many2many('juzgado','rel_exp_juzgado', 'id_expjuz','id_exp', 'Juzgados'),        
        #'juzgados_ids': fields.one2many('juzgado', 'id_exp', 'Juzgados'),        
        #'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
        'message_ids': fields.one2many('mail.message', 'res_id', 'Messages', domain=[('model','=',_name)]),
        'create_date': fields.datetime('Fecha de creación' , readonly=True),                
        'write_date': fields.datetime('Fecha de actualización' , readonly=True),   
        'create_uid': fields.many2one('res.users', 'Creado por', readonly=True),
        'write_uid': fields.many2one('res.users', 'Actualizado por', readonly=True),  
        'notas_ids':fields.one2many('expediente.nota','expediente','Notas'), 
        'state': fields.selection(EXPEDIENTE_ESTADOS, 'Estado', size=16, readonly=True),       
        'is_judicial': fields.boolean('Es expediente judicial', help="Seleccione si el expediente es judicial, sino es extrajudicial"),                   
    }

    _defaults = {
        'active': True,
        'fechaalta': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'number': lambda self,cr,uid,context={}: self.pool.get('ir.sequence').get(cr, uid, 'expediente'),
        'state': 'abierto',
        'is_judicial': True,
    }    
    #_constraints = [(_check_gastos,"Los gastos solo pueden afectar a clientes propios", ['concepto_ids','propios_ids'])]
    
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
	#*************************************************************************
	
		
	#*************************************************************************
    def action_estado_abierto(self, cr, uid, ids, values, context=None):
        subject = 'Cambio de estado a Abierto'
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
    
    def action_nueva_gasto(self, cr, uid, ids, *args):
        if not ids: return {}
        resultado={}
        listagastos=[]
        invoice_ids = []

        sql = ""
        fechadeldia = datetime.date.today().strftime('%Y-%m-%d')
        id_exp = None
        nom_exp =""
        exps = self.browse(cr, uid, ids)  
        contHoras = 0
        for record in exps:
            id_exp = record.id
            nom_exp = record.name
            for recordHoras in record.horas_ids:  
                if recordHoras.conceptuar and not recordHoras.conceptuado:                        
                    if resultado.has_key(recordHoras.product_id):
                        resultado[recordHoras.product_id].append(recordHoras)
                    else:
                        resultado[recordHoras.product_id] =[recordHoras]   
            #contHoras=sum([rechoras.canthoras for rechoras in record.horas_ids if (rechoras.conceptuar and rechoras.conceptuado)])
        
            obj_hora=self.pool.get('horas')
            listagastos = obj_hora.search(cr, uid,[('conceptuar', '=', True),('conceptuado', '=', False),('id_exp','=',id_exp)])
            #contHoras = sum(map(lambda x: x['canthoras'],obj_hora.read(cr,uid,listagastos,['canthoras'])))
            obj_hora.write(cr, uid,listagastos,{'conceptuado':True})
            if resultado:
                for (producto,record) in resultado.iteritems(): 
                    contHoras=0
                    for r in record:
                        contHoras += r.canthoras
                    #obtener el producto horas...si no está definido tomar el primero
                    price=producto.product_tmpl_id.list_price
                    nombre = 'Horas del expediente '+nom_exp
                    #cr.execute("INSERT INTO rel_horas_gastos (gasto_id,invoice_id) VALUES (%s,%s)",(r.id,invoice_id,))
                    #cr.execute("INSERT INTO conceptosdocumentos (fecha,name,id_concepto,product_id,preciounidad,cantidad) VALUES(%s,%s,%s,%s,%s,%s)",(fechadeldia,nombre,id_exp,producto.id,price,contHoras))
                    gasto_id = self.pool.get('conceptosdocumentos').create(cr, uid,{
                        'name' : nombre,
                        'date_invoice' : fechadeldia,
                        'id_concepto' : id_exp,
                        'product_id': producto.id,
                        'preciounidad' : price,
                        'cantidad' : contHoras,
                    }) 
                    for r in record:                    
                        cr.execute("INSERT INTO rel_horas_gasto (gasto_id,hora_id) VALUES (%s,%s)",(gasto_id,r.id,))
        return True
    
    
    def action_nueva_factura(self, cr, uid, ids, *args):
        if not ids: return {}
        invoice_ids = []
        resultado = {}
        fechadeldia = datetime.date.today().strftime('%Y-%m-%d')
        exps = self.browse(cr, uid, ids)  
        exp_id = None
        account=""  
        for record in exps:
			# Obtengo ID del expediente
            exp_id = record.id
            for recordCon in record.concepto_ids:  
                if recordCon.facturar and not recordCon.facturado:
                        if resultado.has_key(recordCon.partner_id.id):
                            resultado[recordCon.partner_id.id].append(recordCon)
                        else:
                            resultado[recordCon.partner_id.id] =[recordCon] 
							
		# Aca es donde realmente escribe en la base de datos las facturas!! (Conceptos documentos)
		condocs = self.pool.get('conceptosdocumentos')
		# Esta linea es la que tengo que modificar para que me guarde solo las facturas que tienen cliente!!
		afacturar= condocs.search(cr, uid, [('id_concepto','in',ids),('facturar','=',True),('facturado','=',False)])
		###***
		fa=False
		for i in afacturar:
			auxiliar= condocs.browse(cr,uid,i)
			#if auxiliar.partner_id == "":
			if auxiliar != None: # and auxiliar.partner_id == "":
				if not auxiliar.partner_id:
					raise osv.except_osv(_('Un gasto se registro sin un cliente'),_('Por favor, verifique que todos los gastos se hallan ingresado con un clientes')) 
		condocs.write(cr,uid,afacturar,{'facturado':True})
		###**
		#*****************
        if resultado:
            journal_ids = self.pool.get('account.journal').search(cr, uid,[('type', '=', 'sale'), 
                ('company_id', '=', 1)],
                limit=1)                    
            if not journal_ids:
                raise osv.except_osv(_('Error!'),
                    _('Debe ingresar un Diario de Venta.'))        
            for (cli,record) in resultado.iteritems():
                cliente = self.pool.get('res.partner').browse(cr, uid, [cli])[0]
                try:  
                    account = cliente.property_account_payable.id
                except:
                    account = ""

                if account != "":
                    _logger.info('cliente'+str(cliente))
                    company = cliente.company_id.id
                    moneda = cliente.property_account_payable.currency_id
                    if not moneda:
                        moneda = cliente.company_id.currency_id
                        if not moneda:
                            raise osv.except_osv(_('Error!'),('La compañía no tiene moneda.'))  
                
                
                    lines = [(0,0,{
                            'name' : r.name,
                            'product_id' : r.product_id.id,
                            'price_unit' : r.preciounidad,
                            'quantity' : r.cantidad,
                            'invoice_line_tax_id': ([(6,0,[r.iva.id])] if r.iva else None)
                            }) 
                                for r in record]                
                    invoice_id = self.pool.get('account.invoice').create(cr, uid,{
                        'name' : 'Factura',
                        'date_invoice' : fechadeldia,
                        'account_id' : account,
                        'invoice_line': lines,
                        'currency_id' : moneda.id,
                        'partner_id' : cli,
                        'journal_id' : journal_ids[0],
                        'company_id' : company,
                        'origin' : 'Factura',
                    })  
                    fact_id=0
                    cr.execute("INSERT INTO facturas_doc_rel (id,invoice_id) VALUES (%s,%s)",(exp_id, invoice_id,))
                        
                    invoice_ids.append(invoice_id)
                    
                    for r in record:
                        cr.execute("INSERT INTO facturas_doc_rel_lineas (gasto_id,invoice_id) VALUES (%s,%s)",(r.id,invoice_id,))

        mod_obj = self.pool.get('ir.model.data')        
        if len(invoice_ids) == 0:
            return True
        elif len(invoice_ids) > 1:
            # res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_tree')
            # return {
                # 'name': 'Factura',
                # 'view_type': 'tree',
                # 'view_mode': 'tree',
                # 'view_id': [res and res[1] or False],
                # 'res_id': invoice_ids,
                # 'res_model': 'account.invoice',
                # 'type': 'ir.actions.act_window',
                # 'nodestroy': True,
                # 'target': 'new',
            # }  
            return True            
        else:
            res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
            return {
                'name': 'Factura de gastos',
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': [res and res[1] or False],
                'res_id': invoice_ids[0],
                'res_model': 'account.invoice',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'target': 'new',
            }


    def action_expediente_sent(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi invoice template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'expedientes', 'ficha')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False
        
            
        ctx = dict(context)
        ctx.update({
            'default_model': 'expedientes',
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

        #raise osv.except_osv(_('Debe ingresar un cliente!!!!!!!'),_('Avivate por favor!!!')) 
        categ_id = ""
        cr.execute("""  select id from categoria_expediente where name = 'Cliente'""")  
        res = cr.dictfetchone()
        if res:   
            categ_id = res['id']   
        exp_id = 0
        
        exp_id = super(expedientes, self).write(cr, uid, ids, values, context=context)
        exps = self.browse(cr, uid, ids) 
        doc_exp_id = ""
        for recordExp in exps:
            #Si no está definido un directorio Expedientes se lo crea
            cr.execute("""  select id from document_directory where name = 'Expedientes' """)     
            resDir2 = cr.dictfetchone()
            if not resDir2:
                doc_exp_id = self.pool.get('document.directory').create(cr, uid,{
                    'resource_find_all' : True,
                    'ressource_tree' : False,
                    'user_id' : uid,
                    'name' : 'Expedientes',
                    'parent_id' : 4,
                    'type' : 'directory',
                    #'res_id':recordExp.id,
                })
            else:
                doc_exp_id = resDir2['id']
            #Se cuelga del directorio Expedientes el expdiente creado si ya no está    
            cr.execute("""  select id from document_directory where res_id = %s AND parent_id=%s AND type = 'directory'""",
                (recordExp.id,doc_exp_id,))           
            res = cr.dictfetchone()
            if not res:
                nomExp = elimina_tildes(recordExp.name)
                nomExp = nomExp.replace("/", "")
                doc_id = self.pool.get('document.directory').create(cr, uid,{
                    'resource_find_all' : True,
                    'ressource_tree' : False,
                    'user_id' : uid,
                    'name' : nomExp,
                    'parent_id' : doc_exp_id,
                    'type' : 'directory',
                    'res_id':recordExp.id,
                    'res_model':'expedientes',
                })          

            #Inserto directorios de clientes en Conocimiento
            for recordProp in recordExp.propios_ids:
                _logger.info('categoriaaaaaaaa'+str(recordProp.partner_id))
                _logger.info('iddddddd categoriaaaaaaaa'+str(recordProp.partner_id.id))
                #saco sólo los propios con categoría cliente
                if recordProp.categoria.id == categ_id:
                    #Si no hay un directorio Clientes se lo crea
                    cr.execute("""  select id from document_directory where name = 'Clientes' """)           
                    resDir = cr.dictfetchone()
                    if not resDir:
                        doc_id = self.pool.get('document.directory').create(cr, uid,{
                            'resource_find_all' : True,
                            'ressource_tree' : False,
                            'user_id' : uid,
                            'name' : 'Clientes',
                            'parent_id' : 4,
                            'type' : 'directory',
                            #'res_id':recordCli.id,
                        })
                    else:                
                        doc_id = resDir['id']                    
                    #Se cuelga del directorio Clientes al cliente creado si ya no está 
                    cr.execute("""  select id from document_directory where res_id = %s AND type = 'directory' """,
                        (recordProp.partner_id.id,))           
                    res = cr.dictfetchone()
                    if not res:
                        dir_cli_id = self.pool.get('document.directory').create(cr, uid,{
                            'resource_find_all' : True,
                            'ressource_tree' : False,
                            'user_id' : uid,
                            'name' : recordProp.partner_id.name,
                            'company_id' : recordProp.partner_id.company_id.id,
                            'parent_id' : doc_id,
                            'type' : 'directory',
                            'res_id':recordProp.partner_id.id,
                            'res_model':'clientes',
                        }) 
                        entre = False
                        #Si ese cliente ya tiene anexos se los tiene que dar de alta
                        cr.execute("""  Select id,name FROM ir_attachment where res_model ='res.partner' and res_id = %s""",
                            (recordProp.partner_id.id,))
                        for result in cr.fetchall():
                            _logger.info('adjuntosss partnerrrrrrrrrrr'+str(recordProp.partner_id.id))
                            _logger.info('adjuntosss nameeeeeeeeeeeeeeee'+str(result[1]))
                            _logger.info('adjuntosss idddddddddddddd'+str(result[0]))
                            _logger.info('adjuntosss dir_cli_idddddddddd'+str(dir_cli_id))
                            
                            if not entre:
                                #Si crea un directorio Archivos adjuntos 
                                docArxh_id = self.pool.get('document.directory').create(cr, uid,{
                                    'resource_find_all' : True,
                                    'ressource_tree' : False,
                                    'user_id' : uid,
                                    'name' : 'Archivos adjuntos',
                                    'parent_id' : dir_cli_id,
                                    'type' : 'directory',
                                })
                            _logger.info('adjuntosss docArxh_idddddddd'+str(docArxh_id))                                
                            
                            #Se agregan los adjuntos
                            doc_id = self.pool.get('document.directory').create(cr, uid,{
                                'resource_find_all' : True,
                                'ressource_tree' : False,
                                'user_id' : uid,
                                'name' : result[1],
                                'parent_id' : docArxh_id,
                                'type' : 'directory',
                                'res_id':result[0],
                                'res_model':'clientes',
                            })                            
                            entre = True
          
                
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
            
        return exp_id        

    def unlink(self, cr, uid, ids, context=None):

        for id in ids:
            cr.execute("""  DELETE FROM document_directory where parent_id = %s """,
                (id,))         
            cr.execute("""  DELETE FROM document_directory where res_id = %s """,
                (id,))                  

        return super(expedientes, self).unlink(cr, uid, ids, context=None)
        
class tipo_procedimiento(osv.osv):
    _name = "tipo.procedimiento"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }
    
class tipo_asunto(osv.osv):
    _name = "tipo.asunto"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }    

class tipo_expediente(osv.osv):
    _name = "tipo.expediente"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }    

  
#class tipo_cliente(osv.osv):
#    _name = "tipo.cliente"
#    _columns = {
#        'name': fields.char('Descripción', size=10, required=True),
#    }     
    
class tipo_propios(osv.osv):
    _name = "tipo.propios"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    } 

class tipo_contrarios(osv.osv):
    _name = "tipo.contrarios"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    } 

class tipo_comunes(osv.osv):
    _name = "tipo.comunes"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }     


class tipo_poder(osv.osv):
    _name = "tipo.poder"
    _columns = {
        'name': fields.char('Descripción', size=50, required=True),
    }    

class expediente_nota(osv.osv):

    _name = "expediente.nota"
    _description = "Notas del expediete"

    _columns = {
        'expediente':fields.integer('Expediente',invisible=True),
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
    
               
expediente_nota()
