from odoo import models, fields, api
from odoo.exceptions import ValidationError

    
class sis_nilai(models.Model):
    _name='sis.nilai'
    
    siswa_id=fields.Many2one('sis.siswa',string="Siswa", domain=[('nama', '!=', 'abc')])    
    pelajaran=fields.Char(size=100,string='Pelajaran',required=True)
    nilai=fields.Float(string='Tinggi',default=100)
    nis=fields.Char(related='siswa_id.nis',string='NIS')
    
    @api.constrains('pelajaran')
    def _constrain_pelajaran(self):
        recs=self.env['sis.pelajaran'].search([('pelajaran','ilike',self.pelajaran)])
        if len(recs)==0:
            raise ValidationError('Pelajaran tidak ditemukan')
    
class sis_pelajaran(models.Model):
    _name='sis.pelajaran'
    
    pelajaran=fields.Char(size=100,string='Pelajaran',required=True)
    