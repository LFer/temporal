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

PODER_ESTADOS = [
    ('abierto', 'Abierto'),
    ('cerrado', 'Cerrado'),
    ('pausado', 'Pausado'),
]

TIPO_FORMATO = [
    ('acta', 'Acta'),
    ('notarial', 'Notarial'),
]

TIPO = [
    ('especial', 'Especial'),
    ('general', 'General'),
]

TIPO_APODERADO = [
    ('abogado', 'Abogado'),
    ('procurador', 'Procurador'),
]

_logger = logging.getLogger(__name__)

class poder_nota(osv.osv):

    _name = "poder.nota"
    _description = "Notas del poder"

    _columns = {
        'id_poder':fields.integer('Poder',invisible=True),
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
    
               
poder_nota()

class poderjudicial(osv.osv):

    _name = "poderjudicial"

    _columns = {
        'id': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fecha': fields.date('Fecha Poder', select=1, required=True),
        'number': fields.char('Nro. Poder', size=64, required=True),
        'nroprotocolo': fields.char('Nro. Protocolo', size=64, required=True),
        'formato': fields.selection(TIPO_FORMATO, 'Formato', size=16),
        'notario': fields.char('Nro. anterior', size=64),
        'tipo': fields.selection(TIPO, 'Tipo', size=16),
        'apoderado': fields.selection(TIPO_APODERADO, 'Formato', size=16),
        'participantes_ids': fields.one2many('participantespoder', 'id_poder','Participantes'), 
        'attachments': fields.one2many('ir.attachment', 'res_id', 'Archivos'),
        'notas_ids':fields.one2many('poder.nota','id_poder','Notas'),
        #'notas': fields.text('Notas'),
        #'attachments': fields.one2many('ir.attachment', 'res_id', 'Archivos'),
        'active': fields.boolean('Activo'),       
        'state': fields.selection(PODER_ESTADOS, 'Estado', size=16, readonly=True),               
    }

    _defaults = {
        'active': True,
        'name' : 'Oculto',
        'fecha': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
        'state': 'abierto',
    }    

    def action_estado_cerrado(self, cr, uid, ids, values, context=None):
        self.write(cr, uid, ids, {'state': 'cerrado', 'fechacierre': time.strftime('%Y-%m-%d %H:%M:%S')})
        return True

    def action_estado_abierto(self, cr, uid, ids, values, context=None):
        self.write(cr, uid, ids, {'state': 'abierto'})
        return True    
        
    def action_estado_pausado(self, cr, uid, ids, values, context=None):
        self.write(cr, uid, ids, {'state': 'pausado'})
        return True 
    
poderjudicial()

       
        

