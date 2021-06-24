from odoo import fields, models, api
from odoo.exceptions import UserError



class sis_retort_header(models.Model):
    _name       = 'sis.retort.header'
    _description = "Retort - Header"
    _rec_name = 'no_retort'
    _order = 'productiondate desc, no_retort'
    
    
    retort_detail_ids = fields.One2many('sis.retort.detail', 'retort_header_id', string='Retort Detail')
    
    productiondate = fields.Date('Tanggal Produksi', default= lambda self:fields.Datetime.now())
    no_retort = fields.Integer('No Retort', required=True)
    location = fields.Char('Lokasi', compute="_get_pabrik_id", store=True) 
    siklus = fields.Integer('Siklus Increment', compute='_get_incr', store=True)
    
    @api.one
    @api.depends('retort_detail_ids')
    def _get_incr(self):
        if self.retort_detail_ids:            
            self.siklus=len(self.retort_detail_ids)
        else:
            self.siklus=0
    
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
            cSQL1="delete from sis_retort_detail where retort_header_id="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
                
            return super(sis_retort_header, self).unlink()
    
 
        
class sis_retort_detail(models.Model):
    _name = 'sis.retort.detail'
    _description = 'Retort - Detail'
    _order = 'no_siklus'
    
#     Relasi
    produk_ids = fields.Many2many('sis.retort.loading.basket', 'rel_retort_detail', 'retort_id', 'produk_id', string="Jenis Produk", domain="[('productiondate','=',productiondate),('location','=',location)]")
    
    basket_ids = fields.Many2many('sis.retort.loading.basket.detail', string='Relasi Loading Basket dan Retort Detail', domain ="[('id','in',basket_filt)]")
    basket_idss = fields.Many2many('sis.retort.loading.basket.detail', 'basket_retort_ids' ,string='Relasi Loading Basket dan Retort Detail', compute="_get_basket_ids", store=True)
    retort_header_id = fields.Many2one('sis.retort.header', string='Retort Detail')
    pro_re_id = fields.Many2one('sis.pro.hd', string='Retort Detail')
    line_ids = fields.One2many('sis.retort.line', 'retort_detail_id', string="Relasi ke Line")
    basket_filt = fields.Many2many('sis.retort.loading.basket.detail', 'rel_basket_filt', 'retort_idf', 'produk_idf', string='Basket Filter', compute="_get_basket_filt", store=True)
    
#   field
    no_siklus = fields.Integer('No Siklus')
    produk = fields.Char('Nama Produk')
    basket_no = fields.Char('No Basket')
    jml_basket = fields.Integer('Jumlah Basket')
    steam_on = fields.Float('Steam On')
    steam_off = fields.Float('Steam Off')
    jam_basket_keluar = fields.Float('Waktu Basket Keluar dari Retort')
    productiondate = fields.Date(string="Tgl Produksi", compute="_get_productiondate", store=True)
    location = fields.Char(size=4, string='Lokasi', compute="_get_location", store=True)
    
    steam_on_real = fields.Char('Steam On R', compute='_get_steam_on', store=True)
    steam_off_real = fields.Char('Steam Off R', compute='_get_steam_off', store=True)
    jam_basket_keluar_real = fields.Char('Waktu Basket Keluar dari Retort R', compute='_get_out', store=True)
            
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self, vals):
#         if vals['basket_ids'][0][2]:
#             for dt in vals['basket_ids'][0][2]:
#                 data = self.env['sis.retort.loading.basket.detail'].search([('id','=',dt)])
#                 if data.stts_tk_rt==True:
#                     raise UserError('Nomor basket sudah '+data.basket_line+' diinput!!')
#                 else:
#                     data.stts_tk_rt=True
#         return models.Model.create(self, vals)
#     
#     @api.multi
#     def unlink(self):
#         if self.basket_ids:
#             for dt in self.basket_ids:
#                 dt.stts_tk_rt=False
#         return models.Model.unlink(self)
    
#     @api.multi
#     def write(self, vals):
#         data = '({})'.format(','.join(vals.get(['basket_ids'][0][2])))
#         print(data)
#         return models.Model.write(self, vals)
    
    @api.one
    @api.depends('steam_on')
    def _get_steam_on(self):
        if self.steam_on:
            self.steam_on_real= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.steam_on) * 60, 60))
            
    @api.one
    @api.depends('steam_off')
    def _get_steam_off(self):
        if self.steam_off:
            self.steam_off_real= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.steam_off) * 60, 60))
    
            
    @api.one
    @api.depends('jam_basket_keluar')
    def _get_out(self):
        if self.jam_basket_keluar:
            self.jam_basket_keluar_real= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_basket_keluar) * 60, 60))
    
    @api.one
    @api.depends('basket_ids')
    def _get_basket_ids(self):
        if self.basket_ids:
            self.basket_idss=self.basket_ids
            
    @api.one
    @api.depends('produk_ids')
    def _get_basket_filt(self):
        if self.produk_ids:
            data_header = self.env['sis.retort.loading.basket'].search([('id', 'in', [id.id for id in self.produk_ids])])
            data_list = []
            if data_header:
                for datas in data_header:
                    for i in range(len(datas)):
                        sama = self.env['sis.retort.loading.basket.detail'].search([('header_id.produk','=like',datas[i].produk),('header_id.productiondate','=',datas[i].productiondate),('header_id.location','=',datas[i].location)])
                        if sama:
                            for samas in sama:
                                data_list.append(samas['id'])
            self.basket_filt = data_list   
    
    @api.one
    @api.depends('retort_header_id.productiondate')
    def _get_productiondate(self):
        if self.retort_header_id:
            self.productiondate = self.retort_header_id.productiondate  
              
    @api.one
    @api.depends('retort_header_id.location')
    def _get_location(self):
        if self.retort_header_id:
            self.location = self.retort_header_id.location
            
    def produk_search_to_list(self):
        tmp_list = list()
        data = self.env['sis.retort.loading.basket'].search([('productiondate', '=', self.retort_header_id.productiondate),('location', '=', self.retort_header_id.location)])
        for datas in data:
            tmp_list.append(datas.produk)
        print(tmp_list)
    
    @api.onchange('basket_ids')
    def _get_basket_total(self):
        if self.basket_ids:
            self.jml_basket = len(self.basket_ids)            
            
    @api.onchange('jml_basket')
    def _control_jml_basket(self):
        if self.jml_basket:
            if self.retort_header_id.no_retort:
                if self.retort_header_id.no_retort >= 2 and self.retort_header_id.no_retort <5:
                    if self.jml_basket > 5:
                        raise UserError('No Basket yang dimasukkan lebih dari kapasitas retort yaitu 5 basket')
                if self.retort_header_id.no_retort >= 5 and self.retort_header_id.no_retort <=11 or self.retort_header_id.no_retort==1:
                    if self.jml_basket > 8:
                        raise UserError('No Basket yang dimasukkan lebih dari kapasitas retort yaitu 8 basket')
    
    def open_produk(self):
        csql= "update sis_retort_loading_basket set pro_id=1 where productiondate='"+str(self.productiondate)+"'"
        self.env.cr.execute(csql)
        datas = self.env['sis.retort.loading.basket'].search([('id', 'in', [id.id for id in self.produk_ids])])
        if datas:
            for data in datas:
                data.status_take_retort=True
        csql2="update sis_pro_hd set retort_detail_id="+str(self.id)+" where id=1"
        self.env.cr.execute(csql2)
        
        return {
            'name'      : 'Produk',
            'res_model' : 'sis.pro.hd',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'form',
            'view_type' : 'form, tree',
            'view_id'   : self.env.ref('sis_traceability.sis_pro_hd_form').id,
            'nodestroy' : False,
            'target'    : 'new',
            'res_id'    : 1,
            'flags'     : {'action_buttons': True},
            'context'   : {'default_retort_detail_id':10},
        }
        
        
    @api.multi
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default.update({        
         'no_siklus': self.retort_header_id.siklus+1,       
         'produk': '',       
         'basket_ids': '',       
         'jml_basket': 0,       
         'steam_on': 0,        
         'steam_off': 0,        
         'jam_basket_keluar': 0,
        })
        return models.Model.copy(self, default=default)

        
class sis_retort_line(models.Model):
    _name='sis.retort.line'
    _description = 'Line retort'
    
    retort_detail_id = fields.Many2one('sis.retort.detail', string="retort detail ID")

    productiondate = fields.Date('Tanggal Produksi')
    line_basket = fields.Char('line poin basket')
    