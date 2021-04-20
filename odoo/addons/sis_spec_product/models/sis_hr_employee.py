from odoo import fields, models

class hr_employee(models.Model):
    _inherit    = 'hr.employee'
    _name       = 'hr.employee'
#     pabrik_id   = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')], required=True)
    section_spec   = fields.Selection(string="Section Spec", selection=[
        ('Admin', 'Admin'),
        ('ASTMAN', 'Asst. Manager'),
        ('CL','Cleaning'),
        ('CS', 'Cold Storage'),
        ('Cooker', 'Cooker'),
        ('Cutting', 'Cutting'),
        ('Defrost', 'Defrost'),
        ('EC','Empty Can'),
        ('FA','Finance Accounting'),
        ('JPN','Japan Staff'),
        ('MAN','Manager'),
        ('PPIC', 'PPIC'),        
        ('Packing', 'Packing'),
        ('PreCL', 'Pre Cleaning'),
        ('QA', 'QA'),
        ('QC', 'QC'),
        ('RND', 'RND'),
        ('Retort', 'Retort'),
        ('SNM', 'Sales and Marketing'),
        ('Seamer', 'Seamer'),
        ('Seasoning', 'Seasoning'),
        ('WH', 'Warehouse')
        ])
#     checker     = fields.Boolean(string='Checker')
#     unchecker   = fields.Boolean(string='Unchecker')
#     shift = fields.Selection(string="Shift", selection=[('1/A', '1/A'),('1/B', '1/B'), ('2/A', '2/A'),('2/B', '2/B')])