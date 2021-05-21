# -*- coding: utf-8 -*-

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


passwd = "mis1.anekatuna"

class sis_epi(models.Model):
    _name = 'sis.epi'
    _rec_name = 'name'
    _inherit = 'mail.thread'
    
    name = fields.Char(string="Name")
    epi_line_ids = fields.One2many('sis.epi.line', 'epi_id')
    
    state = fields.Selection([('schedule', 'Draft Schedule'), ('estimasi_pack', 'Estimasi Pack'), 
                              ('fish_using', 'Fish Using'), ('urut_cutting', 'Urut Cutting'), 
                              ('done', 'Done'), ('cancel', 'Cancel')], default='schedule', string="State", track_visibility='onchange')
    total_qty_fish = fields.Float(string="Total Fish(ton)", compute='compute_total_fish', store=True)
    
    # Production plan
    date_plan = fields.Date(string="Date", required=True, track_visibility='onchange')
    ati12_plan = fields.Selection([('ati1','ATI1'),('ati2','ATI2')], string="ATI1/ATI2", required=True)
    
    # Fish using
    fish_using_line_ids = fields.One2many('sis.epi.fish.using.line', 'epi_id_fu', string="Fish Using")
    
    # Urut cutting
    urut_cutting_line_ids = fields.One2many('sis.urut.cutting.line', 'epi_id_uc', string="Urut Cutting")
    

    
    
    
    @api.model
    def create(self, vals):
        res = super(sis_epi, self).create(vals)

        # Sequence
        sequence = self.env['ir.sequence'].next_by_code('sequence.sis.epi') or ('New')
        res.update({'name': sequence})

        return res
    
    @api.depends('epi_line_ids.qty_fish_total_epi')
    def compute_total_fish(self):
        for rec in self:
            qty_fish = 0
            epi_line = rec.epi_line_ids
            if epi_line:
                for row in epi_line:
                    qty_fish = qty_fish + row.qty_fish_total_epi
                
                rec.total_qty_fish = qty_fish
    
    # get year with range
    def get_date(self):
        year_opts = []
        for i in range(1, 32):
            year_opts.append((str(i), str(i)))
        return (year_opts)
    
    
    # Button confirm
    @api.multi
    def action_confirm(self):
        for rec in self:
            rec.update({'state': 'estimasi_pack'})
    
    # Button action fish using
    @api.multi
    def action_fish_using(self):
        for rec in self:
            epi_line = rec.epi_line_ids
            temp = []
            item_temp = 0
            i = 1
            temp_temp = []
            
            # Create temporary line untuk tab fish using
            values_temp = {}
            values_temp['urutan_item_fu'] = 0
            
            temp.append((0, 0, values_temp))
            
            for row in epi_line:
                start_packing = row.start_packing_epi
                item_id = row.pps_item_id
                start_packing = row.start_packing_epi
                waktu_estimasi_pack = row.waktu_packing_epi
                yield_total = (row.yield_total_epi / 1000)
                qty_fish_total = row.qty_fish_total_epi
                
                j = 0
                
                # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
                if qty_fish_total > 0:
                    row_fish_using = qty_fish_total / 4
                    
                    baris = 1
                    # Insert ke fish using line (pembulatan ke bawah)
                    for line in range(math.floor(row_fish_using)):
                        # Jika line pertama pada item baru, input start packing
                        
                        values = {}
                        values['epi_line_id_fu'] = row.id
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
                        
            return self.update({'fish_using_line_ids': temp})
                    
    
            
    # Button cancel 
    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.update({'state': 'cancel'})
    
    
    @api.constrains('total_qty_fish')
    def cek_qty_fish(self):
        for rec in self:
            qty_fish = rec.total_qty_fish
            
            if qty_fish > 100:
                raise UserError(_(
                     'The Fish Qty : ' + str(qty_fish) + ' is exceeds the limit, please change the fish quantity under 100 ton'))
        
            elif qty_fish < 0:
                raise UserError(_(
                     'The Fish Qty : ' + str(qty_fish) + ' cannot negative qty'))
            else:
                return True
            
            return True
    
    
    # Get item from production plan
    @api.multi
    def get_item_prod_plan(self):
        for rec in self:
            date_plan = rec.date_plan
            ati12_plan = rec.ati12_plan
            temp = []
            
            # Koneksi ke database live untuk mengambil data
            conn = psycopg2.connect(
                host="localhost",
                database="PT_ATI",
                user="odoo",
                password=passwd
            )
            cur = conn.cursor()
            
            if date_plan and ati12_plan:
                
                # Delete sis_epi_line terlebih dahulu
                rec.delete_sis_epi_line()
                
                SQL_db_local=" SELECT DISTINCT ph.id as header_id, "+\
                    " spi.description as desc, "+\
                    " line_id, "+\
                    " qtyperuom, "+\
                    " spi.id as item_id, "+\
                    " t"+str(int(date_plan[8:10]))+ " as qty, "+\
                    " spi.line as line_item, "+\
                    " spi.can_size as can_size, "+\
                    " spi.speed as speed, "+\
                    " spi.kaleng_per_case as kaleng_per_case, "+\
                    " pd.type as type, "+\
                    " spi.net as net, "+\
                    " spi.filling as filling, "+\
                    " spi.sm as sm, "+\
                    " spi.meat as meat "+\
                    " FROM sis_pps_header ph "+\
                    " LEFT JOIN sis_pps_detail pd on ph.id=pd.header_id "+\
                    " LEFT JOIN sis_pps_item spi on pd.description = spi.description"+\
                    " WHERE ph.month="+str(int(date_plan[5:7]))+\
                    " AND pd.type = 'plan'" +\
                    " AND ph.year="+str(int(date_plan[0:4]))+\
                    " AND spi.ati12 = '" +ati12_plan+ "'"+\
                    " AND t"+str(int(date_plan[8:10]))+">0 and ph.ati12='"+ati12_plan+"'"
                
                SQL_db_live=" SELECT ph.id as header_id, "+\
                    " line_id, "+\
                    " qtyperuom, "+\
                    " spi.id as item_id, "+\
                    " t"+str(int(date_plan[8:10]))+ " as qty "+\
                    " FROM sis_pps_header ph "+\
                    " INNER JOIN sis_pps_detail pd on ph.id=pd.header_id and pd.type='plan' "+\
                    " INNER JOIN sis_pps_item spi on pd.description = spi.description"+\
                    " WHERE ph.month="+str(int(date_plan[5:7]))+\
                    " AND ph.year="+str(int(date_plan[0:4]))+\
                    " AND t"+str(int(date_plan[8:10]))+">0 and ph.ati12='"+ati12_plan+"'"

                """ UNTUK KONEKSI DB KE SERVER (PASTI BUTUH)     
                cur.execute(SQL_db_live)
                data_plan = cur.fetchall()
                """
                rec.env.cr.execute(SQL_db_local)
                data_plan = rec.env.cr.fetchall()
                
                if data_plan:
                    for row in data_plan:
                        header_id = row[0]
                        desc_item = row[1]
                        line_item = row[2]
                        qtyperuom = row[3]
                        item_id = row[4]
                        qty_plan = row[5]
                        line = row[6]
                        can_size = row[7]
                        speed = row[8]
                        kaleng_per_case = row[9]
                        type = row[10]
                        net = row[11]
                        meat = row[14]
                        
                        # Menghitung filling dan SM    
                        filling = 0
                        sm = 0
                        if meat != None and kaleng_per_case != None:
                            filling = float(meat * kaleng_per_case) / 1000
                            sm = float(meat * kaleng_per_case)
                        
                        
                        values = {}
                        values['pps_item_id'] = item_id
                        values['target_prd'] = qty_plan
                        values['line_epi'] = line
                        values['net_epi'] = net
                        values['can_size_epi'] = can_size
                        values['kaleng_per_case_epi'] = kaleng_per_case
                        values['speed_epi'] = speed
                        values['filling_epi'] = filling
                        values['sm_epi'] = sm
                         
                        temp.append((0, 0, values))
                     
                    return self.update({'epi_line_ids': temp})
                    
            else:
                raise UserError(_(
                             'Cannot get item from production plan!'))
                
    @api.multi
    def delete_sis_epi_line(self):
        epi_ids_line = []
        epi_id = self.id
        
        epi_line_obj = self.env['sis.epi'].search([('id', '=', epi_id)])
        if epi_line_obj:        
            epi_ids_line.append(([5]))

            return epi_line_obj.update({'epi_line_ids': epi_ids_line})
    
    @api.multi
    def calculate_epi(self):
        for rec in self:
            fish_using_line = rec.fish_using_line_ids
            for line in fish_using_line:
                start_pack = line.start_packing_fu
                jam_hasil_tonase = line.jam_hasil_tonase
                item_id = line.item_id_fu
                id = line.id
                start_pack_temp = line.start_packing_fu_temp
                urutan_item_fu = line.urutan_item_fu
                fish_type = line.fish_type_fu
                start_pack_temp = ""
                
                item_id_temp = 0
                format_datetime = '%Y-%m-%d %H:%M:%S'
                
                cl_time = 0
                pre_pk = 0
                cu_pk = 0
                cutting_time = 0
                co_pk = 0
                cooking_time = 0
                de_pk = 0
                defrost_time = 0
                total_time = 0
                
                for o in fish_type:
                    cl_time = o.cl_time
                    pre_pk = o.pre_pk
                    cu_pk = o.cu_pk
                    cutting_time = o.cutting_time
                    cooking_time = o.cooking_time
                    defrost_time = o.defrost_time
                    total_time = o.total_time
                    co_pk = o.co_pk
                    de_pk = o.de_pk
                    
                    
                # Jika ada tanggal start packing
                if start_pack:
                    
                    # Menggunakan cara ali
                    hasil = datetime.strptime(str(start_pack), format_datetime) + relativedelta(hours=float(jam_hasil_tonase))
                    
                    # Menggunakan cara endah
                    dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(jam_hasil_tonase) * 60, 60))
                    hour = int(dd[:2])
                    minut = int(dd[3:])
                    
                    finish_packing = datetime.strptime(str(start_pack), format_datetime) + relativedelta(hours=hour, minutes=minut)
                    
                    # Cleaning Time
                    cl_time_finish = 0.16666666666666666 # 10 Menit
                    start_cl_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(cl_time))
                    finish_cl_time = datetime.strptime(str(finish_packing), format_datetime) - relativedelta(hours=float(cl_time_finish))
                    
                    # Pre cleaning time
                    pre_cl_time_finish = 0.5 # 30 menit
                    start_pre_cl_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(pre_pk))
                    finish_pre_cl_time = datetime.strptime(str(finish_cl_time), format_datetime) - relativedelta(hours=float(pre_cl_time_finish))
                    
                    # Cutting time + i6
                    start_cutting_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(cu_pk))
                    finish_cutting_time = datetime.strptime(str(start_cutting_time), format_datetime) + relativedelta(hours=float(cutting_time))
                
                    # Cooking time + i6
                    finish_cutting = datetime.strptime(str(finish_cutting_time), format_datetime)
                    start_cutting = datetime.strptime(str(start_cutting_time), format_datetime)
                    # Second to hour / 3600
                    hasil_cutting = (finish_cutting - start_cutting).seconds / 3600
                    # Hitung start cooking
                    start_cooking_time = (datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(co_pk))) - (relativedelta(hours=float(hasil_cutting / 2)))
                    finish_cooking_time = datetime.strptime(str(start_cooking_time), format_datetime) + relativedelta(hours=float(cooking_time))
                    
                    # Defrost time + i6
                    start_defrost_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(de_pk))
                    finish_defrost_time = datetime.strptime(str(start_defrost_time), format_datetime) + relativedelta(hours=float(defrost_time))
                    
                    # Cool Storage time + i6
                    finish_cs_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(total_time))
                    
                    
                    line.write({'start_packing_fu_temp': finish_packing})
                    line.write({'finish_packing_fu': finish_packing})
                    
                    line.write({'start_cleaning_fu': start_cl_time})
                    line.write({'finish_cleaning_fu': finish_cl_time})
                    
                    line.write({'start_pre_cleaning_fu': start_pre_cl_time})
                    line.write({'finish_pre_cleaning_fu': finish_pre_cl_time})
                    
                    line.write({'start_cooking_fu': start_cooking_time})
                    line.write({'finish_cooking_fu': finish_cooking_time})
                     
                    line.write({'start_cutting_fu': start_cutting_time})
                    line.write({'finish_cutting_fu': finish_cutting_time})
                     
                    line.write({'start_defrost_fu': start_defrost_time})
                    line.write({'finish_defrost_fu': finish_defrost_time})
                     
                    line.write({'finish_cs_fu': finish_cs_time})
                    
                    

                # Jika tidak ada tanggal packing
                elif not start_pack and urutan_item_fu > 0:
                    # Get data from finish packing line sebelumnya
                    browse = self.env['sis.epi.fish.using.line'].browse(id-1)
                    for line_before in browse:
                        date = line_before.start_packing_fu_temp
                        item_id_before = line_before.item_id_fu
                        
                        if date:
                            start_pack_temp = datetime.strptime(str(line_before.start_packing_fu_temp), format_datetime)
                            # Isi tanggal start packing dengan tanggal finish packing
                            line.write({'start_packing_fu': start_pack_temp})
                            # Jika tanggal packing terisi, maka hitung kembali tanggal finish
                            if line.start_packing_fu:
                                dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(jam_hasil_tonase) * 60, 60))
                                hour = int(dd[:2])
                                minut = int(dd[3:])
                                
                                finish_packing = datetime.strptime(str(line.start_packing_fu), format_datetime) + relativedelta(hours=hour, minutes=minut)
                                line.write({'finish_packing_fu': finish_packing})
                                line.write({'start_packing_fu_temp': finish_packing})
                                
                                # Cleaning time
                                cl_time_finish = 0.0069444
                                start_cl_time = datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(cl_time))
                                finish_cl_time = datetime.strptime(str(finish_packing), format_datetime) - relativedelta(hours=float(cl_time_finish))
                                
                                # Pre cleaning time
                                pre_cl_time_finish = 0.0208333
                                start_pre_cl_time = datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(pre_pk))
                                finish_pre_cl_time = datetime.strptime(str(finish_packing), format_datetime) - relativedelta(hours=float(pre_cl_time_finish))
                                
                                # Cutting time + i6
                                start_cutting_time = datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(cu_pk))
                                finish_cutting_time = datetime.strptime(str(start_cutting_time), format_datetime) + relativedelta(hours=float(cutting_time))
                            
                                # Cooking time + i6
                                finish_cutting = datetime.strptime(str(finish_cutting_time), format_datetime)
                                start_cutting = datetime.strptime(str(start_cutting_time), format_datetime)
                                # Second to hour / 3600
                                hasil_cutting = (finish_cutting - start_cutting).seconds / 3600
                                # Hitung start cooking
                                start_cooking_time = (datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(co_pk))) - (relativedelta(hours=float(hasil_cutting / 2)))
                                finish_cooking_time = datetime.strptime(str(start_cooking_time), format_datetime) + relativedelta(hours=float(cooking_time))
                                
                                # Defrost time + i6
                                start_defrost_time = datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(de_pk))
                                finish_defrost_time = datetime.strptime(str(start_defrost_time), format_datetime) + relativedelta(hours=float(defrost_time))
                                
                                # Cool Storage time + i6
                                finish_cs_time = datetime.strptime(str(line.start_packing_fu), format_datetime) - relativedelta(hours=float(total_time))
                                
                                line.write({'start_cleaning_fu': start_cl_time})
                                line.write({'finish_cleaning_fu': finish_cl_time})
                                
                                line.write({'start_pre_cleaning_fu': start_pre_cl_time})
                                line.write({'finish_pre_cleaning_fu': finish_pre_cl_time})
                                
                                line.write({'start_cooking_fu': start_cooking_time})
                                line.write({'finish_cooking_fu': finish_cooking_time})
                                 
                                line.write({'start_cutting_fu': start_cutting_time})
                                line.write({'finish_cutting_fu': finish_cutting_time})
                                 
                                line.write({'start_defrost_fu': start_defrost_time})
                                line.write({'finish_defrost_fu': finish_defrost_time})
                                 
                                line.write({'finish_cs_fu': finish_cs_time})
                                
                                # Jika item sama dengan item sebelumnya
                                if item_id.id == item_id_before:
                                    line.write({'start_packing_fu': line_before.finish_packing_fu})
                                    
                                    dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(jam_hasil_tonase) * 60, 60))
                                    hour = int(dd[:2])
                                    minut = int(dd[3:])
                                    
                                    finish_packing = datetime.strptime(str(line.start_packing_fu), format_datetime) + relativedelta(hours=hour, minutes=minut)
                                    line.write({'finish_packing_fu': finish_packing})
                                    
                                    
                else:
                    continue
    
    
    # Action urut cutting wizard
    @api.multi
    def action_urut_cutting(self):
        for rec in self:
            fish_using_line = rec.fish_using_line_ids
            
            temp = []
            cutting_time = 0
            
            if fish_using_line:
                for row in fish_using_line:
                    item_id = row.item_id_fu
                    urutan_item_fu = row.urutan_item_fu
                    start_packing = row.start_packing_fu
                    finish_packing = row.finish_packing_fu
                    start_cleaning = row.start_cleaning_fu
                    finish_cleaning = row.finish_cleaning_fu
                    start_precleaning = row.start_pre_cleaning_fu
                    finish_precleaning = row.finish_pre_cleaning_fu
                    start_cutting = row.start_cutting_fu
                    finish_cutting = row.finish_cutting_fu
                    start_cooking = row.start_cooking_fu
                    finish_cooking = row.finish_cooking_fu
                    start_defrost = row.start_defrost_fu
                    finish_defrost = row.finish_defrost_fu
                    hasil_urut_item = row.hasil_urut_item_fu
                    finish_cs = row.finish_cs_fu
                    fish_type = row.fish_type_fu
                    
                    # Jika urutan item != 0
                    if urutan_item_fu != 0:
                        # Mengambil data cutting time
                        for data in fish_type:
                            cutting_time = data.cutting_time
                        
                        values = {}
                        values['item_id_wiz'] = item_id.id
                        values['start_packing_wiz'] = start_packing
                        values['finish_packing_wiz'] = finish_packing
                        values['start_cleaning_wiz'] = start_cleaning
                        values['finish_cleaning_wiz'] = finish_cleaning
                        values['start_precleaning_wiz'] = start_precleaning
                        values['finish_precleaning_wiz'] = finish_precleaning
                        values['start_cutting_wiz'] = start_cutting
                        values['finish_cutting_wiz'] = finish_cutting
                        values['start_cooking_wiz'] = start_cooking
                        values['finish_cooking_wiz'] = finish_cooking
                        values['start_defrost_wiz'] = start_defrost
                        values['finish_defrost_wiz'] = finish_defrost
                        values['finish_cs_wiz'] = finish_cs
                        values['hasil_urut_item_wiz'] = hasil_urut_item
                        values['cutting_time_wiz'] = cutting_time
                        values['fish_type_wiz'] = fish_type.id
                        
                        temp.append((0, 0, values))
                    
                    
            return {
                'name': 'Create Urut Cutting',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'urut.cutting.wizard',
                'target': 'new',
                'context': {
                     'default_epi_id_wiz': rec.id,
                     'default_urut_cutting_ids': temp
                }
            }
                
    # Fungsi hitung urut cutting
    @api.multi
    def calculate_urut_cutting(self):
        for rec in self:
            urut_cutting_line_ids = rec.urut_cutting_line_ids
            format_datetime = '%Y-%m-%d %H:%M:%S'
            
            
            if urut_cutting_line_ids:
                for row in urut_cutting_line_ids:
                    item = row.item_id_uc
                    toleransi = row.toleransi
                    fish_type = row.fish_type_uc
                    
                    start_cutting = row.start_cutting_uc
                    adj_cutting = row.adj_cutting_uc
                    cut_time = row.cutting_time_uc
                    start_pack = row.start_packing_uc
                    
                    cl_time = 0
                    pre_pk = 0
                    cu_pk = 0
                    cutting_time = 0
                    co_pk = 0
                    cooking_time = 0
                    de_pk = 0
                    defrost_time = 0
                    total_time = 0
                    
                    for o in fish_type:
                        cl_time = o.cl_time
                        pre_pk = o.pre_pk
                        cu_pk = o.cu_pk
                        cutting_time = o.cutting_time
                        cooking_time = o.cooking_time
                        defrost_time = o.defrost_time
                        total_time = o.total_time
                        co_pk = o.co_pk
                        de_pk = o.de_pk
              
                    start_cutting_format = datetime.strptime(str(start_cutting), format_datetime)
                    adj_cutting_format = datetime.strptime(str(adj_cutting), format_datetime)
                    
                    # Perhitungan start cutting 
                    hasil = (start_cutting_format - adj_cutting_format) # Untuk mencari toleransi
                    hasil_hour = (hasil.total_seconds()) / 3600 # minutes to hours
                    
                    # Perhitungan finish cutting
                    dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cut_time) * 60, 60))
                    hour = int(dd[:2])
                    minut = int(dd[3:])
                    
                    start_cutting_change = start_cutting_format - (relativedelta(hours=float(hasil_hour)))
                    finish_cutting_change = datetime.strptime(str(adj_cutting), format_datetime) + relativedelta(hours=hour, minutes=minut)
                    
                    # Cooking time
                    # Cooking time + i6
                    finish_cutting = datetime.strptime(str(finish_cutting_change), format_datetime)
                    start_cutting = datetime.strptime(str(start_cutting_change), format_datetime)
                    # Second to hour / 3600
                    hasil_cutting = (finish_cutting - start_cutting).seconds / 3600
                    # Hitung start cooking
                    start_cooking_change = ((datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(co_pk))) + (relativedelta(hours=float(hasil_hour)))) - (relativedelta(hours=float(hasil_cutting / 2)))
                    finish_cooking_change = datetime.strptime(str(start_cooking_change), format_datetime) + relativedelta(hours=float(cooking_time))
                    
                    
                    row.write({
                        'start_cutting_uc': start_cutting_change,
                        'finish_cutting_uc': finish_cutting_change,
                        'start_cooking_uc': start_cooking_change,
                        'finish_cooking_uc': finish_cooking_change
                        })
#             
                    
                    
                    
    

class sis_epi_line(models.Model):
    _name = 'sis.epi.line'
    _rec_name = 'id'
    
    epi_id = fields.Many2one('sis.epi', ondelete='cascade')
    pps_item_id = fields.Many2one('sis.pps.item', string="Item")
    line_epi = fields.Char(string="Line", readonly=True)
    net_epi = fields.Float(string="Net(w)", readonly=True)
    can_size_epi = fields.Char(string="Can Size", readonly=True)
    kaleng_per_case_epi = fields.Float(string="Kaleng per Case", readonly=True, digits=(12,0))
    speed_epi = fields.Float(string="Speed(cs/jam)", readonly=True, digits=(12,0))
    target_prd = fields.Float(string="Target Produksi(cs)", track_visibility='onchange', readonly=True)
    budomari_epi = fields.Many2one('sis.budomari', string="Budomari")
    filling_epi = fields.Float(string="Filling", readonly=True)
    sm_epi = fields.Float(string="SM", readonly=True)
    yieldd_epi = fields.Float(string="Yield", store=True, compute='calculate_yield')
    yield_total_epi = fields.Float(string="Yield Total", store=True, compute='calculate_total_yield')
    yield_total_epi_epi = fields.Float(string="Target Qty Fish(ton)", compute='calculate_yield_epi_epi', store=True)
    waktu_packing_epi = fields.Float(string="Est Wkt Pack(jam)", store=True, compute='calculate_estimasi_wkt_packing')
    meat_epi = fields.Float(string="Meat", store=True, compute='calculate_sm')
    qty_fish_total_epi = fields.Float(string="Qty Fish Total(ton)", readonly=True)
    start_packing_epi = fields.Datetime(string="Start Pack")
    
    sis_epi_line_temp_ids = fields.One2many('sis.epi.line.temp', 'epi_line_id')
    
    
    # Ambil semua data dari item
    @api.onchange('pps_item_id')
    def get_value_item(self):
        for rec in self:
            item_id = rec.pps_item_id
            
            item_obj = rec.env['sis.pps.item'].search([('id', '=', item_id.id)])
            
            if item_obj:
                for row in item_obj:
                    line = row.line
                    can_size = row.can_size
                    speed = row.speed
                    kaleng_per_case = row.kaleng_per_case
                    net = row.net
                    yieldd = row.yieldd
                    filling = row.filling
                    sm = row.sm
                    
                rec.line_epi = line
                rec.can_size_epi = can_size
                rec.net_epi = net
                rec.kaleng_per_case_epi = kaleng_per_case
                rec.speed_epi = speed
                rec.filling_epi = filling
                rec.sm_epi = sm
    
    
    # Calculate yield
    @api.depends('budomari_epi', 'filling_epi')
    def calculate_yield(self):
        for rec in self:
            filling_epi = rec.filling_epi
            budomari_id = rec.budomari_epi
            
            if budomari_id:
                for row in budomari_id:
                    value_budomari = row.budomari
                
                hasil = (filling_epi / value_budomari) * 100
                rec.yieldd_epi = hasil
    
    # Calculate total yield
    @api.depends('yieldd_epi', 'target_prd')
    def calculate_total_yield(self):
        for rec in self:
            target_prd = rec.target_prd
            yield_epi = rec.yieldd_epi
             
            hasil = yield_epi * target_prd
            rec.yield_total_epi = hasil
        
    
    # Calculate estimasi waktu packing
    @api.depends('target_prd', 'speed_epi')
    def calculate_estimasi_wkt_packing(self):
        for rec in self:
            target_prd = rec.target_prd
            speed = rec.speed_epi
             
            if speed != 0:
                hasil = target_prd / speed
                 
                rec.waktu_packing_epi = hasil
     
    # Calculate meat epi
    @api.depends('waktu_packing_epi', 'sm_epi')
    def calculate_sm(self):
        for rec in self:
            sm = rec.sm_epi
            estimasi_waktu_pck = rec.waktu_packing_epi
            
            if estimasi_waktu_pck != 0:
                hasil = sm / estimasi_waktu_pck
                
                rec.meat_epi = hasil
    
    
    @api.depends('yield_total_epi')
    def calculate_yield_epi_epi(self):
        for rec in self:
            yield_total_epi = rec.yield_total_epi
            hasil = yield_total_epi / 1000
            
            rec.yield_total_epi_epi = hasil

    
    @api.multi
    def action_detail_view(self):
        for rec in self:
#             view = rec.env['ir.model.data'].xmlid_to_res_id('sis_epi.sis_epi_detail_form', raise_if_not_found=True)  
            view = self.env.ref('sis_epi.sis_epi_detail_form')
            fish_size_temp = ""
            fish_qty_temp = 0.0
            temp = []
            epi_line_id = rec.id
            target_prd = rec.target_prd
            sis_epi_line_temp = rec.sis_epi_line_temp_ids
            sis_epi_line_temp_count = len(sis_epi_line_temp)
            yield_total_epi_epi = rec.yield_total_epi_epi
            print(sis_epi_line_temp_count)
            
            # Jika terdapat data temporary, maka : 
            if sis_epi_line_temp_count > 0:
            
                for row in rec.sis_epi_line_temp_ids:
                    fish_size_temp = row.size_fish_temp
                    fish_qty_temp = row.qty_fish_temp
                    
                    values = {}
                    values['size_fish'] = fish_size_temp
                    values['qty_fish'] = fish_qty_temp
                    temp.append((0, 0, values))
                                                         
                              
                result2 = {
                    'name': 'Detailed EPI',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sis.epi.detail',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
#                     'res_id': model.id,
                    'context': {
                            'default_epi_detail_line': temp,
                            'default_epi_line_id': rec.id,
                            'default_target_prd_detail': target_prd,
                            'default_yield_total_detail': yield_total_epi_epi,
                        }
                            
                }
             
                return result2
                
            
            else:
                result = {
                    'name': 'Detailed EPI',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sis.epi.detail',
                    'views': [(view.id, 'form')],
                    'view_id': view.id,
                    'target': 'new',
                    'context':{
                        'default_epi_line_id': rec.id,
                        'default_target_prd_detail': target_prd,
                        'default_yield_total_detail': yield_total_epi_epi,
                    }
                        
                }
                 
                return result


class sis_epi_line_temp(models.Model):
    _name = 'sis.epi.line.temp'
    
    epi_line_id = fields.Many2one('sis.epi.line', ondelete='cascade')
    size_fish_temp = fields.Char()
    qty_fish_temp = fields.Float()
