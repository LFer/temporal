# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class facturas_doc_rel(osv.osv):
    _name = "facturas.doc.rel"
    
    _columns = {
        'id': fields.integer('Exp', size=16),
        'invoice_id': fields.integer('Cta', size=16),
    }

facturas_doc_rel()

