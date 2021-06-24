from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta
import math
import psycopg2
import xlsxwriter
import base64
import html2text
from odoo.addons.mail.models.mail_template import format_date
import time
from odoo.addons.sis_traceability.models.sis_cutting import cutting
from PIL.Image import NORMAL
from odoo.addons.sis_epi.models.sis_urut_cutting import adj_cutting
from jedi.debug import speed


class sis_epi_xls(models.TransientModel):
    _name='sis.coba.print'
    
    date_plan = fields.Date()
    report=fields.Binary(string='Report')
    
    def print(self):
        filename = ' URUTAN POTONG '+datetime.now().strftime('%Y-%m-%d')+'.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/'+filename)
        row = 5
        col = 0
        
        # STYLE
        format_judul = workbook.add_format({'font_size': 14, 'align': 'center'})
        normal_style = workbook.add_format({'valign':'vcenter', 'border':1, 'font_size':10})
        normal_style2 = workbook.add_format({'valign':'vcenter', 'font_size':10})
        header_style = workbook.add_format({'font_size': 10, 'bold': True, 'border':1, 'align': 'center'})
        header2_style = workbook.add_format({'font_size': 10, 'bold': True})
        value_style = workbook.add_format({'font_size': 10, 'align': 'center'})
        left_style = workbook.add_format({'font_size': 10})
        right_style = workbook.add_format({'font_size': 10, 'align': 'right'})
        warning_style = workbook.add_format({'font_size': 10, 'align': 'right', 'bg_color': 'red'})
        urutan_pertama_style = workbook.add_format({'font_size': 10, 'bold': True})
        
        # WORKSHEET
        worksheet = workbook.add_worksheet('Urutan Potong')
        worksheet.set_column('A:AJ', 8.2)
        
        # Membuat Judul
        worksheet.merge_range('D1:F1', 'URUTAN POTONG EPI ', format_judul)
        
        # Set lebar kolom
        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 15)
        worksheet.set_column('C:C', 15)
        worksheet.set_column('D:D', 15)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 8)
        worksheet.set_column('G:G', 6)
        worksheet.set_column('H:H', 25)
        worksheet.set_column('I:I', 6)
        
        # Set header
        worksheet.write('A4', 'EPI:', header2_style)
        
        
        worksheet.write('A5', 'No', header_style)
        worksheet.write('B5', 'Jam keluar CS', header_style)
        worksheet.write('C5', 'Jam Mulai Defrost', header_style)
        worksheet.write('D5', 'Jam Mulai Cutting', header_style)
        worksheet.write('E5', 'Product', header_style)
        worksheet.write('F5', 'Fish', header_style)
        worksheet.write('G5', 'Tonase', header_style)
        worksheet.write('H5', 'Remark', header_style)
        worksheet.write('I5', 'Potong', header_style)
        
        
        
        
        workbook.close()
        ids=self.env['sis.coba.print'].create({'report':base64.b64encode(open("/tmp/"+filename, "rb").read())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/sis.coba.print/%s/report/%s?download=true' %((ids.id),filename)
    
        }        