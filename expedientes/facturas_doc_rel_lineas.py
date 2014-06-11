# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class facturas_doc_rel_lineas(osv.osv):
    _name = "facturas.doc.rel.lineas"
    
    _columns = {
        'invoice_id': fields.integer('invoice', size=16),
        'gasto_id': fields.integer('Doc', size=16),
    }
      

    
facturas_doc_rel_lineas()

