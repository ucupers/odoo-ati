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
from PIL.Image import NORMAL
from odoo.addons.sis_epi.models.sis_urut_cutting import adj_cutting
from jedi.debug import speed


passwd = "mis1.anekatuna"

class sis_epi_xls(models.TransientModel):
    _name='sis.epi.xls'

    report=fields.Binary(string='Report')

class sis_epi(models.Model):
    _name = 'sis.epi'
    _rec_name = 'name'
    _inherit = 'mail.thread'
    
    
    @api.model
    def _get_default_ac(self):
        return self.env['sis.budomari'].search([('fish', '=', 'AC')], limit=1).id
    
    @api.model
    def _get_default_sj(self):
        return self.env['sis.budomari'].search([('fish', '=', 'SJ')], limit=1).id
    
    @api.model
    def _get_default_sm(self):
        return self.env['sis.budomari'].search([('fish', '=', 'SM')], limit=1).id
    
    @api.model
    def _get_default_tg(self):
        return self.env['sis.budomari'].search([('fish', '=', 'TG')], limit=1).id
    
    @api.model
    def _get_default_yf(self):
        return self.env['sis.budomari'].search([('fish', '=', 'YF')], limit=1).id
    
    @api.model
    def _get_default_yfb(self):
        return self.env['sis.budomari'].search([('fish', '=', 'YFB')], limit=1).id
    
    name = fields.Char(string="Name")
    epi_line_ids = fields.One2many('sis.epi.line', 'epi_id')
    
    state = fields.Selection([('schedule', 'Draft Schedule'), ('estimasi_pack', 'Estimasi Pack'), 
                              ('fish_using', 'Fish Using'),('adj_cutting', 'Adj Cutting'), ('urut_cutting', 'Urut Cutting'), 
                              ('done', 'Done'), ('cancel', 'Cancel')], default='schedule', string="State", track_visibility='onchange')
    total_qty_fish = fields.Float(string="Total Actual Fish(ton)", compute='compute_total_fish', store=True)
    total_target_qty_fish = fields.Float(string="Total Target Fish(ton)", compute='compute_target_qty', store=True)
    total_qty_fcl = fields.Float(string="Total Qty FCL", readonly=True)
    
    # Production plan
    date_plan = fields.Date(string="Date", required=True, track_visibility='onchange')
    date_plan_format = fields.Char(string="Date format")
    # budomari_ids = fields.Many2many('sis.epi.budomari.master', string="Budomari")
    
    # Flagging button
    is_sort_asc = fields.Boolean()
    is_insert_adj_cut = fields.Boolean()
    is_urut_cutting = fields.Boolean()
    is_get_item = fields.Boolean()
    
    # Budomari
    budomari_bool_ac = fields.Boolean(string="Budomari AC")
    budomari_bool_sj = fields.Boolean(string="Budomari SJ")
    budomari_bool_sm = fields.Boolean(string="Budomari SM")
    budomari_bool_tg = fields.Boolean(string="Budomari TG")
    budomari_bool_yf = fields.Boolean(string="Budomari YF")
    budomari_bool_yfb = fields.Boolean(string="Budomari YFB")
    
    
    budomari_id_ac = fields.Many2one('sis.budomari', string="Presentase AC(%)", domain=[('fish', '=', 'AC')], default=_get_default_ac)
    budomari_id_sj = fields.Many2one('sis.budomari', string="Presentase SJ(%)", domain=[('fish', '=', 'SJ')], default=_get_default_sj)
    budomari_id_sm = fields.Many2one('sis.budomari', string="Presentase SM(%)", domain=[('fish', '=', 'SM')], default=_get_default_sm)
    budomari_id_tg = fields.Many2one('sis.budomari', string="Presentase TG(%)", domain=[('fish', '=', 'TG')], default=_get_default_tg)
    budomari_id_yf = fields.Many2one('sis.budomari', string="Presentase YF(%)", domain=[('fish', '=', 'YF')], default=_get_default_yf)
    budomari_id_yfb = fields.Many2one('sis.budomari', string="Presentase YFB%)", domain=[('fish', '=', 'YBF')], default=_get_default_yfb)
    
    # Field ini DIPAKAI!
    coba = fields.Float(compute='calculate_budomari')
    
    ati12_plan = fields.Selection([('ati1','ATI1'),('ati2','ATI2')], string="ATI1/ATI2", required=True)
    
    # Fish using
    fish_using_line_ids = fields.One2many('sis.epi.fish.using.line', 'epi_id_fu', string="Fish Using")
    
    # Urut cutting
    urut_cutting_line_ids = fields.One2many('sis.urut.cutting.line', 'epi_id_uc', string="Urut Cutting")
    
    # Adj cutting
    adj_cutting_line_ids = fields.One2many('sis.adj.cutting.line', 'epi_id', string="Adj Cuttting")
    

    
    @api.model
    def create(self, vals):
        res = super(sis_epi, self).create(vals)

        # Sequence
        sequence = self.env['ir.sequence'].next_by_code('sequence.sis.epi') or ('New')
        res.update({'name': sequence})

        return res
    
    # Hitung actual total fish
    @api.depends('epi_line_ids.qty_fish_total_epi')
    def compute_total_fish(self):
        for rec in self:
            qty_fish = 0
            epi_line = rec.epi_line_ids
            if epi_line:
                for row in epi_line:
                    qty_fish = qty_fish + row.qty_fish_total_epi
                
                rec.total_qty_fish = qty_fish
                
    # Hitung total fish
    @api.depends('epi_line_ids.yield_total_epi_epi')
    def compute_target_qty(self):
        for rec in self:
            target_qty = 0
            epi_line = rec.epi_line_ids
            if epi_line:
                for row in epi_line:
                    target_qty = target_qty + row.yield_total_epi_epi
                
                rec.total_target_qty_fish = target_qty
    
    
    
    """ Tidak dipakai
    @api.onchange('budomari_ids')
    def get_budomari(self):
        for rec in self:
            budomari = rec.budomari_ids
            
            if budomari:
                for row in budomari:
                    budomari_name = row.name
                    print("budomari", budomari_name)
                    
                    if budomari_name == 'AC':
                        rec.budomari_bool_ac = True
                     
                        rec.budomari_bool_sj = False
                        rec.budomari_bool_sm = False
                        rec.budomari_bool_tg = False
                        rec.budomari_bool_yf = False
                        rec.budomari_bool_yfb = False
                        
                        print("ac masuk sini bos", rec.budomari_bool_ac)
                        
                    
                    elif budomari_name == 'SJ':
                        rec.budomari_bool_sj = True
                        
                    
                    elif budomari_name == 'SM':
                        rec.budomari_bool_sm = True
                        
                    elif budomari_name == 'TG':
                        rec.budomari_bool_tg = True
                        
                    elif budomari_name == 'YF':
                        rec.budomari_bool_yf = True
                    
                    elif budomari_name == 'YFB':
                        rec.budomari_bool_yfb = True
                    
                    else:
                        rec.budomari_bool_ac = False
                        rec.budomari_bool_sj = False
                        rec.budomari_bool_sm = False
                        rec.budomari_bool_tg = False
                        rec.budomari_bool_yf = False
                        rec.budomari_bool_yfb = False
                        
                        print("ac masuk sini", rec.budomari_bool_ac)
                    
                    
        
        
            else:
                rec.budomari_bool_ac = False
                rec.budomari_bool_sj = False
                rec.budomari_bool_sm = False
                rec.budomari_bool_tg = False
                rec.budomari_bool_yf = False
                rec.budomari_bool_yfb = False 
                
                print("ac masuk sini terakhir", rec.budomari_bool_ac)
            
            """
    
    # Button confirm
    @api.multi
    def action_confirm(self):
        for rec in self:
            
            rec.update({'state': 'estimasi_pack'})
        
            
    
# Button action create fish using tab
#     @api.multi
#     def action_fish_using(self):
#         for rec in self:
#             epi_line = rec.epi_line_ids
#             temp = []
#             item_temp = 0
#             i = 1
#             temp_temp = []
#             fish_using_line_ids = rec.fish_using_line_ids
#             
#             
#             count_fish_using = len(self.mapped('fish_using_line_ids'))
#             if count_fish_using > 0:
#                 return {
#                     'name': 'Warning',
#                     'type': 'ir.actions.act_window',
#                     'view_type': 'form',
#                     'view_mode': 'form',
#                     'res_model': 'message.fish.using',
#                     'target': 'new',
#                     'context': {
#                          'default_id_epi': rec.id,
#                          'default_name': "The data will be replaced, Are you sure create fish using again?",
#                     }
#                }
#             
#             # Create temporary line untuk tab fish using
#             # values_temp = {}
#             # values_temp['urutan_item_fu'] = i
#             
#            #  temp.append((0, 0, values_temp))
#             
#             for row in epi_line:
#                 epi_line_id = row.id
#                 start_packing = row.start_packing_epi
#                 item_id = row.pps_item_id
#                 start_packing = row.start_packing_epi
#                 waktu_estimasi_pack = row.waktu_packing_epi
#                 yield_total = (row.yield_total_epi / 1000)
#                 qty_fish_total = row.qty_fish_total_epi
#                 remark = row.remark_epi
#                 epi_line_temp = row.sis_epi_line_temp_ids
#                 epi_line_temp_count = len(row.sis_epi_line_temp_ids)
#                 
# #                 epi_detail_obj = self.env['sis.epi.detail'].search([('epi_line_id', '=', epi_line_id)])
#                 if epi_line_temp:
#                     for epi_detail in epi_line_temp:
#                         qty_fish_temp = epi_detail.qty_fish_temp
#                         size_fish_temp = epi_detail.size_fish_temp
#                         
#                         print("fish temp ", qty_fish_temp, size_fish_temp)
#                 
#                         j = 0
#                 
#                         # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
#                         if qty_fish_temp > 0:
#                             row_fish_using = qty_fish_temp / 4
#                             hasil_bagi = math.floor(row_fish_using)
#                             
#                             if epi_line_temp_count > 1:
#                                 if hasil_bagi == 0:
#                                     
#                                     values = {}
#                                     values['epi_line_id_fu'] = row.id
#                                 
#                             # Jika hasil pembagian == 0 atau nilai yang diinput < 4
#                             if hasil_bagi == 0:
#                                 
#                                 values = {}
#                                 values['epi_line_id_fu'] = row.id
#                                 values['item_id_fu'] = item_id.id
#                                 values['waktu_packing_fu'] = waktu_estimasi_pack
#                                 values['fish_qty_fu'] = qty_fish_total
#                                 values['start_packing_fu'] = start_packing
#                                 values['remark_fu'] = remark
#                                 values['urutan_item_fu'] = i + 1 # No urut bertambah
#                                 values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
#                                 values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
#                                 i = i + 1
#                                 j = 1
#                                 
#                                 temp.append((0, 0, values))
#                             
#                             
#                             # Jika hasil bagi > 0
#                             else:
#                                 
#                                 baris = 1
#                                 # Insert ke fish using line (pembulatan ke bawah)
#                                 for line in range(hasil_bagi):
#                                     # Jika line pertama pada item baru, input start packing
#                                     
#                                     values = {}
#                                     values['epi_line_id_fu'] = row.id
#                                     values['item_id_fu'] = item_id.id
#                                     values['waktu_packing_fu'] = waktu_estimasi_pack
#                                     values['fish_qty_fu'] = qty_fish_total
#                                     values['remark_fu'] = remark
#                                     
#                                     if baris == 1:
#                                         values['start_packing_fu'] = start_packing
#                                         baris = baris + 1
#                                     
#                                     # Jika item sama dengan sebelumnya
#                                     if item_temp == 0 or item_temp == item_id.id:
#                                         values['urutan_item_fu'] = i # no urut sama dengan sebelumnya
#                                         values['urutan_item_fu_2'] = j + 1 # no urut 2 increament
#                                         values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
#                                         j = j + 1
#                                     
#                                     # Jika item berbeda
#                                     else:
#                                         values['start_packing_fu'] = start_packing
#                                         values['urutan_item_fu'] = i + 1 # No urut bertambah
#                                         values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
#                                         values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
#                                         i = i + 1
#                                         j = 1
#                                 
#                                     item_temp = item_id.id
#                                     temp.append((0, 0, values))
#                         
#             return self.update({'fish_using_line_ids': temp,})
#                     
    
    
    # Button action create fish using tab
    @api.multi
    def action_fish_using(self):
        for rec in self:
            epi_line = rec.epi_line_ids
            temp = []
            item_temp = 0
            i = 1
            temp_temp = []
            fish_using_line_ids = rec.fish_using_line_ids
             
            count_fish_using = len(self.mapped('fish_using_line_ids'))
            if count_fish_using > 0:
                return {
                    'name': 'Warning',
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'message.fish.using',
                    'target': 'new',
                    'context': {
                         'default_id_epi': rec.id,
                         'default_name': "The data will be replaced, Are you sure create fish using again?",
                    }
               }
             
            # Create temporary line untuk tab fish using
            # values_temp = {}
            # values_temp['urutan_item_fu'] = i
             
           #  temp.append((0, 0, values_temp))
             
            for row in epi_line:
                start_packing = row.start_packing_epi
                item_id = row.pps_item_id
                start_packing = row.start_packing_epi
                waktu_estimasi_pack = row.waktu_packing_epi
                yield_total = (row.yield_total_epi / 1000)
                qty_fish_total = row.qty_fish_total_epi
                remark = row.remark_epi
                 
                j = 0
                 
                # Jika ada qty ikan lebih dari nol, maka akan di proses di fish using
                if qty_fish_total > 0:
                    row_fish_using = qty_fish_total / 4
                    hasil_bagi = math.floor(row_fish_using)
                     
                    # Jika hasil pembagian == 0 atau nilai yang diinput < 4
                    if hasil_bagi == 0:
                        values = {}
                        values['epi_line_id_fu'] = row.id
                        values['item_id_fu'] = item_id.id
                        values['waktu_packing_fu'] = waktu_estimasi_pack
                        values['fish_qty_fu'] = qty_fish_total
                        values['start_packing_fu'] = start_packing
                        values['remark_fu'] = remark
                        values['urutan_item_fu'] = i + 1 # No urut bertambah
                        values['urutan_item_fu_2'] = 1 # No urut pertama balik ke angka satu
                        values['hasil_urut_item_fu'] = str(values['urutan_item_fu']) + "." + str(values['urutan_item_fu_2']) # Menggabungkan no urut
                        i = i + 1
                        j = 1
                         
                        temp.append((0, 0, values))
                     
                    # Jika hasil bagi > 0
                    else:
                         
                        baris = 1
                        # Insert ke fish using line (pembulatan ke bawah)
                        for line in range(hasil_bagi):
                            # Jika line pertama pada item baru, input start packing
                             
                            values = {}
                            values['epi_line_id_fu'] = row.id
                            values['item_id_fu'] = item_id.id
                            values['waktu_packing_fu'] = waktu_estimasi_pack
                            values['fish_qty_fu'] = qty_fish_total
                            values['remark_fu'] = remark
                             
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
                         
            return self.update({'fish_using_line_ids': temp, 'state': 'fish_using'})
#     
    # Button Adj Cutting
    @api.multi
    def action_adj_cutting(self):
        for rec in self:
            rec.update({'state': 'urut_cutting'})
            
    # Button cancel 
    @api.multi
    def action_cancel(self):
        for rec in self:
            rec.update({'state': 'cancel'})
    
    # Button Done
    @api.multi
    def action_done(self):
        for rec in self:
            rec.update({'state': 'done'})
    
    
    # BUTTON BACK
    @api.multi
    def back_to_estimasi_pack(self):
        for rec in self:
            rec.update({'state': 'estimasi_pack'})
    
    
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
            is_get_item = rec.is_get_item
            
            
            # Koneksi ke database live untuk mengambil data
#             conn = psycopg2.connect(
#                 host="localhost",
#                 database="PT_ATI",
#                 user="odoo",
#                 password=passwd
#             )
#             cur = conn.cursor()
            
            if date_plan and ati12_plan:
                
                # COMPUTE QTY FCL
                SQL_QTY_FCL =" SELECT DISTINCT SUM(pf.t"+str(int(date_plan[8:10]))+ ") as qty_fcl "+\
                             " FROM sis_pps_header ph "+\
                             " LEFT JOIN sis_pps_fcl pf on ph.id = pf.header_id "+\
                             " WHERE ph.month="+str(int(date_plan[5:7]))+\
                             " AND ph.year="+str(int(date_plan[0:4]))+\
                             " AND ph.ati12='"+ati12_plan+"'"+\
                             " AND pf.description != 'TOTAL'"
                
                if SQL_QTY_FCL:
                    rec.env.cr.execute(SQL_QTY_FCL)
                    qty_fcl = rec.env.cr.fetchone()
                    if qty_fcl:
                        sum_qty = qty_fcl[0]
                        
                        rec.total_qty_fcl = sum_qty
                
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
                    " spi.meat as meat, "+\
                    " spi.remark as remark "+\
                    " FROM sis_pps_header ph "+\
                    " LEFT JOIN sis_pps_detail pd on ph.id=pd.header_id "+\
                    " LEFT JOIN sis_pps_item spi on pd.description = spi.description"+\
                    " WHERE ph.month="+str(int(date_plan[5:7]))+\
                    " AND pd.type = 'production'" +\
                    " AND ph.year="+str(int(date_plan[0:4]))+\
                    " AND spi.ati12 = '" +ati12_plan+ "'"+\
                    " AND t"+str(int(date_plan[8:10]))+">0 and ph.ati12='"+ati12_plan+"'"
                
                
                SQL_db_live=" SELECT DISTINCT ph.id as header_id, "+\
                    " spi.description as desc, "+\
                    " pd.line_id, "+\
                    " pd.qtyperuom as jumlah_kaleng_per_case, "+\
                    " spi.id as item_id, "+\
                    " t"+str(int(date_plan[8:10]))+ " as qty, "+\
                    " spi.line as line_item, "+\
                    " spi.can_size as can_size, "+\
                    " spi.capacity as speed, "+\
                    " spi.kaleng_per_case as kaleng_per_case, "+\
                    " pd.type as type, "+\
                    " spi.net as net, "+\
                    " spi.meat as meat, "+\
                    " spi.remark as remark, "+\
                    " spi.fishmaterial as fishmaterial, "+\
                    " spi.item_no as itemno, "+\
                    " si.nw as nw " +\
                    " FROM sis_pps_header ph "+\
                    " LEFT JOIN sis_pps_detail pd on ph.id=pd.header_id "+\
                    " LEFT JOIN sis_pps_item spi on pd.description = spi.description"+\
                    " LEFT JOIN sis_items si on spi.item_no = si.itemno "+\
                    " LEFT JOIN sis_spec_prod ssp on si.itemno = ssp.item_no "+\
                    " WHERE ph.month="+str(int(date_plan[5:7]))+\
                    " AND pd.type = 'production'" +\
                    " AND ph.year="+str(int(date_plan[0:4]))+\
                    " AND spi.ati12 = '" +ati12_plan+ "'"+\
                    " AND t"+str(int(date_plan[8:10]))+">0 and ph.ati12='"+ati12_plan+"'"+\
                    " AND ssp.spec_state = 'confirm'"+\
                    " ORDER BY spi.line"
                

                # UNTUK KONEKSI DB KE SERVER (PASTI BUTUH)     
#                 cur.execute(SQL_db_live)
#                 data_plan = cur.fetchall()
                
                rec.env.cr.execute(SQL_db_live)
                data_plan = rec.env.cr.fetchall()
            
                
                if data_plan:
                    
                    for row in data_plan:
                        values = {}
                        char = ""
                        array = []
                        
                        header_id = row[0]
                        desc_item = row[1]
                        line_item = row[2]
                        kaleng_per_case_use = row[3]
                        item_id = row[4]
                        qty_plan = row[5]
                        line = row[6]
                        can_size = row[7]
                        speed = row[8]
                        kaleng_per_case = row[9]
                        type = row[10]
                        net = row[11]
                        meat = row[12]
                        remark = row[13]
                        fish_material = row[14]
                        item_no = row[15]
                        nw = row[16]
                        
                        # Menghitung filling dan SM    
                        filling = 0
                        sm = 0
                        if meat != None and kaleng_per_case_use != None:
                            filling = float(meat * kaleng_per_case_use) / 1000
                            sm = float(meat * kaleng_per_case_use)
                        
                        # GET VALUE CAN SIZE
                        if item_no:
                            self.env.cr.execute("select linedesc from sis_production_bom "
                                                "where itemno = '" + str(item_no) + "' "
                                                "and (lineitem like '%EMB%' or lineitem like '%ELB%')")
                            
                            sql = self.env.cr.fetchall()
                            if sql:
                                for data in sql:
                                    can_size = data[0]
                                    if can_size:
                                        # Jika ada data, masukkan ke dalam array
                                        array.append((can_size))
                                
                                if array:
                                    i = 1
                                    for isi in array:
                                        if i == 1:
                                            char = char + str(isi)
                                        
                                        else:
                                            char = char + ", " + str(isi)
                                        
                                        i = i + 1
                                
                                values['can_size_epi'] = char
                        
                        # GET VALUE MEAT
                        if item_no:
                            self.env.cr.execute("select itemno as itemno, "
                                    "description as description, "
                                    "SUM(lineqty) as lineqty "
                                    "from sis_production_bom "
                                    "where lineitem like '%WIP%' "
                                    "and itemno = '" + str(item_no) + "'"
                                    "and linedesc not like '%Meat Shredded%' "
                                    "and linedesc not like '%Meat Red%' "
                                    "group by itemno, description")

                            sql = self.env.cr.fetchone()
                            if sql:
                                qty_meat = sql[2]
                                
                                values['meat'] = qty_meat
                        
                        
                        
                        values['pps_item_id'] = item_id
                        values['target_prd'] = qty_plan
                        values['line_epi'] = line
#                         values['net_epi'] = net
#                         values['can_size_epi'] = can_size
                        values['kaleng_per_case_epi'] = kaleng_per_case_use
                        values['speed_epi'] = speed
#                         values['filling_epi'] = filling
                        values['sm_epi'] = sm
                        values['remark_epi'] = remark
                        values['fish_material_epi'] = fish_material
                        values['item_no_epi'] = item_no
                        values['net_epi'] = nw * 1000 # Dikali 1000 untuk konversi ke gram
                        
                         
                        temp.append((0, 0, values))
                    
                    self.update({'epi_line_ids': temp})
                    
                    # Jika sudah pernah di get item, maka muncul pop up message
                    if is_get_item == True:
                        return rec.message_get_item_action()
                    
                    # Update flagging buttong get item
                    rec.update({'is_get_item': True})
                    
                else:
                    raise UserError(_(
                         'Nothing data from production plan!'))
                    
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
    
    # POP MESSAGE GET ITEM
    @api.multi
    def message_get_item_action(self):
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'message.get.data',
            'target': 'new',
            'context': {'default_name': "Data Successfully Updated"}
        }
        
        
    # SORT ASC URUT ITEM
    # Fungsi sort ASC urut item (kolom N)
    @api.multi
    def sort_asc_urut_item(self):
        for rec in self:
            fish_using_ids = rec.fish_using_line_ids
            epi_id = rec.id
            temp = []
            i = 1
            
            if fish_using_ids:
                self.env.cr.execute("select id as id, item_id_fu as item_id, hasil_urut_item_fu "
                                    "from sis_epi_fish_using_line "
                                    "where epi_id_fu = '"+ str(epi_id) +"' "
                                    "order by hasil_urut_item_fu")
                
                # Data ASC
                sql = self.env.cr.fetchall()
                if sql:
                    for sql_data in sql:
                        id_line = sql_data[0]
                        item_id_sql = sql_data[1]
                        hasil_urut_item_sql = sql_data[2]
                        
                        for row in fish_using_ids:
                            id_line_fu = row.id
                            item_id_fu = row.item_id_fu
                            tonase_fu = row.tonase_fu
                            total_tonase_fu = row.total_tonase_fu
                            temp_total_tonase_fu = row.temp_total_tonase_fu
                            remark_fu = row.remark_fu
                            waktu_packing_fu = row.waktu_packing_fu
                            fish_type_fu = row.fish_type_fu
                            urutan_item_fu = row.urutan_item_fu
                            urutan_item_fu_2 = row.urutan_item_fu_2
                            hasil_urut_item_fu = row.hasil_urut_item_fu
                            fish_qty_fu = row.fish_qty_fu
                            count = row.count
                            hasil_tonase = row.hasil_tonase
                            jam_hasil_tonase = row.jam_hasil_tonase
                            start_packing_fu = row.start_packing_fu
                            finish_packing_fu = row.finish_packing_fu
                            start_cleaning_fu = row.start_cleaning_fu
                            finish_cleaning_fu = row.finish_cleaning_fu
                            start_pre_cleaning_fu = row.start_pre_cleaning_fu
                            finish_pre_cleaning_fu = row.finish_pre_cleaning_fu
                            start_cooking_fu = row.start_cooking_fu
                            finish_cooking_fu = row.finish_cooking_fu
                            start_cutting_fu = row.start_cutting_fu
                            finish_cutting_fu = row.finish_cutting_fu
                            start_defrost_fu = row.start_defrost_fu
                            finish_defrost_fu = row.finish_defrost_fu
                            finish_cs_fu = row.finish_cs_fu
                            start_packing_fu_temp = row.start_packing_fu_temp
                            
                            # Cek jika data ada maka insert ASC
                            if id_line == id_line_fu:
                                
                                values = {}
                                values['item_id_fu'] = item_id_fu
                                values['tonase_fu'] = tonase_fu
                                values['total_tonase_fu'] = total_tonase_fu
                                values['temp_total_tonase_fu'] = temp_total_tonase_fu
                                values['remark_fu'] = remark_fu
                                values['waktu_packing_fu'] = waktu_packing_fu
                                values['fish_type_fu'] = fish_type_fu
                                values['urutan_item_fu'] = urutan_item_fu
                                values['urutan_item_fu_2'] = urutan_item_fu_2
                                values['hasil_urut_item_fu'] = hasil_urut_item_fu
                                values['fish_qty_fu'] = fish_qty_fu
                                values['count'] = count
                                values['hasil_tonase'] = hasil_tonase
                                values['jam_hasil_tonase'] = jam_hasil_tonase
                                values['start_packing_fu'] = start_packing_fu
                                values['finish_packing_fu'] = finish_packing_fu
                                values['start_cleaning_fu'] = start_cleaning_fu
                                values['finish_cleaning_fu'] = finish_cleaning_fu
                                values['start_pre_cleaning_fu'] = start_pre_cleaning_fu
                                values['finish_pre_cleaning_fu'] = finish_pre_cleaning_fu
                                values['start_cooking_fu'] = start_cooking_fu
                                values['finish_cooking_fu'] = finish_cooking_fu
                                values['start_cutting_fu'] = start_cutting_fu
                                values['finish_cutting_fu'] = finish_cutting_fu
                                values['start_defrost_fu'] = start_defrost_fu
                                values['finish_defrost_fu'] = finish_defrost_fu
                                values['finish_cs_fu'] = finish_cs_fu
                                values['start_packing_fu_temp'] = start_packing_fu_temp
                                
                                temp.append((0, 0, values))
                                
                # Hapus terlebih dahulu
                rec.delete_fish_using_line()           
                return rec.update({'fish_using_line_ids': temp})   
            
            
    # Delete fish using ids ketika sort
    @api.multi
    def delete_fish_using_line(self):
        fish_using_ids_line = []
        epi_id = self.id
        
        epi_line_obj = self.env['sis.epi'].search([('id', '=', epi_id)])
        if epi_line_obj:        
            fish_using_ids_line.append(([5]))

            return epi_line_obj.update({'fish_using_line_ids': fish_using_ids_line})    
            
        
    
    # Fungsi untuk menghitung EPI
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
                    finish_packing_format = (datetime.strptime(str(finish_packing), format_datetime) + relativedelta(hours=float(7))).strftime("%d/%m %H:%M")
                    
                    # Cleaning Time
                    cl_time_finish = 0.16666666666666666 # 10 Menit
                    dd_cl = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cl_time_finish) * 60, 60))
                    hour = int(dd_cl[:2])
                    minut = int(dd_cl[3:])
                    
                    start_cl_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(cl_time))
                    finish_cl_time = datetime.strptime(str(finish_packing), format_datetime) - relativedelta(hours=hour, minutes=minut)
                    
                    
                    # Pre cleaning time
                    pre_cl_time_finish = 0.5 # 30 menit
                    dd_precl = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(pre_cl_time_finish) * 60, 60))
                    hour = int(dd_precl[:2])
                    minut = int(dd_precl[3:])
                    
                    start_pre_cl_time = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(pre_pk))
                    finish_pre_cl_time = datetime.strptime(str(finish_cl_time), format_datetime) - relativedelta(hours=hour, minutes=minut)
                    
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
                    
                    
                    # Packing time
                    line.write({'start_packing_fu_temp': finish_packing})
                    line.write({'finish_packing_fu': finish_packing})
                    
                    # Cleaning
                    line.write({'start_cleaning_fu': start_cl_time})
                    line.write({'finish_cleaning_fu': finish_cl_time})
                    
                    # Pre cleaning
                    line.write({'start_pre_cleaning_fu': start_pre_cl_time})
                    line.write({'finish_pre_cleaning_fu': finish_pre_cl_time})
                    
                    # Cooking
                    line.write({'start_cooking_fu': start_cooking_time})
                    line.write({'finish_cooking_fu': finish_cooking_time})
                     
                    # Cutting
                    line.write({'start_cutting_fu': start_cutting_time})
                    line.write({'finish_cutting_fu': finish_cutting_time})
                     
                    # Defrost
                    line.write({'start_defrost_fu': start_defrost_time})
                    line.write({'finish_defrost_fu': finish_defrost_time})
                     
                    # Cold storage
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
    
    
    # Format date
    @api.one
    def get_date_format_epi(self):
        for rec in self:
            date = rec.finish_packing_fu
            
            format = "%Y-%m-%d %H:%M:%S"
            change = datetime.strptime(str(date), format).strftime("%d/%m %H:%M:%S")
            
            rec.date_plan_format = change
                                
                                
                                
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
                    remark = row.remark_fu
                    tonase = row.tonase_fu
                    total_tonase = row.temp_total_tonase_fu
                    fish_qty = row.fish_qty_fu
                    
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
                        values['urutan_item_wiz'] = urutan_item_fu
                        values['hasil_urut_item_wiz'] = hasil_urut_item
                        values['cutting_time_wiz'] = cutting_time
                        values['fish_type_wiz'] = fish_type.id
                        values['remark_wiz'] = remark
                        values['tonase_wiz'] = tonase
                        values['total_tonase_wiz'] = total_tonase
                        values['fish_qty_wiz'] = fish_qty
                        
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
            
    
    # FUNGSI AUTO FILL ADJ CUTTING
    # Auto fill Adj Cutting
    @api.multi
    def auto_fill_date(self):
        for rec in self:
            adj_cutting_line = rec.adj_cutting_line_ids
            epi_id = rec.id
            
            format_datetime = '%Y-%m-%d %H:%M:%S'
            temp = []
            
            
            if adj_cutting_line:
                for row in adj_cutting_line:
                    id_line = row.id
                    adj_cutting = row.adj_cutting
                    cutting_time = row.cutting_time
                    
                    # Jika ada adj cutting
                    if adj_cutting:
            
                        dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
                        hour = int(dd[:2])
                        minut = int(dd[3:])
                        
                        finish_adj = datetime.strptime(str(adj_cutting), format_datetime) + relativedelta(hours=hour, minutes=minut)
                        
                        values = {}
                        row.write({'adj_cutting_temp': finish_adj})
                    
                    else:
                        browse = self.env['sis.adj.cutting.line'].browse(id_line-1)
                        
                        for line_before in browse:
                            adj_cutting_temp = line_before.adj_cutting_temp
                            # Insert adj cutting wizard 
                            row.write({'adj_cutting': adj_cutting_temp})
                            
                            # Hitung ulang pada line saat ini
                            if row.adj_cutting:
                                dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(cutting_time) * 60, 60))
                                hour = int(dd[:2])
                                minut = int(dd[3:])
                        
                                
                                finish_adj = datetime.strptime(str(row.adj_cutting), format_datetime) + relativedelta(hours=hour, minutes=minut)
                                # Insert finish cutting di adj cutting wizard
                                row.write({'adj_cutting_temp': finish_adj})
                  
                    
    
    # FUNGSI INSERT ADJ CUTTING
    # Insert adj cutting ke urut cutting
    @api.multi
    def insert_adj_cutting(self):
        for rec in self:
            urut_cutting_ids = rec.urut_cutting_line_ids
            adj_cutting_ids =rec.adj_cutting_line_ids
            format_datetime = '%Y-%m-%d %H:%M:%S'
            
            if urut_cutting_ids:
                for row in urut_cutting_ids:
                    no_uc = row.no
                    item_uc = row.item_id_uc
                    id_line_uc = row.id
                    hasil_urut_item_uc = row.hasil_urut_item_uc
                    start_cutting = row.start_cutting_uc
                    
                    # Bandingkan dengan adj cutting line
                    if adj_cutting_ids:
                        for row_row in adj_cutting_ids:
                            no_adj = row_row.no
                            hasi_urut_item_adj = row_row.hasil_urut_item
                            item_adj = row_row.item_id
                            cutting_time = row_row.cutting_time
                            adj_cutting = row_row.adj_cutting
                            
                            # Jika no urut sama
                            if no_uc == no_adj:
                                row.write({'cutting_time_uc': cutting_time, 'adj_cutting_uc': adj_cutting})
                                
                                # Perhitunga toleransi (waktu awal - adj cutting)
                                waktu_awal = datetime.strptime(str(start_cutting), format_datetime)
                                waktu_adj_cutting = datetime.strptime(str(adj_cutting), format_datetime)
                                
                                # Di ubah ke hitungan menit, misal (1.35 jam -> 95 menit)
                                toleransi = (waktu_awal - waktu_adj_cutting).total_seconds() / 60.0
                                hasil_toleransi = (toleransi / 60) / 24 # Perhitungan rumus dari excel
                                hasil = round(hasil_toleransi, 2)
                                
                                waktu_awal_compare = datetime.strptime(str(start_cutting), format_datetime) + relativedelta(hours=float(7))
                                waktu_adj_cutting_compare = datetime.strptime(str(adj_cutting), format_datetime) + relativedelta(hours=float(7))
                                
                                
                                if waktu_awal_compare > waktu_adj_cutting_compare:
                                    row.write({'toleransi': hasil * -1}) 
                                    
                                else:
                                    row.write({'toleransi': hasil * -1}) 
                
                rec.update({'is_urut_cutting': True})
    
    # FUNGSI SORRT ASC KOLOM B
    # Fungsi sort ASC start cutting (kolom B)
    @api.multi
    def sort_asc_start_cutting(self):
        for rec in self:
            urut_cutting_ids = rec.urut_cutting_line_ids
            epi_id = rec.id
            temp = []
            i = 1
            
            if urut_cutting_ids:
                # Sorting ASC Start cutting
                self.env.cr.execute("select id as id, item_id_uc as item_id, hasil_urut_item_uc "
                                    "from sis_urut_cutting_line "
                                    "where epi_id_uc = '"+ str(epi_id) +"' "
                                    "order by start_cutting_uc")
                
                # Data ASC
                sql = self.env.cr.fetchall()
                if sql:
                    for sql_data in sql:
                        id_line = sql_data[0]
                        item_id_sql = sql_data[1]
                        hasil_urut_item_sql = sql_data[2]
                        
                        # Bandingkan dengan data yang ada di urut cutting line ids, jika ada maka sorting
                        for row in urut_cutting_ids:
                            id_line_uc = row.id
                            item_id_uc = row.item_id_uc
                            urutan_item_uc = row.urutan_item_uc
                            hasil_urut_item_uc = row.hasil_urut_item_uc
                            tonase_uc = row.tonase_uc
                            total_tonase_uc = row.total_tonase_uc
                            start_packing_uc = row.start_packing_uc
                            finish_packing_uc = row.finish_packing_uc
                            start_cleaning_uc = row.start_cleaning_uc
                            finish_cleaning_uc = row.finish_cleaning_uc
                            start_precleaning_uc = row.start_precleaning_uc
                            finish_precleaning_uc = row.finish_precleaning_uc
                            start_cutting_temp_uc = row.start_cutting_temp_uc
                            start_cutting_uc = row.start_cutting_uc
                            finish_cutting_uc = row.finish_cutting_uc
                            start_cooking_uc = row.start_cooking_uc
                            finish_cooking_uc = row.finish_cooking_uc
                            start_defrost_uc = row.start_defrost_uc
                            finish_defrost_uc = row.finish_defrost_uc
                            finish_cs_uc = row.finish_cs_uc
                            delay_co_pre = row.delay_co_pre
                            cutting_time_uc = row.cutting_time_uc
                            adj_cutting_uc = row.adj_cutting_uc
                            adj_cutting_uc_temp = row.adj_cutting_uc_temp
                            toleransi = row.toleransi
                            remark_uc = row.remark_uc
                            shift_potong_uc = row.shift_potong_uc
                            fish_type_uc = row.fish_type_uc
                            fish_qty_uc = row.fish_qty_uc
                            
                            
                            # Cek jika data ada maka insert ASC
                            if id_line == id_line_uc:
                                
                                values = {}
                                values['no'] = i
                                values['item_id_uc'] = item_id_uc
                                values['urutan_item_uc'] = urutan_item_uc
                                values['hasil_urut_item_uc'] = hasil_urut_item_uc
                                values['tonase_uc'] = tonase_uc
                                values['total_tonase_uc'] = total_tonase_uc
                                values['start_packing_uc'] = start_packing_uc
                                values['finish_packing_uc'] = finish_packing_uc
                                values['start_cleaning_uc'] = start_cleaning_uc
                                values['finish_cleaning_uc'] = finish_cleaning_uc
                                values['start_precleaning_uc'] = start_precleaning_uc
                                values['finish_precleaning_uc'] = finish_precleaning_uc
                                values['start_cutting_temp_uc'] = start_cutting_temp_uc
                                values['start_cutting_uc'] = start_cutting_uc
                                values['finish_cutting_uc'] = finish_cutting_uc
                                values['start_cooking_uc'] = start_cooking_uc
                                values['finish_cooking_uc'] = finish_cooking_uc
                                values['start_defrost_uc'] = start_defrost_uc
                                values['finish_defrost_uc'] = finish_defrost_uc
                                values['finish_cs_uc'] = finish_cs_uc
                                values['delay_co_pre'] = delay_co_pre
                                values['cutting_time_uc'] = cutting_time_uc
                                values['adj_cutting_uc'] = adj_cutting_uc
                                values['adj_cutting_uc_temp'] = adj_cutting_uc_temp
                                values['toleransi'] = toleransi
                                values['remark_uc'] = remark_uc
                                values['shift_potong_uc'] = shift_potong_uc
                                values['fish_type_uc'] = fish_type_uc
                                values['fish_qty_uc'] = fish_qty_uc
                                
                                temp.append((0, 0, values))
                                i = i + 1
                
                # Hapus terlebih dahulu
                rec.delete_urut_cutting_line()           
                return rec.update({'urut_cutting_line_ids': temp, 'is_insert_adj_cut': True})           
    
    # Delete urut cutting ids ketika sort
    @api.multi
    def delete_urut_cutting_line(self):
        urut_cutting_ids_line = []
        epi_id = self.id
        
        epi_line_obj = self.env['sis.epi'].search([('id', '=', epi_id)])
        if epi_line_obj:        
            urut_cutting_ids_line.append(([5]))

            return epi_line_obj.update({'urut_cutting_line_ids': urut_cutting_ids_line})
               
    
    
    # FUNGSI AKHIR HTUNG URUT CUTTING
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
                    
                    start_cutting_temp = row.start_cutting_temp_uc
                    start_cutting = row.start_cutting_uc
                    adj_cutting = row.adj_cutting_uc
                    cut_time = row.cutting_time_uc
                    start_pack = row.start_packing_uc
                    start_precleaning = row.start_precleaning_uc
                    
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
                    
                    print("start cutting : ", start_cutting_format)
                    print("adj cutting : ", adj_cutting_format)
                    print("tol : ", toleransi)
                    
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
                    
                    
                    # Jika toleransi minus
                    if toleransi < 0:
                        
                        # Perhitungan Cooking time + toleransi
                        start_cooking_change = ((datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(co_pk))) - (relativedelta(hours=float(hasil_hour))))
                        cut = (relativedelta(hours=float(hasil_cutting / 2)))
                        hasil_akhir_cooking = start_cooking_change - cut
                        
                        finish_cooking_change = datetime.strptime(str(hasil_akhir_cooking), format_datetime) + relativedelta(hours=float(cooking_time))
                        
                        # Defrost time + i6
                        start_defrost_change = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(de_pk)) - (relativedelta(hours=float(hasil_hour)))
                        finish_defrost_change = datetime.strptime(str(start_defrost_change), format_datetime) + relativedelta(hours=float(defrost_time))
                        
                        # Cool Storage time + i6
                        finish_cs_change = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(total_time)) - (relativedelta(hours=float(hasil_hour)))
                        
                        # hitung delay CO-PRE (rumus: start pre cleaning - finish cooking)
                        if start_precleaning:
                            delay_co_pre = (datetime.strptime(str(start_precleaning), format_datetime) - datetime.strptime(str(finish_cooking_change), format_datetime)).total_seconds() / 60.0
                            hasil_delay = (delay_co_pre / 60)
                            
                            
                    # Jika toleransi positif, hasil hour minus
                    else:
                        start_cooking_change = ((datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(co_pk))) - (relativedelta(hours=float(hasil_hour))))
                        cut = (relativedelta(hours=float(hasil_cutting / 2)))
                        hasil_akhir_cooking = start_cooking_change - cut
                        
                        finish_cooking_change = datetime.strptime(str(hasil_akhir_cooking), format_datetime) + relativedelta(hours=float(cooking_time))
                        
                        # Defrost time + i6
                        start_defrost_change = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(de_pk)) + (relativedelta(hours=float(hasil_hour)))
                        finish_defrost_change = datetime.strptime(str(start_defrost_change), format_datetime) + relativedelta(hours=float(defrost_time))
                        
                        # Cool Storage time + i6
                        finish_cs_change = datetime.strptime(str(start_pack), format_datetime) - relativedelta(hours=float(total_time)) + (relativedelta(hours=float(hasil_hour)))
                        
                        # hitung delay CO-PRE (rumus: start pre cleaning - finish cooking)
                        if start_precleaning:
                            delay_co_pre = (datetime.strptime(str(start_precleaning), format_datetime) - datetime.strptime(str(finish_cooking_change), format_datetime)).total_seconds() / 60.0
                            hasil_delay = (delay_co_pre / 60) 
                    
                    row.write({
                        'start_cutting_temp_uc': start_cutting_change,
                        'finish_cutting_uc': finish_cutting_change,
                        'start_cooking_uc': hasil_akhir_cooking,
                        'finish_cooking_uc': finish_cooking_change,
                        'start_defrost_uc': start_defrost_change,
                        'finish_defrost_uc': finish_defrost_change,
                        'finish_cs_uc': finish_cs_change,
                        'delay_co_pre': hasil_delay
                        })    
    
    
    # Fungsi untuk menghitung budomari
    @api.one
    def calculate_budomari(self):
        for rec in self:
            budomari_ac = rec.budomari_bool_ac
            budomari_sj = rec.budomari_bool_sj
            budomari_sm = rec.budomari_bool_sm
            budomari_tg = rec.budomari_bool_tg
            budomari_yf = rec.budomari_bool_yf
            budomari_yfb = rec.budomari_bool_yfb
            epi_line = rec.epi_line_ids
            
            presentase_ac = 0
            presentase_sj = 0
            presentase_sm = 0
            presentase_tg = 0
            presentase_yf = 0
            presentase_yfb = 0
            filling_line = 0
            hasil = 0
            fish_material_line = ""
            
            
            if epi_line:
                for line in epi_line:
                    fish_material_line = line.fish_material_epi
                    filling_line = line.filling_epi
                    
                    if fish_material_line:
                        if fish_material_line == 'AC' and budomari_ac == True:
                            presentase_ac = rec.budomari_id_ac.budomari 
                            
                            hasil = (filling_line / presentase_ac) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
                        
                        if (fish_material_line == 'SJS' or fish_material_line == 'SJP' or fish_material_line == 'SJ') and budomari_sj == True:
                            presentase_sj = rec.budomari_id_sj.budomari
                            
                            hasil = (filling_line / presentase_sj) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
                        
                        if fish_material_line == 'SM' and budomari_sm == True:
                            presentase_sm = rec.budomari_id_sm.budomari
                            
                            hasil = (filling_line / presentase_sm) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
                        
                        if fish_material_line == 'TG' and budomari_tg == True:
                            presentase_tg = rec.budomari_id_tg.budomari
                            
                            hasil = (filling_line / presentase_tg) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
                            
                        if (fish_material_line == 'YFS' or fish_material_line == 'YFP' or fish_material_line == 'YF') and budomari_yf == True:
                            presentase_yf = rec.budomari_id_yf.budomari
                            
                            hasil = (filling_line / presentase_yf) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
                        
                        if fish_material_line == 'YFB' and budomari_yfb == True:
                            presentase_yfb = rec.budomari_id_yfb.budomari
                    
                            hasil = (filling_line / presentase_yfb) * 100
                            line.write({'yieldd_epi': hasil}) 
                            rec.coba = hasil
     
    # XLS               
    # Create XLS report urutan potong
    def xls_urutan_potong(self):
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
        worksheet.write('B4', self.name, normal_style2)
        
        worksheet.write('A5', 'No', header_style)
        worksheet.write('B5', 'Jam keluar CS', header_style)
        worksheet.write('C5', 'Jam Mulai Defrost', header_style)
        worksheet.write('D5', 'Jam Mulai Cutting', header_style)
        worksheet.write('E5', 'Product', header_style)
        worksheet.write('F5', 'Fish', header_style)
        worksheet.write('G5', 'Tonase', header_style)
        worksheet.write('H5', 'Remark', header_style)
        worksheet.write('I5', 'Potong', header_style)
        
        # Value tabel
        urut_cutting_ids = self.urut_cutting_line_ids
        name = self.name
        hasil = ""
        
        if urut_cutting_ids:
            for line in urut_cutting_ids:
                item = line.item_id_uc.description
                no = line.no
                finish_cs = line.finish_cs_format_uc
                start_defrost = line.start_defrost_format_uc
                start_cutting = line.start_cutting_format_uc
                remark = line.remark_uc
                shift_potong = line.shift_potong_uc
                tonase = line.tonase_uc
                fish_type = line.fish_type_uc.size
                
                if shift_potong == 'pp':
                    hasil = 'PP'
                else:
                    hasil = 'PM'
                
                worksheet.write(row, col, no, normal_style)
                worksheet.write(row, col + 1, finish_cs, normal_style)
                worksheet.write(row, col + 2, start_defrost, normal_style)
                worksheet.write(row, col + 3, start_cutting, normal_style)
                worksheet.write(row, col + 4, item, normal_style)
                worksheet.write(row, col + 5, fish_type, normal_style)
                worksheet.write(row, col + 6, tonase, normal_style)
                worksheet.write(row, col + 7, remark, normal_style)
                worksheet.write(row, col + 8, hasil, normal_style)
                
                row = row + 1
        
        
        
        workbook.close()
        ids=self.env['sis.epi.xls'].create({'report':base64.b64encode(open("/tmp/"+filename, "rb").read())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/sis.epi.xls/%s/report/%s?download=true' %((ids.id),filename)
    
        }        
     
    # XLS   
    # Create XLS CU-CO
    def xls_cu_co(self):
        filename = 'REPORT CU-CO'+datetime.now().strftime('%Y-%m-%d')+'.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/'+filename)
        row = 6
        col = 0
        
        # STYLE
        format_judul = workbook.add_format({'font_size': 14, 'align': 'center'})
        normal_style = workbook.add_format({'valign':'vcenter', 'border':1, 'font_size':10, 'text_wrap': True})
        normal_style2 = workbook.add_format({'valign':'vcenter', 'font_size':10})
        header_style = workbook.add_format({'font_size': 10, 'bold': True, 'border':1, 'align':'center', 'valign': 'vcenter'})
        header2_style = workbook.add_format({'font_size': 10, 'bold': True})
        value_style = workbook.add_format({'font_size': 10, 'align': 'center'})
        left_style = workbook.add_format({'font_size': 10})
        right_style = workbook.add_format({'font_size': 10, 'align': 'right'})
        warning_style = workbook.add_format({'font_size': 10, 'align': 'right', 'bg_color': 'red'})
        urutan_pertama_style = workbook.add_format({'font_size': 10, 'bold': True})
         # Set format float
        cell_delay = workbook.add_format({'num_format': 'h:mm', 'valign':'vcenter', 'border':1, 'font_size':10})
    
        
        # WORKSHEET
        worksheet = workbook.add_worksheet('CU-CO')
        worksheet.set_column('A:AJ', 8.2)
        
        # Membuat Judul
        worksheet.merge_range('E1:H1', 'PLANNING PRODUKSI ', format_judul)
        
        # Set lebar kolom
        worksheet.set_column('A:A', 3)
        worksheet.set_column('B:B', 4)
        worksheet.set_column('C:C', 25)
        worksheet.set_column('D:D', 6)
        worksheet.set_column('E:E', 25)
        worksheet.set_column('F:F', 10)
        worksheet.set_column('G:G', 10)
        worksheet.set_column('H:H', 10)
        worksheet.set_column('I:I', 10)
        worksheet.set_column('J:J', 10)
        worksheet.set_column('K:K', 10)
        worksheet.set_column('L:L', 10)
        
        
        # Set header
        # Nomor epi
        worksheet.write('A4', 'EPI:', header2_style)
        worksheet.write('B4', self.name, normal_style2)
        
        # Tanggal epi
        worksheet.write('D4', 'Tanggal:', header2_style)
        worksheet.write('E4', self.date_plan, normal_style2)
        
        worksheet.merge_range('A5:A6', 'No', header_style)
        worksheet.merge_range('B5:B6', 'Fish', header_style)
        worksheet.merge_range('C5:C6', 'Remark', header_style)
        worksheet.merge_range('D5:D6', 'Tonase', header_style)
        
        worksheet.merge_range('E5:E6', 'Product', header_style)
        
        # Defrost
        worksheet.merge_range('F5:G5', 'Defrost', header_style)
        worksheet.write('F6', 'Start Defrost', header_style)
        worksheet.write('G6', 'Finish Defrost', header_style)
        
        # Cutting
        worksheet.merge_range('H5:I5', 'Cutting', header_style)
        worksheet.write('H6', 'Start Cutting', header_style)
        worksheet.write('I6', 'Finish Cutting', header_style)
        
        # Cooking
        worksheet.merge_range('J5:K5', 'Cooking', header_style)
        worksheet.write('J6', 'Start Cooking', header_style)
        worksheet.write('K6', 'Start Cooking', header_style)
        
        worksheet.merge_range('L5:L6', 'Delay CO-PRE', header_style)
        
        # Isi tabel
        urut_cutting_ids = self.urut_cutting_line_ids
        
        if urut_cutting_ids:
            temp = []
            for line in urut_cutting_ids:
                urut_cutting = line.no
                fish_material = line.fish_type_uc.size
                remark = line.remark_uc
                tonase = line.tonase_uc
                item = line.item_id_uc.description
                start_defrost = line.start_defrost_format_uc
                finish_defrost = line.finish_defrost_format_uc
                start_cutting = temp.append(line.start_cutting_format_uc)
                finish_cutting = line.finish_cutting_format_uc
                start_cooking = line.start_cooking_format_uc
                finish_cooking = line.finish_cooking_format_uc
                delay_co_pre = line.delay_co_pre
                
                dd = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(delay_co_pre) * 60, 60))
                hour = str(dd[:2])
                minut = str(dd[3:])
                
                delay_char = hour + ":" + minut

                
                # Sorting desc
                sorted_desc = sorted(temp, reverse=True)
                print("srot", sorted_desc)
                
                worksheet.write(row, col, urut_cutting, normal_style)
                worksheet.write(row, col + 1, fish_material, normal_style)
                worksheet.write(row, col + 2, remark, normal_style)
                worksheet.write(row, col + 3, tonase, normal_style)
                worksheet.write(row, col + 4, item, normal_style)
                worksheet.write(row, col + 5, start_defrost, normal_style)
                worksheet.write(row, col + 6, finish_defrost, normal_style)
                worksheet.write(row, col + 7, start_cutting, normal_style)
                worksheet.write(row, col + 8, finish_cutting, normal_style)
                worksheet.write(row, col + 9, start_cooking, normal_style)
                worksheet.write(row, col + 10, finish_cooking, normal_style)
                worksheet.write(row, col + 11, (delay_char), normal_style)
                
                row = row + 1
                
        
        workbook.close()
        ids=self.env['sis.epi.xls'].create({'report':base64.b64encode(open("/tmp/"+filename, "rb").read())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/sis.epi.xls/%s/report/%s?download=true' %((ids.id),filename)
    
        }        
 
 
               

class sis_epi_line(models.Model):
    _name = 'sis.epi.line'
    _rec_name = 'id'
    _order = 'line_epi'
    
    epi_id = fields.Many2one('sis.epi', ondelete='cascade')
    pps_item_id = fields.Many2one('sis.pps.item', string="Item")
    item_no_epi = fields.Char(size=20,string="Item No.")
    line_epi = fields.Char(string="Line")
    net_epi = fields.Float(string="Net(w)")
    can_size_epi = fields.Char(string="Can Size")
    kaleng_per_case_epi = fields.Float(string="Kaleng per Case", readonly=True, digits=(12,0))
    speed_epi = fields.Float(string="Speed(cs/jam)", digits=(12,0))
    speed_epi_calculate = fields.Float(string="Speed(cs/jam)", digits=(12,0), compute='calculate_speed_epi', store=True)
    target_prd = fields.Float(string="Target Produksi(cs)", track_visibility='onchange', readonly=True)
    budomari_epi = fields.Many2one('sis.budomari', string="Budomari")
    filling_epi = fields.Float(string="Meat/cs(kg)", compute='calculate_filling_epi') # Awalnya Filling
    sm_epi = fields.Float(string="SM", compute='calculate_sm_epi')
    yieldd_epi = fields.Float(string="Fish/Cs(kg)") # Awalnya Yield
    yield_total_epi = fields.Float(string="Yield Total", store=True, compute='calculate_total_yield')
    yield_total_epi_epi = fields.Float(string="Target Qty Fish(ton)", compute='calculate_yield_epi_epi', store=True)
    waktu_packing_epi = fields.Float(string="Est Wkt Pack(jam)", store=True, compute='calculate_estimasi_wkt_packing')
    meat_epi = fields.Float(string="Meat/jam(kg)", compute='calculate_meat')
    qty_fish_total_epi = fields.Float(string="Actl Fish Total(ton)", readonly=True)
    start_packing_epi = fields.Datetime(string="Start Pack")
    line_count = fields.Integer(string="Line Count", compute='calculate_speed_epi')
    fish_material_epi = fields.Char(string="Fish Material")
    remark_epi = fields.Char(string="Doc")
    remark_epi_fz = fields.Char(string="Remark Fz")
    meat = fields.Float(string="Meat(gr)")
    worker_epi = fields.Integer(string="Worker")
    
    sis_epi_line_temp_ids = fields.One2many('sis.epi.line.temp', 'epi_line_id')
    
    
    # Ambil semua data dari item
    @api.onchange('pps_item_id')
    def get_value_item(self):
        for rec in self:
            item_id = rec.pps_item_id
            
            item_obj = rec.env['sis.pps.item'].search([('id', '=', item_id.id)])
            total_speed = 0
            
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
                    fish_material = row.fishmaterial
                    remark = row.remark
                    item_no = row.item_no
                    
                    # Total speed: line count * speed
                    if line:
                        # Menghitung jumlah line 
                        line_split = line.split(",")
                        jumlah_line = len(line_split)
                        total_speed = jumlah_line * speed
                        
                        rec.line_count = jumlah_line
                    else:
                        total_speed = speed
                        
                rec.line_epi = line
                rec.can_size_epi = can_size
                rec.net_epi = net
                rec.kaleng_per_case_epi = kaleng_per_case
                rec.speed_epi_calculate = speed
                rec.filling_epi = filling
                rec.sm_epi = sm
                rec.fish_material_epi = fish_material
                rec.remark_epi = remark
                rec.item_no_epi = item_no
    
    # Get nilai net(w) langsung dari sis_items         
#     @api.one
#     def get_value_nw(self):
#         for rec in self:
#             item_id = rec.pps_item_id
#             item_no = rec.item_no_epi
#             
#             if item_id and item_no:
#                 items_obj = rec.env['sis.items'].search([('itemno', '=', item_no)])
#                         
#                 if items_obj:
#                     for item in items_obj:
#                         net_item = item.nw # Satuan KG
#                     
#                     # Dikonversi ke dalam gram (KG to gram)
#                     rec.net_epi = net_item * 1000 # Satuan gram
    
    
    # GET VALUE MET IN BOM (TIDAK DIPAKE)
    # MENGAMBIL DAN MENJUMLAHKAN NILAI MEAT PADA BOM, SELAIN MEAT SHREDED DAN MEAT RED
    """
    @api.one
    def get_value_meat(self):
        for rec in self:
            itemno = rec.item_no_epi
            
            if itemno:
                self.env.cr.execute("select itemno as itemno, "
                                    "description as description, "
                                    "SUM(lineqty) as lineqty "
                                    "from sis_production_bom "
                                    "where lineitem like '%WIP%' "
                                    "and itemno = '" + str(itemno) + "'"
                                    "and linedesc not like '%Meat Shredded%' "
                                    "and linedesc not like '%Meat Red%' "
                                    "group by itemno, description")

                sql = self.env.cr.fetchone()
                if sql:
                    qty_meat = sql[2]
                    
                    rec.meat = qty_meat
    
    # GET VALUE CAN SIZE (TIDAK DIPAKE)
    @api.multi
    def get_value_can_size(self):
        for rec in self:
            itemno = rec.item_no_epi
            temp = ""
            
            if itemno:
                self.env.cr.execute("select linedesc from sis_production_bom "
                                    "where itemno = '" + str(itemno) + "' "
                                    "and (lineitem like '%EMB%' or lineitem like '%ELB%')")
                
                sql = self.env.cr.fetchall()
                if sql:
                    for data in sql:
                        can_size = data[0]
                        
                        temp = temp + "/" + str(can_size)
                    
                    rec.can_size_epi = temp
    """
    
    # CALCULATE FILLING
    # uNTUK MENGHITUNG FILLING DI LINE EPI, KARENA KALO DILUAR (MASTER ITEM EPI) LOADING LAMA
    @api.depends('meat', 'kaleng_per_case_epi')
    def calculate_filling_epi(self):
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case_epi
            
            if meat and kaleng_per_case:
                filling = (meat * kaleng_per_case) / 1000
                
                rec.filling_epi = filling
    
    
    # CALCULATE SM
    # UNTUK MENGHITUNG SM DI LINE, KARENA KALO DILUAR (MASTER ITEM EPI) LOADING LAMA
    @api.depends('meat', 'kaleng_per_case_epi')
    def calculate_sm_epi(self): 
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case_epi
            
            if meat and kaleng_per_case:
                sm = meat * kaleng_per_case
                
                rec.sm_epi = sm
    
    
    # CALCULATE SPEED LINE
    @api.depends('speed_epi', 'line_count')
    def calculate_speed_epi(self):
        for rec in self:
            line = rec.line_epi
            speed = rec.speed_epi
            item_id = rec.pps_item_id
            total_speed = 0
            
            if line:
                line_split = line.split(",")
                jumlah_line = len(line_split)
                total_speed = jumlah_line * speed
                
                rec.line_count = jumlah_line
                
            else:
                total_speed = speed
            
            rec.speed_epi_calculate = total_speed
    
    
    # CALCULATE YIELD (ga di pakai, karena perhitungan ada di header)
#     @api.depends('budomari_epi', 'filling_epi')
#     def calculate_yield(self):
#         for rec in self:
#             filling_epi = rec.filling_epi
#             budomari_id = rec.budomari_epi
#             
#             if budomari_id:
#                 for row in budomari_id:
#                     value_budomari = row.budomari
#                 
#                 hasil = (filling_epi / value_budomari) * 100
#                 rec.yieldd_epi = hasil
    
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
     
    # Calculate meat epi di schedule list sheet
    # MEAT DI SHEET SCHEDULE LIST
    @api.depends('waktu_packing_epi', 'sm_epi')
    def calculate_meat(self):
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

    
    # Button untuk mengisi qty di line
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
    
    epi_line_id = fields.Many2one('sis.epi.line')
    size_fish_temp = fields.Char()
    qty_fish_temp = fields.Float()
    
    

class sis_epi_budomari_master(models.Model):
    _name = 'sis.epi.budomari.master'
    
    name = fields.Selection([('AC', 'AC'), ('SJ', 'SJ'), ('SM', 'SM'), ('TG', 'TG'), ('YF', 'YF'), ('YFB', 'YFB')], string="Name")
    
    
