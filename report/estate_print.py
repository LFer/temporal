# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw
#import report_sxw

class estate(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(estate, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'image_url' : _get_imagepath,
        })
    #print 'aca'

        
report_sxw.report_sxw('report.inmobiliaria.estate.urbana','estate','addons/inmobiliaria/report/estate_urbana.rml',parser=estate,header=True)

report_sxw.report_sxw('report.inmobiliaria.estate.rural','estate','addons/inmobiliaria/report/estate_rural.rml',parser=estate,header=True)

report_sxw.report_sxw('report.inmobiliaria.estate.satelital','estate','addons/inmobiliaria/report/estate_satelital.rml',parser=estate,header=True)

report_sxw.report_sxw('report.inmobiliaria.estate.simple','estate','addons/inmobiliaria/report/estate_simple.rml',parser=estate,header=True)

report_sxw.report_sxw('report.inmobiliaria.estate.terreno','estate','addons/inmobiliaria/report/estate_terreno.rml',parser=estate,header=True)


def _get_imagepath(self, ide):
    attach_ids = self.pool.get('ir.attachment').search(self.cr, self.uid, [('res_model','=','estate'), ('res_id', '=',ide)])
    datas = self.pool.get('ir.attachment').read(self.cr, self.uid, attach_ids)
    return datas[0]['datas']
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
