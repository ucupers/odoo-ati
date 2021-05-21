from odoo import models, fields, api

class sis_master_item(models.Model):
    _inherit = 'sis.pps.item'
    
    yieldd = fields.Float(string="Fish Qty")
    net = fields.Float(string="Net(W)")
    meat = fields.Float(string="Meat")
    filling = fields.Float(string="Filling", compute='calculate_filling')
    sm = fields.Float(string="SM", compute='calculate_sm')
    kaleng_per_case = fields.Float(string="Kaleng per Case")
    fcl = fields.Float(string="FCL")
    can_size = fields.Char(string="Can Size")
    karyawan_pk = fields.Float(string="Karyawan PK")
    speed = fields.Float(string="Speed(cs/jam)")
    

    # Calculate filling
    @api.depends('meat', 'kaleng_per_case')
    def calculate_filling(self):
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case
            
            if meat and kaleng_per_case:
                filling = (meat * kaleng_per_case) / 1000
                
                rec.filling = filling
    
    
    # Calculate yield/kebutuhan ikan mentah
    @api.depends('filling')
    def calculate_yield(self):
        for rec in self:
            item_desc = rec.description
            
    
    # Calculate SM
    @api.depends('meat', 'kaleng_per_case')
    def calculate_sm(self): 
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case
            
            if meat and kaleng_per_case:
                sm = meat * kaleng_per_case
                
                rec.sm = sm


class budomari_inherit(models.Model):
    _inherit = 'sis.budomari'
    
    # Change name many2one
    @api.multi
    def name_get(self):
        result = []
        for rec in self:    
            result.append((rec.id, '%s - %s' % (rec.fish, rec.budomari)))
        return result
                
    
    
    
    