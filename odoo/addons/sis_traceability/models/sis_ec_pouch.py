'''
Created on May 15, 2020

@author: endah
'''

from odoo import models, fields, api
from builtins import str
from odoo.exceptions import UserError
from sqlalchemy.sql.expression import false

class sis_ec_pouch(models.Model):
    _name = 'sis.ec.pouch'
    _description = 'Empty Can Pouch'
    _order = 'productiondate desc'
    
    line_id = fields.Many2one('sis.packing.line', string='Line')
    packing_id = fields.Many2one('sis.packing', string='Packing ID', domain="[('productiondate', '=', productiondate)]")
#     packing_id = fields.Many2one('sis.packing', string='Packing ID')
    items_ec_id = fields.Many2one('sis.items.ec.loc', string='Kode Barang')
#     pack_filt_id = fields.Many2many('sis.packing',string='Filter produk', compute='_get_filt', store=True)
#     pack_filt_id = fields.Many2many('sis.packing', 'rel_ec_pouch', 'po_id', 'pack_id',string='Filter produk', compute='_get_filt', store=True)
#     items_list = fields.Many2many('sis.items.ec.loc', 'rel_items_list', 'ec_id', 'items_id', string='Items Filter', compute="get_items_list", store=True)
   
    pouch_id = fields.Integer('ID EC Pouch')
    productiondate = fields.Date('Tanggal Produksi ATI', required=True)
    line = fields.Char('Line', compute='_get_line', store=True)
    nama_produk = fields.Char('Nama Produk', compute='_get_produk', store=True)
    jenis_pouch = fields.Char('Deskripsi Pouch', compute='_get_jenis_pouch', store=True)
    kode_barang = fields.Char('Kode Barang', compute='_get_kode_barang', store=True)
    lot = fields.Date('Tanggal Produksi Supllier', required=True)
    tgl_kedatangan = fields.Date('Tanggal Kedatangan', required=True)
    invoice = fields.Char('Invoice', required=True)
    total_kedatangan = fields.Integer('Total Kedatangan', required=True)
    total_pemakaian = fields.Integer('Total Pemakaian', required=True)
    total_reject = fields.Integer('Total Reject', required=True)
    sisa = fields.Integer('Sisa Kaleng', compute="_get_sisa", store=True)
    remark = fields.Char('Remark')
    
    def _getidp(self):
        self.env.cr.execute("select * from sis_ec_pouch")
        rc=self.env.cr.fetchall()
        if len(rc)==0:
            idp=1
        else:
            self.env.cr.execute("select max(pouch_id) from sis_ec_pouch ")
            rc=self.env.cr.fetchall()
            for rr in rc:
                (da, ) = rr
            idp=da+1            
        return idp
 
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        idp = self._getidp()
        vals.update({'pouch_id':idp})
        return models.Model.create(self, vals)
    
    @api.one
    @api.depends('total_kedatangan', 'total_pemakaian', 'total_reject')
    def _get_sisa(self):
        if self.total_kedatangan:
            pemakaian = 0
            reject = 0
            penguragan = 0
            datas = self.env['sis.ec.pouch'].search([('lot', '=', self.lot), ('tgl_kedatangan', '=', self.tgl_kedatangan), ('kode_barang', '=', self.kode_barang), ('invoice', '=', self.invoice), ('total_kedatangan', '=', self.total_kedatangan), ('pouch_id', '!=', self.pouch_id)])
            if datas:
                for data in datas:
                    pemakaian = pemakaian+data.total_pemakaian
                    reject = reject+data.total_reject
            pengurangan = self.total_pemakaian+self.total_reject+pemakaian+reject
            
            sisanya = self.total_kedatangan-pengurangan
            self.sisa=sisanya
            temp = self.total_kedatangan-pemakaian-reject
            if self.sisa<0:
                raise UserError('Pouch tersisa '+str(temp))

    
#     @api.one
#     @api.depends('productiondate')            
#     def get_product_list(self):
#         if self.productiondate:
#             it_list = []
#             data = self.env['sis.retort.detail'].search([('productiondate','=', self.productiondate)])
#             for datas in data:
#                 for datas2 in datas.produk_ids:
#                     it_list.append(datas2.packing_id.rel_product.id)
#             self.items_list=it_list
    
    def copydata(self):        
        data = {'line_id':self.line_id.id,
                'packing_id':self.packing_id.id,
                'items_ec_id':self.items_ec_id.id,
                'productiondate' : self.productiondate,
                'line' : self.line,
                'nama_produk' : self.nama_produk,
                'jenis_pouch' : self.jenis_pouch,
                'kode_barang' : self.kode_barang,
                'lot' : self.lot,
                'tgl_kedatangan' : self.tgl_kedatangan,
                'invoice' : self.invoice,
                'total_kedatangan' : self.total_kedatangan,
                'total_pemakaian' : 0,
                'total_reject' : 0,
                'remark' : self.remark,
                }
        create_data = self.env['sis.ec.pouch']
        create_data.create(data)
#     @api.one
#     @api.depends('productiondate', 'line_id')
#     def _get_filt(self):
#         if self.productiondate and self.line_id:
#             listnya = []
#             sqlda = """select distinct pack.id from sis_packing as pack
#                         inner join rel_material_line as rel on rel.sis_master_product_id=pack.rel_product
#                         where pack.productiondate='"""+self.productiondate+"""' and rel.sis_packing_line_id="""+str(self.line)
#             self.env.cr.execute(sqlda)
#             datas = self.env.cr.fetchall()
#              
#             for datada in datas:
#                 (ndata, )=datada
#                 listnya.append(ndata)
#                  
#             self.pack_filt_id=listnya
#             print(listnya)
#             print(self.pack_filt_id)
            
    @api.one
    @api.depends('items_ec_id')
    def _get_kode_barang(self):
        if self.items_ec_id:
            self.kode_barang = self.items_ec_id.kode_barang
    
    @api.one
    @api.depends('items_ec_id')
    def _get_jenis_pouch(self):
        if self.items_ec_id:
            self.jenis_pouch = self.items_ec_id.deskripsi_barang
    
    @api.one
    @api.depends('line_id')
    def _get_line(self):
        if self.line_id:
            self.line = self.line_id.line
            
    @api.one
    @api.depends('packing_id')
    def _get_produk(self):
        if self.packing_id:
            self.nama_produk = self.packing_id.kind_of_product
            
    def update_items_ec(self):
        self.env.cr.execute("insert into sis_items_ec_loc(kode_barang, deskripsi_barang) select nav.kode_barang, nav.deskripsi_barang from sis_items_ec nav left join sis_items_ec_loc loc on nav.kode_barang=loc.kode_barang where loc.kode_barang is null")            

class sis_items_ec(models.Model):
    _name = 'sis.items.ec.loc'
    _description = 'Items Code EC'
    _rec_name = 'kode_barang'
    
    pouch_ids = fields.One2many('sis.ec.pouch', 'items_ec_id', string='Pouch Relasi')
        
    kode_barang = fields.Char('Kode Barang')
    deskripsi_barang = fields.Char('Deskripsi Barang')
            
