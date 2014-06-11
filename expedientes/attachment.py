# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import datetime
import time
import hashlib
import itertools
import os
import re

from openerp import tools
from osv import osv
from osv import fields

import logging
_logger = logging.getLogger(__name__)

TIPO_DOCUMENTO = [
    ('ci', 'Cédula de identidad'),
    ('credencial', 'Credencial'),
]

class ir_attachment(osv.osv):
    _name = "ir.attachment"
    _inherit = "ir.attachment"
    _order = "name"

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

    def create(self, cr, uid, values, context=None):
        self.check(cr, uid, [], mode='create', context=context, values=values)
        if 'file_size' in values:
            del values['file_size']
        attach_id = super(ir_attachment, self).create(cr, uid, values, context) 
        cr.execute("""  select res_id,name,res_model from ir_attachment where id = %s """,
                (attach_id,))       
        record = cr.dictfetchone()
        if record:
            #Si el directorio del expdiente o cliente creado ya está
            cr.execute("""  select id from document_directory where res_id = %s  AND type = 'directory'""",
                     (record['res_id'],)) 
            res = cr.dictfetchone()
            if res: 
                #Le agrega el attachment al expdiente o cliente
                cr.execute('UPDATE ir_attachment SET parent_id ='+str(res['id'])+' where id=%s', (attach_id,))
                #Si no hay un directorio Archivos adjuntos hijo del expediente o cliente lo crea
                cr.execute("""  select id from document_directory where name = 'Archivos adjuntos' and parent_id =%s """,
                    (res['id'],))                                      
                resDir = cr.dictfetchone()
                if not resDir:
                    docArxh_id = self.pool.get('document.directory').create(cr, uid,{
                        'resource_find_all' : True,
                        'ressource_tree' : False,
                        'user_id' : uid,
                        'name' : 'Archivos adjuntos',
                        'parent_id' : res['id'],
                        'type' : 'directory',
                        #'res_id':recordCli.id,
                    })
                else:                
                    docArxh_id = resDir['id']                
                
                #Se cuelga del directorio Archivos adjuntos    
                cr.execute("""  select id from document_directory where res_id = %s AND type = 'directory'""",
                    (record['res_id'],))           
                res = cr.dictfetchone()
                if res:
                    doc_id = self.pool.get('document.directory').create(cr, uid,{
                        'resource_find_all' : True,
                        'ressource_tree' : False,
                        'user_id' : uid,
                        'name' : record['name'],
                        'parent_id' : docArxh_id,
                        'type' : 'directory',
                        'res_id':attach_id,
                        'res_model':record['res_model'],
                    })                
        return attach_id         
        
    def unlink(self, cr, uid, ids, context=None):
        for id in ids:
            parent_id = None
            #Saco el padre del adjunto
            cr.execute("""  select parent_id from document_directory where res_id = %s""",
                    (id,))  
            res = cr.dictfetchone()
            if res:   
                parent_id = res['parent_id']  
            #Borro el adjunto de la tabla
            cr.execute("""  DELETE FROM document_directory where res_id = %s """,
                (id,))  
            #Si no hay mas adjuntos borro el directorio Archivos adjuntos
            cr.execute("""  select id from document_directory where parent_id = %s""",
                    (parent_id,))  
            reg = cr.dictfetchone()
            if not reg:
                #Borro el directorio
                cr.execute("""  DELETE FROM document_directory where id = %s """,
                    (parent_id,))            
       
        self.check(cr, uid, ids, 'unlink', context=context)
        location = self.pool.get('ir.config_parameter').get_param(cr, uid, 'ir_attachment.location')
        if location:
            for attach in self.browse(cr, uid, ids, context=context):
                if attach.store_fname:
                    self._file_delete(cr, uid, location, attach.store_fname)
        return super(ir_attachment, self).unlink(cr, uid, ids, context)


        
    _columns = {
        'tipodocumento': fields.selection(TIPO_DOCUMENTO, 'Tipo documento', size=16),
        'copia_attach_id': fields.integer('Attach copia de', readonly=True),
    }

ir_attachment()



