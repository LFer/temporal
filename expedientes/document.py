from osv import osv
from osv import fields
import logging
_logger = logging.getLogger(__name__)

class document_directory(osv.osv):
    _name = "document.directory"
    _inherit = "document.directory"
    
    _columns = { 
        'res_id': fields.integer('Resource ID', readonly=True),
        'res_model': fields.char('Resource Model', readonly=True),
    }

    