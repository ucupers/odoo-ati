from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
import pyodbc

SQLCONN='Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+\
                              'Server=10.0.0.12;'+\
                              'Database=NAV (9-0) ATI LIVE;'+\
                              'UID=Atidev;pwd=Ati1234;'    

class sis_wh2_mapping(models.Model):
    _name='sis.wh2.mapping'
    _rec_name='description'
        
    bin=fields.Char(string='Bin')
    entry_no = fields.Integer(string='Entry No')
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    item_no =fields.Char(string="Item No") 
    variant =fields.Char(size=50,string="Variant")    
    lot_no =fields.Char(string="Lot No")
    proddate=fields.Char(size=10,string="Lot.Date") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(string="Document No")
    description =fields.Char(string="Description",store=True)
    location_code =fields.Char(string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    uom=fields.Char(string="UoM")

    def open_wh2_history(self):
        return {
            'name': self.item_no + ' : ' + self.description,
            'res_model': 'sis.wh2.history',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_wh2.sis_wh2_history_tree').id,
            'target': 'current',
            'nodestroy':True,
            'domain':"[('header_id','=',"+str(self.id)+")]"
        }

    def update_ILE_wh2(self):
        self.env.cr.execute(' drop table if exists sis_temp_ile_rawpkg ')
        self.env.cr.execute(" create table sis_temp_ile_rawpkg as select *,substring(lot_no from '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]') as proddate "+\
                            " from sis_ile_raw where location_code like 'ATI_-WH2'")        

        self.env.cr.execute(' drop table if exists sis_temp_shipment_checking')
        self.env.cr.execute(" create table sis_temp_shipment_checking as select * "+\
                            " from sis_shipment_checking where plno like 'ATI_-WH2%'")        

        #update existing records that has different qty
        self.env.cr.execute('select ile.id,ile.remaining_quantity,ile.lot_no from sis_temp_ile_rawpkg ile inner join sis_wh2_mapping ssm '+\
                            'on ile.id=ssm.entry_no')
        recs=self.env.cr.fetchall()
        for rec in recs:
            (idd,remqty,lotno)=rec
            ssm=self.env['sis.wh2.mapping'].search([('entry_no','=',idd)])
            for s in ssm:
                vals={}
                if s.remaining_quantity!=remqty:
                    vals.update({'remaining_quantity':remqty})
                    if remqty==0:
                        vals.update({'out':True})
                if s.lot_no!=lotno:
                    vals.update({'lot_no':lotno})
                if len(vals)>0:
                    s.write(vals)


        #insert new records 
        self.env.cr.execute("select id,item_no,description,posting_date, document_no,location_code,quantity,remaining_quantity,uom,lot_no,proddate,variant "+\
                            "from sis_temp_ile_rawpkg ile where remaining_quantity>0 and id not in (select entry_no from sis_wh2_mapping ssm where entry_no is not NULL) --and lot_no<>'' ")
        recs=self.env.cr.fetchall()
        for rec in recs:
            (idd,itemno,description,postingdate,docno,loccode,qty,remqty,uom,lotno,proddate,variant)=rec
            vals={'entry_no':idd,
                    'item_no':itemno,
                    'description':description,
                    'posting_date':postingdate,
                    'document_no':docno,
                    'location_code':loccode,
                    'quantity':qty,
                    'remaining_quantity':remqty,
                    'uom':uom,
                    'variant':variant,
                    'lot_no':lotno,
                    'proddate':proddate
                    }
            self.env['sis.wh2.mapping'].create(vals)
            
        recs=self.env['sis.wh2.consumpt'].search([('ileno','=',None)])
        for rec in recs:
            if rec.document_no==False:
                continue
            self.env.cr.execute(" select distinct plno, finished, error "+\
                        " from sis_temp_shipment_checking where plno ='"+rec.document_no[3:]+"' and (finished or error<>'')")
            scs=self.env.cr.fetchall()
            if len(scs)==0:
                continue
            for sc in scs:
                (plno,finished,error)=sc
            vals={}
            if len(error)>0 and rec.error!=error:
                vals={'status':'error',
                      'error':error
                    }
                rec.write(vals)
            if finished :
                rec.status='created'
                self.env.cr.execute("select id from sis_temp_ile_rawpkg where extdocno like '%"+plno+"%' ")
                ps=self.env.cr.fetchall()
                for p in ps:
                    (idd,)=p
                    rec.ileno=idd

        
        self.env.cr.execute("delete from sis_local_released_production_order")
        self.env.cr.execute("insert into sis_local_released_production_order (id,no,item_no,description,bg, dept,startingdate,endingdate,endproductiondate,duedate,location,display) "+\
                            "select id,no,item_no,description,bg, dept,startingdate,endingdate,endproductiondate,duedate,location,no||' : '||location||' : '||duedate||' : '||description from sis_released_production_order")

        self.env.cr.execute("delete from sis_local_released_production_order_component")
        self.env.cr.execute("insert into sis_local_released_production_order_component (id,no,lineno,item_no,variant,description,uom,location,bg,dept) "+\
                            "select id,no,lineno,item_no,variant,description,uom,location,bg,dept from sis_released_production_order_component")

    @api.multi
    def write(self, vals):
        for s in self:
            valshist={'header_id':s.id,
                  'remaining_quantity':s.remaining_quantity,
                  'bin':s.bin
                }
            self.env['sis.wh2.history'].create(valshist)
        return models.Model.write(self, vals)
    
    @api.multi
    def unlink(self):
        raise UserError('Cannot delete data !')
        return models.Model.unlink(self)
    
    @api.one
    @api.constrains('bin')
    def _constrain_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.wh2.bin'].search([('code','=',self.bin)])
            if len(r)==0:
                raise UserError ('Bin does not exist !')
            if len(r)>1:
                raise UserError ('Multiple Bin !')
#             if r.location!=self.location_code:
#                 raise UserError ('Wrong location ATI1/ATI2!')                
    
    @api.one
    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.wh2.bin'].search([('code','=',self.bin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Bin Error !')

    def opname(self):
        recs=self.env['sis.wh2.mapping'].browse(self._context['active_ids'])
        for rec in recs:
            vals={'bin':'OPNAME'}
            rec.env['sis.wh2.mapping'].write(vals)
    
class sis_wh2_history(models.Model):
    _name='sis.wh2.history'
        
    header_id=fields.Many2one('sis.wh2.mapping',string='header')
    bin=fields.Char(string='Bin')
    remaining_quantity =fields.Float(string="Remaining Quantity")

class sis_wh2_mapping_scan(models.TransientModel):
    _name='sis.wh2.mapping.scan'
    _rec_name='description'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin',required=True)
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    description =fields.Char(compute='_compute_description',string="Description",store=True)

    @api.one
    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.wh2.bin'].search([('code','=',self.bin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Bin Error !')

    @api.one
    @api.depends('ile')
    def _compute_description(self):
        if self.ile!=None and self.ile!=False:
            if self.ile[len(self.ile)-1]=="\n":
                self.ile=self.ile[:len(self.ile)-1]
            ile=self.env['sis.wh2.mapping'].search([('lot_no','=',self.ile),('remaining_quantity','>',0)])
            if len(ile)==1:
                self.description=ile.description
            else:
                if len(ile)>1:
                    raise UserError('Multiple lot found!')
                else:
                    raise UserError('Lot not found!')
    
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        ile=self.env['sis.wh2.mapping'].search([('lot_no','=',vals['ile'])])
        if len(ile)==0:
            raise UserError ('Lot no does not exist!')
        if len(ile)>1:
            raise UserError ('Double lot no!')
        bin1=self.env['sis.wh2.bin'].search([('code','=',vals['bin'])])
        if len(bin1)==0:
            raise UserError ('Bin not found!')
        if len(bin1)>1:
            raise UserError ('Double bin!')
        ile.write({'bin':vals['bin']})
        return models.Model.create(self, vals)

                
                
class sis_wh2_bin(models.Model):
    _name='sis.wh2.bin'
    _rec_name='code'
        
    location_id=fields.Many2one('sis.locations',string='Location ID',required=True)
    location=fields.Char(compute='_compute_location',string='Location', required=True)
    code=fields.Char(size=20,string="Code",required=True)
    name=fields.Char(size=200,string="Name")
    
    @api.constrains('code')
    def code_unique(self):
        if self.env['sis.wh2.bin'].search_count([('code','=',self.code),('id','!=',self.id)])>0:
            raise UserError('Duplicate bin code !')
        
    @api.one
    @api.depends('location_id')
    def _compute_location(self):
        if len(self.location_id)==1:
            self.location=self.location_id.code                
            
            
class sis_wh2_consumpt_scan(models.TransientModel):
    _name='sis.wh2.consumpt.scan'
    _rec_name='description'
        
    ile=fields.Char(string='Lot No',required=True)
    description =fields.Char(compute='_compute_description',string="Description",store=True)
    bin=fields.Char(string='Bin')
    qty=fields.Float(string="Qty",required=True) 
    uom=fields.Char(string='UoM')
    location=fields.Char(string='Location')    

    @api.one
    @api.depends('ile')
    def _compute_description(self):
        if self.ile!=None and self.ile!=False:
            if self.ile[len(self.ile)-1]=="\n":
                self.ile=self.ile[:len(self.ile)-1]
            iles=self.env['sis.wh2.mapping'].search([('lot_no','=',self.ile),('remaining_quantity','>',0)])
            for ile in iles:
                continue            
            if len(iles)>0:
                self.description=ile.description
                self.bin=ile.bin
                self.uom=ile.uom
                self.location=ile.location_code
            else:
                if len(iles)==0:
#                     raise UserError('Multiple lot found!')
#                 else:
                    raise UserError('Lot not found!')
    
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if 'qty' not in vals:
            raise UserError('Mohon Isi Qty !!')
        
        iles=self.env['sis.wh2.mapping'].search([('lot_no','=',vals['ile']),('remaining_quantity','>',0)],order='entry_no')
        if len(iles)==0:
            raise UserError ('Lot no does not exist!')
#         if len(ile)>1:
#             raise UserError ('Double lot no!')
        for ile in iles:
            continue

        postingdate=datetime.now().strftime("%Y-%m-%d")
        no='IS/'+ile.location_code+'/'+postingdate[2:4]+postingdate[5:7]+'/'
        rec=self.env['sis.wh2.consumpt'].search([('document_no','ilike',no)],limit=1,order='document_no desc')
        if len(rec)==0:
            seq='0001'
        else:
            seq=str(int(rec['document_no'][-4:])+1).zfill(4)
        no+=seq        


        valsconsumpt={
            'ile':ile.lot_no,
            'entry_no':ile.entry_no,
            'bin_no':ile.bin,
            'item_no':ile.item_no,
            'variant':ile.variant,
            'document_no':no,
            'description':ile.description,
            'location_code':ile.location_code,
            'quantity':vals['qty'],
            'uom':ile.uom,
            'proddate':ile.proddate
            }
        self.env['sis.wh2.consumpt'].create(valsconsumpt)
        return models.Model.create(self, vals)

class sis_wh2_consumpt(models.Model):
    _name='sis.wh2.consumpt'
    _order='id desc'     

    rpo=fields.Many2one('sis.local.released.production.order',string='Input Prod.Order')
    releasedpo=fields.Char(string='Production Order',compute="_onchange_rpo",store=True)
    lineno =fields.Char(string="Comp.Line No",compute="_onchange_rpo",store=True) 
    poitem_no=fields.Char(string='Prod.Item No',compute="_onchange_rpo",store=True)
    podescription =fields.Char(string="Prod.Description",compute="_onchange_rpo",store=True) 
    poduedate=fields.Date(string='Prod.Due Date',compute="_onchange_rpo",store=True)

            
    ile=fields.Char(string='Lot No')
    entry_no = fields.Integer(string='Entry No')
    bin_no =fields.Char(string="Bin") 
    item_no =fields.Char(string="Item No") 
    variant =fields.Char(string="Variant")    
    document_no =fields.Char(string="Document No")
    description =fields.Char(string="Description")
    location_code=fields.Char(string="Location")    
    quantity =fields.Float(string="Quantity", required=True)
    uom=fields.Char(string="UoM")
    proddate=fields.Char(size=10,string="Lot.Date") 
    status = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('nav','NAV'),('error','Error'),('created','Created'),('canceled','Canceled')],default='draft',string="Status",required=True)
    ileno=fields.Integer(string="ILE Entry No")         
    batchno=fields.Char(string="Batch No",compute="_onchange_rpo",store=True)    
    error=fields.Char(string="Error")    
    
    @api.multi
    def copy_row(self):
        for s in self:
            if s.status =='draft':

                if s.location_code:
                    location_code=s.location_code
                else:
                    iles=self.env['sis.wh2.mapping'].search([('lot_no','=',s.ile),('remaining_quantity','>',0)],order='entry_no')
                    if len(iles)==0:
                        raise UserError ('Lot no does not exist!')
                    for ile in iles:
                        continue
                    location_code=ile.location_code
                
                postingdate=datetime.now().strftime("%Y-%m-%d")
                no='IS/'+location_code+'/'+postingdate[2:4]+postingdate[5:7]+'/'
                rec=self.env['sis.wh2.consumpt'].search([('document_no','ilike',no)],limit=1,order='document_no desc')
                if len(rec)==0:
                    seq='0001'
                else:
                    seq=str(int(rec['document_no'][-4:])+1).zfill(4)
                no+=seq   
                
                vals={
                    'ile':s.ile,
                    'entry_no':s.entry_no,
                    'bin_no':s.bin_no,
                    'item_no':s.item_no,
                    'variant':s.variant,
                    'document_no':no,
                    'description':s.description,
                    'quantity':0,
                    'uom':s.uom,
                    'proddate':s.proddate
                    }
                
                if s.location_code:
                    vals.update({'location_code':location_code})
                
                self.env['sis.wh2.consumpt'].create(vals)
            else:
                raise UserError('To copy, status must be DRAFT !')
    
    @api.multi
    def write(self, vals):
        for s in self:
            if 'status' in vals:
                if vals['status'] not in ['confirmed','nav','error','created']:
                    raise UserError('Can edit when status = draft')
            else:
                if 'ileno' not in vals and 'error' not in vals:
                    if s.status!='draft':
                        raise UserError('Can edit when status = draft')
        return models.Model.write(self, vals)
    
    @api.multi
    def unlink(self):
        for s in self:
            if s.status!='draft':
                raise UserError('Can delete when status = draft')
        return models.Model.unlink(self)    
    
    @api.depends('rpo')
    def _onchange_rpo(self):
        if len(self.rpo)>0:
            self.releasedpo=self.rpo.no
            self.poitem_no=self.rpo.item_no
            self.podescription=self.rpo.description
            self.poduedate=self.rpo.duedate                       
            if self.batchno==False:
                self.batchno=self.env.user.batchno
            rec=self.env['sis.local.released.production.order.component'].search([('no','=',self.releasedpo),('item_no','=',self.item_no),('variant','=',self.variant)])
            if len(rec)==1:
                self.lineno=rec.lineno
            else:
                if len(rec)==0:
                    raise UserError('No '+self.item_no+'/'+self.variant+':'+self.description+' in '+self.releasedpo)
                if len(rec)>1:
                    raise UserError(self.item_no+'/'+self.variant+':'+self.description+' in '+self.releasedpo+' more than one')
            

    @api.constrains('releasedpo','item_no')
    def _constrains_rpo_itemno(self):
        if self.releasedpo and self.item_no:
            rec=self.env['sis.local.released.production.order.component'].search_count([('no','=',self.releasedpo),('item_no','=',self.item_no),('variant','=',self.variant)])
            if rec==0:
                raise UserError('No '+self.item_no+'/'+self.variant+':'+self.description+' in '+self.releasedpo)
            if rec>1:
                raise UserError(self.item_no+'/'+self.variant+':'+self.description+' in '+self.releasedpo+' more than one')

    @api.constrains('releasedpo','item_no','status')
    def _constrains_rpo_itemno_status(self):
        if self.status=='confirmed':
            if not self.releasedpo or not self.item_no or self.quantity<=0:
                raise UserError('When confirmed, RPO and Item must be filled and Qty must > 0')

    def open_error(self):
        return {
            'name': self.error,
            'res_model': 'sis.wh2.consumpt',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sis_wh2.sis_wh2_consumpt_error_form').id,
            'target': 'new',
            'nodestroy':True,
            'domain':"[('id','=',"+str(self.id)+")]"
        }

 
    def confirm(self):
        recs=self.env['sis.wh2.consumpt'].browse(self._context['active_ids'])
        for rec in recs:
            if rec.status=='draft':
                rec.status='confirmed'
 
    def update_status_from_NAV(self):
    #def upload_to_NAV(self):
        no=0
        recs=self.env['sis.wh2.consumpt'].search([('status','=','confirmed')],order='document_no')
        if len(recs)>0:
            conn = pyodbc.connect(SQLCONN)
            cursor = conn.cursor()
            plno='first'
        wasrec=False
        for rec in recs:
            if plno!=rec.document_no and plno!='first':            
                wasrec.status='nav'

            variant=rec.variant
            if rec.variant==None:
                variant=""
            try:
                docno= rec.document_no[3:]
                row=cursor.execute(" INSERT INTO [PT_ Aneka Tuna Indonesia$Shipment Checking]([Document Type],[Order No_],"+\
                                   " [Item Ledger Entry No_],[Container No_],[Line No_],[Component Line No_],[Variant Code]"+\
                                   ",[Item No_],[Quantity],[isGet],[Error],[Whs_ Shipment No_],[is Error],[PL No_],[Finished]"+\
                                   ",[Journal Batch Name],[Remaining Qty_],[Finished Qty]) "+\
                                   " VALUES(1,'"+rec.releasedpo+"',"+\
                                   str(rec.entry_no)+",'',10000,"+rec.lineno+",'"+variant+"','"+\
                                   rec.item_no+"',"+str(rec.quantity)+",0,'','',0,'"+docno+"',0,'"+rec.batchno+"',0,0)")
            except Exception as e:
                raise UserError(e)
                
            if row.rowcount==0:
                rec.error='Failed to update NAV, please try again later'
            else:                
                no+=1
            wasrec=rec
            plno=rec.document_no            
        if no>0:
            conn.commit()           
            wasrec.status='nav'   


             
class res_users(models.Model):
    _name='res.users'
    _inherit='res.users'
     
    batchno=fields.Char(string='Batch No')
