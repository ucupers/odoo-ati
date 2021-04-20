from odoo import models, fields, api
from odoo.exceptions import UserError

class sis_packing(models.Model):
    _name = 'sis.packing'
    _rec_name = 'kind_of_product'
    _order = 'productiondate desc'
    
    retort_ids = fields.One2many('sis.retort.loading.basket', 'packing_id', string='Relasi Packing Retort')
    rel_line_pack = fields.Many2many('sis.packing.line', 'rel_pack_line', string="Relasi Line Packing")
    rel_product = fields.Many2one('sis.master.product', string="Jenis Produk")
    packing_detail = fields.One2many('sis.packing.detail', 'rel_header', string="Relasi Packing Detail")
    ecpouch_hd_ids = fields.One2many('sis.ec.pouch.header', 'packing_hd_id', string='Product Pouch ID')
    
    productiondate = fields.Date(string="Tgl Produksi", required=True)
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    kind_of_product = fields.Char(string="Jenis Produk", compute="_get_produk", store=True)
    line = fields.Char(string="Line", compute="_get_line", store=True)
    status_xray = fields.Boolean(string="X-Ray")
    shift = fields.Selection([(1, 'I'), (2, 'II'), (3, 'III')], string="Shift")
    pic = fields.Selection([('yani','Yani'),('riana','Riana')], string='PIC', track_visibility="onchange", default="yani")
    
    @api.onchange('rel_line_pack')
    def filter_produk(self):
        domain = []
        domain = [('id', 'in', self.produk_search_to_list())]
        return {'domain':{'rel_product':domain}}
    
    def produk_search_to_list(self):
        tmp_list = list()
        len_rel_line = len(self.rel_line_pack)
        datas = self.env['sis.master.product'].search([('rel_line_material', 'in', [id.id for id in self.rel_line_pack])])
        
        for data in datas:
            lenfol=0
            for idx in self.rel_line_pack:
                for idd in data.rel_line_material:
                    if idx.id == idd.id:
                        lenfol=lenfol+1
            lenfolreal = len(data.rel_line_material)
            if lenfol == len_rel_line:
                tmp_list.append(data.id)
            
        return tmp_list
    
    @api.one
    @api.depends("rel_line_pack")
    def _get_line(self):
        if self.rel_line_pack:
            xline=""
            for xdetail in self.rel_line_pack:
                if xdetail.line:
                    if xline=="":
                        xline=str(xdetail.line)
                    else:                       
                        xline=xline+", "+str(xdetail.line)
            self.line = xline
    
    @api.depends('rel_product')
    def _get_produk(self):
        if self.rel_product:
            self.kind_of_product=self.rel_product.description
          
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
            cSQL1="delete from sis_packing_detail where rel_header="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
                
            return super(sis_packing, self).unlink()
    
    
        
class sis_packing_detail(models.Model):
    _name = 'sis.packing.detail'
    
    rel_header = fields.Many2one('sis.packing', string="Relasi Packing Header")
    rel_pre = fields.Many2many('sis.pre.cleaning', 'pack_pre_rel', 'pack_id', 'pre_id', string="Relasi Packing Pre Cleaning", domain ="[('productiondate','=',materialdate), ('location','=',location)]")
    rel_cl = fields.Many2many('sis.cleaning', 'rel_packing_detail_cl', string="Relasi Packing Frozen Loin")
    rel_pack_unpack = fields.Many2many('sis.unpacking.defrost.loin','rel_unpack_pack', string="Relasi Packing Loin Unpacking", domain ="[('productiondate','=',materialdate), ('location','=',location)]")
    rel_supply = fields.Many2many('sis.packing.supply.basket', 'rel_packing_detail_sup', string="Relasi Packing Supply", domain ="[('productiondate','=',materialdate), ('location','=',location)]")
    item = fields.Many2many('sis.packing.supply.material', 'packing_material', string='Packing Material')
    jenisikan = fields.Many2many('sis.packing.supply.jenisikan', 'pack_jenisikan', string="Relasi Jenis Ikan Packing")
    
    line_group_cl = fields.Char(string="Line/Group Cleaning")
    jam_cl = fields.Float(string="Jam Cleaning")
    jam_packing = fields.Float(string="Jam Packing")
    jam_cl_real = fields.Char(string="Jam Cleaning Real", compute="_get_jamcl", store=True)
    jam_packing_real = fields.Char(string="Jam Packing Real", compute="_get_jampack", store=True)
    loin = fields.Char(string="Loin", compute="_list_basket_loin", store=True)
    kode_loin = fields.Char(string="Kode Loin", compute="_get_kode_loin", store=True)
    fish = fields.Char(string="Fish", compute="_list_basket_fish", store=True)
    shreded = fields.Char(string="Shreded", compute="_list_basket_shreded", store=True)
    jumlah_ikan = fields.Integer(string="Jumlah Tray Fish")
    jumlah = fields.Integer(string="Jumlah Tray Loin")
    total = fields.Integer(string="Total", compute="_get_total", store=True)
    remark = fields.Char(string="Remark")
    productiondate = fields.Date(string="Tgl Produksi", compute="_get_productiondate", store=True)
    materialdate = fields.Date(string="Tgl Produksi", compute="_get_materialdate", store=True)
    itemss = fields.Char('Material', compute='_get_material', store=True)
    jenis_ikan = fields.Char('Jenis Ikan', compute='_get_ikan', store=True)
    location = fields.Char(string="Location", compute="_get_loc")
    
    def simpanan_pack(self):
        return {
            'type':'ir.actions.act_window',
            'name':'Material Date Wizard',
            'res_model':'materialdate.pack.wizard',
            'src_model':'sis.packing.detail',
            'view_mode':'form',
            'view_type':'form',
            'target':'new',
            'context':{
                'default_pack_id':self.id, 'default_old_date':self.productiondate
                }        
        }
        
    @api.one
    @api.depends('productiondate')
    def _get_materialdate(self):
        if self.productiondate:
            self.materialdate=self.productiondate
            
    @api.one
    @api.depends('item')
    def _get_material(self):
        teks = ''
        if self.item:
            for data in self.item:
                if teks=='':
                    teks=data.item
                else:
                    teks=teks+' + '+data.item
            self.itemss=teks
            
    @api.one
    @api.depends('jenisikan')
    def _get_ikan(self):
        teks = ''
        if self.jenisikan:
            for data in self.jenisikan:
                if teks=='':
                    teks=data.jenis_ikan
                else:
                    teks=teks+' + '+data.jenis_ikan
            self.jenis_ikan=teks
        
                     
    @api.one
    @api.depends('jam_packing')
    def _get_jampack(self):
        if self.jam_packing:
            self.jam_packing_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_packing) * 60, 60))
            
    @api.one
    @api.depends('jam_cl')
    def _get_jamcl(self):
        if self.jam_cl:
            self.jam_cl_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_cl) * 60, 60))
            
    @api.one
    @api.depends('rel_header.productiondate')
    def _get_productiondate(self):
        if self.rel_header:
            self.productiondate = self.rel_header.productiondate
            
    @api.one
    @api.depends('rel_header.location')
    def _get_loc(self):
        if self.rel_header:
            self.location = self.rel_header.location
             
    @api.one
    @api.depends('rel_pack_unpack')
    def _get_kode_loin(self):
        if self.rel_pack_unpack:
            xkode=""
            for xdetail in self.rel_pack_unpack:
                if xdetail.kode_loin:
                    if xkode=="":
                        xkode=xdetail.kode_loin
                        temp = xdetail.kode_loin
                    elif temp!=xdetail.kode_loin:
                        xkode=xkode+", "+xdetail.kode_loin
                        temp = xdetail.kode_loin
            self.kode_loin=xkode
     
     
    @api.one
    @api.depends('rel_pre')
    def _list_basket_fish(self):
        xbasket=""
        for xdetail in self.rel_pre:
            if xdetail.basket_no:
                if xbasket=="":
                    xbasket=str(xdetail.basket_no)
                else:
                    xbasket=xbasket+", "+str(xdetail.basket_no)
        self.fish=xbasket
        
    @api.one
    @api.depends('rel_pack_unpack')
    def _list_basket_loin(self):
        xbasket=""
        for xdetail in self.rel_pack_unpack:
            if xdetail.no_urut_kereta:
                if xbasket=="":
                    xbasket=str(xdetail.no_urut_kereta)
                else:
                    xbasket=xbasket+", "+str(xdetail.no_urut_kereta)
        self.loin=xbasket
     
    @api.one
    @api.depends('rel_supply')
    def _list_basket_shreded(self):
        xbasket=""
        for xdetail in self.rel_supply:
            if xdetail.basket_no:
                if xbasket=="":
                    xbasket=str(xdetail.basket_no)
                else:
                    xbasket=xbasket+", "+str(xdetail.basket_no)
        self.shreded=xbasket
         
    @api.one    
    @api.depends('jumlah', 'jumlah_ikan')
    def _get_total(self):
        if self.jumlah and self.jumlah_ikan:
            self.total=self.jumlah_ikan*self.jumlah
            
    
    def produk_search_to_list(self):
        tmp_list = list()
        len_rel_line = len(self.rel_header.rel_line_pack)
        followers = self.env['sis.unpacking.defrost.loin'].search([('line_ids', 'in', [id.id for id in self.rel_header.rel_line_pack])])
        
        for follower in followers:
            tmp_list.append(follower.id)
                 
    @api.one
    def _get_jam_cl(self):
        if self.rel_supply:
            for data in self.rel_supply:
                xjam = data.rel_supply.jam_packing
            self.jam_cl = xjam
    
class MaterialdatePackWizard(models.TransientModel):
    _name = 'materialdate.pack.wizard'
    _description = 'Material Date Wizard'
    
    new_date = fields.Date('Nama Baru', required=True)
    old_date = fields.Date('Nama Lama')
    pack_id = fields.Many2one('sis.packing.detail', string='Packing')
    
    def change_date_pack(self):
        for rec in self:
            rec.pack_id.materialdate = rec.new_date
            
class sis_packing_line(models.Model):
    _name = 'sis.packing.line'
    _rec_name = 'line'

    rel_supply_line = fields.Many2many('sis.packing.supply', 'rel_line_supply',string="Relasi Line Packing Supply")
    rel_pack_line = fields.Many2many('sis.packing', 'rel_line_pack',string="Relasi Line Packing")
    rel_material_line = fields.Many2many('sis.master.product', 'rel_line_material',string="Relasi Line Material")
    ec_pouch_hd_ids = fields.One2many('sis.ec.pouch.header', 'line_hd_id', string='Line Pouch ID')
    
    line = fields.Integer(string="Line Packing")
    