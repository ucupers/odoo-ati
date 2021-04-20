from odoo import models, api
# from _datetime import datetime
# from time import strftime
# from dateutil.relativedelta import relativedelta
# from odoo.exceptions import UserError
import re

import tempfile
import base64
# import os
# 
# from PIL import Image

class pelaporanXLS(models.AbstractModel):
    _name = 'report.sis_k3.rpt_pelaporan_k3'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
#         format1 = workbook.add_format({'font_size':10, 'font_name': 'Arial Narrow'})
        worksheet = workbook.add_worksheet('Finding and Corrective Action')
#         sheet.write(0,0, 'PT. Aneka Tuna Indonesia', format1)
        header_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#BDBDDF'}) #AFAFD8
        header_format.set_text_wrap()
        wrap_format = workbook.add_format({'border': 1})
        wrap_format.set_text_wrap()
        wrap_format.set_align('vcenter')
        wrap_format_center = workbook.add_format({'border': 1})
        wrap_format_center.set_text_wrap()
        wrap_format_center.set_align('center')
        wrap_format_center.set_align('vcenter')

        worksheet.merge_range('A1:A2', 'No.', header_format)
        worksheet.merge_range('B1:B2', 'Tgl. Pelaporan', header_format)
        worksheet.merge_range('C1:C2', 'Factory', header_format)
        worksheet.merge_range('D1:G1', 'Potensi Bahaya', header_format)
        worksheet.write(1,3,"Keterangan", header_format)
        worksheet.write(1,4,"Section", header_format)
        worksheet.write(1,5,"Foto1", header_format)
        worksheet.write(1,6,"Foto2", header_format)
        worksheet.merge_range('H1:J1', 'K3', header_format)
        worksheet.write(1,7,"Review", header_format)
        worksheet.write(1,8,"Tgl. Target", header_format)
        worksheet.write(1,9,"Section PJ.", header_format)
        worksheet.merge_range('K1:N1', 'Pengendalian Bahaya', header_format)
        worksheet.write(1,10,"Keterangan", header_format)
        worksheet.write(1,11,"Tgl. Pengendalian", header_format)
        worksheet.write(1,12,"Foto1", header_format)
        worksheet.write(1,13,"Foto2", header_format)
        worksheet.merge_range('O1:O2', 'P2K3', header_format)
        worksheet.merge_range('P1:P2', 'Info P2K3', header_format)
        worksheet.merge_range('Q1:Q2', 'Status', header_format)
#         worksheet.write(1,0,"No.", header_format)
#         worksheet.write(1,1,"Tgl. Pelaporan", header_format)
#         worksheet.write(1,2,"Factory", header_format)
#         worksheet.write(1,3,"Potensi Bahaya", header_format)
#         worksheet.write(1,4,"Section", header_format)
#         worksheet.write(1,5,"Foto1", header_format)
#         worksheet.write(1,6,"Foto2", header_format)
#         worksheet.write(1,7,"Review K3", header_format)
#         worksheet.write(1,8,"Target", header_format)
#         worksheet.write(1,9,"Penanggung Jawab", header_format)
#         worksheet.write(1,10,"Pengendalian Bahaya", header_format)
#         worksheet.write(1,11,"Tgl. Pengendalian", header_format)
#         worksheet.write(1,12,"Foto1", header_format)
#         worksheet.write(1,13,"Foto2", header_format)
#         worksheet.write(1,14,"P2K3", header_format)
#         worksheet.write(1,15,"Info P2K3", header_format)

        worksheet.set_column(0, 0, 12)
        worksheet.set_column(1, 1, 10)
        worksheet.set_column(2, 2, 10)
        worksheet.set_column(3, 3, 50)
        worksheet.set_column(4, 4, 15)
        worksheet.set_column(5, 6, 20)
        worksheet.set_column(7, 7, 50)
        worksheet.set_column(8, 8, 10)
        worksheet.set_column(9, 9, 15)
        worksheet.set_column(10, 10, 50)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 13, 20)
        worksheet.set_column(14, 14, 10)
        worksheet.set_column(15, 15, 50)
        
        nrow=2
        for obj in partners:
            worksheet.write(nrow,0,obj.no_doc, wrap_format_center)
            worksheet.write(nrow,1,obj.tgl_doc, wrap_format_center)
            worksheet.write(nrow,2,obj.pabrik_id, wrap_format_center)

            xpotensi_bahaya = re.sub("<.*?>", "", obj.potensi_bahaya_d)
            worksheet.write(nrow,3,xpotensi_bahaya, wrap_format)
            
            worksheet.write(nrow,4,obj.section, wrap_format_center)
            
            obj.ensure_one()
            if not obj.potensi_bahaya_i1:
                worksheet.write(nrow,5,"", wrap_format_center)
                worksheet.insert_image(nrow,5, "")
            else:
                worksheet.write(nrow,5,"", wrap_format_center)
                worksheet.set_row(nrow, 60)
#                 raise UserError("no image on this record")
            # decode the base64 encoded data
#                 data = base64.decodestring(obj.potensi_bahaya_i1)
#                 # create a temporary file, and save the image
#                 fobj = tempfile.NamedTemporaryFile(delete=False)
#                 fname = fobj.name
#                 fobj.write(data)
#                 fobj.close()
                fname=self._xls_image(obj.potensi_bahaya_i1)
                worksheet.insert_image(nrow,5, fname, {'x_offset': 15, 'y_offset': 10,'x_scale': 0.2, 'y_scale': 0.2,'object_position': 4})
#             os.unlink(fname)
            if not obj.potensi_bahaya_i2:
                worksheet.write(nrow,6,"", wrap_format_center)
                worksheet.insert_image(nrow,6, "")
            else:
                worksheet.write(nrow,6,"", wrap_format_center)
                worksheet.set_row(nrow, 60)
                fname=self._xls_image(obj.potensi_bahaya_i2)
                worksheet.insert_image(nrow,6, fname, {'x_offset': 15, 'y_offset': 10,'x_scale': 0.2, 'y_scale': 0.2,'object_position': 4})

            xreview = re.sub("<.*?>", "", obj.review_k3)
            worksheet.write(nrow,7,xreview, wrap_format)

            worksheet.write(nrow,8,obj.tgl_target, wrap_format_center)
            worksheet.write(nrow,9,obj.section_pic, wrap_format_center)

            xcorrective = re.sub("<.*?>", "", obj.corrective_act_d)
            worksheet.write(nrow,10,xcorrective, wrap_format)

            worksheet.write(nrow,11,obj.tgl_act, wrap_format_center)

            if not obj.corrective_act_d1:
                worksheet.write(nrow,12,"", wrap_format_center)
                worksheet.insert_image(nrow,12, "")
            else:
                worksheet.write(nrow,12,"", wrap_format_center)
                worksheet.set_row(nrow, 60)
                fname=self._xls_image(obj.corrective_act_d1)
                worksheet.insert_image(nrow,12, fname, {'x_offset': 15, 'y_offset': 10,'x_scale': 0.2, 'y_scale': 0.2,'object_position': 4})

            if not obj.corrective_act_d2:
                worksheet.write(nrow,13,"", wrap_format_center)
                worksheet.insert_image(nrow,13, "")
            else:
                worksheet.write(nrow,13,"", wrap_format_center)
                worksheet.set_row(nrow, 60)
                fname=self._xls_image(obj.corrective_act_d2)
                worksheet.insert_image(nrow,13, fname, {'x_offset': 15, 'y_offset': 10,'x_scale': 0.2, 'y_scale': 0.2,'object_position': 4})

            worksheet.write(nrow,14,obj.p2k3, wrap_format_center)
            
            xinfo = re.sub("<.*?>", "", obj.info_p2k3)
            worksheet.write(nrow,15,xinfo, wrap_format)
            worksheet.write(nrow,16,obj.step_state, wrap_format_center)

            nrow=nrow+1

    @api.multi
    def _xls_image(self, obj):
        data = base64.decodestring(obj)
        fobj = tempfile.NamedTemporaryFile(delete=False)
        fname = fobj.name
        fobj.write(data)
        fobj.close()

        return fname
        
