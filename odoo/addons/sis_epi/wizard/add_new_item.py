from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError


class sis_new_item(models.Model):
    _name = 'sis.new.item'
    
    
    epi_id = fields.Many2one('sis.epi', readonly=True)
    name = fields.Text(readonly=True)
    
    @api.multi
    def add_item(self):
        for rec in self:
            epi_id = rec.epi_id
            
            for row in epi_id:
                state = row.state
                epi_line_ids = row.epi_line_ids
                fish_using_line = row.fish_using_line_ids
                adj_cutting_line = row.adj_cutting_line_ids
                urut_cutting_line = row.urut_cutting_line_ids
                
                if epi_line_ids:
                    for row_epi_line in epi_line_ids:
                        row_epi_line.update({'is_new_item_epi': False})
                
                if fish_using_line:
                    for row_fish_using in fish_using_line:
                        row_fish_using.update({'is_new_item_fu': False})
                
                if adj_cutting_line:
                    for row_adj_cut in adj_cutting_line:
                        row_adj_cut.update({'is_new_item_adj': False})
                
                if urut_cutting_line:
                    for row_cutting_line in urut_cutting_line:
                        row_cutting_line.update({'is_new_item_uc': False})
                
                if state == 'done':
                    raise UserError(_('Cannot add item, you must change state is not the same as "Done"'))
                    
                row.update({'is_new_item': True,
                            'state': 'schedule'})
                
                