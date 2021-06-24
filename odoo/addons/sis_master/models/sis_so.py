from odoo import models, fields, api
from odoo.exceptions import UserError


class sis_so_header(models.Model):
    _name='sis.so.header'
    _table='sis_so_header'
    _auto=False
        
    itemno=fields.Char(size=20,string="Item No.",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)
    itc=fields.Char(size=20,string="Item Cat.",readonly=True)
    pgc=fields.Char(size=20,string="Product Grp.",readonly=True)
    blocked=fields.Boolean(string="Blocked",readonly=True)
    refitem=fields.Char(string="Ref. Item",readonly=True)            
    realitem=fields.Char(size=20,string="Real Item No.",readonly=True)
    qtyperfcl=fields.Float(string="Qty/FCL",readonly=True)
    salesuom=fields.Char(size=20,string="Sales UoM",readonly=True)
    qtyperuom=fields.Float(size=20,string="Qty/UoM",readonly=True)
    baseuom=fields.Char(size=20,string="Base UoM",readonly=True)
    routingno=fields.Char(size=20,string="Routing No.",readonly=True)                    
    prodbomno=fields.Char(size=20,string="Prod BoM No.",readonly=True)
    fishmaterial=fields.Char(size=20,string="Fish Material",readonly=True)
        
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args=args or []
        recs=self.browse()
        if name:
            recs=self.search([('itemno','=',name)]+args,limit=limit)
        if len(recs)==0:
            recs=self.search([('description',operator,name)]+args,limit=limit)
        return recs.name_get()        
        
        
class sis_item_variants(models.Model):
    _name='sis.item.variants'
    _table='sis_item_variants'
    _auto=False
    _rec_name='variant'
       
    itemno=fields.Char(size=20,string="Item No.",readonly=True)
    variant=fields.Char(size=20,string="Variant",readonly=True)
    blocked=fields.Boolean(string="Blocked",readonly=True)
    qtyperfcl=fields.Float(string="Qty/FCL",readonly=True)
    uom=fields.Char(size=20,string="Sales UoM",readonly=True)
    qtyperuom=fields.Float(size=20,string="Qty/UoM",readonly=True)
