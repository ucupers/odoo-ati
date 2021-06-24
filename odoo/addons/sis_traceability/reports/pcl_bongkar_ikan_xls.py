'''
Created on Jan 5, 2021

@author: endah
'''
from odoo import models
from _datetime import datetime

class CSCooker(models.AbstractModel):
    _name = 'report.sis_traceability.pcl_bongkar_ikan_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Bongkar Ikan')
                
        sheet.set_column('A:A',6.57)
        sheet.set_column('B:B',6.57)
        sheet.set_column('C:C',6.86)
        sheet.set_column('D:D',9.86)
        sheet.set_column('E:E',6.86)
        sheet.set_column('F:F',11.71)
        sheet.set_column('G:G',8.57)
        sheet.set_column('H:H',8.57)
        sheet.set_column('I:I',6.43)
        sheet.set_column('J:J',0.5)
        sheet.set_column('K:K',9.29)
        sheet.set_column('L:L',9.29)
        sheet.set_column('M:M',10.43)
        sheet.set_column('N:N',6.74)
        sheet.set_column('O:O',7.57)
        sheet.set_column('P:P',10)
        sheet.set_row(7, 32)
        sheet.set_row(8, 44)
        
        #head_format
        head_arialn10 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'italic':True})
        head_arialn9 = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'align':'right'})
        head_arialn12b = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'border':1, 'valign':'vcenter'})
        head_arialn22 = workbook.add_format({'font_size':22, 'font_name': 'Arial Narrow', 'align':'center', 'bold':True})
        head_arialn18 = workbook.add_format({'font_size':18, 'font_name': 'Arial Narrow', 'align':'right', 'italic':True})
        
        #th format
        th_arialn10 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'align': 'center', 'valign':'vcenter', 'border':1})
        th_arialn10.set_text_wrap()
        
        #td format
        td_arial9 = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'align': 'center', 'valign':'vcenter', 'border':1})
#         td_arial9_time = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'align': 'center', 'valign':'vcenter', 'border':1, 'num_format':'HH:MM'})
        
        
        #foot Format
        fo_airal10 = workbook.add_format({'font_size':9, 'font_name':'Arial Narrow', 'align':'left'})
        fo_airal10.set_top()
        fo_airal10.set_right()
        fo_airal9 = workbook.add_format({'font_size':9, 'font_name':'Arial Narrow'})
        fo_airal10b = workbook.add_format({'font_size':10, 'font_name':'Arial Narrow', 'bold':True, 'align':'right'})
        fo_airal9w = workbook.add_format({'font_size':9, 'font_name':'Arial Narrow'})
        fo_airal9w.set_text_wrap()
        fo_airalbor = workbook.add_format({'font_size':9, 'font_name':'Arial Narrow'})
        fo_airalbor.set_bottom()
        fo_airalbor.set_right()
        diag_format3 = workbook.add_format({'diag_type': 1})
        diag_format3.set_bottom()
        rightborder_format = workbook.add_format({'font_size':9, 'font_name':'Arial Narrow'})
        rightborder_format.set_right()
        rightborder_format.set_text_wrap()
        fo_arial12 = workbook.add_format({'font_size':12, 'font_name':'Arial Narrow', 'align':'center', 'valign':'vcenter', 'border':1})
        fo_arial12.set_text_wrap()
        
        
        sheet.write(1,0, "PT. Aneka Tuna Indonesia", head_arialn10)
        sheet.write(0,15, "FORM.PCL.01 2020-03-23", head_arialn9)
        sheet.merge_range(4,0,4,15, "BONGKAR IKAN", head_arialn22)
        sheet.merge_range(5,6,5,9, "UNLOADING FISH", head_arialn18)
        sheet.merge_range(5,0,5,1, "Tanggal/ Date", head_arialn12b)
        sheet.merge_range(5,2,5,5, " ", head_arialn12b)
        sheet.write(5,14, "Shift ",head_arialn12b)
        sheet.write(5,15, "", head_arialn12b)
        
        sheet.merge_range(7,0,8,0, "Line Pre Cleaning", th_arialn10)
        sheet.merge_range(7,1,8,1, "Line Cleaning", th_arialn10)
        sheet.merge_range(7,2,8,2, "ID Basket", th_arialn10)
        sheet.merge_range(7,3,8,3, "No. Basket\nBasket No.", th_arialn10)
        sheet.merge_range(7,4,8,4, "Jumlah Tray\nTray Qty", th_arialn10)
        sheet.merge_range(7,5,8,5, "Ukuran Ikan\nFish Size", th_arialn10)
        sheet.merge_range(7,6,7,7, "Jam Bongkar\nUnloading Time", th_arialn10)
        sheet.write(8,6, "Mulai\nStart", th_arialn10)
        sheet.write(8,7, "Selesai\nFinish", th_arialn10)
        sheet.merge_range(7,8,8,9, "Tekstur\nTexture", th_arialn10)
        sheet.merge_range(7,10,7,11, "Rijek\nReject (Kg)", th_arialn10)
        sheet.write(8,10, "Honeycomb", th_arialn10)
        sheet.write(8,11, "Lain-lain\nOther", th_arialn10)
        sheet.merge_range(7,12,8,12, "Verifikasi Organoleptik oleh QC\nOrganoleptic is Verified by QC", th_arialn10)
        sheet.merge_range(7,13,8,15, "Keterangan\nRemark", th_arialn10)
        
        it=0
        
        for obj in partners:
            sheet.write(9+it,0, obj.pcl, td_arial9)
            sheet.write(9+it,1, obj.line_cleaning, td_arial9)
            sheet.write(9+it,2, obj.basket_id, td_arial9)
            sheet.write(9+it,3, obj.basket_no, td_arial9)
            sheet.write(9+it,4, obj.jml_tray, td_arial9)
            if obj.kindoffish and obj.size:    
                sheet.write(9+it,5, obj.kindoffish+" "+obj.size, td_arial9)
            else:
                sheet.write(9+it,5, "", td_arial9)
                                
            sheet.write(9+it,6, obj.jamstart, td_arial9)
            sheet.write(9+it,7, obj.jamfinish, td_arial9)
            sheet.merge_range(9+it,8,9+it,9, obj.nkl, td_arial9)
            sheet.write(9+it,10, obj.hc, td_arial9)
            sheet.write(9+it,11, " ", td_arial9)
            sheet.write(9+it,12, " ", td_arial9)
            if obj.remark:
                sheet.merge_range(9+it,13,9+it,15, obj.remark, td_arial9)
            else:
                sheet.merge_range(9+it,13,9+it,15, "", td_arial9)
            it = it+1
            
        sheet.merge_range(10+it,0,10+it,8, "Catatan/ Note", fo_airal10)
        sheet.write(11+it,0, "'- Isi kolom Tekstur dengan simbol di bawah ini/ Fill Texture column with symbol below:", fo_airal9)
        sheet.write(12+it,0, "N", fo_airal10b)
        sheet.write(13+it,0, "L", fo_airal10b)
        sheet.write(12+it,1, ": Tekstur ikan normal/ Normal meat texture", fo_airal9)
        sheet.write(13+it,1, ": Tekstur ikan lembek/ Fish meat texture is mushy", fo_airal9)
        sheet.write(12+it,5, "K : Tekstur ikan kering/ Fish meat texture is dry", fo_airal9)
        sheet.write(14+it,0, "- Isi kolom Lain-lain dengan total rijek dan kode berikut/ Fill Other column with total of meat rejected and code below:", fo_airal9)
        sheet.write(15+it,0, "  PM : Pasty Meat    BM : Blue Meat  OM : Orange Meat", fo_airal9)
        sheet.merge_range(16+it,0,17+it,8, "- Pemeriksaan organoleptik ikan setiap palka meliputi warna, bau dan rasa dilakukan oleh QC./ Fish organoleptic inspection of each vessel includes color, odor and taste is verified by QC.",rightborder_format)
        sheet.write(18+it,0, "  O : OK/ memenuhi standar (within standard)      X : Tidak memenuhi standar/ Out of standard", fo_airal9)
        sheet.merge_range(19+it,1,19+it,8, ": Tidak ada data/ No data", fo_airalbor)
        sheet.write(19+it,0, "", diag_format3)
        sheet.write(11+it,8, "", rightborder_format)
        sheet.write(12+it,8, "", rightborder_format)
        sheet.write(13+it,8, "", rightborder_format)
        sheet.write(14+it,8, "", rightborder_format)
        sheet.write(15+it,8, "", rightborder_format)
        sheet.write(18+it,8, "", rightborder_format)
        sheet.merge_range(10+it,10,12+it,11, "Penanggung Jawab\nIn Charge", fo_arial12)
        sheet.merge_range(10+it,12,12+it,13, "Diverifikasi oleh QC\nVerified by QC", fo_arial12)
        sheet.merge_range(10+it,14,12+it,15, "Disetujui oleh\nApproved by", fo_arial12)
        sheet.merge_range(13+it,10,18+it,11, "", fo_arial12)
        sheet.merge_range(13+it,12,18+it,13, "", fo_arial12)
        sheet.merge_range(13+it,14,18+it,15, "", fo_arial12)