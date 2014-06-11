# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import logging
import datetime
import time
import openerp.addons.decimal_precision as dp
import account

from osv import osv
from osv import fields
from tools.translate import _

_logger = logging.getLogger(__name__)


class conceptosdocumentos(osv.osv):

	#***********************************************************************************	
    def get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        for record in self.browse(cr, uid, ids,context):
            res[record.id] = record.cantidad * record.preciounidad
        return res
		
    #***********************************************************************************    
    _name = "conceptosdocumentos"

    _columns = {
        'id_concepto': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fecha': fields.date('Fecha', select=1, required=True),
        'product_id': fields.many2one('product.product', 'Product', ondelete='set null', required=True),
        'partner_id': fields.many2one('res.partner', 'Cliente'),
        'cantidad': fields.integer('Cantidad'),
        #'dtounidad': fields.float('Descuento unidad'),
        'iva':  fields.many2one('account.tax',  'Taxes', domain=[('parent_id','=',False)]),
        'facturar': fields.boolean('A facturar'),
        'facturado': fields.boolean('Facturado'),
        'preciounidad': fields.float('Precio unidad'),  
        'total': fields.function(get_total, type='float',method=True, string='Total'),  
        #'mostrar': fields.function(get_mostrar, type='boolean',method=True, string='Mostrar'),         
    }
	    
    # La tercera linea indica que el valor parter_id sera el contexto la id_activada, si la encuentra, y nada
	# si no la encuentra
    _defaults = {
        'fecha': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'cantidad': 1,
		'partner_id': lambda self, cr, uid, context : context['partner_id'] if context and 'partner_id' in context else None 
    } 
	
    #***********************************************************************************
 
    def product_id_change(self, cr, uid, ids, product_id):        
        
        producto = self.pool.get('product.product').browse(cr, uid, [product_id])[0]
        precio = producto.product_tmpl_id.list_price  
        res_final = {'value':{'preciounidad': precio}}
        return res_final
		
	#***********************************************************************************
	## DETERMINA SI SE INGRESO UN CLIENTE SI SE DESEA FACTURAR UN DETERMINADO GASTO
	# Se aplica en la solapa de "Gastos" tanto en expedientes como en Clientes
	# "Facturar" me indica si la checkbox esta activada y partner_id el cliente ingresado
	# En el caso de que este activada y no halla cliente, sale un cartel de advertencia y ademas
	# se desactiva el checkbox facturar
	
    def falta_cliente(self, cr, uid, ids, partner_id, facturar):
		if facturar== True and not partner_id:
			warning = {
				'title': _('Advertencia'),
				'message': _('Debe ingresar un cliente si selecciona facturar gasto.')
			}
			return {'value':{'facturar': False},'warning': warning}
		return True
	#***********************************************************************************
	
    def unlink(self, cr, uid, ids, context=None):
        sql = ""
        for id in ids:
            cr.execute("SELECT hora_id FROM rel_horas_gasto WHERE gasto_id = %s",(id,))
            for result in cr.fetchall():    
                sql +=" UPDATE horas SET conceptuado = False WHERE id = "+str(result[0])+";"                
                sql +="DELETE FROM rel_horas_gasto where hora_id = "+str(result[0])+";"            
        if sql != "":            
            cr.execute(sql)
        return super(conceptosdocumentos, self).unlink(cr, uid, ids, context=None)
	
	#***********************************************************************************
	
        
conceptosdocumentos()



