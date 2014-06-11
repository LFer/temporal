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
        sql = ""
        for id in ids:
            cr.execute("SELECT gasto_id FROM facturas_doc_rel_lineas WHERE invoice_id = %s",(id,))
            for result in cr.fetchall():    
                sql +=" UPDATE conceptosdocumentos SET facturado = False WHERE id = "+str(result[0])+";"                
                sql +="DELETE FROM facturas_doc_rel_lineas where gasto_id = "+str(result[0])+";"            
        if sql != "":            
            cr.execute(sql)
        return super(invoice, self).unlink(cr, uid, ids, context=None)
        
invoice()



