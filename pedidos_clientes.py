# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import string
import datetime
import time
from lxml import etree
import math
import pytz
import re
from openerp.tools.translate import _
from osv import osv
from osv import fields
from openerp import SUPERUSER_ID
from openerp import pooler, tools
import decimal_precision as dp
import logging
_logger = logging.getLogger(__name__)



class pedidos_clientes(osv.osv):
    _name = "pedidos.clientes"
    _columns = {
        #Cabezal
    	'numero_cliente':fields.char(u'N° Cliente'),
    	'fecha':fields.date('Fecha'),
    	'atendido_por':fields.char('Atendido por'), #TODO cambiar a many2one a res.partner
        'colega':fields.char('Colega'),#TODO cambiar many2one a res.partner
        'nombre':fields.char('Nombre'),
        'tel_particular':fields.char('Particular'),
        'tel_celular':fields.char('Celular'),
        'tel_officina':fields.char('Oficina'),
        'mail':fields.char('Mail'),

        #Direcciones
        'calle':fields.char('Calle'),
        'esquina':fields.char('Esquina'),
        'numero_puerta':fields.char(u'Número de puerta'),
        'ciudad':fields.char('Ciudad'),
        'departamento':fields.many2one("departmento", 'Departamento'),

        #Forma de contacto
        'llamo':fields.boolean('Llamo'),
        'vino_officina':fields.boolean('Vino a Oficina'),
        'por_aviso':fields.boolean('Por Aviso'),
        'cartel':fields.boolean('Cartel'),
        'otros':fields.boolean('Otros'),
        'numero_ficha':fields.char(u'Su contacto fue por N° de ficha'),
        'ficha':fields.char('Ubicada en'),

        #Pedido
        'casa':fields.boolean('Casa'),
        'apartamento':fields.boolean('Apartamento'),
        'local':fields.boolean('Local'),
        'otros2':fields.boolean('Otros'),

        #Tipo de transacion
        'compra':fields.boolean('Compra'),
        'alquiler':fields.boolean('Alquiler'),
        'precio':fields.char('Precio que Busca'),
        'zonas':fields.char('Zonas'),

        #Caracteristicas
        'caracteristicas':fields.text(u'Características')#TODO aca deberian ir las caracteristicas de las propiedades, mientras tanto lo dejo en texto

    }


    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['numero_cliente','nombre'], context=context)
        res = []
        for record in reads:
            res.append((record['id'],unicode(record['numero_cliente']) + u' - ' + str(record['nombre'])))
        return res


pedidos_clientes()
