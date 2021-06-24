from odoo import fields, models

class hr_employee_inherit(models.Model):
    _inherit   	 = 'hr.employee'
    _name	 = 'hr.employee'

    pabrik_id   = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')], required=True)
#    section_id   = fields.Selection(string="Section", selection=[('Admin', 'Admin'),('Prod1', 'Produksi 1'),('CSD', 'Cold Storage-Defrost'),('CS', 'Cold Storage'),('Defrost', 'Defrost'),('Cutting', 'Cutting'),('Cooker', 'Cooker'),('QCDoc', 'Dokumen'),('PreCL', 'Pre Cleaning'),('CL','Cleaning')], required=True)
#    checker     = fields.Boolean(string='Checker')
#    unchecker   = fields.Boolean(string='Unchecker')
#    shift = fields.Selection(string="Shift", selection=[('1/A', '1/A'),('1/B', '1/B'), ('2/A', '2/A'),('2/B', '2/B')])
