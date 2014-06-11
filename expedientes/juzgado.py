# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import logging
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

_logger = logging.getLogger(__name__)

class juzgado_nota(osv.osv):

    _name = "juzgado.nota"
    _description = "Notas del juzgado"

    _columns = {
        'id_juzgado':fields.integer('Organismo',invisible=True),
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
    
               
juzgado_nota()

class juzgado(osv.osv):

    _name = "juzgado"

    _columns = {
        'id_exp': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'street': fields.char('Calle/Dirección', size=128),
        'street2': fields.char('Calle 2', size=128),
        'zip': fields.char('Código postal', change_default=True, size=24),
        'city': fields.char('Ciudad', size=128),
        'state_id': fields.many2one("res.country.state", 'Departamento'),
        'country_id': fields.many2one('res.country', 'País'),        
        'barrio': fields.char('Barrio', size=128),        
        'notas_ids':fields.one2many('juzgado.nota','id_juzgado','Notas'),
        'active': fields.boolean('Activo'),                      
    }

    _defaults = {
        'active': True,
    }    

    def onchange_state(self, cr, uid, ids, state_id, context=None):
        if state_id:
            country_id = self.pool.get('res.country.state').browse(cr, uid, state_id, context).country_id.id
            return {'value':{'country_id':country_id}}
        return {}
      
        
juzgado()
