# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo import tools

class SisCoba(models.Model):
    _name = 'sis.coba'
    _order = 'id DESC'
    
    
    itemno = fields.Char(string="Item", readonly=True)
#     sis_bin_id = fields.Many2one('', string="Bin")
    sis_item_id = fields.Many2one('sis.items', string="Item Name", ondelete='cascade')
    sis_itc = fields.Char(string="Itc")
    sis_bin_id = fields.Many2one('sis.bin', string="Bin Code")
    sis_code_bin = fields.Char(string="Bin Name")
    
#     def init(self):
        
        # CREATE OR REPLACE VIEW (nama table)
#         sql = """
#                 CREATE OR REPLACE VIEW sis_coba as
#                 (
#                     SELECT
#                     row_number() OVER () as id,
#                     itemno, description
#                     FROM sis_items
#                 )
#             """
#         
#         tools.sql.drop_view_if_exists(self._cr, 'sis_coba')
#         sql = """
#         INSERT INTO sis_coba (itemno) (SELECT itemno from sis_items)"""
#         self._cr.execute(sql)

    # Get itc from foreign table
    @api.onchange('sis_item_id')
    def get_itc(self):
        for rec in self:
            item_id = rec.sis_item_id
            
            if item_id:
                for row in item_id:
                    itc_var = row.itc
                
                rec.sis_itc = itc_var
        
    
    # Get bin from local table
    @api.onchange('sis_bin_id')
    def get_bin(self):
        for rec in self:
            bin_id = rec.sis_bin_id
            
            if bin_id:
                for row in bin_id:
                    bin_var = row.name
                
                rec.sis_code_bin = bin_var 