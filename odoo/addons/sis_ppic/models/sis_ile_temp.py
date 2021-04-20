from odoo import models, fields, api
from odoo.exceptions import UserError

class sis_ile_temp(models.Model):
    _name='sis.ile.temp'
    _rec_name='description'
        
    posting_date=fields.Date(string='Posting date', readonly=True)
    item_no=fields.Char(size=20,string="Item No.",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)
    variant=fields.Char(size=20,string="Variant",readonly=True)
    itc=fields.Char(size=20,string="Item Cat.",readonly=True)
    pgc=fields.Char(size=20,string="Product Grp.",readonly=True)
    location_code=fields.Char(size=20,string="Location",readonly=True)
    qtyperuom=fields.Float(string="Qty/UoM",readonly=True)
    uom=fields.Char(size=30,string="Sales UoM",readonly=True)
    entrytype=fields.Char(size=30,string="Entry Type",readonly=True)
    qty=fields.Float(string="Qty",readonly=True)
    remainingqty=fields.Float(string="Remaining Qty",readonly=True)        
    bg=fields.Char(size=20,string="BG",readonly=True)    
    