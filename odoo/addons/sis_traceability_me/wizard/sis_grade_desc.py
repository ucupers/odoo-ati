from odoo import models, fields
#from odoo.exceptions import UserError
#from datetime import datetime

class gradedesc(models.Model):
    _name       ='sis.grade.desc'
    
    verygood    = fields.Char(string="A")  
    good        = fields.Char(string="B")
    medium      = fields.Char(string="C")
    bad         = fields.Char(string="D")