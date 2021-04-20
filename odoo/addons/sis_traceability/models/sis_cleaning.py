from odoo import models, fields, api, tools
#from datetime import datetime

class cleaning(models.Model):
    _name  ='sis.cleaning'  
    _rec_name = 'r_name' 
    _order = 'tgl_bongkar desc, tgl_produksi desc'
    
    re_cleaning = fields.One2many('sis.unpacking.defrost.loin', 'rel_cleaning_unpack', string="Relasin Unpacking Frozen Loin")
    rel_packing_detail_cl = fields.Many2many('sis.packing.detail', 'rel_pre', string="Relasi Cleaning Packing")
    rel_cs_detail = fields.Many2one('sis.cs.detail', string='No Fish Box', domain="[('tgl_produksi','=', tgl_produksi),('pabrik_id', '=', location),('fresh_fish','=','3')]")
    
    tgl_bongkar = fields.Date(string="Tanggal Bongkar", required=True, default=fields.Datetime.now)
    tgl_produksi = fields.Date(string="Tanggal Produksi", required=True, default=fields.Datetime.now)
    fish_box_no = fields.Char(string='No Fish Box', compute="_get_fishbox", store=True)
    rak_defrost_id = fields.Char(string="No. ID Rak Defrost", required=True)
    kode_loin = fields.Char(string="Loin/Shredded", compute="_get_kode_loin", store=True)
    kode_loin_urut = fields.Char(string="Loin/Shredded", compute="_get_kode_loin", store=True)
    no_tengah = fields.Integer(string="No Tengah", compute="_get_no_tengah", store=True)
    no_urut_rak_defrost = fields.Char(string="No. Urut Rak Defrost",  required=True)
    lot = fields.Char(string="Lot", compute="_get_lot", store=True)
    kode_produksi = fields.Char(string="Kode produksi", required=True)
    jumlah = fields.Integer(string="Jumlah Quantit (pcs)", required=True)
    qtykantong = fields.Selection(default=5, selection=[(5, '5 KG'),(7.5, '7,5 KG')], String="Quantity Per  Kantong", required=True)
    total = fields.Float(string="Total (kg)", store=True, compute='_total')
    jambongkar = fields.Float(string="Jam Mulai Bongkar", required=True)
    start_thawing = fields.Float(string="Mulai Thawing", required=True)
    delay_time_max = fields.Float(string="Delay Time Maks", required=True)
    jambongkar_real = fields.Char(string="Jam Mulai Bongkar Real", compute="_get_jambongkar", store=True)
    start_thawing_real = fields.Char(string="Mulai Thawing Real", compute="_get_thawing", store=True)
    delay_time_max_real = fields.Char(string="Delay Time Maks Real", compute="_get_delay", store=True)
    temuan_benda = fields.Boolean(string="Temuan Benda Asing")
    remark = fields.Char(string="Remark")
    location = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True)
    r_name = fields.Char('r_name', compute='_get_rname', store=True)
    
    @api.one
    @api.depends('no_urut_rak_defrost','no_tengah')
    def _get_rname(self):
        if self.no_urut_rak_defrost:
            self.r_name = str(self.no_urut_rak_defrost)+'.'+str(self.no_tengah)

#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%s.%s" % (me.no_urut_rak_defrost, me.no_tengah)))
#         return result
                     
    @api.one
    @api.depends('jambongkar')
    def _get_jambongkar(self):
        if self.jambongkar:
            self.jambongkar_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jambongkar) * 60, 60))
            
    @api.one
    @api.depends('start_thawing')
    def _get_thawing(self):
        if self.start_thawing:
            self.start_thawing_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.start_thawing) * 60, 60))
            
    @api.one
    @api.depends('delay_time_max')
    def _get_delay(self):
        if self.delay_time_max:
            self.delay_time_max_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.delay_time_max) * 60, 60))
            
    @api.one
    @api.depends("tgl_produksi", "kode_loin", "no_urut_rak_defrost")
    def _get_no_tengah(self):
        if self.tgl_produksi and self.kode_loin and self.no_urut_rak_defrost:
            xsql="select tgl_produksi, location, kode_loin, no_urut_rak_defrost from sis_cleaning where tgl_produksi='"+str(self.tgl_produksi)+"' and kode_loin='"+self.kode_loin+"' and no_urut_rak_defrost='"+str(self.no_urut_rak_defrost)+"' and location='"+self.location+"'"
            self.env.cr.execute(xsql)
            data=self.env.cr.fetchall()
            self.no_tengah=len(data)
    
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
                
            self.kode_loin_urut=var1+var2+var3+"  "+str(self.no_urut_rak_defrost)
            self.kode_loin=var1+var2+var3  

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
            self.lot=self.rel_cs_detail.lot_no+" "+self.rel_cs_detail.vessel_no
            
#     @api.onchange('tgl_produksi')
#     def onchange_fish_box(self):
#         domain = []
#         domain.append(('tgl_produksi','=',self.tgl_produksi))
#         domain.append(('pabrik_id','=',self.location))
#         domain.append(('fresh_fish','=', '3'))
#         return {'domain':{'rel_cs_detail':domain}}
    
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

class sis_fz_view_alert(models.Model):
    _name = 'sis.fz.view.alert'
    _description = 'Data Loin yang belum di input Frozen Loin'
    _auto = False
    _order = 'tgl_produksi desc'
    
    tgl_produksi = fields.Date('Tanggal Produksi')
    pabrik_id = fields.Char('Lokasi')
    tgl_keluar = fields.Datetime('Tanggal keluar')
    fish_box_no = fields.Char('Fishbox No')
    item_no = fields.Char('Item No')
    description =  fields.Char('Description')
    vessel_no =   fields.Char('Vessel No')
    hatch_no =   fields.Char('Hatch No')
    quantity = fields.Float('Quantity')
    create_date =   fields.Datetime('Create Date')
    
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_fz_view_alert as (
        SELECT DISTINCT
        row_number() OVER () as id, 
        cs.tgl_produksi,cs.pabrik_id, cs.tgl_keluar, cs.fish_box_no, cs.item_no, cs.description, cs.vessel_no, cs.hatch_no, 
        cs.quantity, cs.create_date
        from sis_cs_detail as cs
        left join sis_cleaning as cl on cl.rel_cs_detail=cs.id
        where cs.fresh_fish='3' and cs.tgl_produksi>='2020-11-01' and cl.id is null
        order by cs.tgl_produksi desc)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_fz_view_alert')
        self._cr.execute(cSQL)
            
            