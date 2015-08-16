# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

from osv import osv
from osv import fields
from operator import itemgetter
import logging
_logger = logging.getLogger(__name__)

class res_partner(osv.osv):

    def get_emails(self, cr, uid, ids, name, arg, context=None):
        result = {}
        for id in ids:
            cr.execute("""  select m.id from res_partner r
                    inner join mail_message_res_partner_rel mr on mr.res_partner_id = r.id
                    inner join mail_message m on m.id = mr.mail_message_id
                    where r.id = %s""",
                        (id,))

            res_ids = map(itemgetter(0), cr.fetchall())
            result[id] = self.pool.get('mail.message').search(cr, uid, [('subtype_id','=',1),('model','=','estate'), ('id','in',res_ids)])
        return result

    _name = "res.partner"
    _inherit = "res.partner"
    _columns = {
        #'ci': fields.char('Nro. documento', size=12),
        #'parentSupplier_id': fields.many2one('res.partner', 'Related Supplier'),
        #'supplier_ids': fields.one2many('res.partner', 'parentSupplier_id', 'Suppliers'),

        #'member_ids':fields.many2many('res.users', 'sale_member_rel', 'section_id', 'member_id', 'Team Members'),
        'supplier_ids':fields.many2many('res.partner', 'supplier_rel', 'partner_id', 'supplier_id', 'Suppliers'),

        'estate_ids': fields.one2many('estate', 'partner_id', 'Propiedad'),
        'visit_ids': fields.one2many('visit', 'partner_id', 'Visita'),
        'emails': fields.function(get_emails, string="EMail", relation='mail.message',method=True,type='one2many'),
        'partner_obs':fields.text('Observaciónes'),

    }


res_partner()