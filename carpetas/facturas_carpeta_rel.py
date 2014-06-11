# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields

class facturas_carpeta_rel(osv.osv):
    _name = "facturas.carpeta.rel"
    
    _columns = {
        'id': fields.integer('Carpeta', size=16),
        'account_id': fields.integer('Cta', size=16),
    }
      
    #def write(self,cr, uid, ids, vals, context=None):
    #    _logger.info('!!!!!hhhh343434****'+str(ids))
    #    super(account.invoice, self).write(cr, uid, ids, vals, context=context)            
    #    return True    
    
facturas_carpeta_rel()

