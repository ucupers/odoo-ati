from odoo import models, fields, api
from odoo.exceptions import UserError


class sis_production_bom(models.Model):
    _name='sis.production.bom'
    _table='sis_production_bom'
    _auto=False
    _rec_name='description'
       
    itemno=fields.Char(size=20,string="Item No.",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)
    uom=fields.Char(size=20,string="UoM",readonly=True)
    qtyperuom=fields.Float(string="Qty Per UoM",readonly=True)
    variant=fields.Char(size=20,string="Variant Code",readonly=True)
    variantdesc=fields.Char(size=200,string="Variant Desc.",readonly=True)
    variantuom=fields.Char(size=20,string="Variant UoM",readonly=True)
    variantqtyperuom=fields.Float(string="Variant Qty/UoM",readonly=True)
    linenum=fields.Integer(string="LineNum",readonly=True)
    lineitem=fields.Char(size=20,string="Line Item",readonly=True)            
    linedesc=fields.Char(size=200,string="Line Description",readonly=True)
    lineqty=fields.Float(string="Line Qty",readonly=True)
    linerouting=fields.Char(size=20,string="Routing",readonly=True)        
    lineqtyper=fields.Float(string="Qty Per",readonly=True)
    lineuom=fields.Char(size=20,string="Line UoM",readonly=True)
    lineitc=fields.Char(size=20,string="Line ITC",readonly=True)            
    linepgc=fields.Char(size=20,string="Line PGC",readonly=True)                    
        
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args=args or []
        recs=self.browse()
        if name:
            recs=self.search([('itemno','=',name)]+args,limit=limit)
        if len(recs)==0:
            recs=self.search([('description',operator,name)]+args,limit=limit)
        return recs.name_get()        