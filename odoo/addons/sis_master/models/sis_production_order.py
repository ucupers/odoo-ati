from odoo import models, fields, api
from odoo.exceptions import UserError

class sis_local_released_production_order(models.Model):
    _name='sis.local.released.production.order'
    _rec_name='display'
        
    no=fields.Char(string="Production Order")
    item_no=fields.Char(string="Item No.")
    description=fields.Char(string="Description")
    bg=fields.Char(string="BG")
    dept=fields.Char(string="Dept.")
    startingdate=fields.Date(string="Starting Date")    
    endingdate=fields.Date(string="Ending Date")    
    endproductiondate=fields.Date(string="End Prod.Date")    
    duedate=fields.Date(string="Due Date")    
    location=fields.Char(string="Location")
    
    display=fields.Char(string="Production Order")
    
class sis_local_released_production_order_component(models.Model):
    _name='sis.local.released.production.order.component'
    _rec_name='no'
        
    no=fields.Char(string="Production Order")
    lineno=fields.Char(string="Line no")
    item_no=fields.Char(string="Item No.")
    variant=fields.Char(string="Variant")    
    description=fields.Char(string="Description")
    uom=fields.Char(string="UoM")
    location=fields.Char(string="Location")        
    bg=fields.Char(string="BG")
    dept=fields.Char(string="Dept.")
    
