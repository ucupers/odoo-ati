from odoo import fields, models

class hr_employee(models.Model):
    _inherit    = 'hr.employee'
    _name       = 'hr.employee'
    
    pabrik_id   = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')])
    section_id   = fields.Selection(string="Section", selection=[
        ('Admin', 'Admin'),
        ('Prod1', 'Produksi 1'),
        ('Boiler', 'Boiler'),
        ('CSD', 'Cold Storage-Defrost'),
        ('CS', 'Cold Storage'),
        ('Defrost', 'Defrost'),
        ('FJ', 'Fish Juice'),
        ('FM', 'Fish Meal'),
        ('GA', 'General Affairs'),
        ('RM', 'Raw Material'),
        ('Cutting', 'Cutting'),
        ('Cooker', 'Cooker'),
        ('HR', 'Human Resources'),
        ('IT', 'IT'),
        ('MT', 'Maintenance'),
        ('Office', 'Office'),
        ('PPIC', 'PPIC'),
        ('QT', 'Quality Technology'),
        ('Seamer', 'Seamer'),
        ('Seasoning', 'Seasoning'),
        ('QCDoc', 'Dokumen'),
        ('PreCL', 'Pre Cleaning'),
        ('CL','Cleaning'),
        ('packing','Packing'),
        ('WHUnlabeled','WH Unlabeled'),
        ('WH', 'Warehouse'),
        ('Retort','Retort'),
        ('EC','Empty Can'),
        ('PNF','Purchasing')
        ])
    checker     = fields.Boolean(string='Checker')
    unchecker   = fields.Boolean(string='Unchecker')
    shift = fields.Selection(string="Shift", selection=[('1/A', '1/A'),('1/B', '1/B'), ('2/A', '2/A'),('2/B', '2/B')])
    section_spec   = fields.Selection(string="Section Spec", selection=[
        ('Admin', 'Admin'),
        ('ASTMAN', 'Asst. Manager'),
        ('CL','Cleaning'),
        ('CS', 'Cold Storage'),
        ('Cooker', 'Cooker'),
        ('Cutting', 'Cutting'),
        ('Defrost', 'Defrost'),
        ('FA','Finance Accounting'),
        ('EC','Empty Can'),
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
