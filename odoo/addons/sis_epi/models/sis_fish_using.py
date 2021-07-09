

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import psycopg2
import xlsxwriter
import base64
import html2text


class fish_using(models.Model):
    _name = 'sis.epi.fish.using.line'
    
    epi_id_fu = fields.Many2one('sis.epi')
    epi_line_id_fu = fields.Many2one('sis.epi.line', ondelete='cascade')
    item_id_fu = fields.Many2one('sis.pps.item', string="Item")
    tonase_fu = fields.Float(string="Tonase")
    total_tonase_fu = fields.Float(string="Total Tonase")
    temp_total_tonase_fu = fields.Float(string="Temp", compute='compute_total_tonase')
    remark_fu = fields.Char(string="Remark")
    waktu_packing_fu = fields.Float(string="Est Wkt Pack(jam)")
    fish_type_fu = fields.Many2one('sis.master.time', string="Fish Type")
    urutan_item_fu = fields.Integer(string="No")
    urutan_item_fu_2 = fields.Integer(string="No")
    hasil_urut_item_fu = fields.Char(string="Urut Item", readonly=True)
    fish_qty_fu = fields.Float(string="Fish Qty(ton)")
    count = fields.Integer()
    is_new_item_fu = fields.Boolean()
    
    hasil_tonase = fields.Float(string="Hasil Tonase", store=True, compute='compute_hasil_tonase')
    jam_hasil_tonase = fields.Float(string="Jam Tonase", store=True, compute='compute_hasil_tonase')
    
    
    start_packing_fu = fields.Datetime(string="Start Pack")
    finish_packing_fu = fields.Datetime(string="Finish Pack")
    start_cleaning_fu = fields.Datetime(string="Start Clean")
    finish_cleaning_fu = fields.Datetime(string="Finish Clean")
    start_pre_cleaning_fu = fields.Datetime(string="Start Pre Clean")
    finish_pre_cleaning_fu = fields.Datetime(string="Finish Pre Clean")
    start_cooking_fu = fields.Datetime(string="Start Cook")
    finish_cooking_fu = fields.Datetime(string="Finish Cook")
    start_cutting_fu = fields.Datetime(string="Start Cutting")
    finish_cutting_fu = fields.Datetime(string="Finish Cutting")
    start_defrost_fu = fields.Datetime(string="Start Defrost")
    finish_defrost_fu = fields.Datetime(string="Finish Defrost")
    finish_cs_fu = fields.Datetime(string="Finish CS")
    
    start_packing_fu_temp = fields.Datetime(string="Start Pack Temp")
    
    finish_packing_format_fu = fields.Char(string="Finish Pack", compute='get_format_date')
    start_cleaning_format_fu = fields.Char(string="Start Clean", compute='get_format_date')
    finish_cleaning_format_fu = fields.Char(string="Finish Clean", compute='get_format_date')
    start_pre_cleaning_format_fu = fields.Char(string="Start Pre Clean", compute='get_format_date')
    finish_pre_cleaning_format_fu = fields.Char(string="Finish Pre Clean", compute='get_format_date')
    start_cooking_format_fu = fields.Char(string="Start Cook", compute='get_format_date')
    finish_cooking_format_fu = fields.Char(string="Finish Cook", compute='get_format_date')
    start_cutting_format_fu = fields.Char(string="Start Cutting", compute='get_format_date')
    finish_cutting_format_fu = fields.Char(string="Finish Cutting", compute='get_format_date')
    start_defrost_format_fu = fields.Char(string="Start Defrost", compute='get_format_date')
    finish_defrost_format_fu = fields.Char(string="Finish Defrost", compute='get_format_date')
    finish_cs_format_fu = fields.Char(string="Finish CS", compute='get_format_date')
    
    
    @api.one
    def get_format_date(self):
        for rec in self:
            finish_pack = rec.finish_packing_fu
            start_cleaning = rec.start_cleaning_fu
            finish_cleaning = rec.finish_cleaning_fu
            
            start_pre_cleaning = rec.start_pre_cleaning_fu
            finish_pre_cleaning = rec.finish_pre_cleaning_fu
            
            start_cooking = rec.start_cooking_fu
            finish_cooking = rec.finish_cooking_fu
            
            start_cutting = rec.start_cutting_fu
            finish_cutting = rec.finish_cutting_fu
            
            start_defrost = rec.start_defrost_fu
            finish_defrost = rec.finish_defrost_fu
            
            finish_cs = rec.finish_cs_fu
            
            format = "%Y-%m-%d %H:%M:%S"
            
            if finish_pack:
                finish_pack_format = (datetime.strptime(str(finish_pack), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
            
                rec.finish_packing_format_fu = finish_pack_format
            
            if start_cleaning and finish_cleaning:
                start_cleaning_format = (datetime.strptime(str(start_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cleaning_format = (datetime.strptime(str(finish_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cleaning_format_fu = start_cleaning_format
                rec.finish_cleaning_format_fu = finish_cleaning_format
            
            if start_pre_cleaning and finish_pre_cleaning:
                start_pre_cleaning_format = (datetime.strptime(str(start_pre_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_pre_cleaning_format = (datetime.strptime(str(finish_pre_cleaning), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_pre_cleaning_format_fu = start_pre_cleaning_format
                rec.finish_pre_cleaning_format_fu = finish_pre_cleaning_format
                
            if start_cooking and finish_cooking:
                start_cooking_format = (datetime.strptime(str(start_cooking), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cooking_format = (datetime.strptime(str(finish_cooking), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cooking_format_fu = start_cooking_format
                rec.finish_cooking_format_fu = finish_cooking_format
            
            if start_cutting and finish_cutting:
                start_cutting_format = (datetime.strptime(str(start_cutting), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_cutting_format = (datetime.strptime(str(finish_cutting), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_cutting_format_fu = start_cutting_format
                rec.finish_cutting_format_fu = finish_cutting_format
            
            if start_defrost and finish_defrost:
                start_defrost_format = (datetime.strptime(str(start_defrost), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                finish_defrost_format = (datetime.strptime(str(finish_defrost), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.start_defrost_format_fu = start_defrost_format
                rec.finish_defrost_format_fu = finish_defrost_format
            
            if finish_cs:
                finish_cs_format = (datetime.strptime(str(finish_cs), format) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                
                rec.finish_cs_format_fu = finish_cs_format
                
                
    
    # Fungsi untuk menghitung total tonase
    @api.onchange('fish_type_fu')
    def get_tonase(self):
        for rec in self:
             
            fish_type = rec.fish_type_fu
            fish_qty_fu = rec.fish_qty_fu
            tonase = 0
            tonase_before = 0
            total_tonase = 0
            no_urut = rec.urutan_item_fu
            no_urut_before = 0
            count = 0
            res = {}
            i = 1
            item_id = rec.item_id_fu
            hasil = 0
            tonase_next = 0
             
             
            if fish_type:
                for row in fish_type:
                    tonase = row.tonase
                 
                rec.tonase_fu = tonase * 10
                total_tonase = tonase * 10
                 
                 
                # Insert value tonase ke dalam item
#                 fish_using_line_temp_obj = rec.env['sis.epi.fish.using.temp.line'].search([('item_id_temp', '=', item_id.id)])
#                 
#                 if fish_using_line_temp_obj:
#                     total_tonase_temp = 0
#                     for aa in fish_using_line_temp_obj:
#                         item_id_temp = aa.item_id_temp
#                         total_tonase_temp = aa.total_tonase_temp
#                         
#                         hasil = total_tonase_temp + rec.tonase_fu
#                     fish_using_line_temp_obj.write({'total_tonase_temp': hasil})
 
                        
                # Jika line pertama (dikomen sementara)
#                 id = self._origin.id - 1
#                 sis_epi_obj = self.env['sis.epi.fish.using.line'].browse(id)
#                 temp_id = []
#                 if sis_epi_obj:
#                     temp_id.append(id)
#                     for line in sis_epi_obj:
#                         no_urut_before = line.urutan_item_fu
#                         tonase_before = line.tonase_fu
#                         total_tonase_before = line.total_tonase_fu
#                          
#                         # Jika item sama dengan item sebelumnya
#                         if no_urut == no_urut_before:
#                             total_tonase = total_tonase_before + total_tonase
#                              
#                             """
#                             if total_tonase > fish_qty_fu:
#                                 raise UserError(_(
#                                         'Total tonase can not bigger than qty fish!'))
#                             """
#                         # Jika yang di klik adalah line atasnya
#                         """
#                         else:
#                             id_plus = self._origin.id + 1
#                             sis_epi_obj_plus = self.env['sis.epi.fish.using.line'].browse(id_plus)
#                             if sis_epi_obj_plus:
#                                 for line_line in sis_epi_obj_plus:
#                                     no_urut_next = line_line.urutan_item_fu
#                                     tonase_next = line_line.tonase_fu
#                                      
#                                     if no_urut == no_urut_next:
#                                         total_tonase_next = tonase_next + total_tonase
#                                         line_line.write({'total_tonase_fu': total_tonase_next})
#                                         """
#                              
#                      
#                     rec.total_tonase_fu = total_tonase
#                     rec.count = count
                    
    
  
    
    # Calculate total hasil tonase per item
    @api.one
    def compute_total_tonase(self):
        for rec in self:
            id = self.id
            item_id = rec.item_id_fu
            tonase_fu = rec.tonase_fu
            epi_id = rec.epi_id_fu
            hasil = 0
            
            
            # Query untuk mencari line dengan item yang sama
            if item_id and tonase_fu != 0:
                self.env.cr.execute("SELECT id FROM sis_epi_fish_using_line WHERE item_id_fu = '"+ str(item_id.id) +"' AND epi_id_fu = '"+ str(epi_id.id) +"'")
                
                fish_using = self.env.cr.fetchall()
                if fish_using:
                    for row in fish_using:
                        id_line = row[0]
                        browse = self.env['sis.epi.fish.using.line'].browse(id_line)
                        if browse:
                            for line in browse:
                                hasil = hasil + line.tonase_fu
                                
                                
                            rec.temp_total_tonase_fu = hasil
                            
    
    @api.depends('tonase_fu', 'temp_total_tonase_fu', 'waktu_packing_fu')
    def compute_hasil_tonase(self):
        for rec in self:
            tonase_fu = rec.tonase_fu
            temp_total_tonase_fu = rec.temp_total_tonase_fu
            waktu_pck = rec.waktu_packing_fu
            hasil_tonase = rec.hasil_tonase
            
            if temp_total_tonase_fu != 0:
                hasil = (tonase_fu / temp_total_tonase_fu) * waktu_pck
                rec.hasil_tonase = hasil
                print("hasil tonase: ", hasil)
                rec.jam_hasil_tonase = hasil
                
                
    
    # Onchange urutan item
    @api.onchange('urutan_item_fu', 'urutan_item_fu_2')
    def onchange_urutan_item(self):
        for rec in self:
            urutan_item = rec.urutan_item_fu
            urutan_item_2 = rec.urutan_item_fu_2
            nol ="0"
            hasil = ""
            
            if urutan_item and urutan_item_2 == 0:
                hasil = str(urutan_item) + "." + nol
            
            if urutan_item == 0 and urutan_item_2:
                hasil = nol + "." + str(urutan_item_2)
                
            hasil = str(urutan_item) + "." + str(urutan_item_2)
            rec.update({'hasil_urut_item_fu': hasil})
    
    # Get estimasi pack dan qty fish
    @api.onchange('item_id_fu')
    def get_estimasi_pack(self):
        for rec in self:
            item_id = rec.item_id_fu
            epi_id = rec.epi_id_fu
            estimasi_pack = 0
            qty_fish = 0
            
            for row in epi_id:
                epi_line_ids = row.epi_line_ids
                
                for line in epi_line_ids:
                    item_id_epi = line.pps_item_id
                    
                    if item_id == item_id_epi:
                        estimasi_pack = line.waktu_packing_epi
                        qty_fish = line.qty_fish_total_epi
                        
                        rec.update({'waktu_packing_fu': estimasi_pack, 'fish_qty_fu': qty_fish})
                        
    
    
    
    

                    
            
  




                            
                
                    
                