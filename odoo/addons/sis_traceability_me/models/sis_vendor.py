from odoo import models, fields, api

class sis_vendor(models.Model):
    _name = 'sis.vendor'
    
    supplierName = fields.Char(String="Nama Supplier")
    kode = fields.Char(String="Kode")
    hatch = fields.Char(String="Hatch")
    vessel = fields.Char(String="Vessel")