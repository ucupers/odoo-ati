from odoo import models, fields, api
import time, datetime
from datetime import datetime
from PyPDF2.generic import char


class sis_perhitungan_shreded(models.Model):
    _name = 'sis.perhitungan.shreded'
    _inherit = 'mail.thread'
    
    name = fields.Char(string="Name", readonly=True)
    date_shreded = fields.Date(string="Date", required=True)
    epi_id_shreded = fields.Many2one('sis.epi', string="Epi ID", readonly=True)
    ati12 = fields.Selection([('ati1', 'ATI1'), ('ati2', 'ATI2')], string="ATI1/ATI2", required=True)
    hasil_output_cl_sj = fields.Float(string="Out CL SJ", compute='compute_output_cl')
    hasil_output_cl_yf = fields.Float(string="Out CL YF", compute='compute_output_cl')
    hasil_output_cl_ac = fields.Float(string="Out CL AC", compute='compute_output_cl')
    budomari_cl_sj = fields.Float(string="Bud SJ(%)")
    budomari_cl_yf = fields.Float(string="Bud YF(%)")
    budomari_cl_ac = fields.Float(string="Bud AC(%)")
    
    sisa_output_cl_sj = fields.Float(string="Sisa Out CL SJ(kg)", compute='compute_sisa_cl')
    sisa_output_cl_yf = fields.Float(string="Sisa Out CL YF(kg)", compute='compute_sisa_cl')
    sisa_output_cl_ac = fields.Float(string="Sisa Out CL AC(kg)", compute='compute_sisa_cl')
    
    shreded_line_ids = fields.One2many('sis.perhitungan.shreded.line', 'shreded_id')
    
    # TOTAL
    total_kebutuhan_shreded = fields.Float(string="Total Kebutuhan Shreded", compute='compute_total')
    total_shreded_defrost_sj = fields.Float(string="Total Kebutuhan Defrost SJ", compute='compute_total')
    total_shreded_defrost_yf = fields.Float(string="Total Kebutuhan Defrost YF", compute='compute_total')
    total_shreded_defrost_ac = fields.Float(string="Total Kebutuhan Defrost AC", compute='compute_total')
    
    total_shreded_cleaning_sj = fields.Float(string="Total Kebutuhan Cleaning SJ", compute='compute_total')
    total_shreded_cleaning_yf = fields.Float(string="Total Kebutuhan Cleaning YF", compute='compute_total')
    total_shreded_cleaning_ac = fields.Float(string="Total kebutuhan Cleaning AC", compute='compute_total')
    total_shreded_cleaning_bsb = fields.Float(string="Total Kebutuhan Cleaning BSB", compute='compute_total')
    
    total_shreded_ati_sj = fields.Float(string="Total Shreded ATI SJ", compute='compute_total')
    total_shreded_ati_yf_ac = fields.Float(string="Total Shreded ATI YF AC", compute='compute_total')
    total_repack_sj = fields.Float(string="Total Repack SJ", compute='compute_total')
    total_repack_yf = fields.Float(string="Total Repack YF", compute='compute_total')
    total_kepala_rahang = fields.Float(string="Total Kepala Rahang", compute='compute_total')
    total_giling_loin = fields.Float(string="Total Giling Loin", compute='compute_total')
    
    
    @api.model
    def create(self, vals):
        res = super(sis_perhitungan_shreded, self).create(vals)

        # Sequence
        sequence = self.env['ir.sequence'].next_by_code('sequence.sis.shreded') or ('New')
        res.update({'name': sequence})

        return res
    
    # Compute total
    @api.depends('shreded_line_ids.kebutuhan_shreded', 'shreded_line_ids.hasil_shreded_defrost_sj', 'shreded_line_ids.hasil_shreded_defrost_yf', 
                 'shreded_line_ids.hasil_shreded_defrost_ac', 'shreded_line_ids.hasil_shreded_cleaning_sj', 'shreded_line_ids.hasil_shreded_cleaning_yf',
                 'shreded_line_ids.hasil_shreded_cleaning_ac', 'shreded_line_ids.hasil_shreded_cleaning_bsb', 'shreded_line_ids.hasil_shreded_ati_sj')
    def compute_total(self):
        for rec in self:
            total_kebutuhan = 0
            total_shreded_defrost_sj = 0
            total_shreded_defrost_yf = 0
            total_shreded_defrost_ac = 0
            
            total_shreded_cleaning_sj = 0
            total_shreded_cleaning_yf = 0
            total_shreded_cleaning_ac = 0
            total_shreded_cleaning_bsb = 0
            
            total_shreded_ati_sj = 0
            total_shreded_ati_yf_ac = 0
            total_repack_sj = 0
            total_repack_yf = 0
            total_kepala_rahang = 0
            total_giling_loin = 0
            
            shreded_line_ids = rec.shreded_line_ids
            
            if shreded_line_ids:
                for row in shreded_line_ids:
                    total_kebutuhan = total_kebutuhan + row.kebutuhan_shreded
                    total_shreded_defrost_sj = total_shreded_defrost_sj + row.hasil_shreded_defrost_sj
                    total_shreded_defrost_yf = total_shreded_defrost_yf + row.hasil_shreded_defrost_yf
                    total_shreded_defrost_ac = total_shreded_defrost_ac + row.hasil_shreded_defrost_ac
                    
                    total_shreded_cleaning_sj = total_shreded_cleaning_sj + row.hasil_shreded_cleaning_sj
                    total_shreded_cleaning_yf = total_shreded_cleaning_yf + row.hasil_shreded_cleaning_yf
                    total_shreded_cleaning_ac = total_shreded_cleaning_ac + row.hasil_shreded_cleaning_ac
                    total_shreded_cleaning_bsb = total_shreded_cleaning_bsb + row.hasil_shreded_cleaning_bsb
                    
                    total_shreded_ati_sj = total_shreded_ati_sj + row.hasil_shreded_ati_sj
                    total_shreded_ati_yf_ac = total_shreded_ati_yf_ac + row.hasil_shreded_ati_yf_ac
                    total_repack_sj = total_repack_sj + row.hasil_repack_sj
                    total_repack_yf = total_repack_yf + row.hasil_repack_yf
                    total_kepala_rahang = total_kepala_rahang + row.hasil_kepala_rahang
                    total_giling_loin = total_giling_loin + row.hasil_giling_loin
                
                rec.total_kebutuhan_shreded = total_kebutuhan
                rec.total_shreded_defrost_sj = total_shreded_defrost_sj
                rec.total_shreded_defrost_yf = total_shreded_defrost_yf
                rec.total_shreded_defrost_ac = total_shreded_defrost_ac
                
                rec.total_shreded_cleaning_sj = total_shreded_cleaning_sj
                rec.total_shreded_cleaning_yf = total_shreded_cleaning_yf
                rec.total_shreded_cleaning_ac = total_shreded_cleaning_ac
                rec.total_shreded_cleaning_bsb = total_shreded_cleaning_bsb
                
                rec.total_shreded_ati_sj = total_shreded_ati_sj
                rec.total_shreded_ati_yf_ac = total_shreded_ati_yf_ac
                rec.total_repack_sj = total_repack_sj
                rec.total_repack_yf = total_repack_yf
                rec.total_kepala_rahang = total_kepala_rahang
                rec.total_giling_loin = total_giling_loin    
                
    
    # Compute output cleaning          
    @api.depends('budomari_cl_sj', 'budomari_cl_yf', 'budomari_cl_ac')
    def compute_output_cl(self):
        for rec in self:
            budomari_cl_sj = rec.budomari_cl_sj
            budomari_cl_yf = rec.budomari_cl_yf
            budomari_cl_ac = rec.budomari_cl_ac
            date = rec.date_shreded
            epi_id = rec.epi_id_shreded
            
            if epi_id:
                epi_obj = rec.env['sis.epi'].search([('id', '=', epi_id.id)])
                
                if epi_obj:
                    for row in epi_obj:
                        total_sj = row.total_rawmat_sj * 1000 # Konversi TON to KG (dikali 1000)
                        total_yf = row.total_rawmat_yf * 1000
                        total_ac = row.total_rawmat_ac * 1000
                        
                        if budomari_cl_sj != 0:
                            hasil = total_sj * (budomari_cl_sj / 100)
                            rec.hasil_output_cl_sj = hasil
                            
                        if budomari_cl_yf != 0:
                            hasil = total_yf * (budomari_cl_yf / 100)
                            rec.hasil_output_cl_yf = hasil
                        
                        if budomari_cl_ac != 0:
                            hasil = total_ac * (budomari_cl_ac / 100)
                            rec.hasil_output_cl_ac = hasil
    
    # Compute sisa cleaning                    
    @api.depends('hasil_output_cl_sj', 'hasil_output_cl_yf', 'hasil_output_cl_ac')
    def compute_sisa_cl(self):
        for rec in self:
            hasil_output_cl_sj = rec.hasil_output_cl_sj
            hasil_output_cl_yf = rec.hasil_output_cl_yf
            hasil_output_cl_ac = rec.hasil_output_cl_ac
            
            total_shreded_cleaning_sj = rec.total_shreded_cleaning_sj
            total_shreded_cleaning_yf = rec.total_shreded_cleaning_yf
            total_shreded_cleaning_ac = rec.total_shreded_cleaning_ac
            
            if hasil_output_cl_sj != 0:
                rec.sisa_output_cl_sj = hasil_output_cl_sj - total_shreded_cleaning_sj
            
            if hasil_output_cl_yf != 0:
                rec.sisa_output_cl_yf = hasil_output_cl_yf - total_shreded_cleaning_yf
            
            if hasil_output_cl_ac != 0:
                rec.sisa_output_cl_ac = hasil_output_cl_ac - total_shreded_cleaning_ac
    
                        
    @api.multi
    def get_item_epi(self):
        for rec in self:
            date_shreded = rec.date_shreded
            ati12 = rec.ati12
            
            meat = 0
            temp = []
            
            
            if date_shreded:
                rec.env.cr.execute("select distinct sel.pps_item_id as item_id, "
                                   "sel.kaleng_per_case_epi as kaleng_per_case, "
                                   "sel.target_prd as target_prd, "
                                   "sel.item_no_epi as item_no, "
                                   "sel.epi_id as epi_line_id, "
                                   "sel.fish_material_epi as fish, "
                                   "spi.description as desc "
                                   "from sis_epi se "
                                   "left join sis_epi_line sel on se.id = sel.epi_id "
                                   "left join sis_pps_item spi on spi.id = sel.pps_item_id "
                                   "left join sis_ppic_dpe_detail spdd on spi.description = spdd.product "
                                   "where se.date_plan = '" + str(date_shreded) + "' "
                                   "and se.state in ('done', 'urut_cutting')")
                
                sql =  self.env.cr.fetchall()
                if sql:
                    
                    for row in sql:
                        item_id = row[0]
                        kaleng_per_case = row[1]
                        target_prd = row[2]
                        item_no = row[3]
                        epi_id = row[4]
                        fish_material = row[5]
                        desc_prod = row[6]
                        
                        values = {}
                        # Get meat in dpe berdasarkan nama product
                        dpe_obj = rec.env['sis.ppic.dpe'].search([('dpe_date', '=', date_shreded),('ati12', '=', ati12)])
                        if dpe_obj:
                            for dpe in dpe_obj:
                                detail_id = dpe.detail_id
                                
                                for detail in detail_id:
                                    description_dpe = detail.product
                                    
                                    if description_dpe == desc_prod:
                                        meat = detail.meat
                        
                        
                        
                        values['item_id']= item_id
                        values['kaleng_per_case']= kaleng_per_case
                        values['qty_target']= target_prd
                        values['no_item']= item_no
                        values['komposisi_meat'] = meat
                        values['epi_id'] = epi_id
                        values['fish_material'] = fish_material
                        
                        temp.append((0, 0, values))
                    
                    rec.epi_id_shreded = epi_id
                    
                rec.update({'shreded_line_ids': temp})


class sis_perhitungan_shreded_line(models.Model):
    _name = 'sis.perhitungan.shreded.line'
    
    shreded_id = fields.Many2one('sis.perhitungan.shreded')
    item_id = fields.Many2one('sis.pps.item', string="Item")
    no_item = fields.Char(string="Item No")
    qty_target = fields.Float(string="Qty Target")
    kaleng_per_case = fields.Float(string="Case")
    pemakaian_shreded = fields.Float(string="Pemakaian Shreded")
    komposisi_meat = fields.Float(string="Meat")
    kebutuhan_shreded = fields.Float(string="Kebutuhan Shreded(kg)", compute='calculate_kebutuhan_shreded')
    epi_id = fields.Many2one('sis.epi')
    
    shreded_defrost_sj = fields.Float(string="DF SJ")
    hasil_shreded_defrost_sj = fields.Float(string="Val", compute='calculate_shreded')
    shreded_defrost_yf = fields.Float(string="DF YF")
    hasil_shreded_defrost_yf = fields.Float(string="Val", compute='calculate_shreded')
    shreded_defrost_ac = fields.Float(string="DF AC")
    hasil_shreded_defrost_ac = fields.Float(string="Val", compute='calculate_shreded')
    
    shreded_cleaning_sj = fields.Float(string="CL SJ")
    hasil_shreded_cleaning_sj = fields.Float(string="Val", compute='calculate_shreded')
    shreded_cleaning_yf = fields.Float(string="CL YF")
    hasil_shreded_cleaning_yf = fields.Float(string="Val", compute='calculate_shreded')
    shreded_cleaning_ac = fields.Float(string="CL AC")
    hasil_shreded_cleaning_ac = fields.Float(string="Val", compute='calculate_shreded')
    shreded_cleaning_bsb = fields.Float(string="CL BSB")
    hasil_shreded_cleaning_bsb = fields.Float(string="Val", compute='calculate_shreded')
    
    shreded_ati_sj = fields.Float(string="ATI SJ")
    hasil_shreded_ati_sj = fields.Float(string="Val", compute='calculate_shreded')
    shreded_ati_yf_ac = fields.Float(string="ATI YF AC")
    hasil_shreded_ati_yf_ac = fields.Float(string="Val", compute='calculate_shreded')
    repack_sj = fields.Float(string="Rpck SJ")
    hasil_repack_sj = fields.Float(string="Val", compute='calculate_shreded')
    repack_yf = fields.Float(string="Rpck YF")
    hasil_repack_yf = fields.Float(string="Val", compute='calculate_shreded')
    kepala_rahang = fields.Float(string="Kpl Rahang")
    hasil_kepala_rahang = fields.Float(string="Val", compute='calculate_shreded')
    giling_loin = fields.Float(string="Gil Loin")
    hasil_giling_loin = fields.Float(string="Val", compute='calculate_shreded')


    
    # Calculate kebutuhan shreded
    @api.depends('qty_target', 'kaleng_per_case', 'pemakaian_shreded', 'komposisi_meat')
    def calculate_kebutuhan_shreded(self):
        for rec in self:
            qty_target = rec.qty_target
            kaleng_per_case = rec.kaleng_per_case
            pemakaian_shreded = rec.pemakaian_shreded
            komposisi_meat = rec.komposisi_meat
            hasil = 0
            
            hasil = (qty_target * kaleng_per_case * pemakaian_shreded * komposisi_meat) / 100
            rec.kebutuhan_shreded = hasil / 1000
    
    
    # hitung hasil shreded
    @api.depends('shreded_defrost_sj', 'shreded_defrost_yf', 'shreded_defrost_ac', 
                 'shreded_cleaning_sj', 'shreded_cleaning_yf', 'shreded_cleaning_ac', 'kebutuhan_shreded')
    def calculate_shreded(self):
        for rec in self:
            shreded_defrost_sj = rec.shreded_defrost_sj
            shreded_defrost_yf = rec.shreded_defrost_yf
            shreded_defrost_ac = rec.shreded_defrost_ac
            
            shreded_cleaning_sj = rec.shreded_cleaning_sj
            shreded_cleaning_yf = rec.shreded_cleaning_yf
            shreded_cleaning_ac = rec.shreded_cleaning_ac
            shreded_cleaning_bsb = rec.shreded_cleaning_bsb
            
            shreded_ati_sj = rec.shreded_ati_sj
            shreded_ati_yf_ac = rec.shreded_ati_yf_ac
            repack_sj = rec.repack_sj
            repack_yf = rec.repack_yf
            kepala_rahang = rec.kepala_rahang
            giling_loin = rec.giling_loin
            
            
            kebutuhan_shreded = rec.kebutuhan_shreded
            
            hasil_df_sj = (shreded_defrost_sj / 100) * kebutuhan_shreded
            hasil_df_yf = (shreded_defrost_yf / 100) * kebutuhan_shreded
            hasil_df_ac = (shreded_defrost_ac / 100) * kebutuhan_shreded
            
            hasil_cl_sj = (shreded_cleaning_sj / 100) * kebutuhan_shreded
            hasil_cl_yf = (shreded_cleaning_yf / 100) * kebutuhan_shreded
            hasil_cl_ac = (shreded_cleaning_ac / 100) * kebutuhan_shreded
            hasil_cl_bsb = (shreded_cleaning_bsb / 100) * kebutuhan_shreded
            
            hasil_shreded_ati_sj = (shreded_ati_sj / 100) * kebutuhan_shreded
            hasil_shreded_ati_yf_ac = (shreded_ati_yf_ac / 100) * kebutuhan_shreded
            hasil_repack_sj = (repack_sj / 100) * kebutuhan_shreded
            hasil_repack_yf = (repack_yf / 100) * kebutuhan_shreded
            hasil_kepala_rahang = (kepala_rahang / 100) * kebutuhan_shreded
            hasil_giling_loin = (giling_loin / 100) * kebutuhan_shreded
            
            
            rec.hasil_shreded_defrost_sj = hasil_df_sj
            rec.hasil_shreded_defrost_yf = hasil_df_yf
            rec.hasil_shreded_defrost_ac = hasil_df_ac
            
            rec.hasil_shreded_cleaning_sj = hasil_cl_sj
            rec.hasil_shreded_cleaning_yf = hasil_cl_yf
            rec.hasil_shreded_cleaning_ac = hasil_cl_ac
            rec.hasil_shreded_cleaning_bsb = hasil_cl_bsb
            
            rec.hasil_shreded_ati_sj = hasil_shreded_ati_sj
            rec.hasil_shreded_ati_yf_ac = hasil_shreded_ati_yf_ac
            rec.hasil_repack_sj = hasil_repack_sj
            rec.hasil_repack_yf = hasil_repack_yf
            rec.hasil_kepala_rahang = hasil_kepala_rahang
            rec.hasil_giling_loin = hasil_giling_loin
                      
                
            