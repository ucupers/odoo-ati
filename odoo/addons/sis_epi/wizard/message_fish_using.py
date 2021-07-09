
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math


class fish_using_wizard_message(models.TransientModel):
    _name = 'message.fish.using'
    
    name = fields.Char(readonly=True)
    id_epi = fields.Many2one('sis.epi')
    urutan_item_last = fields.Integer()
    
    @api.multi
    def create_fish_using_wiz(self):
        for rec in self:
            epi_id = rec.id_epi
            temp = []
            item_temp = 0
            i = rec.urutan_item_last
            baris = 1
            temp_temp = []
            item_array = []
            nama = ""
            id_line_max = 0
            max_urutan_item = 0
            item_error = []
            

            # Looping data epi line
            for row_row in epi_id:
                
                for row in row_row.epi_line_ids:
                    start_packing = row.start_packing_epi
                    item_id = row.pps_item_id
                    start_packing = row.start_packing_epi
                    waktu_estimasi_pack = row.waktu_packing_epi
                    yield_total = (row.yield_total_epi / 1000)
                    qty_fish_total = row.qty_fish_total_epi
                    remark = row.remark_epi
                    epi_line_temp = row.sis_epi_line_temp_ids
                    epi_line_temp_count = len(row.sis_epi_line_temp_ids)
                    is_new_item_epi = row.is_new_item_epi
    
                    if qty_fish_total != 0 and is_new_item_epi == True:
                        
                        # Cek terlebih dahulu, apakah item sudah ada pada fish using line?
                        fish_using_obj = self.env['sis.epi.fish.using.line'].search([('epi_id_fu', '=', epi_id.id), ('item_id_fu', '=', item_id.id)])
                        if fish_using_obj:
                            item_error.append((item_id))
                            
                            # jika ada item, maka error
                            if item_error:
                                raise UserError(_(
                                        'Item ' + str(item_id.description) + ' has been exist in Fish Using line!'))
                            
                        # Jika mash dalam satu item yang sama
                        if item_temp == item_id.id:
                            j = 0
                            if epi_line_temp:
                                for epi_detail in epi_line_temp:
                                    qty_fish_temp = epi_detail.qty_fish_temp
                                    size_fish_temp = epi_detail.size_fish_temp
                                    no_urut_temp = epi_detail.no_urut
                                    
                                    # Line temporary untuk mengisi qty actual dan fish size
                                    # Jika jumlah line temp fish == 1 dan qty fish tidak NOL
                                    if epi_line_temp_count == 1 and qty_fish_temp != 0:
                                        
                                        # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
                                        if qty_fish_temp > 0:
                                            row_fish_using = qty_fish_temp / 4
                                            hasil_bagi = math.floor(row_fish_using)
                                            
                                            # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                                            if hasil_bagi == 0 or hasil_bagi == 1:
                                                values = {}
                                                values['epi_line_id_fu'] = row.id
                                                values['item_id_fu'] = item_id.id
                                                values['waktu_packing_fu'] = waktu_estimasi_pack
                                                values['fish_qty_fu'] = qty_fish_total
                                                values['start_packing_fu'] = start_packing
                                                values['remark_fu'] = remark
                                                values['urutan_item_fu'] = i # No urut bertambah
                                                values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                values['is_new_item_fu'] = True
                                                i = i
                                                j = j + 1
                                                
                                                item_temp = item_id.id
                                                temp.append((0, 0, values))
                                            
                                            # Jika jumlah line temp cuman satu, tapi qty > 4 maka:
                                            else:
                                                
                                                for line in range(hasil_bagi):
                                                    values = {}
                                                    
                                                    values['epi_line_id_fu'] = row.id
                                                    values['item_id_fu'] = item_id.id
                                                    values['waktu_packing_fu'] = waktu_estimasi_pack
                                                    values['fish_qty_fu'] = qty_fish_total
                                                    values['remark_fu'] = remark
                                                    values['is_new_item_fu'] = True
                                                    
                                                    if no_urut_temp == 1 and baris ==1:
                                                        values['start_packing_fu'] = start_packing
                                                        values['urutan_item_fu'] = i # No urut bertambah
                                                        values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        
                                                        i = i
                                                        j = j + 1
                                                        baris = baris + 1
                                                        item_temp = item_id.id
                                                    
                                                    
                                                    # Jika baris kedua
                                                    else:
                                                        values['epi_line_id_fu'] = row.id
                                                        values['item_id_fu'] = item_id.id
                                                        values['waktu_packing_fu'] = waktu_estimasi_pack
                                                        values['fish_qty_fu'] = qty_fish_total
                                                        values['remark_fu'] = remark
                                                        # Jika item sama dengan item sebelumnya
                                                        if item_temp == item_id.id:
                                                            
                                                            values['urutan_item_fu'] = i # No urut bertambah
                                                            values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            j = j + 1
                                                        
                                                        # jika item berbeda dengan sebelumnya
                                                        else:
                                                            
                                                            values['start_packing_fu'] = start_packing
                                                            values['urutan_item_fu'] = i # No urut bertambah
                                                            values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            
                                                            i = i + 1
                                                            j = 1
                                                        
                                                    item_temp = item_id.id
                                                    temp.append((0, 0, values))
                                    
                                    # Jika jumlah line temp fish > dari satu ukuran / lebih dari satu line temp, maka :
                                    else:
                                        
                                        if qty_fish_temp > 0:
                                            row_fish_using = qty_fish_temp / 4
                                            hasil_bagi = math.floor(row_fish_using)
                                            
                                            # Jika qty yang diisi < 4, maka :
                                            # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                                            if hasil_bagi == 0 or hasil_bagi == 1:
                                                values = {}
                                                values['epi_line_id_fu'] = row.id
                                                values['item_id_fu'] = item_id.id
                                                values['waktu_packing_fu'] = waktu_estimasi_pack
                                                values['fish_qty_fu'] = qty_fish_total
                                                values['remark_fu'] = remark
                                                values['is_new_item_fu'] = True
                                                    
                                                if no_urut_temp == 1 and qty_fish_temp != 0:
                                                    
                                                    values['start_packing_fu'] = start_packing
                                                    values['urutan_item_fu'] = i  # No urut bertambah
                                                    values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                    values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                    
                                                    j = j + 1
                                                    i = i
                                        
                                                # Jika bukan baris pertama
                                                else:
                                                    
                                                    if item_temp == item_id.id:
                                                        
                                                        values['urutan_item_fu'] = i  # No urut bertambah
                                                        values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        i = i
                                                        j = j + 1
                                                        
                                                    
                                                item_temp = item_id.id
                                                temp.append((0, 0, values))
                                            
                                            else:
                                                # Looping sesuai jumlah qty actual fish / 4
                                                for line in range(hasil_bagi):
                                                    
                                                    values = {}
                                                    values['epi_line_id_fu'] = row.id
                                                    values['item_id_fu'] = item_id.id
                                                    values['waktu_packing_fu'] = waktu_estimasi_pack
                                                    values['fish_qty_fu'] = qty_fish_total
                                                    values['remark_fu'] = remark
                                                    values['is_new_item_fu'] = True
                                                    
                                                    # Jika baris pertama
                                                    if no_urut_temp == 1 and baris == 1:
                                                        values['start_packing_fu'] = start_packing
                                                        values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
                                                        values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        
                                                        j = j + 1
                                                        baris = baris + 1
                                                        
                                                    
                                                    # jika baris kedua
                                                    else:
                                                        if item_temp == item_id.id:
                                                            values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
                                                            values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            j = j + 1
                                                        
                                                        # jika item berbeda dengan sebelumnya
                                                        else:
                                                            values['epi_line_id_fu'] = row.id
                                                            values['item_id_fu'] = item_id.id
                                                            values['waktu_packing_fu'] = waktu_estimasi_pack
                                                            values['fish_qty_fu'] = qty_fish_total
                                                            values['remark_fu'] = remark
                                                            values['start_packing_fu'] = start_packing
                                                            values['urutan_item_fu'] = i + 1 # No urut bertambah
                                                            values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            values['is_new_item_fu'] = True
                                                            
                                                            i = i + 1
                                                            j = 1
                                                    
                                                    item_temp = item_id.id      
                                                    temp.append((0, 0, values))
                                                    
                        # Jika item pada epi line berbeda
                        else:
                            j = 0
                            
                            if epi_line_temp:
                                for epi_detail in epi_line_temp:
                                    qty_fish_temp = epi_detail.qty_fish_temp
                                    size_fish_temp = epi_detail.size_fish_temp
                                    no_urut_temp = epi_detail.no_urut
                                    
                                    # Line temporary untuk mengisi qty actual dan fish size
                                    # Jika jumlah line temp fish == 1 dan qty fish tidak NOL
                                    if epi_line_temp_count == 1 and qty_fish_temp != 0:
                                        
                                        # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
                                        if qty_fish_temp > 0:
                                            row_fish_using = qty_fish_temp / 4
                                            hasil_bagi = math.floor(row_fish_using)
                                            
                                            # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                                            if hasil_bagi == 0 or hasil_bagi == 1:
                                                values = {}
                                                values['epi_line_id_fu'] = row.id
                                                values['item_id_fu'] = item_id.id
                                                values['waktu_packing_fu'] = waktu_estimasi_pack
                                                values['fish_qty_fu'] = qty_fish_total
                                                values['start_packing_fu'] = start_packing
                                                values['remark_fu'] = remark
                                                values['urutan_item_fu'] = i # No urut bertambah
                                                values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                values['is_new_item_fu'] = True
                                                
                                                i = i
                                                j = j + 1
                                                
                                                item_temp = item_id.id
                                                temp.append((0, 0, values))
                                            
                                            # Jika jumlah line temp cuman satu, tapi qty > 4 maka:
                                            else:
                                                
                                                for line in range(hasil_bagi):
                                                    values = {}
                                                    
                                                    values['epi_line_id_fu'] = row.id
                                                    values['item_id_fu'] = item_id.id
                                                    values['waktu_packing_fu'] = waktu_estimasi_pack
                                                    values['fish_qty_fu'] = qty_fish_total
                                                    values['remark_fu'] = remark
                                                    values['is_new_item_fu'] = True
                                                    
                                                    if no_urut_temp == 1 and baris ==1:
                                                        values['start_packing_fu'] = start_packing
                                                        values['urutan_item_fu'] = i # No urut bertambah
                                                        values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        
                                                        
                                                        j = j + 1
                                                        baris = baris + 1
                                                        item_temp = item_id.id
                                                    
                                                    
                                                    # Jika baris kedua
                                                    else:
                                                        values['epi_line_id_fu'] = row.id
                                                        values['item_id_fu'] = item_id.id
                                                        values['waktu_packing_fu'] = waktu_estimasi_pack
                                                        values['fish_qty_fu'] = qty_fish_total
                                                        values['remark_fu'] = remark
                                                        values['is_new_item_fu'] = True
                                                        # Jika item sama dengan item sebelumnya
                                                        if item_temp == item_id.id:
                                                            
                                                            values['urutan_item_fu'] = i # No urut bertambah
                                                            values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            j = j + 1
                                                        
                                                        # jika item berbeda dengan sebelumnya
                                                        else:
                                                            
                                                            values['start_packing_fu'] = start_packing
                                                            values['urutan_item_fu'] = i # No urut bertambah
                                                            values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            
                                                            i = i 
                                                            j = 1
                                                        
                                                    item_temp = item_id.id
                                                    temp.append((0, 0, values))
                                    
                                    # Jika jumlah line temp fish > dari satu ukuran / lebih dari satu line temp, maka :
                                    else:
                                        
                                        if qty_fish_temp > 0:
                                            row_fish_using = qty_fish_temp / 4
                                            hasil_bagi = math.floor(row_fish_using)
                                            
                                            # Jika qty yang diisi < 4, maka :
                                            # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                                            if hasil_bagi == 0 or hasil_bagi == 1:
                                                values = {}
                                                values['epi_line_id_fu'] = row.id
                                                values['item_id_fu'] = item_id.id
                                                values['waktu_packing_fu'] = waktu_estimasi_pack
                                                values['fish_qty_fu'] = qty_fish_total
                                                values['remark_fu'] = remark
                                                values['is_new_item_fu'] = True
                                                    
                                                if no_urut_temp == 1 and qty_fish_temp != 0:
                                                    
                                                    values['start_packing_fu'] = start_packing
                                                    values['urutan_item_fu'] = i  # No urut bertambah
                                                    values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                    values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                    
                                                    j = j + 1
                                                    i = i
                                        
                                                # Jika bukan baris pertama
                                                else:
                                                    
                                                    if item_temp == item_id.id:
                                                        
                                                        values['urutan_item_fu'] = i  # No urut bertambah
                                                        values['urutan_item_fu_2'] = j + 1 # No urut pertama balik ke angka satu
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        i = i
                                                        j = j + 1
                                                        
                                                    
                                                item_temp = item_id.id
                                                temp.append((0, 0, values))
                                            # Jika hasil bagi > 0, atau yang di input > 4, maka :
                                            else:
                                                # Looping sesuai jumlah qty actual fish / 4
                                                for line in range(hasil_bagi):
                                                    
                                                    values = {}
                                                    values['epi_line_id_fu'] = row.id
                                                    values['item_id_fu'] = item_id.id
                                                    values['waktu_packing_fu'] = waktu_estimasi_pack
                                                    values['fish_qty_fu'] = qty_fish_total
                                                    values['remark_fu'] = remark
                                                    values['is_new_item_fu'] = True
                                                    
                                                    # Jika baris pertama
                                                    if no_urut_temp == 1 and baris == 1:
                                                        values['start_packing_fu'] = start_packing
                                                        values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
                                                        values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
                                                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                        
                                                        j = j + 1
                                                        baris = baris + 1
                                                        
                                                    
                                                    # jika baris kedua
                                                    else:
                                                        if item_temp == item_id.id:
                                                            values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
                                                            values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            j = j + 1
                                                        
                                                        # jika item berbeda dengan sebelumnya
                                                        else:
                                                            values['epi_line_id_fu'] = row.id
                                                            values['item_id_fu'] = item_id.id
                                                            values['waktu_packing_fu'] = waktu_estimasi_pack
                                                            values['fish_qty_fu'] = qty_fish_total
                                                            values['remark_fu'] = remark
                                                            values['start_packing_fu'] = start_packing
                                                            values['urutan_item_fu'] = i + 1 # No urut bertambah
                                                            values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                                            values['is_new_item_fu'] = True
                                                            
                                                            i = i + 1
                                                            j = 1
                                                    
                                                    item_temp = item_id.id      
                                                    temp.append((0, 0, values))
                                    
                            i = i + 1               
                        item_temp = item_id.id  
                        
                # ubah i = urutan terakhir fish using
#                 i = max_urutan_item + 1
                           
            return row_row.update({'fish_using_line_ids': temp, 'state': 'fish_using'})
                         
        
    @api.multi
    def delete_fish_using_line(self):
        fish_using_line = []
        epi_id = self.id_epi
        
        epi_obj = self.env['sis.epi'].search([('id', '=', epi_id.id)])
        if epi_obj:        
            fish_using_line.append(([5]))

            return epi_obj.update({'fish_using_line_ids': fish_using_line})
        
        
        
            
                