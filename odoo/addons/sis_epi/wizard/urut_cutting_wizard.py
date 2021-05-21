
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
            baris = 1
            
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
                    fish_type = row.fish_type_wiz
                    
                    # Insert ke urut cutting line
                    values = {}
                    values['item_id_uc'] = item.id
                    values['fish_type_uc'] = fish_type.id
                    values['start_packing_uc'] = start_packing
                    values['finish_packing_uc'] = finish_packing
                    values['start_cleaning_uc'] = start_cleaning
                    values['finish_cleaning_uc'] = finish_cleaning
                    values['start_precleaning_uc'] = start_precleaning
                    values['finish_precleaning_uc'] = start_precleaning
                    values['start_cutting_uc'] = start_cutting
                    values['finish_cutting_uc'] = finish_cutting
                    values['start_cooking_uc'] = start_cooking
                    values['finish_cooking_uc'] = finish_cooking
                    values['start_defrost_uc'] = start_defrost
                    values['finish_defrost_uc'] = finish_defrost
                    values['finish_cs_uc'] = finish_cs
                    
                    # Jika ada adj cutting dan cutting time
                    if adj_cutting_date and cutting_time:
                        dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
                        hour = int(dd[:2])
                        minut = int(dd[3:])
                        
                        finish_adj = datetime.strptime(str(adj_cutting_date), format_datetime) + relativedelta(hours=hour, minutes=minut)
                        
                        values['cutting_time_uc'] = cutting_time
                        values['adj_cutting_uc'] = adj_cutting_date
                        values['adj_cutting_uc_temp'] = finish_adj
                        
                        # Perhitunga toleransi (waktu awal - adj cutting)
                        waktu_awal = datetime.strptime(str(start_cutting), format_datetime)
                        waktu_adj_cutting = datetime.strptime(str(adj_cutting_date), format_datetime)
                        
                        # Di ubah ke hitungan menit, misal (1.35 jam -> 95 menit)
                        toleransi = (waktu_awal - waktu_adj_cutting).total_seconds() / 60.0
                        hasil_toleransi = (toleransi / 60) / 24 # Perhitungan rumus dari excel
                        hasil = round(hasil_toleransi, 2)
                        
                        waktu_awal_compare = datetime.strptime(str(start_cutting), format_datetime) + relativedelta(hours=float(7))
                        waktu_adj_cutting_compare = datetime.strptime(str(adj_cutting_date), format_datetime) + relativedelta(hours=float(7))
                        
                        
                        if waktu_awal_compare > waktu_adj_cutting_compare:
                            values['toleransi'] = hasil * -1
                            print ("True")
                        else:
                            print ("False")
                            values['toleransi'] = hasil * -1
                
                        
                    # jika jam adj tidak diisi
                    else:
                        browse = self.env['urut.cutting.wizard.line'].browse(id_line-1)
                        
                        for line_before in browse:
                            adj_cutting_temp = line_before.adj_cutting_wiz_temp
                            # Insert adj cutting wizard 
                            row.write({'adj_cutting_wiz': adj_cutting_temp})
                            
                            if row.adj_cutting_wiz:
                                dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
                                hour = int(dd[:2])
                                minut = int(dd[3:])
                        
                                
                                finish_adj = datetime.strptime(str(row.adj_cutting_wiz), format_datetime) + relativedelta(hours=hour, minutes=minut)
                                # Insert finish cutting di adj cutting wizard
                                row.write({'adj_cutting_wiz_temp': finish_adj})
                                
                                # Isi urut cutting line epi
                                values['adj_cutting_uc'] = row.adj_cutting_wiz
                                values['adj_cutting_uc_temp'] = row.adj_cutting_wiz_temp
                                
                                values['cutting_time_uc'] = cutting_time
                                
                                # Perhitunga toleransi (waktu awal - adj cutting)
                                waktu_awal = datetime.strptime(str(row.start_cutting_wiz), format_datetime)
                                waktu_adj_cutting = datetime.strptime(str(row.adj_cutting_wiz_temp), format_datetime)
                                
                                # Di ubah ke hitungan menit, misal (1.35 jam -> 95 menit)
                                toleransi = (waktu_awal - waktu_adj_cutting).total_seconds() / 60.0
                                hasil_toleransi = (toleransi / 60) / 24 # Perhitungan rumus dari excel
                                hasil = round(hasil_toleransi, 2)
                                
                                waktu_awal_compare = datetime.strptime(str(row.start_cutting_wiz), format_datetime) + relativedelta(hours=float(7))
                                waktu_adj_cutting_compare = datetime.strptime(str(row.adj_cutting_wiz_temp), format_datetime) + relativedelta(hours=float(7))
                                
                                
                                if waktu_awal_compare > waktu_adj_cutting_compare:
                                    values['toleransi'] = hasil * -1
                                    print ("True")
                                else:
                                    print ("False")
                                    values['toleransi'] = hasil * -1
                
                    
                    temp.append((0, 0, values))
                    
                # Insert ke urut cutting lin    
                if sis_epi_obj:
                    sis_epi_obj.update({'urut_cutting_line_ids': temp})
                    
                        

class urut_cutting_wizard_line(models.TransientModel):
    _name = 'urut.cutting.wizard.line'
    
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
    hasil_urut_item_wiz = fields.Char(string="Urut Item", readonly=True)
    shift_potong = fields.Selection([('pp', 'PP'), ('pm', 'PM')], string="Shift Potong", default=None)
    adj_cutting_wiz = fields.Datetime(string="Adj Cut")
    adj_cutting_wiz_temp = fields.Datetime(string="Adj Cut temp")
    fish_type_wiz = fields.Many2one('sis.master.time', string="Fish Type")
    
    
    @api.onchange('adj_cutting_wiz')
    def onchange_adj_cutting(self):
        for rec in self:
            cutting_time = rec.cutting_time_wiz
            adj_cutting_date = rec.adj_cutting_wiz
            format_datetime = '%Y-%m-%d %H:%M:%S'
            
            dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
            hour = int(dd[:2])
            minut = int(dd[3:])
            
            finish_adj = datetime.strptime(str(adj_cutting_date), format_datetime) + relativedelta(hours=hour, minutes=minut)
            rec.update({'adj_cutting_wiz_temp': finish_adj})


    
    
    