from odoo import models, fields

class sis_section_id(models.Model):
    _name   = "sis.section"    
    _description = 'SIS Section ATI'

    kode        = fields.Char(size=12, string="Kode")
    keterangan  = fields.Char(size=50, string="Keterangan")
