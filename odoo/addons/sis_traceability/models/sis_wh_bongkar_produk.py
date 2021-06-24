from odoo import fields, models, api, tools
from odoo.exceptions import ValidationError

class bongkar_produk(models.Model):
    _name = 'sis.wh.bongkar.produk'
    _description = 'WH Bongkatproduk dari basket'
    _rec_name = 'produk'
    _order = 'productiondate desc, loadingdate desc'
    
    produk_wh_id = fields.Many2one('sis.master.product', string="Jenis Produk", domain ="[('id','in',produk_list)]")
    bongkar_produk_ids = fields.One2many('sis.wh.bongkar.produk.detail', 'header_id', string='Bongkar Detail')
    produk_list = fields.Many2many('sis.master.product', 'rel_produk_list', 'wh_id', 'produk_id', string='Produk Filter', compute="get_product_list", store=True)
    
    productiondate = fields.Date('Tanggal Produksi', required=True)
    loadingdate = fields.Date('Tanggal Bongkar', required=True)
    produk = fields.Char( 'Jenis Produk', compute="_get_product", store="True")
    line = fields.Char('Line')
    
    def update_ile_nav_odoo(self):
        self.env.cr.execute("""insert into sis_ile_whunlabel_loc(tanggal_produksi, item_no, no_pallet, gudang) select nav.tanggal_produksi, nav.item_no, nav.no_pallet, nav.gudang from sis_ile_whunlabel nav left join sis_ile_whunlabel_loc loc on nav.no_pallet=loc.no_pallet where loc.no_pallet is null""")
    
    @api.depends('produk_wh_id')
    def _get_product(self):
        if self.produk_wh_id:
            self.produk = self.produk_wh_id.description
            
    @api.one
    @api.depends('productiondate')            
    def get_product_list(self):
        if self.productiondate:
            prod_list = []
            data = self.env['sis.retort.detail'].search([('productiondate','=', self.productiondate)])
            for datas in data:
                for datas2 in datas.produk_ids:
                    prod_list.append(datas2.packing_id.rel_product.id)
            self.produk_list=prod_list
                
    @api.multi
    def unlink(self):
        qqs="delete from sis_wh_bongkar_produk_detail where header_id="+str(self.id)
        self.env.cr.execute(qqs)
        return models.Model.unlink(self)
    
class bongkar_produk_detail(models.Model):
    _name = 'sis.wh.bongkar.produk.detail'
    _description = 'WH Bongkar produk dari basket detail'
    _rec_name ='basket_no'
    

    pallet_ids = fields.Many2many('sis.ile.whunlabel.loc', 'pallet_relation', 'wh_id', 'pallet_id', string='Relasi Pallet', domain ="[('tanggal_produksi','=',productiondate),('item_no','=',kode_nav)]")
    retort_loading_id = fields.Many2one('sis.retort.loading.basket.detail', string='relasi ke retort loading', domain="[('basket_line','!=',False),('header_id.produk','=',product),('header_id.productiondate','=',productiondate)]")
    header_id = fields.Many2one('sis.wh.bongkar.produk', string='relasi header')
    
    jam_mulai = fields.Float('Jam Mulai Bongkar')
    jam_selesai = fields.Float('Jam Selesai Bongkar')
    jam_mulai_real = fields.Float('Jam mulai real', compute="_get_jammulai", store=True)
    jam_selesai_real = fields.Float('Jam selesai real', compute="_get_jamselesai", store=True)
    basket_no = fields.Char('No Basket', compute="_get_basket", store=True)
    product = fields.Char('Jenis Produk', compute="_get_produk", store=True)
    productiondate = fields.Date('Tanggal Produksi', compute="_get_productiondate", store=True)
    loadingdate = fields.Date('Tanggal Bongkar', compute="_get_loadingdate", store=True)
    remark = fields.Char('Remark')
    pallet = fields.Char('No Pallet', compute="_get_pallet", store=True)
    kode_nav = fields.Char('Kode NAV', compute="_get_kode_nav", store=True)
    
    @api.constrains('retort_loading_id')
    def _constrains_double_basket(self):
        if self.basket_no:
            rec=self.env['sis.wh.bongkar.produk.detail'].search([('retort_loading_id','=',self.retort_loading_id.id),('id','!=',self.id)])
            if len(rec)>0:
                raise ValidationError('Basket No '+str(self.retort_loading_id.basket_line)+' sudah diinput')
        else:
            raise ValidationError('Terdapat No Basket yang belum diinput')
    
    @api.one
    @api.depends('jam_mulai')
    def _get_jammulai(self):
        if self.jam_mulai:
            self.jam_mulai_real= '{0:02.0f}.{1:02.0f}'.format(*divmod(float(self.jam_mulai) * 60, 60))
    
    @api.one
    @api.depends('jam_selesai')
    def _get_jamselesai(self):
        if self.jam_selesai:
            self.jam_selesai_real= '{0:02.0f}.{1:02.0f}'.format(*divmod(float(self.jam_selesai) * 60, 60))
    
    @api.one
    @api.depends('header_id')
    def _get_kode_nav(self):
        if self.header_id:
            if self.header_id.produk_wh_id:
                self.kode_nav=self.header_id.produk_wh_id.kode_nav

    @api.one
    @api.depends('pallet_ids')
    def _get_pallet(self):
        if self.pallet_ids:
            for data in self.pallet_ids:
                if self.pallet:
                    self.pallet=self.pallet+", "+data.no_pallet
                else:
                    self.pallet=data.no_pallet   

    
    @api.one
    @api.depends('retort_loading_id')
    def _get_basket(self):
        if self.retort_loading_id:
            self.basket_no = self.retort_loading_id.basket_line
    
    @api.one
    @api.depends('header_id.productiondate')
    def _get_productiondate(self):
        if self.header_id.productiondate:
            self.productiondate = self.header_id.productiondate
            
    @api.one
    @api.depends('header_id.loadingdate')
    def _get_loadingdate(self):
        if self.header_id.loadingdate:
            self.loadingdate = self.header_id.loadingdate
            
    @api.one
    @api.depends('header_id.produk')
    def _get_produk(self):
        if self.header_id.produk:
            self.product = self.header_id.produk
    
    @api.multi
    def write(self, vals):
        if self.pallet:
            vals['pallet']=self.pallet
        return models.Model.write(self, vals)
    
class sis_wh_view_alert(models.Model):
    _name = 'sis.wh.view.alert'
    _description = 'Data basket retort yang belum diinput WH'
    _auto = False
    _order = 'productiondate desc, produk'
    
    productiondate = fields.Date('Tanggal produksi')
    location = fields.Char('Lokasi')
    produk = fields.Char('Nama Produk')
    basket_line = fields.Char('Line - Basket')

     
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_wh_view_alert as (
        SELECT DISTINCT
        row_number() OVER () as id, 
        lod.productiondate, lod.location,lod.produk, lo.basket_line from sis_retort_loading_basket_detail as lo
        left join basket_retort_ids as re on re.sis_retort_loading_basket_detail_id=lo.id
        left join sis_wh_bongkar_produk_detail as wh on lo.id=wh.retort_loading_id
        left join sis_retort_loading_basket as lod on lod.id=lo.header_id
        where lo.productiondate>='2020-12-02' and wh.id is null and re.sis_retort_loading_basket_detail_id is not null)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_wh_view_alert')
        self._cr.execute(cSQL)

