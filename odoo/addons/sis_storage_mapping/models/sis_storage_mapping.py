from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

    
class sis_storage_mapping(models.Model):
    _name='sis.storage.mapping'
    _rec_name='description'
        
    bin=fields.Char(string='Bin')
    entry_no = fields.Integer(string='Entry No')
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    item_no =fields.Char(string="Item No") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(string="Document No")
    description =fields.Char(compute='_compute_description',string="Description",store=True)
    location_code =fields.Char(string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    uom=fields.Char(string="UoM")
    out=fields.Boolean(string="Out",default=False)        

    def open_history(self):
        return {
            'name': self.item_no + ' : ' + self.description,
            'res_model': 'sis.storage.history',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_storage_mapping.sis_storage_history_tree').id,
            'target': 'new',
            'nodestroy':True,
            'domain':"[('header_id','=',"+str(self.id)+")]"
        }

    def update_ILE_storage(self):
        self.env.cr.execute('drop table if exists sis_temp_ile_rawst')
        self.env.cr.execute("create table sis_temp_ile_rawst as select * from sis_ile_raw where location_code like 'ATI_-STG'")        

        #update existing records that has different qty
        self.env.cr.execute('select ile.id,ile.remaining_quantity from sis_temp_ile_rawst ile inner join sis_storage_mapping ssm '+\
                            'on ile.id=ssm.entry_no')
        recs=self.env.cr.fetchall()
        for rec in recs:
            (idd,remqty)=rec
            ssm=self.env['sis.storage.mapping'].search([('entry_no','=',idd)])
            for s in ssm:
                if s.remaining_quantity!=remqty:
                    vals={'remaining_quantity':remqty}
                    if remqty==0:
                        vals.update({'out':True})
                    s.write(vals)

        #insert new records 
        self.env.cr.execute("select id,item_no,description,posting_date, document_no,location_code,quantity,remaining_quantity,uom "+\
                            "from sis_temp_ile_rawst ile where remaining_quantity>0 and id not in (select entry_no from sis_storage_mapping ssm where entry_no is not NULL)")
        recs=self.env.cr.fetchall()
        for rec in recs:
            (idd,itemno,description,postingdate,docno,loccode,qty,remqty,uom)=rec
            vals={'entry_no':idd,
                    'item_no':itemno,
                    'description':description,
                    'posting_date':postingdate,
                    'document_no':docno,
                    'location_code':loccode,
                    'quantity':qty,
                    'remaining_quantity':remqty,
                    'uom':uom
                    }
            if remqty==0:
                vals.update({'out':True})
            self.env['sis.storage.mapping'].create(vals)

    @api.multi
    def write(self, vals):
        for s in self:
            valshist={'header_id':s.id,
                  'remaining_quantity':s.remaining_quantity,
                  'bin':s.bin
                }
            self.env['sis.storage.history'].create(valshist)
        return models.Model.write(self, vals)
    
    @api.one
    @api.constrains('bin')
    def _constrain_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.storage.bin'].search([('code','=',self.bin)])
            if len(r)==0:
                raise UserError ('Bin does not exist !')
            if len(r)>1:
                raise UserError ('Multiple Bin !')
            if r.location!=self.location_code:
                raise UserError ('Wrong location ATI1/ATI2!')                
    
    @api.one
    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.storage.bin'].search([('code','=',self.bin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Bin Error !')

    def opname(self):
        recs=self.env['sis.storage.mapping'].browse(self._context['active_ids'])
        for rec in recs:
            vals={'bin':'OPNAME'}
            rec.env['sis.storage.mapping'].write(vals)
    
class sis_storage_history(models.Model):
    _name='sis.storage.history'
        
    header_id=fields.Many2one('sis.storage.mapping',string='header')
    bin=fields.Char(string='Bin')
    remaining_quantity =fields.Float(string="Remaining Quantity")
    
class sis_storage_bin(models.Model):
    _name='sis.storage.bin'
    _rec_name='code'
        
    location_id=fields.Many2one('sis.locations',string='Location ID',required=True)
    location=fields.Char(compute='_compute_location',string='Location', required=True)
    code=fields.Char(size=20,string="Code",required=True)
    name=fields.Char(size=200,string="Name")
    
    @api.constrains('code')
    def code_unique(self):
        if self.env['sis.bin'].search_count([('code','=',self.code),('id','!=',self.id)])>0:
            raise UserError('Duplicate bin code !')
        
    @api.one
    @api.depends('location_id')
    def _compute_location(self):
        if len(self.location_id)==1:
            self.location=self.location_id.code    
    