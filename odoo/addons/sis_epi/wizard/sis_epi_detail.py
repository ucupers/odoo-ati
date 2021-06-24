
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
    
    
    # Function save to sis_epi_line
    @api.multi
    def save(self):
        if self.env.context.get('active_id'):
            target_prd_detail = self.target_prd_detail
            qty_fish_total = self.qty_fish_total
             
            sis_epi_id = self.env.context.get('active_id')
            sis_epi_obj = self.env['sis.epi'].browse(sis_epi_id)
            epi_detail_line_ids = len(self.epi_detail_line)
            
             
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
                        
                            sis_epi_line_obj.write({
                                'target_prd': target_prd_detail,
                                'qty_fish_total_epi': qty_fish_total,
                                'sis_epi_line_temp_ids': [(0, 0, {
                                    'size_fish_temp': size_fish,
                                    'qty_fish_temp': qty_fish,
                        
                                })]
                            })
                 
                        return True
                
                    # Jika tidak ada line yang diisi
                    else:
                        
                        sis_epi_line_obj.write({
                            'target_prd': target_prd_detail,
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
                                  ('salmon', 'Salmon'), ('tonggol', 'Tonggol'), ('bonito', 'Bonito'), ('be', 'BE'), 
                                  ('defrost_sj', 'Defrost SJ(%)')], default=None, string="Size Fish")
    qty_fish = fields.Float(string="Qty(ton)")
    name = fields.Char(string="Name")
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    