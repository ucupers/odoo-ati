from odoo import models, fields, api
from odoo.exceptions import UserError


class sis_items(models.Model):
    _name='sis.items'   
    _table='sis_items'
    _auto=False
    _rec_name='description'
        
    itemno=fields.Char(size=20,string="Item No.")
    description=fields.Char(size=200,string="Description")
    itc=fields.Char(size=20,string="Item Cat.")
    pgc=fields.Char(size=20,string="Product Grp.")
    blocked=fields.Boolean(string="Blocked")
    refitem=fields.Char(string="Ref. Item")            
    realitem=fields.Char(size=20,string="Real Item No.")
    qtyperfcl=fields.Float(string="Qty/FCL")
    salesuom=fields.Char(size=20,string="Sales UoM")
    qtyperuom=fields.Float(size=20,string="Qty/UoM")
    baseuom=fields.Char(size=20,string="Base UoM")
    routingno=fields.Char(size=20,string="Routing No.")                    
    prodbomno=fields.Char(size=20,string="Prod BoM No.")
    fishmaterial=fields.Char(size=20,string="Fish Material")
    purchuom=fields.Char(size=20,string="Purchase UoM")
    purchqtyperuom=fields.Float(size=20,string="Purch Qty/UoM") 
    unitcost=fields.Float(string="Unit cost") 
            
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args=args or []
        recs=self.browse()
        if name:
            recs=self.search([('itemno','=',name)]+args,limit=limit)
        if len(recs)==0:
            recs=self.search([('description',operator,name)]+args,limit=limit)
        return recs.name_get()        

class sis_items_local(models.Model):
    _name='sis.items.local'   
    _rec_name='description'
        
    itemno=fields.Char(size=20,string="Item No.")
    description=fields.Char(size=200,string="Description")
    itc=fields.Char(size=20,string="Item Cat.")
    pgc=fields.Char(size=20,string="Product Grp.")
    blocked=fields.Boolean(string="Blocked")
    refitem=fields.Char(string="Ref. Item")            
    realitem=fields.Char(size=20,string="Real Item No.")
    qtyperfcl=fields.Float(string="Qty/FCL")
    salesuom=fields.Char(size=20,string="Sales UoM")
    qtyperuom=fields.Float(size=20,string="Qty/UoM")
    baseuom=fields.Char(size=20,string="Base UoM")
    routingno=fields.Char(size=20,string="Routing No.")                    
    prodbomno=fields.Char(size=20,string="Prod BoM No.")
    fishmaterial=fields.Char(size=20,string="Fish Material")
    purchuom=fields.Char(size=20,string="Purchase UoM")
    purchqtyperuom=fields.Float(size=20,string="Purch Qty/UoM") 
    unitcost=fields.Float(string="Unit cost") 
            
    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args=args or []
        recs=self.browse()
        if name:
            recs=self.search([('itemno','=',name)]+args,limit=limit)
        if len(recs)==0:
            recs=self.search([('description',operator,name)]+args,limit=limit)
        return recs.name_get()        

    def upload_from_NAV(self):
        self.env.cr.execute(" insert into sis_items_local(id,itemno,description,itc,pgc,blocked,refitem,realitem,qtyperfcl,salesuom,qtyperuom,baseuom,routingno,prodbomno,fishmaterial,purchuom,purchqtyperuom,unitcost) "+ \
                            " select id,itemno,description,itc,pgc,blocked,refitem,realitem,qtyperfcl,salesuom,qtyperuom,baseuom,routingno,prodbomno,fishmaterial,purchuom,purchqtyperuom,unitcost "+ \
                            " from sis_items where itemno not in (select itemno from sis_items_local)")

        self.env.cr.execute(" update sis_items_local sl set itemno=si.itemno,description=si.description,itc=si.itc,pgc=si.pgc,blocked=si.blocked,refitem=si.refitem,realitem=si.realitem,qtyperfcl=si.qtyperfcl, "+\
                            " salesuom=si.salesuom,qtyperuom=si.qtyperuom,baseuom=si.baseuom,routingno=si.routingno,prodbomno=si.prodbomno,fishmaterial=si.fishmaterial,purchuom=si.purchuom,purchqtyperuom=si.purchqtyperuom "+ \
                            " from sis_items si"+ \
                            " where sl.itemno=si.itemno and (sl.description!=si.description or sl.itc!=si.itc or sl.pgc!=si.pgc or sl.blocked!=si.blocked or sl.refitem!=si.refitem or sl.realitem!=si.realitem or sl.qtyperfcl!=si.qtyperfcl or  "+\
                            " sl.salesuom!=si.salesuom or sl.qtyperuom!=si.qtyperuom or sl.baseuom!=si.baseuom or sl.routingno!=si.routingno or sl.prodbomno!=si.prodbomno or sl.fishmaterial!=si.fishmaterial or sl.purchuom!=si.purchuom or sl.purchqtyperuom!=si.purchqtyperuom) ")

        self.env.cr.execute(" insert into sis_item_variants_local(id,itemno,description,blocked,qtyperfcl,uom,qtyperuom,variant) "+ \
                            " select id,itemno,description,blocked,qtyperfcl,uom,qtyperuom,variant "+ \
                            " from sis_item_variants where itemno not in (select itemno from sis_item_variants_local)")

        self.env.cr.execute(" update sis_item_variants_local sl set itemno=si.itemno,description=si.description,blocked=si.blocked,qtyperfcl=si.qtyperfcl, "+\
                            " uom=si.uom,qtyperuom=si.qtyperuom "+ \
                            " from sis_item_variants si"+ \
                            " where sl.itemno=si.itemno and sl.variant=si.variant and (sl.description!=si.description or sl.blocked!=si.blocked or sl.qtyperfcl!=si.qtyperfcl or  "+\
                            " sl.uom!=si.uom or sl.qtyperuom!=si.qtyperuom) ")


    itemno=fields.Char(size=20,string="Item No.",readonly=True)
    variant=fields.Char(size=20,string="Variant",readonly=True)
    blocked=fields.Boolean(string="Blocked",readonly=True)
    qtyperfcl=fields.Float(string="Qty/FCL",readonly=True)
    uom=fields.Char(size=20,string="Sales UoM",readonly=True)
    qtyperuom=fields.Float(size=20,string="Qty/UoM",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)    
        
        
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
    description=fields.Char(size=200,string="Description",readonly=True)    

class sis_item_variants_local(models.Model):
    _name='sis.item.variants.local'
    _rec_name='variant'
       
    itemno=fields.Char(size=20,string="Item No.",readonly=True)
    variant=fields.Char(size=20,string="Variant",readonly=True)
    blocked=fields.Boolean(string="Blocked",readonly=True)
    qtyperfcl=fields.Float(string="Qty/FCL",readonly=True)
    uom=fields.Char(size=20,string="Sales UoM",readonly=True)
    qtyperuom=fields.Float(size=20,string="Qty/UoM",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)    
