from odoo import models, fields, api
from odoo.exceptions import UserError
from psycopg2.sql import NULL
from datetime import datetime
from dateutil.relativedelta import relativedelta

class sis_ile_remaining_quantity(models.Model):
    _name='sis.ile.remaining.quantity'
    _table='sis_ile_remaining_quantity'
    _auto=False
    _rec_name='lot_no'

    item_no =fields.Char(size=20,string="Item No",readonly=True) 
    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(size=20,string="Document No",readonly=True)
    description =fields.Char(size=200,string="Description",readonly=True)
    location_code =fields.Char(size=20,string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    lot_no =fields.Char(string="Lot No",readonly=True)
    fish_box_no =fields.Char(size=20,string="Fish Box No",readonly=True)
    vessel_no =fields.Char(size=20,string="Vessel No",readonly=True)
    container_no =fields.Char(size=40,string="Container No",readonly=True)
    voyage_no =fields.Char(size=20,string="Voyage No",readonly=True)
    hatch_no =fields.Char(size=20,string="Hatch No",readonly=True)
    no_basket =fields.Char(size=20,string="No Basket",readonly=True)
    no_contract =fields.Char(size=20,string="No Contract",readonly=True)
    inkjet_print =fields.Char(size=250,string="Inkjet Print",readonly=True)    

class sis_temp_ile_remaining_quantity(models.Model):
    _name='sis.temp.ile.remaining.quantity'

    item_no =fields.Char(size=20,string="Item No") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(size=20,string="Document No")
    description =fields.Char(size=200,string="Description")
    location_code =fields.Char(size=20,string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    lot_no =fields.Char(string="Lot No")
    fish_box_no =fields.Char(size=20,string="Fish Box No")
    vessel_no =fields.Char(size=20,string="Vessel No")
    container_no =fields.Char(size=40,string="Container No")
    voyage_no =fields.Char(size=20,string="Voyage No")
    hatch_no =fields.Char(size=20,string="Hatch No")
    no_basket =fields.Char(size=20,string="No Basket")
    no_contract =fields.Char(size=20,string="No Contract")
    inkjet_print =fields.Char(size=250,string="Inkjet Print")    

    
class sis_goods_bin(models.Model):
    _name='sis.goods.bin'
    _rec_name='description'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin',required=True)
    next_id=fields.Many2one('sis.goods.bin',string='Next')
    entry_no = fields.Integer(string='Entry No')
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    item_no =fields.Char(string="Item No") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(string="Document No")
    description =fields.Char(compute='_compute_description',string="Description",store=True)
    location_code =fields.Char(string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    lot_no =fields.Char(string="Lot No")
    fish_box_no =fields.Char(string="Fish Box No")
    vessel_no =fields.Char(string="Vessel No")
    container_no =fields.Char(string="Container No")
    voyage_no =fields.Char(string="Voyage No")
    hatch_no =fields.Char(string="Hatch No")
    no_basket =fields.Char(string="No Basket")
    no_contract =fields.Char(string="No Contract")
    inkjet_print =fields.Char(string="Inkjet Print")    
    out=fields.Boolean(string="Out",default=False)        
#     inkubasi = fields.Boolean(compute='_compute_inkubasi',string="Inkubasi")

    #@api.one
#     def _compute_inkubasi(self):
#         d=datetime.today()-datetime.strptime(self.posting_date,"%Y-%m-%d")
#         if self.item_no[:2]=='UC' and d.days<14:
#             self.inkubasi = True
#         else:
#             self.inkubasi = False

    def update_outbound(self):
        self.env.cr.execute('delete from sis_temp_ile_remaining_quantity')
        self.env.cr.execute('insert into sis_temp_ile_remaining_quantity select * from sis_ile_remaining_quantity')
                
        rs=self.env['sis.goods.bin'].search([('next_id','=',None),('out','=',False)])
        for r in rs:
            iles=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',r.entry_no)])
            if len(iles)==0:
                r.out=True


    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.bin'].search([('code','=',self.bin)])
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
            ile=self.env['sis.ile.remaining.quantity'].search([('lot_no','like',self.ile)])
            if len(ile)>0:
                self.description=ile.description
            else:
                raise UserError('Lot not found!')
    
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        ile=self.env['sis.ile.remaining.quantity'].search([('lot_no','=',vals['ile'])])
        if len(ile)==0:
            raise UserError ('Lot no does not exist!')
        if len(ile)>1:
            raise UserError ('Double lot no!')
        bin1=self.env['sis.bin'].search([('code','=',vals['bin'])])
        if len(bin1)==0:
            raise UserError ('Bin not found!')
        if len(bin1)>1:
            raise UserError ('Double bin!')
        next1=None
        if len(ile)>0:
            next1=self.env['sis.goods.bin'].search([('entry_no','=',ile['id']),('next_id','=',None)])
            vals.update ({
                'bin_no': bin1.code,
                'item_no':ile.item_no, 
                'posting_date':ile.posting_date,
                'document_no': ile.document_no,
                'location_code': ile.location_code,
                'quantity':ile.quantity,
                'remaining_quantity':ile.remaining_quantity,
                'lot_no':ile.lot_no,
                'fish_box_no':ile.fish_box_no,
                'vessel_no':ile.vessel_no,
                'container_no':ile.container_no,
                'voyage_no':ile.voyage_no,
                'hatch_no':ile.hatch_no,
                'no_basket':ile.no_basket,
                'no_contract':ile.no_contract,
                'inkjet_print':ile.inkjet_print,
                'out':False,
                'entry_no':ile.id
            })
        else:
            raise UserError('Lot not found!')
        n = models.Model.create(self, vals)
        if len(next1)>0:
            valsnext={'next_id':n.id,
                      'out':True
                }
            next1.write(valsnext)
        return n