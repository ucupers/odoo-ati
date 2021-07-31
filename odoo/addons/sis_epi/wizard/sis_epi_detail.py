
from odoo import models, fields, api, _
from odoo.exceptions import UserError


class sis_epi_detail(models.Model):
    _name = 'sis.epi.detail'
    
    epi_line_id = fields.Many2one('sis.epi.line', string="EPI Line ID")
    epi_detail_line = fields.One2many('sis.epi.detail.line', 'epi_detail_id')
    epi_detail_line_nosuggest = fields.One2many('sis.epi.detail.line', 'epi_detail_id')
    target_prd_detail = fields.Float(string="Target Produksi", digits=(12,0))
    qty_fish_total = fields.Float(string="Total Qty Fish", store=True, compute='compute_total_fish')
    yield_total_detail = fields.Float(string="Target Qty Fish(ton)", readonly=True)
    total_point_detail = fields.Float(string="Total Point")
    
    
    # Function save to sis_epi_line
    @api.multi
    def save(self):
        if self.env.context.get('active_id'):
            target_prd_detail = self.target_prd_detail
            qty_fish_total = self.qty_fish_total
            total_point_detail = self.total_point_detail
            print("point: ", total_point_detail)
             
            sis_epi_id = self.env.context.get('active_id')
            sis_epi_obj = self.env['sis.epi'].browse(sis_epi_id)
            epi_detail_line_ids = len(self.epi_detail_line)
            i = 1
            
            total = 0
            total_total = 0
             
            if sis_epi_obj:
                # hapus terlebih dahulu data yang ada
                self.delete_sis_epi_line_temp()
                sis_epi_line = self.epi_line_id.id
                sis_epi_line_obj = self.env['sis.epi.line'].browse(sis_epi_line)
                if sis_epi_line_obj:
                    if self.epi_detail_line:
                        for row in self.epi_detail_line:
                            size_fish = row.size_fish
                            qty_fish = row.qty_fish
                            point = row.point
                            total_point = row.total_point
                            
                            # Perhitungan point
                            total = qty_fish * point
                            total_total = total_total + total
                        
                            sis_epi_line_obj.write({
                                'target_prd': target_prd_detail,
                                'qty_fish_total_epi': qty_fish_total,
                                'total_point_epi': total_total,
                                'sis_epi_line_temp_ids': [(0, 0, {
                                    'size_fish_temp': size_fish,
                                    'qty_fish_temp': qty_fish,
                                    'no_urut': i,
                                    'point': point,
                                    'total_point': total_total,
                                })]
                            })
                            i = i + 1
                 
                        return True
                
                    # Jika tidak ada line yang diisi
                    else:
                        
                        sis_epi_line_obj.write({
                            'target_prd': target_prd_detail,
                            'total_point_epi': total_point_detail,
                        })
                        
                        return True
                    
    
    # Function to delete sis epi line temp ids
    @api.multi
    def delete_sis_epi_line_temp(self):
        epi_temp_ids_line = []
        epi_line_id = self.epi_line_id
        
        epi_line_obj = self.env['sis.epi.line'].search([('id', '=', epi_line_id.id)])
        if epi_line_obj:        
            epi_temp_ids_line.append(([5]))

            return epi_line_obj.update({'sis_epi_line_temp_ids': epi_temp_ids_line})
    
        
    # Hitung total qty fish
    @api.depends('epi_detail_line.qty_fish')
    def compute_total_fish(self):
        for rec in self:
            total = 0
            detail_line = rec.epi_detail_line
            
            for line in detail_line:
                size_fish = line.size_fish
                if size_fish != 'defrost_sj':
                    total = total +  line.qty_fish
            
            rec.qty_fish_total = total
    
    


class sis_epi_line_detail(models.Model):
    _name = 'sis.epi.detail.line'
    
    epi_detail_id = fields.Many2one('sis.epi.detail', ondelete='cascade')
    size_fish = fields.Selection([('sss', 'SSS'), ('ss', 'SS'), ('s', 'S'), ('m', 'M'), ('l', 'L'), 
                                  ('salmon', 'Salmon'), ('tonggol', 'Tonggol'), ('bonito', 'Bonito'), ('be', 'BE'), ('plus_tujuh', '+7'), 
                                  ('plus_sepuluh_duapuluh', '+10/+20'), ('hg_ni', 'Hg Ni'), ('l1l2', 'L1/L2'),
                                  ('defrost_sj', 'Defrost SJ(%)')], default=None, string="Size Fish")
    qty_fish = fields.Float(string="Qty(ton)")
    name = fields.Char(string="Name")
    no_urut = fields.Integer()
    point = fields.Float(string="Point")
    total_point = fields.Float(string="Total Point")
    
    
            
    # get point berdasarkan size fish
    @api.onchange('size_fish')
    def get_point(self):
        for rec in self:
            size_fish = rec.size_fish
            
            if size_fish == 'sss':
                rec.point = 1.6
            
            elif size_fish == 'ss':
                rec.point = 1.4
            
            elif size_fish == 's':
                rec.point = 1.2
            
            elif size_fish == 'm':
                rec.point = 1
            
            elif size_fish == 'l1l2':
                rec.point = 0.9
            
            elif size_fish == 'plus_tujuh':
                rec.point = 0.8
            
            elif size_fish == 'hg_ni':
                rec.point = 0.6
            
            elif size_fish == 'plus_sepuluh_duapuluh':
                rec.point = 0.7
            
            elif size_fish == 'be':
                rec.point = 1
            
            elif size_fish == 'tonggol':
                rec.point = 1
            
            elif size_fish == 'bonito':
                rec.point = 1
            
            elif size_fish == 'salmon':
                rec.point = 1.8
            
            else:
                rec.point = 0
                
            
            
            
        
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    