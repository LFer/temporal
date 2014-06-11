# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import logging
import datetime
import time
import openerp.addons.decimal_precision as dp

from osv import osv
from osv import fields

TIPO_PRIORIDAD = [
    ('alta', 'Alta'),
    ('media', 'Media'),
    ('baja', 'Baja'),
]

TIPO_ESTADO = [
    ('planificado', 'Planificado'),
    ('hecho', 'Hecho'),
]


_logger = logging.getLogger(__name__)


class historialdoc(osv.osv):
    _name = "historialdoc"

    _columns = {
        'id_historial': fields.integer('ID', readonly=True),
        'name': fields.char('Descripción', size=256, required=True),
        'fechaalta': fields.date('Fecha alta', select=1, required=True),
        'fechavto': fields.date('Fecha vencimiento', select=1, required=True),
        'duracion': fields.integer('Duración en hs'),
        'prioridad': fields.selection(TIPO_PRIORIDAD, 'Prioridad', size=16),
        'partner_ids': fields.many2many('res.partner','doc_asistentes', id1='id', id2='partner_id', string='Asistentes'),
        'estado': fields.selection(TIPO_ESTADO, 'Estado', size=16),
        'agendar': fields.boolean('Agendar'),
        'notas': fields.text('Notas'),
    }
    
    _defaults = {
        'fechaalta': lambda *a: datetime.date.today().strftime('%Y-%m-%d'),
    }    
   
    # def create(self,cr, uid, ids, context=None):
    #     _logger.info('!!!!!create 7777****')
        #historial = self.pool.get('historialexp').browse(cr, uid, context)
        #_logger.info('!!!!!agendarrrr****'+str(historial.agendar))
        
    #     your_class_records = self.browse(cr, uid, ids)    
    #     for record in your_class_records:
    #         _logger.info('!!!!!create 88888****')
        #    if record.agendar == 'False':
        #        _logger.info('!!!!!biennnn****')

            #self.pool.get('crm.meeting').create(cr, uid,{
            #    'date' : record.fechaalta,
            #    'name' : record.name,
            #    'date_deadline' : record.fechavto,
            #})         
        
        #    _logger.info('!!!!!podridaaaa****'+str(invoice_id))
        
    #     super(historialexp, self).create(cr, uid, ids, context=context)
    #     return True

    def write(self,cr, uid, ids, vals, context=None):   

        #for id in ids:
        #    _logger.info('!!!!!hhhh 6666666****'+str(self.browse(cr,uid,id).duracion))
    
        super(historialdoc, self).write(cr, uid, ids, vals, context=context)    
        your_class_records = self.browse(cr, uid, ids)    
        for record in your_class_records:

            cr.execute("""  delete from crm_meeting where location = '%s'""",
                        (record.id,))             
                
            if record.agendar == True:
                cr.execute("""  insert into crm_meeting (date, name, date_deadline,location,duration,active) values(%s,%s,%s,%s,%s,True)""",
                    (record.fechaalta, record.name, record.fechaalta,record.id,record.duracion,))
                cr.execute("""  select id from crm_meeting where location = '%s'""",
                            (record.id,))                      
                idmeeting = cr.fetchone()[0]                    
                _logger.info('!!!!!yyyyyy****'+str(idmeeting))
                cr.execute(""" SELECT d.partner_id,name,email FROM doc_asistentes d inner join res_partner r on r.id = d.partner_id WHERE d.id = %s """,
                    (record.id,))
                _logger.info('!!!!!zzzzz****'+str(record.id))
                for result in cr.fetchall():                
                    _logger.info('!!!!!xxxxx****'+str(result[0]))
                    _logger.info('!!!!!kkkkk****'+str(result[1]))
                    cr.execute("""  insert into crm_meeting_partner_rel (meeting_id,partner_id) values(%s,%s,%s,%s,%s,True)""",
                        (idmeeting, result[0],)) 
                    #varmeeting = "crm.meeting,"+str(idmeeting)
                    #cr.execute("""  insert into calendar_attendee (cn,partner_id,language,state,role,ref,email,rsvp) values(%s,%s,'%s','%s','%s','%s','%s',True)""",
                    #    (result[1],result[0],"es-UY","needs-action","req-participant",varmeeting,result[2]))                          
                    #cr.execute("""  select id from crm_meeting where location = '%s'""",
                    #        (record.id,))                      
                    #idmeeting = cr.fetchone()[0]                        
                    #cr.execute("""  insert into meeting_attendee_rel (meeting_id,partner_id) values(%s,%s,%s,%s,%s,True)""",
                    #    (idmeeting, result[0],))                        
        return True
    
     
    
    #def create(self, cr, uid, vals, context=None):        
    #    _logger.info('!!!!!222222****')
        #your_class_records = self.browse(cr, uid, ids)                
        #for record in your_class_records:
        #    if context.get('agendar') == 'False':
        #        _logger.info('!!!!!111111111****')
        #    if record.agendar == 'False':
        #        _logger.info('!!!!!222222****')
            #invoice_id = self.pool.get('account.invoice').create(cr, uid,{
            #    'name' : record.name,
            #    'date_invoice' : record.fecha,
            #    'account_id' : 4,
            #    'currency_id' : 1,
            #    'partner_id' : 9,
            #    'journal_id' : 1,
            #    'company_id' : 1,
            #    'origin' : record.name,
            #})         
            #_logger.info('!!!!!podridaaaa****'+str(invoice_id))
    #    return True  
    
historialdoc()



