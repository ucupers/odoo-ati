from odoo import models, fields, api

class sis_master_item(models.Model):
    _inherit = 'sis.pps.item'
    
    yieldd = fields.Float(string="Yield")
    net = fields.Float(string="Net(W)")
    meat = fields.Float(string="Meat")
    filling = fields.Float(string="Filling")
    sm = fields.Float(string="SM")
    kaleng_per_case = fields.Float(string="Kaleng per Case")
    fcl = fields.Float(string="FCL")
    can_size = fields.Char(string="Can Size")
    

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if self.env.context.get('custom_search', False):
                # Only goes off when the custom_search is in the context values.
                result.append((record.id, "{} {}".format(record.item_no, record.description)))
            else:
                result.append((record.item_no, record.description))
        return result