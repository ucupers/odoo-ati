from odoo import fields, models, api, tools
from odoo.exceptions import UserError

class sis_retort_loading_basket(models.Model):
    _name       = 'sis.retort.loading.basket'
    _description = "Retort - Muat Produk ke dalam Basket"
    _rec_name = 'produk'
    _order = 'productiondate desc, line'
    
    detail_ids = fields.One2many('sis.retort.loading.basket.detail', 'header_id', string='Relasi detail')
    packing_id = fields.Many2one('sis.packing', string='Relasi Packing', domain ="[('productiondate','=',productiondate),('location','=',location)]")
    line_id = fields.Many2one('sis.packing.line', string='Line ID')
    pro_id = fields.Many2one('sis.pro.hd', string="ID Loading Basket")

    
    productiondate = fields.Date('Tanggal Produksi', default=lambda self:fields.Datetime.now())
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    produk = fields.Char('Nama Produk', compute='_get_product', store=True)
    line = fields.Integer('Line', compute='_get_line', store=True)
    status_take_retort = fields.Boolean('Selesai', default=False)
    pcs_layer = fields.Integer('Pcs per layer/base')
    ttl_rjct = fields.Integer('Total Reject', compute='_sum_reject', store=True)
    
    @api.one
    @api.depends('detail_ids')
    def _sum_reject(self):
        if self.detail_ids:
            temp = 0
            for obj in self.detail_ids:
                temp = temp + obj.rjct
                
            self.ttl_rjct = temp
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        res = super(sis_retort_loading_basket, self).create(vals)
        res.new_detail()
        return res
    
    def new_detail(self):
        vals_header = {'header_id':self.id, 'basket_no':1, 'jam_mulai':0, 'jam_selesai':0, 'basket_line':str(self.line)+'.1'}
        create_header = self.env['sis.retort.loading.basket.detail']
        create_header.create(vals_header)
    
    @api.depends('packing_id')
    def _get_product(self):
        if self.packing_id:
            self.produk = self.packing_id.kind_of_product
    
    @api.one
    @api.depends('line_id')
    def _get_line(self):
        if self.line_id:
            self.line = self.line_id.line
    
#     @api.onchange('productiondate')
#     def filter_packing(self):
#         domain = []
#         domain.append(('productiondate','=',self.productiondate))
#         domain.append(('location','=',self.location))
#         return {'domain':{'packing_id':domain}}
                      
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
                
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_retort_loading_basket_detail where header_id="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
                
            return super(sis_retort_loading_basket, self).unlink()
           
class sis_retort_loading_basket_detail(models.Model):
    _name = 'sis.retort.loading.basket.detail'
    _description = "Retort - Muat Produk ke dalam Basket - Detail"
    _rec_name = 'basket_line'
    _order = 'basket_no'

    header_id = fields.Many2one('sis.retort.loading.basket', string='Relasi Header')
    basket_retort_ids = fields.Many2many('sis.retort.detail', 'basket_idss' ,string='Relasi Loading Basket dan Retort Detail')
    wh_ids = fields.One2many('sis.wh.bongkar.produk.detail', 'retort_loading_id', string='relasi ke wh')
    
    produk = fields.Char('Nama Produk', compute='_get_product', store=True)
    basket_no = fields.Integer('Nomor Basket', required=True)
    jam_mulai = fields.Float('Jam Mulai', required=True)
    jam_mulai_real = fields.Char('Jam Mulai Real', compute='_get_mulai', store=True)
    jam_selesai = fields.Float('Jam Selesai')
    jam_selesai_real = fields.Char('Jam Selesai Real', compute='_get_selesai', store=True)
    basket_line = fields.Char('Basket dg ket Line', compute='_get_basket_line', store=True)
    status_button_new = fields.Boolean('Status button new')
    productiondate = fields.Date('Tanggal Produksi', compute='_get_productiondate', store=True)
    location = fields.Char('Lokasi', compute='_get_location', store=True)
    stts_tk_rt = fields.Boolean('Status Take Retort', default=False)
    jml_layer = fields.Integer('Jumlah (Layer)')
    jml_pcs = fields.Integer('Jumlah sisa pcs')
    rjct = fields.Integer('Reject')
    rjct_remark = fields.Char('Ket Reject')
    total_pcs = fields.Integer('Total pcs', compute='_get_total_pcs', store=True)
    remark = fields.Char('Remark')
    
    @api.one
    @api.depends('jml_layer','jml_pcs', 'header_id.pcs_layer')
    def _get_total_pcs(self):
        if self.header_id.pcs_layer and self.jml_layer:
            if self.jml_pcs==0:
                self.total_pcs=self.header_id.pcs_layer*self.jml_layer
            else:
                self.total_pcs=(self.header_id.pcs_layer*self.jml_layer)+self.jml_pcs
    
    @api.one
    @api.depends('header_id')
    def _get_product(self):
        if self.header_id.produk:
            self.produk = self.header_id.produk
            
    @api.one
    @api.depends('header_id')
    def _get_location(self):
        if self.header_id.location:
            self.location = self.header_id.location
    
    @api.one
    @api.depends('header_id')
    def _get_productiondate(self):
        if self.header_id.productiondate:
            self.productiondate = self.header_id.productiondate

    @api.one
    @api.depends('jam_mulai')
    def _get_mulai(self):
        if self.jam_mulai:
            self.jam_mulai_real= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_mulai) * 60, 60))
            
    @api.one
    @api.depends('jam_selesai')
    def _get_selesai(self):
        if self.jam_selesai:
            self.jam_selesai_real= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_selesai) * 60, 60))
            
    @api.one
    @api.depends('header_id', 'basket_no')
    def _get_basket_line(self):
        if self.header_id:
            self.basket_line = str(self.header_id.line)+"."+str(self.basket_no)
    
    def copydata(self):
        data = {'basket_no':self.basket_no+1, 'jam_mulai':self.jam_selesai, 'header_id':self.header_id.id}
        create_data = self.env['sis.retort.loading.basket.detail']
        create_data.create(data)
        self.status_button_new=True
        
    @api.multi
    def unlink(self):
        if self.status_button_new==False:
            qsql="SELECT id FROM sis_retort_loading_basket_detail where status_button_new=True and header_id="+str(self.header_id.id)+" ORDER BY basket_no DESC LIMIT 1"
                  
            self.env.cr.execute(qsql)
            qsqln=self.env.cr.fetchall()
            
            if qsqln:
                for data in qsqln:
                    (xid,)=data
                datanya = self.env['sis.retort.loading.basket.detail'].search([('id', '=', xid)])
                datanya.status_button_new=False
                return models.Model.unlink(self)
            else:
                data = {'basket_no':1, 'jam_mulai':0, 'jam_selesai':0}
                self.write(data)
        else:
            return models.Model.unlink(self)

    def cari_big(self):
        data= False
        for datas in self.detail_ids:
            if data==False:
                data=datas
            elif data.basket_no > datas.basket_no:
                data=datas
        print (datas.basket_no)
       

    @api.onchange('basket_no')
    def _basket_get(self):
        if self.basket_no:
            print(self.basket_no)
            detailid = []
            i=0
            for data in self.header_id.detail_ids:
                if isinstance(data.id, int):
                    detailid.append(data)
                    print(detailid[i].basket_no)
                    i=i+1
                    
            print(detailid)
    
    @api.model
    def default_get(self, fields_list):
        print(fields_list)
        return models.Model.default_get(self, fields_list)
#             basket = False
#             for datas  in detailid:
#                 hem = self.env['sis.retort.loading.basket.detail'].search([('id','=', datas)])
#                 if hem.status_button_new==False:
#                     hem.status_button_new==True
#                 if basket==False:
#                     basket=hem
#                 else:
#                     if hem.basket_no > basket.basket_no:
#                         basket=hem
#             basket.status_button_new=False

class sis_pro_hd(models.Model):
    _name = 'sis.pro.hd'
    _description = "Prod HD"
    
    prod_ids = fields.One2many('sis.retort.loading.basket', 'pro_id', string="ID Loading Basket")
#     retort_detail_id = fields.One2many('sis.retort.detail', 'pro_re_id', string='Retort Detail')
    retort_detail_id = fields.Integer(string='Retort Detail')
        
    @api.multi
    def write(self, vals):
        models.Model.write(self, vals)
        data = self.env['sis.retort.loading.basket'].search([('status_take_retort','=',True),('pro_id','=',self.id)])
        rt = self.env['sis.retort.detail'].search([('id','=',self.retort_detail_id)])
        rt.produk_ids = data
        print(rt.produk_ids)
        if data:
            for datas in data:
                datas.status_take_retort=False
                
        return {
            'type': 'ir.actions.client', 
            'tag': 'reload'
            }
        
class sis_retort_cek_basket(models.Model):
    _name = 'sis.retort.cek.basket'
    _description = 'Data basket retort yang belum sterilisasi'
    _auto = False
    _order = 'productiondate desc, produk'
    
    productiondate = fields.Date('Tanggal produksi')
    location = fields.Char('Lokasi')
    produk = fields.Char('Nama Produk')
    basket_line = fields.Char('Line - Basket')

     
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_retort_cek_basket as (
        SELECT DISTINCT
        row_number() OVER () as id, 
        lo.productiondate, lo.location, lo.produk, lo.basket_line from sis_retort_loading_basket_detail as lo
        left join basket_retort_ids as rel on rel.sis_retort_loading_basket_detail_id=lo.id
        where rel.sis_retort_loading_basket_detail_id is null and lo.productiondate is not null and lo.produk is not null and lo.basket_line is not null
        and lo.productiondate>='2020-12-01')"""
          
        tools.sql.drop_view_if_exists(self._cr, 'sis_retort_cek_basket')
        self._cr.execute(cSQL)   
        
class tran_tes(models.TransientModel):
    _name = 'tran.tes'
    _description = "Transient Tes"
    
    productiondate = fields.Date('Tanggal Produksi')
    
class tran_tes_line(models.TransientModel):
    _name = 'tran.tes.line'
    _description = "Transient Tes Line"
    
    productiondate = fields.Date('Tanggal Produksi')
    produk = fields.Char('Nama Produk')
    status_take_retort = fields.Boolean('Status', default='False')
    
    