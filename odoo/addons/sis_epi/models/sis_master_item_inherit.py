from odoo import models, fields, api

class sis_master_item(models.Model):
    _inherit = 'sis.pps.item'
    
    yieldd = fields.Float(string="Fish Qty")
    net = fields.Float(string="Net(W)")
    meat = fields.Float(string="Meat")
    filling = fields.Float(string="Filling", compute='calculate_filling')
    sm = fields.Float(string="SM", compute='calculate_sm')
    kaleng_per_case = fields.Float(string="Kaleng per Case")
    fcl = fields.Float(string="FCL")
    can_size = fields.Char(string="Can Size")
    karyawan_pk = fields.Float(string="Karyawan PK")
    speed = fields.Float(string="Speed(cs/jam)")
    remark = fields.Text(string="Remark")
    

    # Calculate filling (fungsi ini juga dipake di epi line)
    @api.depends('meat', 'kaleng_per_case')
    def calculate_filling(self):
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case
            
            if meat and kaleng_per_case:
                filling = (meat * kaleng_per_case) / 1000
                
                rec.filling = filling
    
    
    # Calculate yield/kebutuhan ikan mentah
    @api.depends('filling')
    def calculate_yield(self):
        for rec in self:
            item_desc = rec.description
            
    
    # Calculate SM (Fungsi ini juga dipake di epi line)
    @api.depends('meat', 'kaleng_per_case')
    def calculate_sm(self): 
        for rec in self:
            meat = rec.meat
            kaleng_per_case = rec.kaleng_per_case
            
            if meat and kaleng_per_case:
                sm = meat * kaleng_per_case
                
                rec.sm = sm
    
    
    # Get nilai net(w) langsung dari sis_items (BELUM DIPAKE)        
    @api.one
    def get_value_nw(self):
        for rec in self:
            item_no = rec.item_no
            
            if item_no:
                items_obj = rec.env['sis.items'].search([('itemno', '=', item_no)])
                        
                if items_obj:
                    for item in items_obj:
                        net_item = item.nw # Satuan KG
                    
                    # Dikonversi ke dalam gram (KG to gram)
                    rec.net = net_item * 1000 # Satuan gram
    
    
    # Get value meat in bom (BELUM DIPAKE)
    @api.one
    def get_value_meat(self):
        for rec in self:
            itemno = rec.item_no
            
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
    


class budomari_inherit(models.Model):
    _inherit = 'sis.budomari'
    
    # Change name many2one
    @api.multi
    def name_get(self):
        result = []
        for rec in self:    
            result.append((rec.id, '%s - %s' % (rec.fish, rec.budomari)))
        return result
                
    
    
    
    