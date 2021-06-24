'''
Created on Dec 18, 2020

@author: endah
'''
from odoo import models
from _datetime import datetime
from time import strftime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

class CSOutgoingXLS(models.AbstractModel):
    _name = 'report.sis_traceability.cs_outgoing_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        today = datetime.now()+relativedelta(hours=7)
        hari = today.strftime("%A")
        tgl = today.strftime("%d %B %Y")
        tglprod=''
        format1 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow'})
        cell_format = workbook.add_format({'font_size':10, 'font_name': 'Arial', 'border':1})
        dt_format = workbook.add_format({'font_size':10, 'font_name': 'Arial', 'border':1,'num_format': 'hh:mm'})
        format3 = workbook.add_format({'font_size':11, 'font_name': 'Arial Narrow'})
        format2 = workbook.add_format({'font_size':10, 'font_name': 'Arial'})
        format4 = workbook.add_format({'font_size':11, 'font_name': 'Arial'})  
        th_format = workbook.add_format({'font_size':11, 'font_name': 'Arial','border':1}) 
        th_format.set_text_wrap()       
#         ttd_format2 = workbook.add_format({'font_size':8, 'font_name': 'Arial', 'border':1})
        merge_format1 = workbook.add_format({'align': 'center', 'valign':   'vcenter', 'border': 1})
        merge_format1.set_text_wrap()
        ttd_format = workbook.add_format({'font_size':8, 'font_name': 'Arial', 'border':1})
        sheet = workbook.add_worksheet('CS Outgoing')
        sheet.write(0,0, 'Cold Storage Section - PT. Aneka Tuna Indonesia', format1)
        sheet.set_column(0, 0, 6.57)
        sheet.set_column('B:B', 6.57)
        sheet.set_column('C:C', 7)
        sheet.set_column('D:D', 4.86)
        sheet.set_column('E:E', 6.14)
        sheet.set_column('F:F', 4.14)
        sheet.set_column('G:G', 8.43)
        sheet.set_column('H:H', 10.29)
        sheet.set_column('I:I', 14.43)
        sheet.set_column('J:J', 21.71)
        sheet.set_column('K:K', 10.57)
        sheet.set_column('L:L', 10.57)

        sheet.write(0,10, 'FRM.CS.05 2017-12-26', format2)
        sheet.write(5,0, 'Shift', format3)
        sheet.write(6,0, 'Hari/Day', format3)
        sheet.write(7,0, 'Tanggal', format3)
        sheet.write(5,3, ': 1 / 2', format3)
        sheet.write(6,3, ': '+hari, format3)
        sheet.write(7,3, ': '+tgl, format3)
        sheet.write(6,7, 'Diproduksi/Produced', format4)
        sheet.write(5,9, 'Waktu Potong/ Cutting Time', format3)
        sheet.write(6,9, 'Hari/ Day', format3)
        sheet.write(7,9, 'Tanggal/ Day', format3)
        sheet.write(5,10, ': PP / PM', format3)
        sheet.merge_range('A10:A11', 'No Potong', merge_format1)
        sheet.merge_range('B10:B11', 'Frozen (FZ)', merge_format1)
        sheet.merge_range('C10:D11', 'Jenis dan Ukuran Ikan', merge_format1)
        sheet.merge_range('E10:E11', 'jam', merge_format1)
        sheet.merge_range('F10:F11', 'No Urut', merge_format1)
        sheet.merge_range('G10:G11', 'No Boks', merge_format1)
        sheet.merge_range('H10:H11', 'Berat', merge_format1)
        sheet.merge_range('I10:J11', 'Carrier / Hatch / Lot No.', merge_format1)
        sheet.merge_range('K10:L10', 'Tonase', merge_format1)
        sheet.write(10,10, 'Per Palka', cell_format)
        sheet.write(10,11, 'T O T A L', cell_format)
        
#         sheet.merge_range(11, 0, 14, 0, 'Tonase1', merge_format1)
#         sheet.merge_range(15, 0, 'Tonase', merge_format1)
        sheet.insert_textbox('G2', 'O U T G O I N G\n FOR DAILY PRODUCTION',{
            'object_position': 3, 
            'height': 75, 
            'width': 250,
            'align' :{'vertical': 'middle', 'horizontal': 'center'},
            'line' :{'width':2}})
        
        it=0
        it2=0
        ttl_ton=0
        
        for obj in partners: 
            ijer=0            
            for det in obj.cs_line_id:
                jam = datetime.strptime(det.tgl_keluar, "%Y-%m-%d %H:%M:%S")
                descc = det.vessel_no+' '+det.voyage_no+' '+det.hatch_no
                sheet.merge_range(11+it,2,11+it,3, str(det.item_no),merge_format1)
                sheet.write(11+it,4, jam,dt_format)
                sheet.write(11+it,5,str(ijer+1),cell_format)
                sheet.write(11+it,6,str(det.fish_box_no),cell_format)
                sheet.write(11+it,7,str(det.quantity),cell_format)
                sheet.merge_range(11+it,8,11+it,9, str(descc),merge_format1)
                it=it+1
                ijer=ijer+1
#                 print('det it='+str(it)+' it2='+str(it2)+' ijer='+str(ijer))
                
            if it2==0:
                sheet.merge_range(11,0,10+it,0, str(obj.no_potong), merge_format1)
                sheet.merge_range(11,11,10+it,11, str(obj.total_tonase), merge_format1)
                sheet.merge_range(11,1,10+it,1, '', merge_format1)
                tglprod=obj.tgl_produksi
            else:
                sheet.merge_range(11+it-ijer,0,10+it,0, str(obj.no_potong), merge_format1)
                sheet.merge_range(11+it-ijer,11,10+it,11, str(obj.total_tonase), merge_format1)
                sheet.merge_range(11+it-ijer,1,10+it,1,'', merge_format1)
                if tglprod!=obj.tgl_produksi:
                    raise UserError('Tanggal Produksi lebih dari satu')
                
            it2=it2+1
            ttl_ton=ttl_ton+obj.total_tonase
        tglprod2 = datetime.strptime(tglprod, "%Y-%m-%d")
        hariprod = tglprod2.strftime("%A")
        tglprod = tglprod2.strftime("%d %B %Y")
        sheet.write(6,10, ': '+hariprod, format3)
        sheet.write(7,10, ': '+tglprod, format3)
        
        sheet.write(11+it,9, 'T O T A L', format3)    
        sheet.merge_range(it+11,10,it+11,11, str(ttl_ton), merge_format1)
        sheet.write(it+13,9, 'Penanggung Jawab/ In Charge', ttd_format)
        sheet.merge_range(it+13,10,it+13,11, 'Disetujui oleh/Approved By', ttd_format)
        sheet.write(it+13,2, 'Catatan/ Note :', format3)
        sheet.write(it+15,6, 'cc : PPC & Raw Material', format3)
        sheet.merge_range(it+14,9,it+17,9, '', merge_format1)
        sheet.merge_range(it+14,10,it+17,11, '', ttd_format)
        
        sheet.insert_textbox(it+13,2, '',{'object_position': 3, 
                                          'height': 75, 
                                          'width': 350,
                                          'align' :{'vertical': 'middle', 'horizontal': 'center'},
                                          'fill': {'none': True},
                                          'line' :{'width':2}})



