'''
Created on Jul 17, 2020

@author: endah
'''
from odoo import models, fields

class sis_ec_trial(models.Model):
    _name = 'sis.ec.trial'
    _description = 'Empty Can Trial'
    
    detail_ids = fields.One2many('sis.ec.trial.detail', 'header_id', string='Header ID')
    
    productiondate_ati = fields.Date('Tanggal Produksi ATI')
    line = fields.Integer('Line')
    nama_produk = fields.Char('Nama Produk')
    kode_barang = fields.Char('Kode Barang')
    deskripsi_pouch = fields.Char('Deskripsi Pouch')
    productiondate_supplier = fields.Date('Tanggal Produksi Supplier')
    total_kedatangan = fields.Integer('Total Kedatangan')
    total_reject = fields.Integer('Total Reject')
    remark  = fields.Char('Remark')
    
class sis_ec_trial_detail(models.Model):
    _name = 'sis.ec.trial.detail'
    _description = 'Empty Can Trial'
    
    header_id = fields.Many2one('sis.ec.trial', string='Header ID')
    
    incoming_date = fields.Date('Tanggal Kedatangan')
    invoices = fields.Char('Invoice')
    incoming_total = fields.Integer('Total Kedatangan')
    using_total = fields.Integer('Total Pemakaian')
    
    
    
    