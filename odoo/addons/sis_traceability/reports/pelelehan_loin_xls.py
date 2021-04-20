'''
Created on Jan 7, 2021

@author: endah
'''
from odoo import models
from _datetime import datetime

class CSFrozenLoin(models.AbstractModel):
    _name = 'report.sis_traceability.pelelehan_loin_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Pelelehan Loin')

        #set column width
        sheet.set_column('A:A',10.86)
        sheet.set_column('B:B',8.86)
        sheet.set_column('C:C',15.57)
        sheet.set_column('D:D',26)
        sheet.set_column('E:E',6.14)
        sheet.set_column('F:F',5.29)
        sheet.set_column('G:G',9.86)
        sheet.set_column('H:H',7.71)
        sheet.set_column('I:I',6.29)
        sheet.set_column('J:J',8.86)
        sheet.set_column('K:K',7.14)
        sheet.set_column('L:L',3.57)
        sheet.set_column('M:M',3.86)
        sheet.set_column('N:N',3.71)
        sheet.set_column('O:O',5.57)
        sheet.set_column('P:P',5.57)
        sheet.set_column('Q:Q',5.57)
        sheet.set_column('R:R',9)
        sheet.set_column('S:S',15)
        sheet.set_column('T:T',15)

        #header format
        head_arial11 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11})
        head_arial11bord = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'border':1})
        head_arial11right = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'align':'right'})
        head_arial20 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':20, 'align':'center', 'valign':'vcenter', 'bold':True})
        head_arial20ita = workbook.add_format({'font_name':'Arial Narrow', 'font_size':20, 'align':'center', 'valign':'vcenter', 'italic':True})

        #header template write
        sheet.write(0,0, "Cleaning Section - PT. Aneka Tuna Indonesia", head_arial11)
        sheet.write(0,9, "FRM.CLN.33 2020-03-09", head_arial11right)
        sheet.merge_range(2,0,2,19, "KONTROL PELELEHAN LOIN/ SHREDDED BEKU, SANITASI  LOIN DAN PERALATAN", head_arial20)
        sheet.merge_range(3,0,3,19, "CONTROL OF DEFROST FROZEN LOIN/ SHREDDED, LOIN AND EQUIPMENT SANITATION", head_arial20ita)
        sheet.merge_range(4,0,4,3, "Tanggal Bongkar/ Unloading Date : ", head_arial11bord)
        sheet.merge_range(4,14,4,19, "Tanggal produksi/Production date: ", head_arial11bord)
        sheet.write(5,0, "A. PELEHAN LOIN/ SHREDDED BEKU/ DEFROST FROZEN LOIN/SHREDDED", head_arial11)

        #th_format
        th_arial11 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'align':'center', 'valign':'vcenter', 'border':1})
        th_arial11.set_text_wrap()
        th_arial8 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':8, 'align':'center', 'valign':'vcenter', 'border':1})
        th_arial8.set_text_wrap()

        #column write
        sheet.merge_range(6,0,7,0, "No.Boks Ikan\nFish Box No.", th_arial11)
        sheet.merge_range(6,1,7,1, "No. ID \nRak Defrost\nDefrost Rack \nID Number", th_arial11)
        sheet.merge_range(6,2,7,2, "Loin/ Shredded & No Urut Rak Defrost\nLoin/ Shredded & Defrost Rack Serial Number", th_arial11)
        sheet.merge_range(6,3,7,3, "Lot", th_arial11)
        sheet.merge_range(6,4,7,5, "Kode Produksi\nProduction Code", th_arial11)
        sheet.merge_range(6,6,7,6, "Jumlah\nQuantity (pcs)", th_arial11)
        sheet.merge_range(6,7,7,7, "Jam Mulai Bongkar\nStart Time of Unloading", th_arial11)
        sheet.merge_range(6,8,7,8, "Mulai Thawing\nStart Thawing", th_arial11)
        sheet.merge_range(6,9,7,9, "Maks. Waktu Tunda\nDelay Time Max.", th_arial11)
        sheet.merge_range(6,10,7,10, "Temuan Benda Asing \nForeign Material Finding", th_arial8)
        sheet.merge_range(6,11,6,13, "Suhu\nTemperature", th_arial11)
        sheet.write(7,11, "1", th_arial11)
        sheet.write(7,12, "2", th_arial11)
        sheet.write(7,13, "3", th_arial11)
        sheet.merge_range(6,14,6,16, "Organoleptik\nOrganoleptic", th_arial11)
        sheet.write(7,14, "Warna\nColour", th_arial11)
        sheet.write(7,15, "Bau\nOdor", th_arial11)
        sheet.write(7,16, "Rasa\nFlavor", th_arial11)
        sheet.merge_range(6,17,7,17, "Diperiksa oleh QCP\nChecked by QCP", th_arial11)
        sheet.merge_range(6,18,7,19, "Keterangan\nRemark", th_arial11)
        
        #td format
        td_format = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'border':1, 'align':'center'})

        #data write
        it=0
        for obj in partners:
            sheet.write(8+it,0,obj.fish_box_no,td_format)
            sheet.write(8+it,1,obj.rak_defrost_id,td_format)
            sheet.write(8+it,2,obj.kode_loin_urut,td_format)
            sheet.write(8+it,3,obj.lot,td_format)
            sheet.merge_range(8+it,4,8+it,5,obj.kode_produksi,td_format)
            sheet.write(8+it,6,obj.jumlah,td_format)
            sheet.write(8+it,7,obj.jambongkar_real,td_format)
            sheet.write(8+it,8,obj.start_thawing_real,td_format)
            sheet.write(8+it,9,obj.delay_time_max_real,td_format)
            sheet.write(8+it,10,obj.temuan_benda,td_format)
            sheet.write(8+it,11,"",td_format)
            sheet.write(8+it,12,"",td_format)
            sheet.write(8+it,13,"",td_format)
            sheet.write(8+it,14,"",td_format)
            sheet.write(8+it,15,"",td_format)
            sheet.write(8+it,16,"",td_format)
            sheet.write(8+it,17,"",td_format)
            if obj.remark:
                sheet.merge_range(8+it,18,8+it,19, obj.remark,td_format)
            else:
                sheet.merge_range(8+it,18,8+it,19, "",td_format)
            it=it+1
        
        #foot format
        fo_arial11 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'border':1})
        fo_arial11.set_text_wrap()
        fo_arial11_2 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11,'italic':True, 'border':1, 'align':'left', 'valign':'top'})
        fo_arial11ali = workbook.add_format({'font_name':'Arial Narrow', 'font_size':11, 'align':'center', 'valign':'vcenter', 'border':1})
        fo_arial11ali.set_text_wrap()

        sheet.merge_range(9+it,0,16+it,3, """Keterangan/ Remark :\n-Waktu Tunggu Maksimal/ Maximum Delay Time:\n
        •Frozen Loin : 15 jam (5 kg) , 13 jam (3 kg)\n
        •Frozen Shredded : 13 jam (5 kg), 10 jam (3 kg)\n
        - Suhu setelah pelelehan 7 - 20 °C/ Temperature after thawing 7 - 20 °C\n
        - O : Tidak ditemukan benda asing/ No foreign material found\n
        - X : Ditemukan benda asing (objek ditempel)/ Foreign material found (paste the object)""",fo_arial11)

        sheet.merge_range(9+it,5,15+it,14, "Catatan/ Note:", fo_arial11_2)
        sheet.merge_range(9+it,16, 10+it,17, "Penanggung Jawab\nPerson In Charge",fo_arial11ali)
        sheet.merge_range(9+it,18, 9+it,19, "Disetujui oleh/ Approved by",fo_arial11ali)
        sheet.write(10+it,18, "PPIC", fo_arial11ali)
        sheet.write(10+it,19, "Cleaning", fo_arial11ali)
        sheet.merge_range(11+it,16, 14+it,17, "",fo_arial11ali)
        sheet.merge_range(11+it,18, 14+it,18, "",fo_arial11ali)
        sheet.merge_range(11+it,19, 14+it,19, "",fo_arial11ali)