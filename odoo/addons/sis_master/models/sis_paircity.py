from odoo import models, fields, api
from odoo.exceptions import UserError


class sis_paircity(models.Model):
    _name='sis.paircity'
        
    old=fields.Char(size=20,string="Older EXP",required=True)
    new=fields.Char(size=20,string="Newer EXP",required=True)
    
    @api.constrains('old','new')
    def old_new_unique(self):
        if self.env['sis.paircity'].search_count([('old','=',self.old),('new','=',self.new),('id','!=',self.id)])>0:
            raise UserError('Duplicate pair city !')