from odoo import models, fields,api

class hr_employee(models.Model):
    _inherit    = 'hr.employee'
    _name       = 'hr.employee'

    dpe_view_only= fields.Boolean(string='DPE View Only')
