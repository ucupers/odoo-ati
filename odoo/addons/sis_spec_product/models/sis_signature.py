from odoo import models, fields, api

class sis_spec_sign(models.Model):
    _name='sis.spec.signature'
    _order = 'id'
        
    ttd_jabatan1= fields.Char(size=50,string='Jabatan1',required=True)
    ttd_jabatan2= fields.Char(size=50,string='Jabatan2',required=True)
    ttd_jabatan3= fields.Char(size=50,string='Jabatan3',required=True)
    ttd_nama1   = fields.Char(size=50,string='Nama1',required=True)
    ttd_nama2   = fields.Char(size=50,string='Nama2',required=True)
    ttd_nama3   = fields.Char(size=50,string='Nama3',required=True)
    ttd_status  = fields.Boolean(string="Diaktifkan")
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['ttd_status']==True:
            self.env.cr.execute("update sis_spec_signature set ttd_status=false")

        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        if vals.get('ttd_status')==True:
            self.env.cr.execute("update sis_spec_signature set ttd_status=false")
        return models.Model.write(self, vals)
        



