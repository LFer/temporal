# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import hashlib
import itertools
import os
import re

from openerp import tools
from osv import osv
from osv import fields

import logging
_logger = logging.getLogger(__name__)


class ir_attachment(osv.osv):

    _name = "ir.attachment"
    _inherit = "ir.attachment"


    def upload_create(self, cr, uid, values, context=None):
        self.check(cr, uid, [], mode='create', context=context, values=values)
        if 'file_size' in values:
            del values['file_size']

        try:
            value = values['db_datas']
            # We dont handle setting data to null
            if not value:
                return True
            if context is None:
                context = {}

            location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
            file_size = len(value.decode('base64'))
            if location:
                attach = self.browse(cr, uid, id, context=context)
                if attach.store_fname:
                    self._file_delete(cr, uid, location, attach.store_fname)
                fname = self._file_write(cr, uid, location, value)   
        except: 
            pass
    
        salida = super(ir_attachment, self).create(cr, uid, values, context)
        cr.execute('UPDATE ir_attachment SET db_datas = null WHERE id = ' + str(salida))

        return salida
        
    def _file_read(self, cr, uid, location, fname, bin_size=False):

        full_path = self._full_path(cr, uid, location, fname)
        r = ''
        try:
            if bin_size:
                r = os.path.getsize(full_path)
            else:
                r = open(full_path).read().encode('base64')
        except IOError:
            _logger.error("_read_file reading %s",full_path)
        return r


    def _data_get(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        result = {}
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        bin_size = context.get('bin_size')
        for attach in self.browse(cr, uid, ids, context=context):
            if location and attach.store_fname:
                result[attach.id] = self._file_read(cr, uid, location, attach.store_fname, bin_size)
            else:
                result[attach.id] = attach.db_datas
        return result        

                        
    _columns = {

        'web': fields.boolean('Web'),
        'email': fields.boolean('EMail'),
        'satelital': fields.boolean('Satelital'),
        'sequence': fields.integer('Secuencia'),
        'mapa': fields.boolean('Mapa'),
        #'image': fields.function(_data_get, string='File Content', type="binary", nodrop=True),
        #'fullPath': fields.function(_full_path, string='File path', type="char"),

    }

    _order = "sequence"

ir_attachment()



