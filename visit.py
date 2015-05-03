# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import datetime
import time
from osv import osv
from osv import fields

class visit(osv.osv):
    _name = "visit"
    _columns = {
    	'estate_id': fields.many2one('estate', 'Propiedad', required=True),
		'date': fields.date('Fecha', select=1, required=True),
		'partner_id': fields.many2one('res.partner', 'Visitante', required=True),
		'notes': fields.text('Comentarios'),
	    }
visit()




