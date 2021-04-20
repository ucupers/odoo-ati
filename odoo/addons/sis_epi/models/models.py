# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sis_epi(models.Model):
    _name = 'sis.epi'
    _rec_name = 'name'
    _inherit = 'mail.thread'
    
    name = fields.Char(string="Name")
    epi_line_ids = fields.One2many('sis.epi.line', 'epi_id')
    
    
    @api.model
    def create(self, vals):
        res = super(sis_epi, self).create(vals)

        # Sequence
        sequence = self.env['ir.sequence'].next_by_code('sequence.sis.epi') or ('New')
        res.update({'name': sequence})

        return res



class sis_epi_line(models.Model):
    _name = 'sis.epi.line'
    
    epi_id = fields.Many2one('sis.epi', ondelete='cascade')
    pps_item_id = fields.Many2one('sis.pps.item', string="Item")
    line = fields.Char(string="Line")
    net = fields.Float(string="Net(w)")
    target_prd = fields.Float(string="Target Produksi", track_visibility='onchange')

