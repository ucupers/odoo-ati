'''
Created on Jan 12, 2021

@author: endah
'''

from odoo import models
from _datetime import datetime
from odoo.exceptions import UserError

class FishThawingXLSX(models.AbstractModel):
    _name = 'report.sis_traceability.unpacking_defrost_loin_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        sheet = workbook.add_worksheet('Pelelehan Loin')

        #set column width
        sheet.set_column('A:A',4.86)
        sheet.set_column('B:B',9.86)
        sheet.set_column('C:C',21.43)
        sheet.set_column('D:D',12.86)
        sheet.set_column('E:E',13.71)
        sheet.set_column('F:F',18)
        sheet.set_column('G:G',12.14)
        sheet.set_column('H:H',19.86)
        sheet.set_column('I:I',0.83)
        sheet.set_column('J:J',5)
        sheet.set_column('K:K',31.29)
        sheet.set_column('L:L',12.86)
        sheet.set_column('M:M',13.71)
        sheet.set_column('N:N',18)
        sheet.set_column('O:O',12.14)
        sheet.set_column('P:P',19.86)
        sheet.set_row(4, 5.25)
        sheet.set_row(5,76)

        #header format
        head_arial10 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':10})
        head_arial10r = workbook.add_format({'font_name':'Arial Narrow', 'font_size':10, 'align':'right'})
        head_arial20b = workbook.add_format({'font_name':'Arial Narrow', 'font_size':20, 'align':'center', 'bold':True})
        head_arial20 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':20, 'align':'center'})
        head_arial12 = workbook.add_format({'font_name':'Arial Narrow', 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':1})
        head_arial12.set_text_wrap()

        #header write
        sheet.write(0,0, "Packing Section - PT. Aneka Tuna Indonesia", head_arial10)
        sheet.write(0,15, "FRM.PCK.21  2020-03-16", head_arial10r)
        sheet.merge_range(1,0,1,15, "BONGKAR LOIN DEFROST", head_arial20b)
        sheet.merge_range(2,0,2,15, "DEFROST LOIN UNPACKING", head_arial20)
        sheet.merge_range(3,0,3,1, "Tanggal Produksi\nProduction Date", head_arial12)
        sheet.merge_range(3,2,3,4, "", head_arial12)
        sheet.write(3,13, "Shift", head_arial12)
        sheet.merge_range(3,14,3,15, "", head_arial12)

        #column format
        co_format = workbook.add_format({'font_name':'Arial Narrow', 'font_size':12, 'align':'center', 'valign':'vcenter', 'border':1})
        co_format.set_text_wrap()

        sheet.write(5,0, "No", co_format)
        sheet.merge_range(5,1,5,2, "Kode Loin/ Shredded & No Urut Kereta Packing\nLoin/ Shredded Code & Packing Trolley Serial Number", co_format)
        sheet.write(5,3, "Jumlah Kantong\nBag Total (pcs)", co_format)
        sheet.write(5,4, "Status", co_format)
        sheet.write(5,5, "Waktu Bongkar Kantong\nBag Unloading Time", co_format)
        sheet.write(5,6, "Line Packing\nPacking Line", co_format)
        sheet.write(5,7, "Keterangan\nRemark", co_format)
        sheet.write(5,9, "No", co_format)
        sheet.write(5,10, "Kode Loin/ Shredded & No Urut Kereta Packing\nLoin/ Shredded Code & Packing Trolley Serial Number", co_format)
        sheet.write(5,11, "Jumlah Kantong\nBag Total (pcs)", co_format)
        sheet.write(5,12, "Status", co_format)
        sheet.write(5,13, "Waktu Bongkar Kantong\nBag Unloading Time", co_format)
        sheet.write(5,14, "Line Packing\nPacking Line", co_format)
        sheet.write(5,15, "Keterangan\nRemark", co_format)

        
        if len(partners)%2==0:
            dt = int(len(partners)/2)
        else:
            dt = int((len(partners)+1)/2)

        itcol1=0
        itcol2=0
        no=0
        print(partners)
        for obj in partners:
            if itcol1<dt:
                sheet.write(6+itcol1,0, no+1, co_format)
                sheet.merge_range(6+itcol1,1,6+itcol1,2, str(obj.kode_loin)+' '+str(obj.no_urut_kereta), co_format)
                sheet.write(6+itcol1,3, str(obj.jml_kantong), co_format)
                sheet.write(6+itcol1,4, obj.status, co_format)
                sheet.write(6+itcol1,5, obj.jam_bongkar_real, co_format)
                sheet.write(6+itcol1,6, obj.line_packing, co_format)
                sheet.write(6+itcol1,7, obj.remark, co_format)
                itcol1 = itcol1+1
            else:
                sheet.write(6+itcol2,9, no+1, co_format)
                sheet.write(6+itcol2,10, str(obj.kode_loin)+' '+str(obj.no_urut_kereta), co_format)
                sheet.write(6+itcol2,11, str(obj.jml_kantong), co_format)
                sheet.write(6+itcol2,12, obj.status, co_format)
                sheet.write(6+itcol2,13, obj.jam_bongkar_real, co_format)
                sheet.write(6+itcol2,14, obj.line_packing, co_format)
                sheet.write(6+itcol2,15, obj.remark, co_format)
                itcol2 = itcol2+1
            no = no+1
                    
        sheet.merge_range(itcol1+7,12,itcol1+7,13, "Penanggung Jawab/ In Charge", co_format)
        sheet.merge_range(itcol1+7,14,itcol1+7,15, "Disetujui oleh\nApproved by", co_format)
        sheet.merge_range(itcol1+8,12,itcol1+10,13, "", co_format)
        sheet.merge_range(itcol1+8,14,itcol1+10,15, "", co_format)



        