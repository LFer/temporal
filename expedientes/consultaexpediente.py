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

class consultaexpediente(osv.osv):
	
	_name = "consultaexpediente"
	_columns = {
		'id_consulta': fields.integer('ID'),
		'resultado': fields.char('Resultado Consulta', size=256),
        'origen': fields.char('Origen', size=256),
		'expediente': fields.char('Expediente', size=256),
		'caratula': fields.char('Caratula', size=256),
		'abogado_actor': fields.char('Abogado Actor', size=256),
		'abogado_demandante': fields.char('Abogado Demandante', size=256),
		'movimientos_expedientes_ids': fields.one2many('movimientoexpediente','id_consulta','Movimientos' )
    }
	
	
	
class movimientoexpediente(osv.osv):
	
	_name = "movimientoexpediente"
	_columns = {
		'id_movimiento': fields.integer('ID Movimiento', readonly=True),
		'fecha': fields.date('Fecha', select=1),
		'tipo_movimiento': fields.char('Tipo de Movimiento', size=256),
        'decreto': fields.char('Decreto', size=256),
		'vencimiento': fields.char('Vencimiento', size=256),
		'sede': fields.char('Sede', size=256),
		'id_consulta': fields.many2one('consultaexpediente', 'ID Consulta')
    }
	
	
	