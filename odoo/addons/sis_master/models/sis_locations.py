from odoo import models, fields, api
from odoo.exceptions import UserError


class sis_locations(models.Model):
    _name='sis.locations'
    _table='sis_locations'
    _auto=False
    _rec_name='code'
        
    code=fields.Char(size=20,string="Code",readonly=True)
    name=fields.Char(size=200,string="Name",readonly=True)
    
    
class sis_bin(models.Model):
    _name='sis.bin'
    _rec_name='code'
        
    location_id=fields.Many2one('sis.locations',string='Location ID',required=True)
    location=fields.Char(compute='_compute_location',string='Location', required=True)
    code=fields.Char(size=20,string="Code",required=True)
    name=fields.Char(size=200,string="Name")
    
    @api.constrains('code')
    def code_unique(self):
        if self.env['sis.bin'].search_count([('code','=',self.code),('id','!=',self.id)])>0:
            raise UserError('Duplicate bin code !')
        
    @api.one
    @api.depends('location_id')
    def _compute_location(self):
        if len(self.location_id)==1:
            self.location=self.location_id.code