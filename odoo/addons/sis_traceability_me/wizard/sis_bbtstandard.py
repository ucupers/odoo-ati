from odoo import models, fields
#from odoo.exceptions import UserError
#from datetime import datetime

class bbtstandard(models.TransientModel):
    _name       ='sis.bbt.standard'
    
    ok    = fields.Char(string="O", default="OK")  
    larva = fields.Char(string="L", default="Larva")
    lain  = fields.Char(string="X", default="Lain-lain")
    verygood    = fields.Char(string="A", default="Very Good")  
    good        = fields.Char(string="B", default="Good")
    medium      = fields.Char(string="C", default="Medium")
    bad         = fields.Char(string="D", default="Bad")