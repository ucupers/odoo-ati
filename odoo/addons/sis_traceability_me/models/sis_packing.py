from odoo import models, fields, api

class sis_packing(models.Model):
    _name = 'sis.packing'
    
    productiondate = fields.Date(string="Tgl Produksi", required=True)
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    jamFinish = fields.Float(string="Jam Finish Cleaning", required=True)
    rel_pre = fields.Many2one('sis.pre.cleaning', string="Relasi Pre Cleaning")
    basket_id = fields.Integer(size=4, string='Basket ID', compute='_get_basket_id', store=True)
    label = fields.Integer(string="No Urut Basket", compute='_get_basket_no', store=True)
    lineCleaning = fields.Integer(size=4, string='Line Cleaning', compute='_get_line_cleaning', store=True)
    jamPacking = fields.Float(string="Jam Finish Cleaning", required=True)
    linePacking = fields.Integer(size=4, string='Line Packing', required=True)
    namaProduct = fields.Char(size=4, string='Nama Product', required=True)
            
    @api.one        
    @api.depends('productiondate')
    def _get_pabrik_id(self):
        if self.productiondate:                
            xuid = self.env.uid
            cSQL1="select a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.location=xpabrik_id  

    
        
    @api.one     
    @api.depends('rel_pre')
    def _get_line_cleaning(self):
        if self.rel_pre:
            self.lineCleaning=self.rel_pre.line_cleaning    
        
    @api.one     
    @api.depends('rel_pre')
    def _get_basket_id(self):
        if self.rel_pre:
            self.basket_id=self.rel_pre.basket_id
            
    @api.one     
    @api.depends('rel_pre')
    def _get_basket_no(self):
        if self.rel_pre:
            self.label=self.rel_pre.basket_no
    
    @api.onchange('productiondate')
    def onchange_label(self):
        domain = []
        domain.append(('productiondate','=',self.productiondate))
        
        return {'domain':{'rel_pre':domain}}