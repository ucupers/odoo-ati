from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime


class urut_cutting(models.Model):
    _name = 'sis.urut.cutting.line'
    
    epi_id_uc = fields.Many2one('sis.epi', ondelete='cascade')
    epi_line_id_uc = fields.Many2one('sis.epi.line', ondelete='cascade')
    item_id_uc = fields.Many2one('sis.pps.item', string="Item")
    
    start_packing_uc = fields.Datetime(string="Start Packing")
    finish_packing_uc = fields.Datetime(string="Finish Packing")
    start_cleaning_uc = fields.Datetime(string="Start Cleaning")
    finish_cleaning_uc = fields.Datetime(string="Finish Cleaning")
    start_precleaning_uc = fields.Datetime(string="Start Pre Cleaning")
    finish_precleaning_uc = fields.Datetime(string="Finish Pre Cleaning")
    start_cutting_uc = fields.Datetime(string="Start Cutting")
    finish_cutting_uc = fields.Datetime(string="Finish Cutting")
    start_cooking_uc = fields.Datetime(string="Start Cooking")
    finish_cooking_uc = fields.Datetime(string="Finish Cooking")
    start_defrost_uc = fields.Datetime(string="Start Defrost")
    finish_defrost_uc = fields.Datetime(string="Finish Defrost")
    finish_cs_uc = fields.Datetime(string="Finish CS")
    cutting_time_uc = fields.Float(string="Cut Time")
    adj_cutting_uc = fields.Datetime(string="Adj Cut")
    adj_cutting_uc_temp = fields.Datetime(string="Temp")
    toleransi = fields.Float(string="Toleransi")
    
    remark_uc = fields.Char(string="Remark")
    hasil_urut_item_uc = fields.Char(string="Urut Item", readonly=True)
    shift_potong_uc = fields.Selection([('pp', 'PP'), ('pm', 'PM')], string="Shift Potong", default=None)
    fish_type_uc = fields.Many2one('sis.master.time', string="Fish Type")
    