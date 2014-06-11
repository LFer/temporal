# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import logging
from osv import osv
from osv import fields

_logger = logging.getLogger(__name__)

class invoice(osv.osv):
    _name = "account.invoice"
    _inherit = "account.invoice"
    
    def unlink(self, cr, uid, ids, context=None):
        _logger.info('!!!!!ayyyyyyyyyyyy****')
        sql = ""
        for id in ids:
            fac_ids = self.pool.get('facturas.carpeta.rel').search(cr, uid, [('account_id','=',id)])
            facs = self.pool.get('facturas.carpeta.rel').read(cr, uid, fac_ids)
            for f in facs:                
                sql +=" UPDATE conceptocarpetas SET facturado = False WHERE id_concepto = "+str(f['id'])+";"
        if sql != "":
            _logger.info('!!!!!ayyyyyyyyyyyy****sql:'+sql)
            cr.execute(sql)
        return super(invoice, self).unlink(cr, uid, ids, context=None)
        
invoice()



