from odoo import models, fields, api
from odoo.exceptions import ValidationError

class sis_master_product(models.Model):
    _name = "sis.master.product"
    _rec_name = "description"
    _description = "Master Product"
    
    no = fields.Integer(string="No. ")
    description = fields.Char(string="Description", required=True)
    kode_nav = fields.Char(string="Kode NAV", compute="_get_kodenav", store=True)

    rel_pack = fields.One2many('sis.packing', 'rel_product', string="Relasi Packing")
    wh_ids = fields.One2many('sis.wh.bongkar.produk', 'produk_wh_id', string="Relasi WH")
    rel_pack_product = fields.One2many('sis.packing.supply', 'rel_product_supply', string="Relasi Packing")
    rel_line_material = fields.Many2many('sis.packing.line', 'rel_material_line', string="Relasi Line Material")
    
    @api.one
    @api.depends('description')
    def _get_kodenav(self):
        if self.description:
            print(self.description)
            csql="select itemno from sis_items where description='"+self.description+"'"             
            self.env.cr.execute(csql)
            data=self.env.cr.fetchall()
            if data:        
                for datas in data:
                    (da, )=datas                  
                self.kode_nav=da
            else:
                raise ValidationError('Produk tidak terdapat di NAV !! Pastikan penulisan nama produk benar.')
    
        