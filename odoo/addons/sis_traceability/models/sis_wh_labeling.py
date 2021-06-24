'''
Created on Dec 7, 2020

@author: endah
'''
from odoo import fields, models, api, tools

class sis_wh_labeling(models.Model):
    _name = 'sis.wh.labeling.header'
    _description = 'WH Labeling'
    _rec_name = 'jenis_produk'
    
    detail_ids = fields.One2many('sis.wh.labeling.detail', 'header_id', string='Detail ID')
    produk_id = fields.Many2one('sis.master.product', string='Jenis Produk')
    
    productiondate = fields.Date('Tanggal Produksi')
    bongkar_date = fields.Date('Tanggal Bongkar')
    jenis_produk = fields.Char('Jenis Produk', compute='_get_jenis_produk', store=True)
    item_no = fields.Char('Item No', compute='_get_item_no', store=True)
    merk = fields.Char('Merk')
    line = fields.Char('Line')
    button_stts = fields.Boolean('Status button')
    pcs_layer = fields.Integer('Per Layer')
    ttl_rjct = fields.Integer('Total Reject', compute='_sum_reject', store=True)
    pcs_percase = fields.Integer('Pcs per Case')
    
    @api.one
    @api.depends('detail_ids')
    def _sum_reject(self):
        if self.detail_ids:
            temp = 0
            for obj in self.detail_ids:
                temp = temp + obj.rjct
                
            self.ttl_rjct = temp
    
    @api.one
    @api.depends('produk_id')
    def _get_jenis_produk(self):
        if self.produk_id:
            self.jenis_produk=self.produk_id.description
    
    @api.one
    @api.depends('produk_id')
    def _get_item_no(self):
        if self.produk_id:
            self.item_no=self.produk_id.kode_nav
    
    def get_data(self):
#         data= self.env['sis.ile.whunlabel.loc'].search([('tanggal_produksi','=', self.productiondate), ('item_no','=',self.item_no)])
        dssql="""select distinct ile.id, ile.no_pallet from sis_ile_whunlabel_loc as ile
                left join pallet_relation as pr on pr.pallet_id=ile.id
                left join sis_wh_bongkar_produk_detail as whd on whd.id=pr.wh_id
                where ile.tanggal_produksi='"""+str(self.productiondate)+"' and ile.item_no='"+self.item_no+"' and loadingdate='"+str(self.bongkar_date)+"'"
        self.env.cr.execute(dssql)
        data =self.env.cr.fetchall() 
        new_lines = self.env['sis.wh.labeling.detail'] 
        for dt in data:
            (pal_id, xpallet, )= dt
            csql ="select wh_id from pallet_relation where pallet_id="+str(pal_id)
            self.env.cr.execute(csql)
            que_data =self.env.cr.fetchall() 
            data_list =[] 
            if len(que_data)>0:
                for que in que_data:
                    (xid, ) = que
                    data_list.append(xid)
            vals = {'header_id': self.id,
                    'pallet'    : xpallet,
                    'pallet_id' : pal_id,
                    'basket_ids' : data_list,
                    'button_stts' : True
                    }
            new_lines += new_lines.new(vals)
        self.detail_ids = new_lines
        self.button_stts=True
    
    @api.multi
    def unlink(self):
        qqs="delete from sis_wh_labeling_detail where header_id="+str(self.id)
        self.env.cr.execute(qqs)
        return models.Model.unlink(self)
    
class sis_wh_labeling_detail(models.Model):
    _name = 'sis.wh.labeling.detail'
    _description = 'WH Labeling Detail'
    _order = 'pallet'
    
    header_id = fields.Many2one('sis.wh.labeling.header', string='Header ID')
    pallet_id = fields.Many2one('sis.ile.whunlabel.loc', string='pallet ID')
    basket_ids = fields.Many2many('sis.wh.bongkar.produk.detail', 'basket_relation', 'pallet2_id', 'basket_id', string='Relasi Basket')
    rjct_id = fields.Many2one('sis.master.reject', string='Reject Remark', domain="[('section', '=', 'WH')]") 
#     rjct_id = fields.Many2one('sis.master.reject', string='Reject Remark', domain=(['section','=','wh'])) 
    
    jam_penuh = fields.Float('Jam Penuh')
    jam_penuh_real = fields.Char('Jam Penuh Real')
    pallet = fields.Char('Pallet')
    basket_no = fields.Char('Basket No', compute='_get_basket', store=True)
    seaming_condition = fields.Selection([('Oke','O'),('X','Tidak Memenuhi Syarat'),('/','Tidak Ada Data'),('Z','Berhenti')], string='Seaming Condition', default='Oke')
    clean = fields.Selection([('Oke','O'),('Tidak Memenuhi Syarat','X'),('Tidak Ada Data','/'),('Berhenti','Z')], string='Bersih', default='Oke')
    no_rust = fields.Selection([('Oke','O'),('Tidak Memenuhi Syarat','X'),('Tidak Ada Data','/'),('Berhenti','Z')], string='Berkarat', default='Oke')
    no_oily = fields.Selection([('Oke','O'),('Tidak Memenuhi Syarat','X'),('Tidak Ada Data','/'),('Berhenti','Z')], string='Berminyak', default='Oke')
    can_mark_print_result = fields.Selection([('Oke','O'),('Tidak Memenuhi Syarat','X'),('Tidak Ada Data','/'),('Berhenti','Z')], string='Hasil Print', default='Oke')
    button_stts = fields.Boolean('Status button')
    jml_layer = fields.Integer('Jumlah (Layer)')
    jml_pcs = fields.Integer('Jumlah sisa pcs')
    rjct = fields.Integer('Reject')
    rjct_remark = fields.Char('Ket Reject', compute='_get_ket_reject', store=True)
    total_pcs = fields.Integer('Total pcs', compute='_get_total_pcs', store=True)
    remark = fields.Char('Remark')
    
    @api.one
    @api.depends('rjct_id')
    def _get_ket_reject(self):
        if self.rjct_id:
            self.rjct_remark = self.rjct_id.description
    
    @api.one
    @api.depends('jml_layer','jml_pcs','header_id.pcs_layer','header_id.pcs_percase')
    def _get_total_pcs(self):
        if self.header_id.pcs_layer and self.jml_layer:
            if self.header_id.item_no[:2]=='UC':
                if self.header_id.pcs_percase:
                    self.total_pcs=(self.header_id.pcs_layer*self.header_id.pcs_percase*self.jml_layer)+self.jml_pcs
            elif self.header_id.item_no[:2]!='UC':
                self.total_pcs=(self.header_id.pcs_layer*self.jml_layer)+self.jml_pcs
                
    @api.one
    @api.depends('basket_ids')
    def _get_basket(self):
        if self.basket_ids:
            data = ''
            for dt in self.basket_ids:
                if data =='':
                    data = str(dt.basket_no)
                else:
                    data = data +", "+str(dt.basket_no)
            self.basket_no=data
       
    