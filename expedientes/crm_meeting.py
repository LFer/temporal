# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
import logging

_logger = logging.getLogger(__name__)


class crm_meeting(osv.osv):
        
    _name = "crm.meeting"
    _inherit = "crm.meeting"
    
    _columns = {
        'id_exp': fields.many2one('expedientes', 'Exp'),
        'descripcion': fields.related('id_exp', 'name', type='char', string='Descripción expediente'),
    }
crm_meeting()

