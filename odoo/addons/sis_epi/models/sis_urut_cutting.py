from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class urut_cutting(models.Model):
    _name = 'sis.urut.cutting.line'
#     _order = 'start_cutting_temp_uc'
    
    no = fields.Integer()
    epi_id_uc = fields.Many2one('sis.epi')
    epi_id_uc_int = fields.Integer()
    epi_line_id_uc = fields.Many2one('sis.epi.line')
    item_id_uc = fields.Many2one('sis.pps.item', string="Item")
    urut_potong = fields.Integer(string="No Urut")
    
    start_packing_uc = fields.Datetime(string="Start Packing")
    finish_packing_uc = fields.Datetime(string="Finish Packing")
    start_cleaning_uc = fields.Datetime(string="Start Cleaning")
    finish_cleaning_uc = fields.Datetime(string="Finish Cleaning")
    start_precleaning_uc = fields.Datetime(string="Start Pre Cleaning")
    finish_precleaning_uc = fields.Datetime(string="Finish Pre Cleaning")
    start_cutting_temp_uc = fields.Datetime(string="Start Cutting")
    start_cutting_uc = fields.Datetime(string="Start Cutting Old")
    finish_cutting_uc = fields.Datetime(string="Finish Cutting")
    start_cooking_uc = fields.Datetime(string="Start Cooking")
    finish_cooking_uc = fields.Datetime(string="Finish Cooking")
    start_defrost_uc = fields.Datetime(string="Start Defrost")
    finish_defrost_uc = fields.Datetime(string="Finish Defrost")
    finish_cs_uc = fields.Datetime(string="Finish CS")
    delay_co_pre = fields.Float(string="Delay CO-Pre")
    
    cutting_time_uc = fields.Float(string="Cut Time")
    adj_cutting_uc = fields.Datetime(string="Adj Cut")
    adj_cutting_uc_temp = fields.Datetime(string="Temp")
    toleransi = fields.Float(string="Toleransi")
    tonase_uc = fields.Float(string="Tonase")
    total_tonase_uc = fields.Float(string="Total Tonase")
    
    remark_uc = fields.Char(string="Remark")
    hasil_urut_item_uc = fields.Char(string="Urut Item")
    urutan_item_uc = fields.Integer()
    shift_potong_uc = fields.Selection([('pp', 'PP'), ('pm', 'PM')], string="Shift", default=None, compute='get_shift_potong')
    fish_type_uc = fields.Many2one('sis.master.time', string="Fish Type")
    fish_qty_uc = fields.Float(string="Fish Qty(ton)")
    
    # Format date
    start_packing_format_uc = fields.Char(string="Start Packing", compute='get_date_format')
    finish_packing_format_uc = fields.Char(string="Finish Packing", compute='get_date_format')
    start_cleaning_format_uc = fields.Char(string="Start Cleaning", compute='get_date_format')
    finish_cleaning_format_uc = fields.Char(string="Finish Cleaning", compute='get_date_format')
    start_precleaning_format_uc = fields.Char(string="Start Pre Cleaning", compute='get_date_format')
    finish_precleaning_format_uc = fields.Char(string="Finish Pre Cleaning", compute='get_date_format')
    start_cutting_temp_format_uc = fields.Char(string="Start Cutting", compute='get_date_format')
    start_cutting_format_uc = fields.Char(string="Start Cutting Old", compute='get_date_format')
    finish_cutting_format_uc = fields.Char(string="Finish Cutting", compute='get_date_format')
    start_cooking_format_uc = fields.Char(string="Start Cooking", compute='get_date_format')
    finish_cooking_format_uc = fields.Char(string="Finish Cooking", compute='get_date_format')
    start_defrost_format_uc = fields.Char(string="Start Defrost", compute='get_date_format')
    finish_defrost_format_uc = fields.Char(string="Finish Defrost", compute='get_date_format')
    finish_cs_format_uc = fields.Char(string="Finish CS", compute='get_date_format')
    
    # Get date format string
    @api.one
    def get_date_format(self):
        for rec in self:
            start_packing = rec.start_packing_uc
            finish_packing = rec.finish_packing_uc
            
            start_cleaning = rec.start_cleaning_uc
            finish_cleaning = rec.finish_cleaning_uc
            
            start_precleaning = rec.start_precleaning_uc
            finish_precleaning = rec.finish_precleaning_uc
            
            start_cutting = rec.start_cutting_temp_uc
            finish_cutting = rec.finish_cutting_uc
            # Old
            start_cutting_old = rec.start_cutting_uc
            
            start_cooking = rec.start_cooking_uc
            finish_cooking = rec.finish_cooking_uc
            
            start_defrost = rec.start_defrost_uc
            finish_defrost = rec.finish_defrost_uc
            
            finish_cs = rec.finish_cs_uc
            
            format = "%Y-%m-%d %H:%M:%S"
            
            if start_packing and finish_packing:
                start_packing_format = (datetime.strptime(str(start_packing), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_packing_format = (datetime.strptime(str(finish_packing), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_packing_format_uc = start_packing_format
                rec.finish_packing_format_uc = finish_packing_format
                
            if start_cleaning and finish_cleaning:
                start_cleaning_format = (datetime.strptime(str(start_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cleaning_format = (datetime.strptime(str(finish_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cleaning_format_uc = start_cleaning_format
                rec.finish_cleaning_format_uc = finish_cleaning_format
            
            if start_precleaning and finish_precleaning:
                start_precleaning_format = (datetime.strptime(str(start_precleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_precleaning_format = (datetime.strptime(str(finish_precleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_precleaning_format_uc = start_precleaning_format
                rec.finish_precleaning_format_uc = finish_precleaning_format
                
            if start_cutting and finish_cutting:
                start_cutting_format = (datetime.strptime(str(start_cutting), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cutting_format = (datetime.strptime(str(finish_cutting), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cutting_temp_format_uc = start_cutting_format
                rec.finish_cutting_format_uc = finish_cutting_format
            
            if start_cutting_old:
                start_cutting_old_format = (datetime.strptime(str(start_cutting_old), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cutting_format_uc = start_cutting_old_format
            
            if start_cooking and finish_cooking:
                start_cooking_format = (datetime.strptime(str(start_cooking), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cooking_format = (datetime.strptime(str(finish_cooking), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cooking_format_uc = start_cooking_format
                rec.finish_cooking_format_uc = finish_cooking_format
                
            if start_defrost and finish_defrost:
                start_defrost_format = (datetime.strptime(str(start_defrost), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_defrost_format = (datetime.strptime(str(finish_defrost), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_defrost_format_uc = start_defrost_format
                rec.finish_defrost_format_uc = finish_defrost_format
            
            if finish_cs:
                finish_cs_format = (datetime.strptime(str(finish_cs), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.finish_cs_format_uc = finish_cs_format
     
    # Untuk mencari nilai minimal dari waktu adj cutting
    @api.one
    def get_shift_potong(self):
        for rec in self:
            id_epi = rec.epi_id_uc
            
            min_adj_cutting = ""
            adj_cutting = ""
            
            if id_epi:
                # Cari min waktu adj cutting
                self.env.cr.execute("SELECT MIN(adj_cutting_uc) from sis_urut_cutting_line where epi_id_uc = '" + str(id_epi.id) + "'")
        
                sql = self.env.cr.fetchone()
                if sql:
                    min_adj_cutting = sql[0]
                    
                    if min_adj_cutting and adj_cutting:
                        # Perhitungan shift potong       
                        min_time_cutting = datetime.strptime(str(min_adj_cutting), "%Y-%m-%d %H:%M:%S")
                        adj_cutting = datetime.strptime(str(adj_cutting), "%Y-%m-%d %H:%M:%S")
                                                
                        hour_to_minute = (adj_cutting.hour * 60) + adj_cutting.minute
                        
                        if (adj_cutting.date() > min_time_cutting.date() and hour_to_minute >= 365):
                            rec.update({'shift_potong_uc': 'pp'})
                            
                        else:
                            rec.update({'shift_potong_uc': 'pm'})


class adj_cutting(models.Model):
    _name = 'sis.adj.cutting.line'
    
    no = fields.Integer()
    epi_id = fields.Many2one('sis.epi')
    adj_cutting = fields.Datetime(string="Adj Cutting")
    adj_cutting_temp = fields.Datetime(string="Adj Temp")
    hasil_urut_item = fields.Char(string="Hasil Urut Item")
    item_id = fields.Many2one('sis.pps.item', string="Item")
    cutting_time = fields.Float(string="Cutting Time")
    is_adj_cutting = fields.Boolean(default=False)
    fish_type_adj = fields.Many2one('sis.master.time', string="Fish Type")
    tonase_adj = fields.Float(string="Tonase")
    total_tonase_adj = fields.Float(string="Total Tonase")
    fish_qty_adj = fields.Float(string="Fish Qty(ton)")
    
     
    @api.onchange('adj_cutting')
    def flag_adj_cutting(self):
        for rec in self:
            if rec.adj_cutting:
                rec.update({'is_adj_cutting': True})
#     
    
                        
    
    
    