# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-


from osv import osv
from osv import fields

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"
    
    _columns = {
        'ci': fields.char('Nro. documento', size=12),
        #'parentSupplier_id': fields.many2one('res.partner', 'Related Supplier'),
        #'supplier_ids': fields.one2many('res.partner', 'parentSupplier_id', '"Suppliers"'),
        'supplier_id': fields.many2many('res.partner.supplier', id1='partner_id', id2='supplier_id', string='"Suppliers"'),

    }


res_partner()


class res_partner_supplier(osv.osv):


    _description = 'Partner Suppliers'
    _name = 'res.partner.supplier'
    _columns = {
        'parent_id': fields.many2one('res.partner.supplier', 'Parent Supplier', select=True, ondelete='cascade'),
        'partner_ids': fields.many2many('res.partner', id1='supplier_id', id2='partner_id', string='Partners'),
        'active': fields.boolean('Active', help="The active field allows you to hide the category without removing it."),
    }
    _constraints = [
        (osv.osv._check_recursion, 'Error ! You can not create recursive suppliers.', ['parent_id'])
    ]
    _defaults = {
        'active': 1,
    }
    _order = 'partner_ids'

res_partner_supplier()
