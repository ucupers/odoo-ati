'''
Created on Jan 22, 2021

@author: endah
'''
from odoo import models, fields

class sisMasterReject(models.Model):
    _name = 'sis.master.reject'
    _description = 'Master Reject'
    _order = 'description'
    _rec_name = 'description'
    
    description = fields.Char('Description Reject')
    section = fields.Char('Section')