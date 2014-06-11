# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    
    _columns = {
        'carpar_ids': fields.one2many('participantes.carpeta', 'partner_id','Participantes'),             
    }
res_partner()
