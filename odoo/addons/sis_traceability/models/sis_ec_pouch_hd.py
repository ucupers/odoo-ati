'''
Created on May 15, 2020

@author: endah
'''

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo import tools


class sis_ec_pouch_header(models.Model):
    _name = 'sis.ec.pouch.header'
    _description = 'Empty Can Pouch Header'
    _order = 'productiondate_ati desc'
    _rec_name = 'nama_produk'
    
    line_hd_id = fields.Many2one('sis.packing.line', string='Line')
    packing_hd_id = fields.Many2one('sis.packing', string='Packing ID', domain="[('productiondate', '=', productiondate_ati)]")
    items_ec_hd_id = fields.Many2one('sis.items.ec.loc', string='Kode Barang')
    detail_ids = fields.One2many('sis.ec.pouch.detail', 'header_id', string="Detail ID")
   
    productiondate_ati = fields.Date('Tanggal Produksi ATI', required=True)
#     incomingdate = fields.Date('Tanggal Kedatangan', required=True)
    line = fields.Char('Line', compute="_get_line_hd", store=True)
    nama_produk = fields.Char('Nama Produk', compute="_get_produk_hd", store=True)
    deskripsi_pouch = fields.Char('Deskripsi Pouch', compute="_get_desk_pouch", store=True)
    kode_barang = fields.Char('Kode Barang', compute="_get_kode_brg", store=True)
#     total_kedatangan = fields.Integer('Total Kedatangan')
    total_pemakaian = fields.Integer('Total Pemakaian')
    total_reject = fields.Integer('Total Reject')
    sisa = fields.Integer('Sisa Pouch')
    sample_ec = fields.Integer('Sample')
    ket_sample = fields.Char('Ket Sample')
    remark = fields.Char('Remark', default="-")
    status_button = fields.Boolean('Status Button Get Detail', default=False)
    
    @api.depends('line_hd_id')
    def _get_line_hd(self):
        if self.line_hd_id:
            self.line = self.line_hd_id.line
            
    @api.depends('packing_hd_id')
    def _get_produk_hd(self):
        if self.packing_hd_id:
            self.nama_produk = self.packing_hd_id.kind_of_product
    
    @api.depends('items_ec_hd_id')
    def _get_desk_pouch(self):
        if self.items_ec_hd_id:
            self.deskripsi_pouch = self.items_ec_hd_id.deskripsi_barang
    
    @api.depends('items_ec_hd_id')
    def _get_kode_brg(self):
        if self.items_ec_hd_id:
            self.kode_barang = self.items_ec_hd_id.kode_barang
            
#     def get_ttl_kedatangan(self):
#         sqlx = "select sum(qty_kedatangan) from sis_ile_receipt where kode_barang='"+self.kode_barang+"' and tgl_kedatangan='"+self.incomingdate+"'"
#         ttl_kedatangan = 0
#         self.env.cr.execute(sqlx)
#         xdata = self.env.cr.fetchall()
#         for data in xdata:
#             (xtotal, ) = data
#             ttl_kedatangan = ttl_kedatangan + xtotal
#         self.total_kedatangan = ttl_kedatangan
        
#     def get_sisa(self):
#         ssql="select sum(total_pemakaian), sum(total_reject) from sis_ec_pouch_header where kode_barang='ELB705' and incomingdate='2020-03-18'"
#         self.env.cr.execute(ssql)
#         data = self.env.cr.fetchall()
#         for datas in data:
#             (pemakaian, rejects) = datas
#         self.sisa = self.total_kedatangan - pemakaian - rejects
                    
    def get_detail(self):
        data = self.env['sis.ile.ec'].search([('source_fg', '=', self.nama_produk),('productiondate_ati', '=', self.productiondate_ati), ('kode_barang', '=', self.kode_barang)])
        ttl_pemakaian = 0
        ttl_reject = 0
        if data:
            for datas in data:
                ttl_pemakaian = ttl_pemakaian + datas.qty_pemakaian
                ttl_reject = ttl_reject + datas.qty_reject
                vals_detail = {
                    'header_id' : self.id,
                    'kode_barang':datas.kode_barang + ' ' + datas.varian,
                    'no_box':datas.no_box,
                    'productiondate_sup':datas.productiondate_sup,
                    'nama_supplier':datas.nama_supplier,
                    'invoice':datas.invoice,
                    'tgl_kedatangan':datas.tgl_kedatangan,
                    'qty_kedatangan':datas.qty_kedatangan,
                    'qty_pemakaian':datas.qty_pemakaian,
                    'qty_reject':datas.qty_reject,
                    'qty_sample':datas.sisa_qty,
                    'sisa_qty':datas.qty_sample}
                create_detail = self.env['sis.ec.pouch.detail']
                create_detail.create(vals_detail)
#             self.get_ttl_kedatangan()
            self.total_pemakaian = ttl_pemakaian
            self.total_reject = ttl_reject
            self.status_button = True
        else:
            raise UserError('Data tidak ditemukan !!')
        
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_ec_pouch_detail where header_id="+str(me_id.id)+""
            self.env.cr.execute(cSQL1)           
                
            return super(sis_ec_pouch_header, self).unlink()    
            
    def update_ile_ec(self):
        self.env.cr.execute("delete from sis_ile_ec")
        self.env.cr.execute("""
        insert into 
        sis_ile_ec(source_fg, productiondate_ati, varian, no_box, productiondate_sup, nama_supplier, qty_kedatangan, tgl_kedatangan, invoice, qty_pemakaian, qty_reject, kode_barang, deskripsi, nomor_kedatangan, location_code, document_no, qty_sample, qty_sisa)
        select
        distinct ile1.source_fg, ile1.posting_date as tgl_produksi_ati, ile1.variant, ile1.lot_no no_box, ile4.productiondate_sup, ile4.nama_supplier, abs(ile2.quantity) as qty_kedatangan,
        ile2.posting_date as tgl_kedatangan, ile2.extdocno as invoice,  abs(ile1.quantity) as qty_pemakaian, abs(ile3.quantity) as qty_reject,
        ile1.item_no as kode_barang, ile1.description as deskripsi,ile2.document_no, ile2.location_code, ile4.nomor_kedatangan, abs(ile5.quantity) as qty_sample, sisa_qty
        
        from sis_ile_raw as ile1
        
        left join sis_ile_raw as ile2
        on ile1.lot_no=ile2.lot_no and ile1.item_no=ile2.item_no and ile1.variant=ile2.variant and ile2.entry_type='Purchase'
        
        left join sis_ile_raw as ile3
        on
        ile1.lot_no=ile3.lot_no and ile1.item_no=ile3.item_no and ile1.variant=ile3.variant
        and ile3.entry_type='Transfer Receipt' and ile3.location_code='ATI1-RJCT'
        
        left join sis_ile_receipt as ile4
        on
        ile2.posting_date=ile4.tgl_kedatangan and ile1.lot_no=ile4.lot_no and ile1.item_no=ile4.kode_barang and ile2.location_code=ile4.lokasi and
        ile2.document_no=ile4.nomor_kedatangan
        
        left join sis_ile_raw as ile5
        on
        ile1.lot_no=ile5.lot_no and ile1.item_no=ile5.item_no and ile1.variant=ile5.variant
        and ile5.entry_type='Negative Adj' and ile5.location_code='ATI1-EC'
        
        /*where ile1.item_no like 'E_B7%' and ile1.posting_date>='2020-01-01' and ile1.entry_type='Consumption'*/
        where ile1.itc = 'PKG' and ile1.pgc in ('CAN','POUCH') and ile1.item_no not like 'ELS%' and ile1.posting_date>='2021-01-01' and ile1.entry_type='Consumption'
                
        order by ile1.posting_date desc, ile1.lot_no asc
        """)

            
class sis_ec_pouch_detail(models.Model):
    _name = 'sis.ec.pouch.detail'
    _description = 'Empty Can Pouch Detail'
    
    header_id = fields.Many2one('sis.ec.pouch.header', string="Header ID")
    kode_barang = fields.Char('Kode barang')
    no_box = fields.Char('No Box')
    productiondate_sup = fields.Date('Tanggal Produksi Supllier')
    nama_supplier = fields.Char('Nama Supplier')
    tgl_kedatangan = fields.Date('Tanggal Kedatangan')
    invoice = fields.Char('Invoice')
    qty_kedatangan = fields.Integer('Total Kedatangan')
    qty_pemakaian = fields.Integer('Total Pemakaian')
    qty_reject = fields.Integer('Total Reject')
    qty_sample = fields.Integer('Qty Sample')
    sisa_qty = fields.Float('Qty Sisa')
     
#     @api.one
#     @api.depends('header_id.tgl_kedatangan')
#     def _get_tgl_kedatangan(self):
#         if self.header_id.tgl_kedatangan:
#             self.tgl_kedatangan=self.header_id.tgl_kedatangan
    
    
    def updt_ttl_kedatangan(self):
        sqlx = "select distinct no_box, qty_kedatangan, tgl_kedatangan from sis_ec_pouch_detail where header_id="+str(self.header_id.id)+" and id<>"+str(self.id)
        ttl_kedatangan = 0
        self.env.cr.execute(sqlx)
        xdata = self.env.cr.fetchall()
        for data in xdata:
            (xno_box, xqty_kedatangan, xtgl_kedatangan) = data
            ttl_kedatangan = ttl_kedatangan + xqty_kedatangan
        self.header_id.total_kedatangan = ttl_kedatangan
    
    @api.multi
    def unlink(self):
        data = self.env['sis.ec.pouch.detail'].search([('header_id', '=', self.header_id.id),('id','!=',self.id)])
        pemakaian = 0
        rjct = 0
        for datas in data:
            pemakaian = pemakaian + datas.qty_pemakaian
            rjct = rjct + datas.qty_reject
#         self.updt_ttl_kedatangan()
        self.header_id.total_pemakaian = pemakaian
        self.header_id.total_reject = rjct
        return models.Model.unlink(self)
        
    
class sis_ile_ec(models.Model):
    _name = 'sis.ile.ec'
    _description = 'sis ile ec'
        
    productiondate_ati = fields.Date('Tanggal Produksi ATI')
    kode_barang = fields.Char('Kode barang')
    deskripsi = fields.Char('Deskripsi Barang')
    source_fg = fields.Char('Jenis Produk')
    varian = fields.Char('Variant')
    no_box = fields.Char('No Box')
    productiondate_sup = fields.Date('Tanggal Produksi Supllier')
    nama_supplier = fields.Char('Nama Supplier')
    nomor_kedatangan = fields.Char('Nomor Kedatangan')
    tgl_kedatangan = fields.Date('Tanggal Kedatangan')
    invoice = fields.Char('Invoice')
    qty_kedatangan = fields.Integer('Total Kedatangan')
    qty_pemakaian = fields.Integer('Total Pemakaian')
    qty_reject = fields.Integer('Total Reject')
    location_code = fields.Char('Kode Lokasi')
    document_no = fields.Char('No Document')
    qty_sample = fields.Integer('Total Reject')
    sisa_qty = fields.Float('Total Reject')
    
class sis_items_ec(models.Model):
    _name = 'sis.items.ec.loc'
    _description = 'Items Code EC'
    _rec_name = 'kode_barang'
    
    pouch_hd_ids = fields.One2many('sis.ec.pouch.header', 'items_ec_hd_id', string='Pouch Relasi')
        
    kode_barang = fields.Char('Kode Barang')
    deskripsi_barang = fields.Char('Deskripsi Barang')
    

class sis_ec_pouch_lot_view(models.Model):
    _name = 'sis.ec.pouch.lot'
    _description = 'View pe Tanggal Produksi Supplier'
    _order = 'productiondate_sup desc, tgl_kedatangan desc'
    
    detail_ids = fields.One2many('sis.ec.pouch.lot.detail', 'header_id', string='Detail ID')
    
    productiondate_sup = fields.Date('Tanggal Produksi Supplier')
    nama_supplier = fields.Char('Supplier')
    tgl_kedatangan = fields.Date('Tanggal Kedatangan')
    invoice = fields.Char('Invoice')
    total_kedatangan = fields.Integer('Total Kedatangan')
    total_pemakaian = fields.Integer('Total Pemakaian')
    total_reject = fields.Integer('Total Reject')
    total_sample = fields.Integer('Total Sample')
    sisa = fields.Integer('Sisa')
    btn_stts = fields.Boolean('Button Status', default=False)
    
    def get_detail_lot_view(self):
        xtx = """
        insert into
        sis_ec_pouch_lot_detail(header_id, productiondate, produk, deskripsi_pouch, kode_barang, total_kedatangan, total_pemakaian, total_reject, sample_ec)
        select vie.id, ec.productiondate_ati, ec.nama_produk, ec.deskripsi_pouch, ec.kode_barang, ec.total_kedatangan, ec.total_pemakaian, ec.total_reject,
        ec.sample_ec from sis_ec_pouch_lot as vie
        left join sis_ec_pouch_header as ec on ec.incomingdate = vie.tgl_kedatangan and ec.total_kedatangan=vie.total_kedatangan
        where vie.id="""+str(self.id)
          
        self.env.cr.execute(xtx)
        self.btn_stts=True

        
#     @api.model_cr   
#     def init(self):
#         ccSQL="""
#         CREATE OR REPLACE VIEW sis_ec_pouch_lot_view as (
#         SELECT distinct
#         row_number() OVER () as id, 
#         sis_ec_pouch_detail.productiondate_sup, sis_ec_pouch_detail.nama_supplier, sis_ec_pouch_detail.tgl_kedatangan, 
#         sis_ec_pouch_detail.invoice, sis_ec_pouch_header.total_kedatangan, sum(sis_ec_pouch_header.total_pemakaian) as total_pemakaian,  
#         sum(sis_ec_pouch_header.total_reject) as total_reject, sum(sis_ec_pouch_header.sample_ec) as total_sample, 
#         sis_ec_pouch_header.total_kedatangan-sum(sis_ec_pouch_header.total_pemakaian)-sum(sis_ec_pouch_header.sample_ec) as sisa
#         from sis_ec_pouch_detail
#         left join sis_ec_pouch_header on header_id= sis_ec_pouch_header.id
#         where sis_ec_pouch_detail.productiondate_sup is not null
#         group by sis_ec_pouch_detail.productiondate_sup, sis_ec_pouch_detail.nama_supplier, sis_ec_pouch_detail.tgl_kedatangan, 
#         sis_ec_pouch_detail.invoice, sis_ec_pouch_header.total_kedatangan
#         order by productiondate_sup desc)
#         """    
#         
#         delsql="delete from sis_ec_pouch_lot_view"
# #         self._cr.execute(delsql)
#         tools.sql.drop_view_if_exists(self._cr, 'sis_ec_pouch_lot_view')
#         self._cr.execute(ccSQL)
    
class lot_view_detail(models.Model):
    _name = 'sis.ec.pouch.lot.detail'
    _description = 'Model lot view Detail'
    
    header_id = fields.Many2one('sis.ec.pouch.lot', string='Header ID')
    
    productiondate = fields.Date('Tanggal Produksi ATI')
    produk = fields.Char('Nama Produk')
    kode_barang = fields.Char('Kode Barang')
    deskripsi_pouch = fields.Char('Deskripsi Barang')
    total_kedatangan = fields.Integer('Kedatangan')
    total_pemakaian = fields.Integer('Pemakaian')
    total_reject = fields.Integer('Reject')
    sample_ec = fields.Integer('Sample')
    
