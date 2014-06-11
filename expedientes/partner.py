# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
from osv import osv
from osv import fields
import logging
_logger = logging.getLogger(__name__)

class res_partner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    def get_total_facturado(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.gastos_ids:        
                if recordConc.facturado:
                    total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res  
        
    def get_total_sin_facturar(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.gastos_ids:        
                if not recordConc.facturado:
                    total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res 
        
    def get_total(self, cr, uid, ids, name, arg, context=None):
        res = {}
        total = 0
        your_class_records = self.browse(cr, uid, ids)                
        for record in your_class_records:
            for recordConc in record.gastos_ids:        
                total += recordConc.cantidad * recordConc.preciounidad
            res[record.id] = total
        return res
    
    def action_nueva_factura_gastos_cli(self, cr, uid, ids, *args):        
        if not isinstance(ids,list):
            ids=[ids]
        invoice_ids = []
        sql = ""        
        varfacturar = False  
        account=""        
        partners = self.browse(cr, uid, ids) 
        for recordCli in partners:
            
            # for recordConc in record.gastos_ids:
                # if recordConc.facturar == True:
                    # if recordConc.facturado == False:
                        # varfacturar = True
                       #sql += " UPDATE conceptosdocumentos SET facturado = True WHERE id = "+str(recordConc.id)+";"   

                        
            condocs = self.pool.get('conceptosdocumentos')
            afacturar= condocs.search(cr, uid, [('partner_id','=',recordCli.id),('facturar','=',True),('facturado','=',False)])                                    
            if afacturar:
                type = 'form' if len(ids)==1 else 'tree'
                #partners_a_facturar={ partner.id:[concepto for concepto in partner.gastos_ids if (concepto.facturar and not concepto.facturado)] 
                #    for partner in partners if any([ (concepto.facturar and not concepto.facturado) for concepto in partner.gastos_ids])}
                #for (cli,record) in partners_a_facturar.iteritems():
                record= [concepto for concepto in recordCli.gastos_ids if (concepto.facturar and not concepto.facturado)]
                account = recordCli.property_account_payable.id
                if account != "":
                    # search_domain = [('name', '=', 'property_account_payable')]
                    # search_domain = []
                    # valor = "res.partner,"+str(cli)

                    # obj = self.pool.get('ir.property')
                    # ids = obj.search(cr, uid, search_domain+[('res_id', '=', valor)])
                    # res = obj.read(cr, uid, ids, ['value_reference'], context=None)
                    # account = res[0]['value_reference'].split(',')[1] 		if len(res)!=0 else False
                    #conceptos = [concepto for concepto in record.gastos_ids if (concepto.facturar and not concepto.facturado)]
                    fecha_factura = max(map(lambda x:x.fecha, record))
                    
                    journal_ids = self.pool.get('account.journal').search(cr, uid,[('type', '=', 'sale'), 
                        ('company_id', '=', 1)],
                        limit=1)                                        
                    if not journal_ids:
                        raise osv.except_osv(_('Error!'),('Debe ingresar un Diario de Venta.'))  
                    company = recordCli.company_id.id
                    moneda = recordCli.property_account_payable.currency_id
                    if not moneda:
                        moneda = recordCli.company_id.currency_id
                        if not moneda:
                            raise osv.except_osv(_('Error!'),('La compañía no tiene moneda.'))  
                    
                    lines = [(0,0,{
                            'name' : r.name,
                            'product_id' : r.product_id.id,
                            'price_unit' : r.preciounidad,
                            'quantity' : r.cantidad,
                            'invoice_line_tax_id': ([(6,0,[r.iva.id])] if r.iva else None)
                            }) 
                                for r in record]  
                                    
                    invoice_id = self.pool.get('account.invoice').create(cr, uid,{
                        'name' : 'Factura',
                        'date_invoice' : fecha_factura,
                        'account_id' : account,
                        'invoice_line': lines,
                        'currency_id' : moneda.id,
                        'partner_id' : recordCli.id,
                        'journal_id' : journal_ids[0],
                        'company_id' : company,
                        'origin' : 'Factura',
                    })                              
                            
                    invoice_ids.append(invoice_id)
                    
                    condocs.write(cr,uid,afacturar,{'facturado':True})                    
                    
                    for r in record:
                        cr.execute("INSERT INTO facturas_doc_rel_lineas (gasto_id,invoice_id) VALUES (%s,%s)",(r.id,invoice_id,))
                        
                    mod_obj = self.pool.get('ir.model.data')
                    
                    
                    if len(invoice_ids) == 0:
                        return True
                    elif len(invoice_ids) > 1:
                        # res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_tree')
                        # return {
                            # 'name': 'Provide your popup window name',
                            # 'view_type': 'tree',
                            # 'view_mode': 'tree',
                            # 'view_id': [res and res[1] or False],
                            # 'res_id': invoice_ids,
                            # 'res_model': 'account.invoice',
                            # 'type': 'ir.actions.act_window',
                            # 'nodestroy': True,
                            # 'target': 'new',
                        # } 
                        return True                        
                    else:
                        res = mod_obj.get_object_reference(cr, uid, 'account', 'invoice_form')
                        return {                            
                            'name': 'Factura de gastos',
                            'view_type': 'form',
                            'view_mode': 'form',
                            'view_id': [res and res[1] or False],
                            'res_id': invoice_ids[0],
                            'res_model': 'account.invoice',
                            'type': 'ir.actions.act_window',
                            'nodestroy': True,
                            'target': 'new',
                        }                        
        return True    
    
    _columns = {
        'expp_ids': fields.one2many('participantes.expediente', 'partner_id','Propios', domain=[('tipo','=',1)]),       
        'expc_ids': fields.one2many('participantes.expediente', 'partner_id','Contrarios', domain=[('tipo','=',2)]),       
        'expco_ids': fields.one2many('participantes.expediente', 'partner_id','Comunes', domain=[('tipo','=',3)]),
        'gastos_ids':  fields.one2many('conceptosdocumentos', 'partner_id','Gastos asociados'),
        'invoice_ids':  fields.one2many('account.invoice', 'partner_id','Facturas'),      
        'totalgral': fields.function(get_total, type='float',method=True, string='Total'),         
        'totalfacturado': fields.function(get_total_facturado, type='float',method=True, string='Total facturado'),         
        'totalsinfacturar': fields.function(get_total_sin_facturar, type='float',method=True, string='Saldo no facturado'),         
        
    }
    

    def unlink(self, cr, uid, ids, context=None):

        for id in ids:
           cr.execute("""  DELETE FROM document_directory where parent_id = %s """,
                (id,))                  
           cr.execute("""  DELETE FROM document_directory where res_id = %s """,
                (id,))                  
        return super(res_partner, self).unlink(cr, uid, ids, context=None)        
    
res_partner()
