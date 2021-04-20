'''
Created on Dec 22, 2020

@author: endah
'''
from odoo import models
from _datetime import datetime
from odoo.exceptions import UserError

class FishThawingXLSX(models.AbstractModel):
    _name = 'report.sis_traceability.fish_thawing_control_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Fish Thawing')
        
        #coulumn Set
        sheet.set_column('A:A',8)
        sheet.set_column('B:B',9.57)
        sheet.set_column('C:C',13.29)
        sheet.set_column('D:D',8)
        sheet.set_column('E:E',10.71)
        sheet.set_column('F:F',42.43)
        sheet.set_column('G:G',9.86)
        sheet.set_column('H:H',9.86)
        sheet.set_column('I:I',9.86)
        sheet.set_column('J:J',9.86)
        sheet.set_column('K:K',9.86)
        sheet.set_column('L:L',9.86)
        sheet.set_column('M:M',20)
        sheet.set_column('N:N',20)
#         sheet.set_row(6,0,71)
#         sheet.set_row(5,5, 4.5)
        
        #format
        head_format = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow'})
        head_format2 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'right'})
        head_format3 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'align': 'left', 'border':1})
        head_format3_2 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'align': 'left', 'border':1,'num_format': 'd mmmm yyyy'})
        head_format4 = workbook.add_format({'font_size':26, 'font_name': 'Arial Narrow', 'align': 'center', 'bold' : True})
        head_format5 = workbook.add_format({'font_size':24, 'font_name': 'Arial Narrow', 'align': 'center', 'italic' : True})
        th_format = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'center','valign':   'vcenter', 'border':1})
        th_format.set_text_wrap()
        td_format1 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'center','valign':   'vcenter', 'border':1})
        td_format2 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'center','valign':   'vcenter', 'border':1,'num_format': 'hh:mm'})
        foot_format1 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'align': 'left', 'border':1,'valign':   'vcenter'})
        foot_format2 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'align': 'center', 'border':1})
        foot_format3 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'center', 'border':1})
        foot_format3.set_text_wrap()
        
        #template write
        sheet.write(0,0, 'Cold Storage Section - PT. Aneka Tuna Indonesia', head_format)
        sheet.write(0,13, 'FRM.CS.11 2020-05-11', head_format2)
        sheet.merge_range(3, 0, 3, 1, 'TANGGAL / DATE', head_format3)
        sheet.merge_range(4, 0, 4, 1, 'SHIFT', head_format3)
        sheet.merge_range(4, 2, 4, 4, '', head_format3)
        sheet.merge_range(3, 5, 3, 13,'PEMERIKSAAN PELELEHAN IKAN', head_format4)
        sheet.merge_range(4, 5, 4, 13,'FISH THAWING CONTROL', head_format5)
        
        #Nama Kolom
        sheet.write(6,0, 'No. Potong\nCut Number', th_format)
        sheet.write(6,1, 'No. Fish Box\nFish Box Number', th_format)
        sheet.write(6,2, 'No Tangki\nTank No.', th_format)
        sheet.write(6,3, 'Line', th_format)
        sheet.write(6,4, 'Jenis dan Ukuran Ikan\nKind and Size of Fish', th_format)
        sheet.write(6,5, 'Nama Vessel\nVessel Name', th_format)
        sheet.write(6,6, 'Jam Ikan Keluar dari Cold Storage\nTime of Fish Out from CS', th_format)
        sheet.write(6,7, 'Jam Masuk ke Line\nTime of Entering to Line', th_format)
        sheet.write(6,8, 'Mulai Sirkulasi\nCirculation Start', th_format)
        sheet.write(6,9, 'Akhir Sirkulasi\nEnd Circulation', th_format)
        sheet.write(6,10, 'Suhu Awal', th_format)
        sheet.write(6,11, 'Suhu Akhir', th_format)
        sheet.write(6,12, 'Keterangan\nRemark', th_format)
        sheet.write(6,13, 'Tanda Tangan QCP \n QCP Sign', th_format)
        
        #variable iterasi
        it1 = 0
        tgl_prod=''
        
        #print data
        for obj in partners:
            if tgl_prod=='':
                tgl_prod=obj.tgl_produksi
            else:
                if tgl_prod!=obj.tgl_produksi:
                    raise UserError("Data yang dipilih memiliki Tanggal Produksi lebih dari satu")
                
            for det in obj.defrost_detail:
                sheet.write(it1+7,0, str(det.no_potong), td_format1)
                sheet.write(it1+7,1, det.fish_box_no, td_format1)
                sheet.write(it1+7,2, str(det.no_tangki), td_format1)
                
                if det.no_line:
                    sheet.write(it1+7,3, str(det.no_line), td_format1)
                else:
                    sheet.write(it1+7,3, ' ', td_format1)
                    
                sheet.write(it1+7,4, det.jenis_ikan+' '+det.ukuran_ikan, td_format1)
                sheet.write(it1+7,5, str(det.defrost_link_id.vessel_no), td_format1)
                
                jam_keluar_cs = datetime.strptime(det.defrost_link_id.tgl_keluar, "%Y-%m-%d %H:%M:%S")
                sheet.write(it1+7,6, jam_keluar_cs, td_format2)
                
                #belum ada datanya
                sheet.write(it1+7,7, ' ', td_format1)
                
                jam_mulai_def = datetime.strptime(det.tgl_start, "%Y-%m-%d %H:%M:%S")
                sheet.write(it1+7,8, jam_mulai_def, td_format2)
                
                jam_selesai_def = datetime.strptime(det.tgl_finish, "%Y-%m-%d %H:%M:%S")
                sheet.write(it1+7,9, jam_selesai_def, td_format2)                
                
                sheet.write(it1+7,10, str(det.suhu_before), td_format1)
                sheet.write(it1+7,11, str(det.suhu_after), td_format1)
                sheet.write(it1+7,12, str(det.remark), td_format1)
                it1=it1+1
            sheet.merge_range(7,13,it1+6,13, ' ', td_format1)
            
        #tanggal Produksi di atas
        productiondate = datetime.strptime(tgl_prod, "%Y-%m-%d")     
        sheet.merge_range(3, 2, 3, 4, productiondate, head_format3_2)
        
        sheet.merge_range(it1+8,0,it1+9,2, 'Standar BBT akhir pelelehan\nEnd Thawing BBT Standard',foot_format1)
        sheet.merge_range(it1+8,3,it1+8,4, "'-1 ~ 3°C (<7Kg)",foot_format2)
        sheet.merge_range(it1+9,3,it1+9,4, "'-2 ~ 3°C (>7Kg)",foot_format2)
        
        sheet.write(it1+11,0, "Catatan/ Note : ",head_format)
        sheet.write(it1+12,0, "No.1 : Tangki paling bawah/ The bottom tank",head_format)
        
        sheet.merge_range(it1+8,7,it1+9,10, "1 siklus/ 1 cycle : On 10'  - Off : 10'\nSuhu air kolam/ Water Tank Temperature : Max 15 °C",foot_format1)
        sheet.merge_range(it1+8,11,it1+9,11, "Penanggung Jawab",foot_format3)
        sheet.merge_range(it1+8,12,it1+8,13, "Diperiksa oleh/ Checked by",foot_format2)
        sheet.merge_range(it1+9,12,it1+9,13, "Cold Storage",foot_format2)
        sheet.merge_range(it1+10,11,it1+11,11, " ",foot_format3)
        sheet.merge_range(it1+10,12,it1+11,13, " ",foot_format3)
        
                

