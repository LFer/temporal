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

from openerp.report import report_sxw
import os
import logging
from lxml import etree

_logger = logging.getLogger(__name__)

class parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(parser, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'eval_self' : self._eval_self
        })
    def _eval_self(self, cr, uid, ids, name, args, context=None):
        pass

path = os.path.abspath(__file__)			# Obtengo la dir absoluta de este script
dir_path = os.path.dirname(path) 			#Obtengo el directorio

dir_list = dir_path.split('/')

try:
	xml_tree = etree.parse(os.path.join(dir_path,'report_print_report.xml'))
	root=xml_tree.getroot()
	assert root.tag=='openerp', 'XML malformado'
except:
	_logger.info('XML malformando, recreando report_print_report.xml')
	root = etree.fromstring('<openerp><data/></openerp>')
	xml_tree = root.getroottree()

report_nodes ={}
for child in root.iter():
	_logger.info(('nodes',child.tag))
_logger.info(('xml_text',etree.tostring(root, pretty_print=True)))

_logger.info("acaaadsdffg")
for child in root.iter(tag='report'):
	_logger.info(('Atrrib',child.attrib['file']))
	report_nodes[child.attrib['file']] = child

data = root.find('data')
if data is None:
	oe=root.find('openerp')
	data=etree.SubElement(oe,'data')


if ('addons' in dir_list):
	dir_list =dir_list[dir_list.index('addons')+1:]
	for template in [ x for x in os.listdir(dir_path) if x[-4:] in ['.odt','.sxw','.rml']]: # archivos que generan reportes
		rpt_path = os.sep.join(dir_list)+os.sep+template
		_logger.info(('rpt_path',rpt_path))
		rpt_basemodel = dir_list[0]
		rpt_name = '.'.join(['report',rpt_basemodel,template[:-4].replace(' ','_')])
		rpt_id = '_'.join([rpt_basemodel,template[:-4]]).replace(' ','_')
		# report_sxw.report_sxw(
			# rpt_name,
			# rpt_basemodel,
			# rpt_path,
			# parser=parser,
			# header=False
		# )
		if rpt_path in report_nodes:
			report_node= report_nodes[rpt_path]
		else:
			report_node=etree.SubElement(data,'report')

		a = report_node.attrib
		a['auto']="True"
		a['id']= rpt_id
		a['model']=rpt_basemodel
		a['name']='.'.join([rpt_basemodel,template[:-4].replace(' ','_')])
		a['string']=template[:-4]
		a['usage']="default"
		a['report_type']=template[-3:]
		a['file']=rpt_path
		a['menu']="True"
        a['header']="False"

	xml_tree.write(os.path.join(dir_path,'report_print_report.xml'),pretty_print=True, encoding="UTF-8")
else:
	_logger.error("No hay addons!!!")

        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
