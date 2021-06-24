'''
Created on Dec 23, 2020

@author: endah
'''
from odoo import models
from _datetime import datetime


class QCCutting(models.AbstractModel):
    _name = 'report.sis_traceability.quality_control_cutting_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Quality Control Cutting')
        
        #coulumn Set
        sheet.set_column('A:A',27.71)
        sheet.set_column('B:B',13.43)
        sheet.set_column('C:C',13.43)
        sheet.set_column('D:D',13.43)
        sheet.set_column('E:E',0.5)
        sheet.set_column('F:F',13.43)
        sheet.set_column('G:G',13.43)
        sheet.set_column('H:H',13.43)
        sheet.set_column('I:I',13.43)
        sheet.set_column('J:J',13.43)
        sheet.set_column('K:K',5.29)
        sheet.set_column('L:L',7.14)
        sheet.set_column('M:M',13.43)
        
        #format
        head_format = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow'})
        head_format2 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'align': 'right'})
        head_format3 = workbook.add_format({'font_size':16, 'font_name': 'Arial Narrow', 'align': 'center'})
        head_format4 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1})
        head_format5 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1, 'align': 'center'})
        
        #th format
        th_format1 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1})
        th_format2 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1})
        th_format2.set_text_wrap()
        
        #td format        
        td_format1 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1, 'align': 'center'})
        td_format2 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1, 'align': 'center', 'valign': 'center'})
        td_format2.set_text_wrap()
        td_time = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border':1, 'num_format':'HH:MM', 'align': 'center'})
        
        #foot Format
        fo_format = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'border':1})
        fo_formathead = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'border':1})
        fo_formathead.set_bg_color('#7F8C8D')
        fo_format_wrap = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'border':1, 'align': 'center', 'valign': 'center'})
        fo_format_wrap.set_text_wrap()
        fo_format2 = workbook.add_format({'font_size':8, 'font_name': 'Arial Narrow'})
        
        #template write Header
        sheet.write(0,0, 'Raw Material Section - PT. Aneka Tuna Indonesia', head_format)
        sheet.write(0,12, 'FRM.RM.03  2020-02-03', head_format2)
        sheet.merge_range(1,0,1,8, 'KONTROL KUALITAS IKAN DI BAGIAN CUTTING - COOKING',head_format3)
        sheet.merge_range(2,0,2,8, 'RAW FISH QUALITY CONTROL CUTTING - COOKING SECTION',head_format3)
        sheet.merge_range(1,9,1,10, 'TANGGAL / DATE ', head_format4)
        sheet.merge_range(2,9,2,10, 'SHIFT ', head_format4)
        sheet.merge_range(1,11,1,12, ' ', head_format4)
        sheet.merge_range(2,11,2,12, 'PP / PM ', head_format5)
        
        #template write Footer
        sheet.write(25,0, 'BBT Standard : < 4°C', fo_format)
        sheet.write(26,0, 'O = OK', fo_format)
        sheet.write(27,0, 'L = LARVA (White)', fo_format)
        sheet.write(28,0, 'X = LAIN-LAIN (Parasit)', fo_format)
        sheet.write(25,2, 'NILAI / GRADE', fo_formathead)
        sheet.write(26,2, 'A = VERY GOOD', fo_format)
        sheet.write(27,2, 'B = GOOD', fo_format)
        sheet.write(28,2, 'C = MEDIUM', fo_format)
        sheet.write(29,2, 'D = BAD', fo_format)
        sheet.write(25,3, 'ANGKA / SCORE', fo_formathead)
        sheet.write(26,3, '9', fo_format)
        sheet.write(27,3, '7 - 8', fo_format)
        sheet.write(28,3, '5 - 6', fo_format)
        sheet.write(29,3, '1 - 3', fo_format)
        sheet.write(30,2, 'Penentuan angka berdasarkan penilaian organoleptik/ Determine of score based on organoleptic value (STD.QC.12)', fo_format2)
        sheet.merge_range(25,5,25,6, 'IKAN RIJEK / REJECTED FISH', fo_formathead)
        sheet.merge_range(26,5,26,6, ' ', fo_format)
        sheet.merge_range(27,5,27,6, ' ', fo_format)
        sheet.merge_range(28,5,28,6, ' ', fo_format)
        sheet.merge_range(29,5,29,6, ' ', fo_format)
        sheet.write(25,7, 'JUMLAH/ QTY (kg)', fo_formathead)
        sheet.write(26,7, ' ', fo_format)
        sheet.write(27,7, ' ', fo_format)
        sheet.write(28,7, ' ', fo_format)
        sheet.write(29,7, ' ', fo_format)
        sheet.merge_range(25,9,26,10, 'Penanggung Jawab\nIn Charge', fo_format_wrap)
        sheet.merge_range(25,11,26,12, 'Disetujui Oleh\nApproved By', fo_format_wrap)
        sheet.merge_range(27,9,29,10, '', fo_format_wrap)
        sheet.merge_range(27,11,29,12, '', fo_format_wrap)
        
        #nama Kolom
        sheet.write(4,0, 'No.Potong/ Cutting No.',th_format1)
        sheet.write(5,0, 'No. Tangki Defrost\nDefrost Tank No.', th_format2)
        sheet.write(6,0, 'Jenis Ikan / Kind Of Fish', th_format1)
        sheet.write(7,0, 'Ukuran/ Size', th_format1)
        sheet.write(8,0, 'Nama Vessel dan Voyage\nVessel Name and Voyage', th_format2)
        sheet.write(9,0, 'Hatch', th_format1)
        sheet.write(10,0, 'Suhu Punggung Ikan\nBack Bone Temperature  (OC)', th_format2)
        sheet.write(11,0, 'Jam Potong/ Cutting Time', th_format1)
        sheet.write(12,0, 'Nomor Basket\nBasket No.', th_format2)
        sheet.write(13,0, 'Mata/ Eyes', th_format1)
        sheet.write(14,0, 'Insang/ Gill', th_format1)
        sheet.write(15,0, 'Kulit / Skin', th_format1)
        sheet.write(16,0, 'Kerusakan Fisik\nPhysical Damage', th_format2)
        sheet.write(17,0, 'Tekstur/ Texture', th_format1)
        sheet.write(18,0, 'Rongga Perut/ Belly Cavity', th_format1)
        sheet.write(19,0, 'Bau/ Odour', th_format1)
        sheet.write(20,0, 'Nilai/ Grade Assigned', th_format1)
        sheet.write(21,0, 'Parasit/ Parasite', th_format1)
        sheet.write(22,0, 'Tanda tangan QCP/ QCP Sign', th_format1)
        sheet.write(23,0, 'Keterangan\nRemark', th_format1)
        
        #variable
        ite=0
        
        #data
        for obj in partners:
            ite2=0
            
            if ite==3 or ite==9: 
                sheet.merge_range(4,1+ite,4,2+ite, str(obj.no_potong), td_format1)
                sheet.merge_range(5,1+ite,5,2+ite, str(obj.list_tangki), td_format1)
                sheet.merge_range(6,1+ite,6,2+ite, ' ', td_format1)
                sheet.merge_range(7,1+ite,7,2+ite, ' ', td_format1)
                sheet.merge_range(8,1+ite,8,2+ite, ' ', td_format1)
                sheet.merge_range(9,1+ite,9,2+ite, ' ', td_format1)
                sheet.merge_range(10,1+ite,10,2+ite, "'"+str(obj.suhu)+" - "+str(obj.suhu_akhir), td_format1)
                
                jam_potong = datetime.strptime(obj.jam_potong, "%Y-%m-%d %H:%M:%S")
                sheet.merge_range(11,1+ite,11,2+ite, jam_potong, td_time)
                
                sheet.merge_range(12,1+ite,12,2+ite, str(obj.list_basket), td_format1)
                sheet.merge_range(13,1+ite,13,2+ite, str(obj.eyes), td_format1)
                sheet.merge_range(14,1+ite,14,2+ite, str(obj.gill), td_format1)
                sheet.merge_range(15,1+ite,15,2+ite, str(obj.skin), td_format1)
                sheet.merge_range(16,1+ite,16,2+ite, str(obj.physical_damage), td_format1)
                sheet.merge_range(17,1+ite,17,2+ite, str(obj.texture), td_format1)
                sheet.merge_range(18,1+ite,18,2+ite, str(obj.belly_cavity), td_format1)
                sheet.merge_range(19,1+ite,19,2+ite, str(obj.odour), td_format1)
                sheet.merge_range(20,1+ite,20,2+ite, str(obj.grade_assigned), td_format1)
                sheet.merge_range(21,1+ite,21,2+ite, str(obj.parasite), td_format1)
                sheet.merge_range(22,1+ite,22,2+ite, ' ', td_format1)
                sheet.merge_range(23,1+ite,23,2+ite, obj.remark, td_format1)
                
                ite=ite+2
                
            else:
                sheet.write(4,1+ite, str(obj.no_potong), td_format1)
                sheet.write(5,1+ite, str(obj.list_tangki), td_format1)
                sheet.write(6,1+ite, ' ', td_format1)
                sheet.write(7,1+ite, ' ', td_format1)
                sheet.write(8,1+ite, ' ', td_format1)
                sheet.write(9,1+ite, ' ', td_format1)
                sheet.write(10,1+ite, "'"+str(obj.suhu)+" - "+str(obj.suhu_akhir), td_format1)
                
                jam_potong = datetime.strptime(obj.jam_potong, "%Y-%m-%d %H:%M:%S")
                sheet.write(11,1+ite, jam_potong, td_time)
                
                sheet.write(12,1+ite, str(obj.list_basket), td_format1)
                sheet.write(13,1+ite, str(obj.eyes), td_format1)
                sheet.write(14,1+ite, str(obj.gill), td_format1)
                sheet.write(15,1+ite, str(obj.skin), td_format1)
                sheet.write(16,1+ite, str(obj.physical_damage), td_format1)
                sheet.write(17,1+ite, str(obj.texture), td_format1)
                sheet.write(18,1+ite, str(obj.belly_cavity), td_format1)
                sheet.write(19,1+ite, str(obj.odour), td_format1)
                sheet.write(20,1+ite, str(obj.grade_assigned), td_format1)
                sheet.write(21,1+ite, str(obj.parasite), td_format1)
                sheet.write(22,1+ite, ' ', td_format1)
                sheet.write(23,1+ite, obj.remark, td_format1)
                
                ite=ite+1

        
        