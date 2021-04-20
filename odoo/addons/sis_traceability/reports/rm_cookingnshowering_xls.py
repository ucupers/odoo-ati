'''
Created on Jan 4, 2021

@author: endah
'''
from odoo import models
from _datetime import datetime

class CSCooker(models.AbstractModel):
    _name = 'report.sis_traceability.rm_cookingnshowering_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Cooking and Showering Cooker')
        
        #coulumn Set
        sheet.set_column('A:A',8.25)
        sheet.set_column('B:B',9)
        sheet.set_column('C:C',33.75)
        sheet.set_column('D:D',9.63)
        sheet.set_column('E:E',9.63)
        sheet.set_column('F:F',9.63)
        sheet.set_column('G:G',7.5)
        sheet.set_column('H:H',7.5)
        sheet.set_column('I:I',9)
        sheet.set_column('J:J',9)
        sheet.set_column('K:K',9)
        sheet.set_column('L:L',9)
        sheet.set_column('M:M',7.38)
        sheet.set_column('N:N',7.38)
        sheet.set_column('O:O',7.38)
        sheet.set_column('P:P',7.38)
        sheet.set_column('Q:Q',7.38)
        sheet.set_column('R:R',4.13)
        sheet.set_column('S:S',5.25)
        sheet.set_column('T:T',9.63)
        sheet.set_column('U:U',9)
        sheet.set_column('V:V',9)
        sheet.set_column('W:W',9)
        sheet.set_column('X:X',9)
        sheet.set_column('Y:Y',4.38)
        sheet.set_column('Z:Z',4.38)
        sheet.set_column('AA:AA',9.13)
        sheet.set_column('AB:AB',13.5)
        sheet.set_column('AC:AC',8.63)
        sheet.set_column('AD:AD',8.63)
        sheet.set_column('AE:AE',8.63)
        sheet.set_column('AF:AF',8.63)
        
        #head_format
        head_arialn11 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow'})
        head_arialn11_border = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow', 'border' : 1})
        head_arialn9 = workbook.add_format({'font_size':9, 'font_name': 'Arial Narrow', 'align' : 'right'})
        head_arialn24 = workbook.add_format({'font_size':24, 'font_name': 'Arial Narrow', 'align' : 'center', 'bold': True})
        head_arialn22 = workbook.add_format({'font_size':22, 'font_name': 'Arial Narrow', 'align' : 'center'})
        
        #th_format        
        th_arialn10 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'align' : 'center', 'border':1, 'valign' : 'vcenter'})
        th_arialn12 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'align' : 'center', 'border':1, 'valign' : 'vcenter'})
        th_arialn14 = workbook.add_format({'font_size':14, 'font_name': 'Arial Narrow', 'align' : 'center', 'border':1, 'valign' : 'vcenter'})
        th_arialn10.set_text_wrap()
        th_arialn12.set_text_wrap()
        th_arialn14.set_text_wrap()
        
        #td_format
        td_arialn8 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'align' : 'center', 'border':1, 'valign' : 'vcenter'})
        td_time = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow', 'border':1, 'num_format':'HH:MM', 'align': 'center'})
        
        #foot_format
        fo_format1 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'bold': True})
        fo_format1.set_top()
        fo_format2 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'bold': True})
        fo_format3 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow'})
        fo_format3.set_top()
        fo_format4 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow'})
        fo_format5 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow'})
        fo_format5.set_bottom()
        fo_format5.set_right()
        fo_format6 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow'})
        fo_format6.set_top()
        fo_format6.set_right()
        fo_format7 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow'})
        fo_format7.set_right()
        fo_format7.set_text_wrap()
        fo_format8 = workbook.add_format({'font_size':12, 'font_name': 'Arial Narrow', 'border':1, 'align': 'center', 'valign': 'vcenter'})
        fo_format8.set_text_wrap()
        #template write Header
        sheet.write(0,0, "Raw Material Section - PT. Aneka Tuna Indonesia", head_arialn11)
        sheet.write(0,31, "FRM.RM.06 2015-05-20", head_arialn9)
        sheet.merge_range(1,0,1,31, "WAKTU MASAK DAN PENYIRAMAN IKAN", head_arialn24)
        sheet.merge_range(2,10,2,18, "COOKING AND SHOWERING FISH", head_arialn22)
        sheet.merge_range(4,0,4,1, "Tanggal/ Date / Shift:", head_arialn11_border)
        sheet.merge_range(4,2,4,3, "", head_arialn11_border)
        
        #nama Kolom
        sheet.merge_range(6,0,7,0, "No. Cooking\nCooking No.", th_arialn10)
        sheet.merge_range(6,1,7,1, "No. Cooker\nCooker No.", th_arialn10)
        sheet.merge_range(6,2,7,2, "No. Basket\nBasket No.", th_arialn14)
        sheet.merge_range(6,3,7,3, "Jenis Ikan\nKind of Fish", th_arialn10)
        sheet.merge_range(6,4,7,4, "Ukuran\nSize", th_arialn10)
        sheet.merge_range(6,5,7,5, "Total \nTray", th_arialn10)
        sheet.merge_range(6,6,6,7, "Cooking", th_arialn10)
        sheet.write(7,6, "Waktu\nTime", th_arialn10)
        sheet.write(7,7, "T (°C)", th_arialn10)
        sheet.merge_range(6,8,7,8, "Uap Masuk\nSteam On", th_arialn10)
        sheet.merge_range(6,9,7,9, "Lubang Angin Ditutup\nVent Closed", th_arialn10)
        sheet.merge_range(6,10,7,10, "Uap Ditutup\nSteam\nOff", th_arialn10)
        sheet.merge_range(6,11,7,11, "Standar Suhu Pusat Setelah Dimasak/ After Cooking BBT Standard          (°C)", th_arialn10)
        sheet.merge_range(6,12,6,18, "Suhu Ikan (°C)/ Fish Temperature (°C)", th_arialn12)
        sheet.merge_range(7,12,7,14, "Sebelum Masak\nBefore Cooking", th_arialn12)
        sheet.merge_range(7,15,7,18, "Setelah Masak\nAfter Cooking", th_arialn12)
        sheet.merge_range(6,19,6,20, "Waktu Siram\nShowering Time", th_arialn12)
        sheet.write(7,19, "Mulai\nStart", th_arialn12)
        sheet.write(7,20, "Selesai\nFinish", th_arialn12)
        sheet.merge_range(6,21,7,23, "Suhu Ikan Setelah Penyiraman (°C)/ Fish Temp. (°C) After Showering", th_arialn12)
        sheet.merge_range(6,24,7,25, "Jalur No.\nShowering Line", th_arialn10)
        sheet.merge_range(6,26,7,26, "C. Room Line", th_arialn10)
        sheet.merge_range(6,27,7,27, "Diperiksa oleh QCP\nChecked by QCP", th_arialn10)
        sheet.merge_range(6,28,7,31, "Keterangan\nRemark", th_arialn14)
            
        it=0
        
        for obj in partners:
            sheet.write(8+it,0, obj.nocooking, td_arialn8)
            sheet.write(8+it,1, obj.nocooker, td_arialn8)
            sheet.write(8+it,2, obj.list_label, td_arialn8)
            sheet.write(8+it,3, " ", td_arialn8)
            sheet.write(8+it,4, " ", td_arialn8)
            sheet.write(8+it,5, obj.total_tray, td_arialn8)
            sheet.write(8+it,6, obj.cookingtime_real, td_arialn8)
            sheet.write(8+it,7, obj.cookingtemp, td_arialn8)
            
            steamon = datetime.strptime(obj.steamon, "%Y-%m-%d %H:%M:%S")
            sheet.write(8+it,8, steamon, td_time)
            
            vent_closed = datetime.strptime(obj.vent_closed, "%Y-%m-%d %H:%M:%S")
            sheet.write(8+it,9, vent_closed, td_time)
            
            steamoff = datetime.strptime(obj.steamoff, "%Y-%m-%d %H:%M:%S")
            sheet.write(8+it,10, steamoff, td_time)
            
            sheet.write(8+it,11, obj.standardtemp, td_arialn8)
            sheet.write(8+it,12, obj.tempaftertop, td_arialn8)
            sheet.write(8+it,13, obj.tempbeforecenter, td_arialn8)
            sheet.write(8+it,14, obj.tempbeforebottom, td_arialn8)
            sheet.write(8+it,15, obj.tempaftertop, td_arialn8)
            sheet.write(8+it,16, obj.tempbeforecenter, td_arialn8)
            sheet.merge_range(8+it,17,8+it,18, obj.tempbeforebottom, td_arialn8)
            
            startshowertime = datetime.strptime(obj.startshowertime, "%Y-%m-%d %H:%M:%S")
            sheet.write(8+it,19, startshowertime, td_time)
            
            stopshowertime = datetime.strptime(obj.stopshowertime, "%Y-%m-%d %H:%M:%S")
            sheet.write(8+it,20, stopshowertime, td_time)
            
            sheet.write(8+it,21, obj.aftershowertemp1, td_arialn8)
            sheet.write(8+it,22, obj.aftershowertemp2, td_arialn8)
            sheet.write(8+it,23, obj.aftershowertemp3, td_arialn8)
            sheet.merge_range(8+it,24,8+it,25, obj.showerline, td_arialn8)
            sheet.write(8+it,26, obj.coolingroomline, td_arialn8)
            sheet.write(8+it,27, " ", td_arialn8)
            sheet.merge_range(8+it,28,8+it,31, obj.remark, td_arialn8)
            it = it +1

        #template Footer write
        sheet.write(10+it, 0, 'Catatan :', fo_format1)
        sheet.write(11+it,0, 'Note', fo_format2)
        sheet.merge_range(10+it,1,10+it,6, "Standar Suhu Pusat sebelum Dimasak/ Before Cooking BBT Standard : -2 ~ 3 °C", fo_format3)
        sheet.merge_range(10+it,7,10+it,16, "Standar Suhu Pusat setelah Dimasak/ After Cooking BBT Standard :  ≥60° C", fo_format6)
        sheet.merge_range(11+it,7,12+it,16, "Come Up Time Standard min. : 20 menit/ minutes : Pelelehan Ikan/ Defrost Fish;\n10 menit/ minutes : Ikan yang didinginkan/ Chilled Fish", fo_format7)
        sheet.write(11+it, 1, "Standar Suhu Sesudah Penyiraman/ After Cooling BBT Standard  : < 55 °C", fo_format4)
        sheet.merge_range(13+it, 1,13+it, 16, "Ukuran Ikan/ Size of Fish : SSS: -1 ,   SS : -1.4 ,    S :1.4-1.8 ,     M : 1.8-3.4 ,    L1 : 3.4-4.5 ,     L2 : 4.5-5.5 ,    L3 : +5,5", fo_format5)
        sheet.write(13+it,0, " ", fo_format5)
        sheet.merge_range(10+it,18,11+it,20, "Penanggung Jawab\nIn Charge", fo_format8)
        sheet.merge_range(10+it,21,11+it,24, "Diperiksa Oleh Cooker\nChecked by Cooker",fo_format8)
        sheet.merge_range(10+it,25,10+it,31, "Disetujui oleh/ Approved by",fo_format8)
        sheet.merge_range(11+it,25,11+it,28, "Cooker",fo_format8)
        sheet.merge_range(11+it,29,11+it,31, "QCP",fo_format8)
        sheet.merge_range(12+it,18,15+it,20, " ", fo_format8)
        sheet.merge_range(12+it,21,15+it,24, " ",fo_format8)
        sheet.merge_range(12+it,25,15+it,28, " ",fo_format8)
        sheet.merge_range(12+it,29,15+it,31, " ",fo_format8)

        
        
        