
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.addons.sis_traceability.models.sis_cutting import cutting


class urut_cutting_wizard(models.TransientModel):
    _name = 'urut.cutting.wizard'
    
    
    epi_id_wiz = fields.Many2one('sis.epi', string="Epi Id Wiz")
    urut_cutting_ids = fields.One2many('urut.cutting.wizard.line', 'urut_cutting_wiz_id')
                                            
    
    @api.multi
    def adj_cutting_wiz(self):
        for rec in self:
            urut_cutting_ids = rec.urut_cutting_ids
            epi_id = rec.epi_id_wiz
            format_datetime = '%Y-%m-%d %H:%M:%S'
            temp = []
            temp_temp = []
            baris = 1
            i = 1
            
            # Sis epi object
            sis_epi_obj = rec.env['sis.epi'].search([('id', '=', epi_id.id)])
            
            if urut_cutting_ids:
                for row in urut_cutting_ids:
                    id_line = row.id
                    item = row.item_id_wiz
                    start_packing = row.start_packing_wiz
                    finish_packing = row.finish_packing_wiz
                    start_cleaning = row.start_cleaning_wiz
                    finish_cleaning = row.finish_cleaning_wiz
                    start_precleaning = row.start_precleaning_wiz
                    finish_precleaning = row.finish_precleaning_wiz
                    start_cutting = row.start_cutting_wiz
                    finish_cutting = row.finish_cutting_wiz
                    start_cooking = row.start_cooking_wiz
                    finish_cooking = row.finish_cooking_wiz
                    start_defrost = row.start_defrost_wiz
                    finish_defrost = row.finish_defrost_wiz
                    finish_cs = row.finish_cs_wiz
                    cutting_time = row.cutting_time_wiz
                    
                    adj_cutting_date = row.adj_cutting_wiz
                    adj_cutting_date_temp = row.adj_cutting_wiz_temp
                    hasil_urut_item = row.hasil_urut_item_wiz
                    urutan_item_wiz = row.urutan_item_wiz
                    fish_type = row.fish_type_wiz
                    remark = row.remark_wiz
                    tonase = row.tonase_wiz
                    total_tonase = row.total_tonase_wiz
                    fish_qty = row.fish_qty_wiz
                    
                    
                    # INSERT ADJ CUTTING LINE
                    values_adj = {}
                    values_adj['no'] = i
                    values_adj['item_id'] = item
                    values_adj['hasil_urut_item'] = hasil_urut_item
                    values_adj['cutting_time'] = cutting_time
                    values_adj['fish_type_adj'] = fish_type.id
                    values_adj['tonase_adj'] = tonase
                    values_adj['total_tonase_adj'] = total_tonase
                    values_adj['fish_qty_adj'] = fish_qty
                    
                    temp_temp.append((0, 0, values_adj))
                    
                    
                    # Insert ke urut cutting line
                    values = {}
                    values['no'] = i
                    values['urut_potong'] = baris
                    values['hasil_urut_item_uc'] = hasil_urut_item
                    values['urutan_item_uc'] = urutan_item_wiz
                    values['item_id_uc'] = item.id
                    values['fish_type_uc'] = fish_type.id
                    values['start_packing_uc'] = start_packing
                    values['finish_packing_uc'] = finish_packing
                    values['start_cleaning_uc'] = start_cleaning
                    values['finish_cleaning_uc'] = finish_cleaning
                    values['start_precleaning_uc'] = start_precleaning
                    values['finish_precleaning_uc'] = finish_precleaning
                    values['start_cutting_uc'] = start_cutting
                    values['finish_cutting_uc'] = finish_cutting
                    values['start_cooking_uc'] = start_cooking
                    values['finish_cooking_uc'] = finish_cooking
                    values['start_defrost_uc'] = start_defrost
                    values['finish_defrost_uc'] = finish_defrost
                    values['finish_cs_uc'] = finish_cs
                    values['remark_uc'] = remark
                    values['tonase_uc'] = tonase
                    values['total_tonase_uc'] = total_tonase
                    values['fish_qty_uc'] = fish_qty
                    
                    i = i + 1
                                    
                    
                    temp.append((0, 0, values))
                    
                # Insert ke urut cutting line 
                if sis_epi_obj:
#                     sis_epi_obj.update({'urut_cutting_line_ids': temp, 'state': 'urut_cutting'})
                    sis_epi_obj.update({'urut_cutting_line_ids': temp, 
                                        'adj_cutting_line_ids': temp_temp, 
                                        'state': 'adj_cutting'
                    })
                    
                        

class urut_cutting_wizard_line(models.TransientModel):
    _name = 'urut.cutting.wizard.line'
    _order = 'hasil_urut_item_wiz'
    
    urut_cutting_wiz_id = fields.Many2one('urut.cutting.wizard')
    item_id_wiz = fields.Many2one('sis.pps.item', string="Item")
    start_packing_wiz = fields.Datetime(string="Start Packing")
    finish_packing_wiz = fields.Datetime(string="Finish Packing")
    start_cleaning_wiz = fields.Datetime(string="Start Cleaning")
    finish_cleaning_wiz = fields.Datetime(string="Finish Cleaning")
    start_precleaning_wiz = fields.Datetime(string="Start Pre Cleaning")
    finish_precleaning_wiz = fields.Datetime(string="Finish Pre Cleaning")
    start_cutting_wiz = fields.Datetime(string="Start Cutting")
    finish_cutting_wiz = fields.Datetime(string="Finish Cutting")
    start_cooking_wiz = fields.Datetime(string="Start Cooking")
    finish_cooking_wiz = fields.Datetime(string="Finish Cooking")
    start_defrost_wiz = fields.Datetime(string="Start Defrost")
    finish_defrost_wiz = fields.Datetime(string="Finish Defrost")
    finish_cs_wiz = fields.Datetime(string="Finish CS")
    cutting_time_wiz = fields.Float(string="Cut Time")
    
    remark_wiz = fields.Char(string="Remark")
    hasil_urut_item_wiz = fields.Char(string="Urut Item")
    urutan_item_wiz = fields.Integer()
    shift_potong = fields.Selection([('pp', 'PP'), ('pm', 'PM')], string="Shift Potong", default=None)
    adj_cutting_wiz = fields.Datetime(string="Adj Cut")
    adj_cutting_wiz_temp = fields.Datetime(string="Adj Cut temp")
    fish_type_wiz = fields.Many2one('sis.master.time', string="Fish Type")
    tonase_wiz = fields.Float(string="Tonase")
    total_tonase_wiz = fields.Float(string="Total Tonase")
    fish_qty_wiz = fields.Float(string="Fish Qty(ton)")
    
    
    
    @api.onchange('adj_cutting_wiz')
    def onchange_adj_cutting(self):
        for rec in self:
            cutting_time = rec.cutting_time_wiz
            adj_cutting_date = rec.adj_cutting_wiz
            id_cut_wiz = rec.urut_cutting_wiz_id
            format_datetime = '%Y-%m-%d %H:%M:%S'
            
            adj_cutting_first = ""
            
            dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
            hour = int(dd[:2])
            minut = int(dd[3:])
            
            finish_adj = datetime.strptime(str(adj_cutting_date), format_datetime) + relativedelta(hours=hour, minutes=minut)
            rec.update({'adj_cutting_wiz_temp': finish_adj})
            
            
           
                    


    
    
    