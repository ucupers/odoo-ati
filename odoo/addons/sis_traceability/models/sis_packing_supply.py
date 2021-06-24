from odoo import fields, models, api
from odoo.api import one
from datetime import datetime
from _datetime import timedelta

class sis_packing_supply(models.Model):
    _name       = 'sis.packing.supply'
    _description = "Pemakaian Ikan di Packing (untuk supply)"
    _order = 'productiondate desc'
    
    rel_line_supply = fields.Many2many('sis.packing.line', 'rel_supply_line',string="Relasi Line Packing Supply")
    rel_unpack_supply = fields.Many2many('sis.unpacking.defrost.loin', 'rel_supply_unpack',string="Relasi Supply Unpacking")
    rel_item = fields.Many2many('sis.packing.supply.material', 'rel_supply_item', string="Relasi Supply Material")
    rel_pre_supply = fields.Many2many('sis.pre.cleaning', 'rel_supply_pre', string="Relasi Supply Pre Cleaning", domain ="[('productiondate','=',materialdate), ('location','=',location)]")
    rel_product_supply = fields.Many2one('sis.master.product', string="Jenis Produk")
    basket_id = fields.One2many('sis.packing.supply.basket', 'rel_supply', string='Basket ID')
    rel_supply_jenisikan = fields.Many2many('sis.packing.supply.jenisikan', 'rel_jenisikan', string="Relasi Jenis Ikan Supply")
    
    line_cl = fields.Char(string="Line Cleaning")
    productiondate  = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now)
    materialdate = fields.Date(string="Tgl Produksi", compute="_get_materialdate", store=True)
    location = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True) 
    shift = fields.Selection([(1, 'I'), (2, 'II'), (3, 'III')], string='Shift', required=True) 
    jam_cl = fields.Float(string="Jam Cleaning")
    jam_packing = fields.Float(string="Jam Packing")
    jam_cl_real = fields.Char(string="Jam Cleaning Real", compute="_get_jamcl", store=True)
    jam_packing_real = fields.Char(string="Jam Packing Real", compute="_get_jampack", store=True)
    item = fields.Char(string="Item", compute="_get_item", store=True)
    kindoffish = fields.Selection([('SJ','SJ'),('YF','YF'),('YFB','YFB'),('AC','AC'), ('TG', 'TG')], string="Jenis Ikan")
    kindoffish2 = fields.Char('Jenis Ikan', compute="_get_jenisikan", store=True)
    status = fields.Selection([('CC','CC'),('NCC','NCC'),('H2','H2'), ('H1', 'H1')],string="status")
    material = fields.Char(string="Material", compute="_get_material", store=True)
    basket_no = fields.Char(string="No Basket")
    for_line = fields.Integer(string="Untuk Line")
    qty_box = fields.Integer(string="Jumlah Tray/Box")
    qty_kg = fields.Integer(string="Quantity Per Tray/Box", default=8)
    total_kg = fields.Integer(string="Jumlah Total KG", compute="_get_total_kg", store=True)
    kind_of_product = fields.Char(string="Jenis Produk", compute="_get_produk", store=True)
    remark = fields.Char(string="Remark")
    status_fish = fields.Selection([('RM', 'RM'), ('FZ', 'FZ')], string="Status Ikan", default="RM")
    status_xray = fields.Boolean(string="X-Ray")
    pic = fields.Selection([('yani','Yani'),('riana','Riana')], string='PIC', track_visibility="onchange", default="yani")
    id_sup = fields.Integer('ID Sup', compute='_get_id')
    status_simpanan = fields.Boolean(string="Simpanan", compute='_get_simp', store=True)
    
    
    @api.one
    @api.depends('materialdate')
    def _get_simp(self):
        if self.materialdate and self.productiondate:
            if self.materialdate != self.productiondate:
                self.status_simpanan=True
    
    @api.one
    @api.depends('productiondate')
    def _get_materialdate(self):
        if self.productiondate:
            self.materialdate=self.productiondate
            
    def _get_id(self):
        if self.id:
            self.id_sup=self.id
    
    
    @api.one
    @api.depends('rel_supply_jenisikan')
    def _get_jenisikan(self):
        ikan =''
        if self.status_fish=='RM':
            if self.rel_supply_jenisikan:
                for data in self.rel_supply_jenisikan:
                    ikan = ikan+' '+data.jenis_ikan
                self.kindoffish2=ikan
            
                
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
            
    @api.onchange('rel_unpack_supply')
    def _get_jam_cl(self):
        if self.status_fish=='FZ':
            if self.rel_unpack_supply:
                for data in self.rel_unpack_supply:
                    jam=data.jam_bongkar
                    break
                self.jam_cl=jam
            
    @api.onchange('productiondate')
    def _get_shift(self):
        if self.productiondate:
            date = datetime.now()+ timedelta(hours = 7) 
            day = date.weekday() 
            hour = date.time().hour
            minute = date.time().minute
            time = float('%s.%s' % (hour, minute))
            
            if day >=0 and day <= 3:
                if time > 6.00 and time < 13.00:
                    self.shift=1
                elif time >= 13.00 and time < 21.30:
                    self.shift=2
                elif time >= 21.30 and time <6.00:
                    self.shift=3 
            else:
                self.shift=1  

    @api.onchange('rel_line_supply')
    def filter_produk(self):
        domain = []
        domain = [('id', 'in', self.produk_search_to_list())]
        return {'domain':{'rel_product_supply':domain}}
    
    def produk_search_to_list(self):
        tmp_list = list()
#         len_rel_line = len(self.rel_line_pack)
        followers = self.env['sis.master.product'].search([('rel_line_material', 'in', [id.id for id in self.rel_line_supply])])
        
        for follower in followers:
            tmp_list.append(follower.id)
            
        return tmp_list
    
    def xrayfunc(self):
        rec=self.env['sis.packing'].search([('productiondate','=',self.productiondate), ('rel_product','=',self.rel_product_supply.id), ('rel_line_pack', 'in', [id.id for id in self.rel_line_supply])])
        if len(rec)==0:
            vals_header = {'productiondate':self.productiondate, 'rel_product':self.rel_product_supply.id, 'rel_line_pack': [(6, 0, self.rel_line_supply.ids)], 'shift':self.shift, 'status_xray':self.status_xray}
            create_header = self.env['sis.packing']
            create_header.create(vals_header)
            
        rec2=self.env['sis.packing'].search([('productiondate','=',self.productiondate), ('rel_product','=',self.rel_product_supply.id), ('rel_line_pack', 'in', [id.id for id in self.rel_line_supply])])
        if self.status_fish=='RM':
            vals_detail = {'jam_cl':self.jam_cl, 'jam_packing':self.jam_packing, 'rel_header':rec2.id, 'line_group_cl':self.line_cl, 'rel_pre': [(6, 0, self.rel_pre_supply.ids)],'remark':self.remark}
            create_detail = self.env['sis.packing.detail']
            create_detail.create(vals_detail)
        elif self.status_fish=='FZ':
            vals_detail = {'jam_cl':self.jam_cl, 'jam_packing':self.jam_packing, 'rel_header':rec2.id, 'line_group_cl':self.line_cl, 'rel_pack_unpack': [(6, 0, self.rel_unpack_supply.ids)], 'kode_loin':self.material, 'remark':self.remark}
            create_detail = self.env['sis.packing.detail']
            create_detail.create(vals_detail)
        
        
    @api.one
    @api.depends('qty_box', 'qty_kg')
    def _get_total_kg(self):
        self.total_kg = self.qty_box*self.qty_kg
    
    @api.one
    @api.depends('rel_item')
    def _get_item(self):
        if self.rel_item:
            xitem = ""
            for data in self.rel_item:
                if xitem=="":
                    xitem = data.item
                else:
                    xitem = xitem+" + "+data.item
            self.item = xitem
    
    @api.one
    @api.depends('item', 'kindoffish2', 'status', 'rel_unpack_supply')
    def _get_material(self):
        if self.status_fish == 'RM':
            if self.item and self.kindoffish2 and self.status:
                self.material = self.item+" "+self.kindoffish2+" "+self.status
            elif self.item and self.kindoffish2:
                self.material = self.item+" "+self.kindoffish2
            elif self.item and self.status:
                self.material = self.item+" "+self.status
            elif self.kindoffish2 and self.status:
                self.material = self.kindoffish2+" "+self.status
            elif self.kindoffish2:
                self.material = self.kindoffish2
            elif self.status:
                self.material = self.status
            elif self.item:
                self.material = self.item
        elif self.status_fish=='FZ':
            if self.rel_unpack_supply:
                xkode=""
                for xdetail in self.rel_unpack_supply:
                    if xdetail.kode_loin:
                        if xkode=="":
                            xkode=xdetail.kode_loin
                            temp = xdetail.kode_loin
                        elif temp!=xdetail.kode_loin:
                            xkode=xkode+", "+xdetail.kode_loin
                            temp = xdetail.kode_loin
                self.material=xkode
    
#     @api.onchange('productiondate', 'rel_supply_jenisikan')
#     def filter_basket(self):
#         domain = []
#         domain.append(('productiondate','=',self.productiondate))
#         domain.append(('location','=',self.location))
#         return {'domain':{'rel_pre_supply':domain}}
        
    @api.onchange('productiondate', 'status_xray')
    def filter_basket_loin(self):
        domain = []
        if self.status_xray==True:
            domain.append(('productiondate','=',self.materialdate))
            domain.append(('location','=',self.location))
            domain.append(('kode_loin','=like', 'L%'))
            return {'domain':{'rel_unpack_supply':domain}}
        else:
            domain.append(('productiondate','=',self.materialdate))
            domain.append(('location','=',self.location))
            domain.append(('kode_loin','=like', 'S%'))
            return {'domain':{'rel_unpack_supply':domain}}
    
    @api.depends('rel_product_supply')
    def _get_produk(self):
        if self.rel_product_supply:
            self.kind_of_product=self.rel_product_supply.description
            
    @api.multi
    def my_func(self):
        sqll ='delete from sis_packing_supply_basket where rel_supply='+str(self.id)+''        
        self.env.cr.execute(sqll)           
        if self.rel_pre_supply:
            for data in self.rel_pre_supply:
                vals = {'basket_no': data.basket_no, 'rel_supply': self.id, 'material': self.material, 'productiondate':self.productiondate, 'location':self.location}
                other_object = self.env['sis.packing.supply.basket']                
                other_object.create(vals)
        elif self.rel_unpack_supply:
            for data in self.rel_unpack_supply:
                vals = {'basket_no': data.no_urut_kereta, 'rel_supply': self.id, 'material': self.material, 'productiondate':self.productiondate, 'location':self.location}                
                other_object = self.env['sis.packing.supply.basket']
                other_object.create(vals)
                  
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        res = super(sis_packing_supply, self).create(vals)
        if vals['status_xray']:
            res.xrayfunc()
        res.my_func()
        return res
    
    @api.multi
    def write(self, vals):               
        models.Model.write(self, vals)
        self.my_func()
    
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
            cSQL1="delete from sis_packing_supply_basket where rel_supply="+str(me_id.id)+""
            cSQL2="delete from materialdate_sup_wizard where sup_id="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
            self.env.cr.execute(cSQL2)           
                
            return super(sis_packing_supply, self).unlink()
    
        
    def simpanan(self):
        return {
            'type':'ir.actions.act_window',
            'name':'Material Date Wizard',
            'res_model':'materialdate.sup.wizard',
            'src_model':'sis.packing.supply',
            'view_mode':'form',
            'view_type':'form',
            'target':'new',
            'context':{
                'default_sup_id':self.id, 'default_old_date':self.productiondate
                }        
        }   
            
class sis_packing_supply_basket(models.Model):
    _name       = 'sis.packing.supply.basket'
    _description = "Basket di Pemakaian Ikan di Packing (untuk supply)"
    _rec_name = 'basket_no'

    rel_supply = fields.Many2one('sis.packing.supply', string="Relasi Supply")
    rel_packing_detail_sup = fields.Many2many('sis.packing.detail', 'rel_supply',string="Relasi Basket Supply Packing")
    
    material = fields.Char(string="Material")
    basket_no = fields.Char(string="No Basket")
    productiondate  = fields.Date(string='Tanggal Produksi')
    location  = fields.Char(string='Location')

    
#           
#     @api.one
#     @api.depends('rel_supply')
#     def _get_productiondate(self):
#         if self.rel_supply:
#             self.productiondate = self.rel_supply.productiondate


class MaterialdateSupWizard(models.TransientModel):
    _name = 'materialdate.sup.wizard'
    _description = 'Material Date Supply Wizard'
    
    new_date = fields.Date('Tanggal Produksi Bahan', required=True)
    old_date = fields.Date('Tanggal Produksi')
    sup_id = fields.Many2one('sis.packing.supply', string='Packing Supply', required=True)
    
    def change_date(self):
        for rec in self:
            rec.sup_id.materialdate = rec.new_date
            
class sis_packing_supply_material(models.Model):
    _name = 'sis.packing.supply.material'
    _description = 'Material Packing Supply'
    _rec_name = 'item'
    
    rel_supply_item = fields.Many2many('sis.packing.supply', 'rel_item', string="Relasi Material Supply")
    item = fields.Char(string="Item")
    
class sis_packing_supply_jenisikan(models.Model):
    _name = 'sis.packing.supply.jenisikan'
    _description = 'Jenis Ikan Packing Supply'
    _rec_name = 'jenis_ikan'
    
    jenis_ikan = fields.Char(string="Jenis Ikan")
    