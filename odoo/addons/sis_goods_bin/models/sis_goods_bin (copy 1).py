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
    lot_no =fields.Char(size=20,string="Lot No",readonly=True)
    fish_box_no =fields.Char(size=20,string="Fish Box No",readonly=True)
    vessel_no =fields.Char(size=20,string="Vessel No",readonly=True)
    container_no =fields.Char(size=40,string="Container No",readonly=True)
    voyage_no =fields.Char(size=20,string="Voyage No",readonly=True)
    hatch_no =fields.Char(size=20,string="Hatch No",readonly=True)
    no_basket =fields.Char(size=20,string="No Basket",readonly=True)
    no_contract =fields.Char(size=20,string="No Contract",readonly=True)
    inkjet_print =fields.Char(size=250,string="Inkjet Print",readonly=True)    
    
class sis_goods_bin(models.Model):
    _name='sis.goods.bin'
    _rec_name='ile_id'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin',required=True)

    item_no =fields.Char(string="Item No",readonly=True) 
    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(string="Document No",readonly=True)
    description =fields.Char(string="Description",readonly=True)
    location_code =fields.Char(string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    lot_no =fields.Char(string="Lot No",readonly=True)
    fish_box_no =fields.Char(string="Fish Box No",readonly=True)
    vessel_no =fields.Char(string="Vessel No",readonly=True)
    container_no =fields.Char(string="Container No",readonly=True)
    voyage_no =fields.Char(string="Voyage No",readonly=True)
    hatch_no =fields.Char(string="Hatch No",readonly=True)
    no_basket =fields.Char(string="No Basket",readonly=True)
    no_contract =fields.Char(string="No Contract",readonly=True)
    inkjet_print =fields.Char(string="Inkjet Print",readonly=True)    

    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        
        ile=self.env['sis.ile.remaining.quantity'].search([('lot_no','=',self.ile)])
        bin=self.env['sis.bin'].search([('code','=',self.bin)])
        if len(ile)>0:
            vals.add ({
                'item_no':ile.item_no, 
                'posting_date':ile.posting_date,
                'document_no': ile.document_no,
                'description':ile.description,
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
                'inkjet_print':ile.inkjet_print   
            })
        else:
            raise UserError('Lot not found!')
        if len(bin)==0:
            raise UserError ('Bin not found!')
        n = models.Model.create(self, vals)
        return n
    
class sis_goods_pivot_bin(models.Model):
    _name='sis.goods.pivot.bin'
    _rec_name='ile_id'
        
    ile_id=fields.Many2one('sis.ile.remaining.quantity',string='Lot No',required=True)
    bin_id=fields.Many2one('sis.bin',string='Bin',required=True)
    next_id=fields.Many2one('sis.goods.bin',string='Previous ID')
    user_id=fields.Integer('UserID')
    clr=fields.Char(string='Color')

    item_no =fields.Char(string="Item No",readonly=True) 
    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(string="Document No",readonly=True)
    description =fields.Char(string="Description",readonly=True)
    location_code =fields.Char(string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    lot_no =fields.Char(string="Lot No",readonly=True)
    fish_box_no =fields.Char(string="Fish Box No",readonly=True)
    vessel_no =fields.Char(string="Vessel No",readonly=True)
    container_no =fields.Char(string="Container No",readonly=True)
    voyage_no =fields.Char(string="Voyage No",readonly=True)
    hatch_no =fields.Char(string="Hatch No",readonly=True)
    no_basket =fields.Char(string="No Basket",readonly=True)
    no_contract =fields.Char(string="No Contract",readonly=True)
    inkjet_print =fields.Char(string="Inkjet Print",readonly=True)    

    @api.depends('ile_id')
    def compute_color(self):
        postdate=datetime.strptime(self.posting_date[:10],'%Y-%m-%d')
        nowdate=datetime.strptime(datetime.now(),'%Y-%m-%d')
        datedelta=nowdate-postdate        
        if self.description[:3]=='UC ' and datedelta.days<14:
            self.clr='red'

    def fill_data(self):
        #recs=self.env['sis.goods.bin'].search([('remaining_quantity','>',0)])
        #self.env['sis.goods.pivot.bin'].search([('user_id','=',self.env.user_id.id)])
        self.env.cr.execute("delete from sis_goods_pivot_bin where user_id="+str(self.env.uid))
        self.env.cr.execute("insert into sis_goods_pivot_bin(id,ile_id,bin_id,next_id,user_id,item_no,posting_date,document_no,description,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print) \
            select sgb.id,ile_id,bin_id,next_id,"+str(self.env.uid)+",item_no,posting_date,document_no,description,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print \
            from sis_goods_bin sgb inner join sis_ile_remaining_quantity sirq on sgb.ile_id=sirq.id and sgb.next_id is NULL and sirq.remaining_quantity>0 \
            inner join sis_bin sb on sgb.bin_id=sb.id")

        recs=self.env['sis.goods.pivot.bin'].search([('user_id','=',self.env.uid)])
        nowdate=datetime.now()+relativedelta(hours=7)
        for r in recs:
            postdate=datetime.strptime(r.posting_date[:10],'%Y-%m-%d')
            datedelta=nowdate-postdate        
            if r.description[:3]=='UC ' and datedelta.days<14:
                r.clr='red'
            else:
                r.clr='black'

        return {
                "name":"Goods Bin",
                "type": "ir.actions.act_window",
                "view_mode": "tree,pivot",
                "res_model": "sis.goods.pivot.bin",
                "domain":[("user_id","=",self.env.uid),("next_id","=",None)]
            }
        
class sis_goods_move_bin(models.Model):
    _name='sis.goods.move.bin'
    _rec_name='ile_id'
        
    ile_id=fields.Many2one('sis.ile.remaining.quantity',string='Lot No',required=True)
    bin_id=fields.Many2one('sis.bin',string='Bin',required=True)
    next_id=fields.Many2one('sis.goods.bin',string='Previous ID')
    user_id=fields.Integer('UserID')

    item_no =fields.Char(string="Item No",readonly=True) 
    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(string="Document No",readonly=True)
    description =fields.Char(string="Description",readonly=True)
    location_code =fields.Char(string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    lot_no =fields.Char(string="Lot No",readonly=True)
    fish_box_no =fields.Char(string="Fish Box No",readonly=True)
    vessel_no =fields.Char(string="Vessel No",readonly=True)
    container_no =fields.Char(string="Container No",readonly=True)
    voyage_no =fields.Char(string="Voyage No",readonly=True)
    hatch_no =fields.Char(string="Hatch No",readonly=True)
    no_basket =fields.Char(string="No Basket",readonly=True)
    no_contract =fields.Char(string="No Contract",readonly=True)
    inkjet_print =fields.Char(string="Inkjet Print",readonly=True)    


    def fill_data(self):
        self.env.cr.execute("delete from sis_goods_move_bin where user_id="+str(self.env.uid))
        self.env.cr.execute("insert into sis_goods_move_bin(id,ile_id,bin_id,next_id,user_id,item_no,posting_date,document_no,description,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print, create_date) \
            select sgb.id,ile_id,bin_id,next_id,"+str(self.env.uid)+",item_no,posting_date,document_no,description,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print,sgb.create_date+interval '7 hour' \
            from sis_goods_bin sgb inner join sis_ile_remaining_quantity sirq on sgb.ile_id=sirq.id and sirq.remaining_quantity>0 \
            inner join sis_bin sb on sgb.bin_id=sb.id")

        return {
                "name":"Movement History",
                "type": "ir.actions.act_window",
                "view_mode": "tree",
                "res_model": "sis.goods.move.bin",
                "domain":[("user_id","=",self.env.uid)]
            }        
        
        