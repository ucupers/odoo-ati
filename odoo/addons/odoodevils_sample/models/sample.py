'''
Created on Sep 5, 2018

@author: chodet
'''
from odoo import fields, models, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, Warning
from odoo.tools.translate import _



class Sample(models.Model):
    _name = 'sample'
    
    name = fields.Char(string='Name', required=True, readonly=False)
    sample_ids = fields.One2many('sample.line', 'sample_id', string='Sample')

class SampleLine(models.Model):
    _name = 'sample.line'
    
    sample_id = fields.Many2one('sample', string='Sample')       
    col_1 = fields.Char(string='Col 1', required=False, readonly=False)
    col_2 = fields.Char(string='Col 2', required=False, readonly=False)
    col_3 = fields.Char(string='Col 3', required=False, readonly=False)
    col_4 = fields.Char(string='Col 4', required=False, readonly=False)
    col_5 = fields.Char(string='Col 5', required=False, readonly=False)   