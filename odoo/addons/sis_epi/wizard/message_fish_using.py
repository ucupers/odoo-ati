
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import math


class fish_using_wizard_message(models.TransientModel):
    _name = 'message.fish.using'
    
    name = fields.Char(readonly=True)
    id_epi = fields.Many2one('sis.epi')
    
    @api.multi
    def create_fish_using_wiz(self):
        for rec in self:
            epi_id = rec.id_epi
            temp = []
            item_temp = 0
            i = 1
            temp_temp = []
            
            # Delete data fish using line first
            rec.delete_fish_using_line()
            
            # Create temporary line untuk tab fish using
#             values_temp = {}
#             values_temp['urutan_item_fu'] = 0
#             
#             temp.append((0, 0, values_temp))
#             
            for row in epi_id:
                for line in row.epi_line_ids:
                    start_packing = line.start_packing_epi
                    item_id = line.pps_item_id
                    start_packing = line.start_packing_epi
                    waktu_estimasi_pack = line.waktu_packing_epi
                    yield_total = (line.yield_total_epi / 1000)
                    qty_fish_total = line.qty_fish_total_epi
                    
                    j = 0
                    
                    # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
                    if qty_fish_total > 0:
                        row_fish_using = qty_fish_total / 4
                        hasil_bagi = math.floor(row_fish_using)
                        
                        # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                        if hasil_bagi == 0:
                            values = {}
                            values['epi_line_id_fu'] = line.id
                            values['item_id_fu'] = item_id.id
                            values['waktu_packing_fu'] = waktu_estimasi_pack
                            values['fish_qty_fu'] = qty_fish_total
                            values['start_packing_fu'] = start_packing
                            values['urutan_item_fu'] = i + 1 # No urut bertambah
                            values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                            values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                            i = i + 1
                            j = 1
                            
                            temp.append((0, 0, values))
                        
                        # Jika hasil bagi > 0
                        else:
                            
                            baris = 1
                            # Insert ke fish using line (pembulatan ke bawah)
                            for line_line in range(hasil_bagi):
                                # Jika line pertama pada item baru, input start packing
                                
                                values = {}
                                values['epi_line_id_fu'] = line.id
                                values['item_id_fu'] = item_id.id
                                values['waktu_packing_fu'] = waktu_estimasi_pack
                                values['fish_qty_fu'] = qty_fish_total
                                
                                if baris == 1:
                                    values['start_packing_fu'] = start_packing
                                    baris = baris + 1
                                
                                # Jika item sama dengan sebelumnya
                                if item_temp == 0 or item_temp == item_id.id:
                                    values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
                                    values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
                                    values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                    j = j + 1
                                
                                # Jika item berbeda
                                else:
                                    values['start_packing_fu'] = start_packing
                                    values['urutan_item_fu'] = i + 1 # No urut bertambah
                                    values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                                    values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                                    i = i + 1
                                    j = 1
                            
                                item_temp = item_id.id
                                temp.append((0, 0, values))
                            
                return row.update({'fish_using_line_ids': temp, 'state': 'fish_using'})
            
        
    @api.multi
    def delete_fish_using_line(self):
        fish_using_line = []
        epi_id = self.id_epi
        
        epi_obj = self.env['sis.epi'].search([('id', '=', epi_id.id)])
        if epi_obj:        
            fish_using_line.append(([5]))

            return epi_obj.update({'fish_using_line_ids': fish_using_line})
        
        
        
            
                