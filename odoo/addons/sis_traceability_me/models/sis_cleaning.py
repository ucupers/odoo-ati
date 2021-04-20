from odoo import models, fields, api
#from datetime import datetime

class cleaning(models.Model):
    _name  ='sis.cleaning'   
    
    tgl_bongkar = fields.Date(string="Tanggal Bongkar", required=True, default=fields.Datetime.now)
    tgl_produksi = fields.Date(string="Tanggal Produksi", required=True)
    fish_box_no = fields.Char(string='No Fish Box', compute="_get_fishbox", store=True)
    rak_defrost_id = fields.Char(string="No. ID Rak Defrost", required=True)
    kode_loin = fields.Char(string="Loin/Shredded", compute="_get_kode_loin", store=True)
    no_urut_rak_defrost = fields.Integer(string="No. Urut Rak Defrost",  compute="_get_urut", store=True)
    lot = fields.Char(string="Lot", compute="_get_lot", store=True)
    kode_produksi = fields.Char(string="Kode produksi", required=True)
    jumlah = fields.Integer(string="Jumlah Quantit (pcs)", required=True)
    qtykantong = fields.Selection(default=5, selection=[(5, '5 KG'),(7.5, '7,5 KG')], String="Quantity Per  Kantong", required=True)
    total = fields.Float(string="Total (kg)", store=True, compute='_total')
    jambongkar = fields.Float(string="Jam Mulai Bongkar", required=True)
    start_thawing = fields.Float(string="Mulai Thawing", required=True)
    delay_time_max = fields.Float(string="Delay Time Maks", required=True)
    temuan_benda = fields.Boolean(string="Temuan Benda Asing")
    remark = fields.Char(string="Remark")
    rel_cs_detail = fields.Many2one('sis.cs.detail', string='No Fish Box')
    location = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True)
    
    @api.one    
    @api.depends('jumlah')
    def _total(self):
        if self.jumlah:
            self.total=float(self.qtykantong) * float(self.jumlah)
    
    @api.one     
    @api.depends('rel_cs_detail')
    def _get_fishbox(self):
        if self.rel_cs_detail:
            self.fish_box_no=self.rel_cs_detail.fish_box_no  
              
    @api.one     
    @api.depends('rel_cs_detail')
    def _get_kode_loin(self):
        if self.rel_cs_detail:
            var3=""
            cSQL=""
            if self.rel_cs_detail.item_no[-2:]=="3F":
                var1="S"
            elif self.rel_cs_detail.item_no[-2:]=="3L":
                var1="L"
            else:
                var1="T"
            
            var2=self.rel_cs_detail.product_group_code
            
            if self.rel_cs_detail.hatch_no[:1]=="L":
                cSQL="select kode from sis_vendor where hatch='"+self.rel_cs_detail.hatch_no[:5]+"'"
            else:
                cSQL="select kode from sis_vendor where vessel='"+self.rel_cs_detail.vessel_no+"'"
            
            if cSQL!="":
                self.env.cr.execute(cSQL)
                data=self.env.cr.fetchall()
                
                if len(data)!=0:
                    for data_kode in data:
                        (xkode,)=data_kode
            
                    if xkode!="":
                        var3=xkode
                
            self.kode_loin=var1+var2+var3+" "+str(self.no_urut_rak_defrost)  

    @api.one     
    @api.depends('tgl_produksi')
    def _get_urut(self):
        if self.tgl_produksi:
            cSQL="select max(no_urut_rak_defrost) from sis_cleaning where tgl_produksi='"+self.tgl_produksi+"'"
            self.env.cr.execute(cSQL)
            data=self.env.cr.fetchall()
    
            for data_kode in data:
                (xurut,)=data_kode
            
            if xurut:
                self.no_urut_rak_defrost=xurut+1
            else:
                self.no_urut_rak_defrost=1
    
    @api.one     
    @api.depends('rel_cs_detail')
    def _get_lot(self):
        if self.rel_cs_detail:
            self.lot=self.rel_cs_detail.lot_no
            
    @api.onchange('tgl_produksi')
    def onchange_fish_box(self):
        domain = []
        domain.append(('tgl_produksi','=',self.tgl_produksi))
        domain.append(('pabrik_id','=',self.location))
        domain.append(('fresh_fish','=', '3'))
        return {'domain':{'rel_cs_detail':domain}}
    
    @api.one        
    @api.depends('tgl_produksi')
    def _get_pabrik_id(self):
        if self.tgl_produksi:
            xuid = self.env.uid
            cSQL1="select a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.location=xpabrik_id