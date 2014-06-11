# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class facturas_doc(osv.osv):
    _name = "facturas.doc"
    
    _columns = {
        'id': fields.integer('Doc', size=16),
        'account_id': fields.integer('Cta', size=16),
    }
    
    def unlink(self, cr, uid, ids, context=None)
        _logger.info('!!!!!hhhh343434****'+str(ids))
        return True    
    #def write(self,cr, uid, ids, vals, context=None):
    #    _logger.info('!!!!!hhhh343434****'+str(ids))
    #    super(account.invoice, self).write(cr, uid, ids, vals, context=context)            
    #    return True    
    
facturas_doc()

