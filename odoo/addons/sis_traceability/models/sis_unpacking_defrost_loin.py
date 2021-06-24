from odoo import models, fields, api, tools
#from datetime import datetime

class defrost_loin_unpacking(models.Model):
    _name  ='sis.unpacking.defrost.loin'
    _rec_name ='no_urut_kereta'
    _order = 'productiondate desc, no_urut_kereta'
    
    rel_supply_unpack = fields.Many2many('sis.packing.supply','rel_unpack_supply', string="Relasi Supply Unpacking")
    rel_cleaning_unpack = fields.Many2one('sis.cleaning', string="Relasi Frozen Loin Unpacking", domain="[('tgl_produksi','=', materialdate),('location','=',location)]")
    rel_unpack_pack = fields.Many2many('sis.packing.detail', 'rel_pack_unpack', string="Relasi Packing Loin Unpacking")
    line_ids = fields.Many2many('sis.packing.line', string='Relasi Unpacking Line')
    
    
    productiondate = fields.Date(string="Tanggal Produksi", required=True, default=fields.Datetime.now)
    location = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True)
    kode_loin = fields.Char(string="Kode Loin/Shredded", compute="_get_kode_loin", store=True)
    no_urut_kereta = fields.Char(string="No Urut Kereta Packing", compute='_get_no_urut_kereta', store=True)
    no_urut = fields.Integer(string="No Urut", required=True)
    jml_kantong = fields.Integer(string="Jumlah Kantong", required=True)
    status = fields.Selection([('OK', 'OK')], string="Status", default='OK')
    jam_bongkar = fields.Float(string="Waktu Bongkar Kantong", required=True)
    jam_bongkar_real = fields.Char(string="Waktu Bongkar Kantong Real", compute="_get_jambongkar", store=True)
    line_packing = fields.Char(string="Line packing", compute="_get_line", store=True)
    remark = fields.Char(string="Remark", default=" ")
    materialdate = fields.Date(string="Tgl Produksi", compute="_get_materialdate", store=True)
    
    @api.one
    @api.depends('line_ids')
    def _get_line(self):
        if self.line_ids:
            temp = ""
            for data in self.line_ids:
                if temp=="":
                    temp = str(data.line)
                else:
                    temp = temp+', '+str(data.line)
    
    @api.multi
    @api.returns('self', lambda value:value.id)
    def copy(self, default=None):
        default.update({
            'jam_bongkar'   : 0,
            })
        print('copy data')
        print(self.id)
        return models.Model.copy(self, default=default)
    
    @api.one
    @api.depends('productiondate')
    def _get_materialdate(self):
        if self.productiondate:
            self.materialdate=self.productiondate
    
    def simpanan(self):
        return {
            'type':'ir.actions.act_window',
            'name':'Material Date Wizard',
            'res_model':'materialdate.unpack.wizard',
            'src_model':'sis.unpacking.defrost.loin',
            'view_mode':'form',
            'view_type':'form',
            'target':'new',
            'context':{
                'default_unpack_id':self.id, 'default_old_date':self.productiondate
                }        
        }  
               
    @api.one
    @api.depends('jam_bongkar')
    def _get_jambongkar(self):
        if self.jam_bongkar:
            self.jam_bongkar_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.jam_bongkar) * 60, 60))
    
    @api.one
    @api.depends('rel_cleaning_unpack')
    def _get_kode_loin(self):
        if self.rel_cleaning_unpack:
            self.kode_loin = self.rel_cleaning_unpack.kode_loin
    
    @api.multi
    def my_func(self):
        self.ensure_one()            
        koma=0
        x=self.line_cleaning
        for n in range(len(x)):
            if x[n:n+1]==",":
                data=x[koma:n].strip()
                print(data+" if")
                vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id, 'productiondate': self.productiondate}                
                koma=n+1
                other_object = self.env['sis.line.cleaning.pre']
                other_object.create(vals)
            else:
                if n+1==len(x):
                    data=x[koma:koma+(len(x)-koma)].strip()
                    print(data+" else")
                    vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id, 'productiondate': self.productiondate} 
                    other_object = self.env['sis.line.cleaning.pre']
                    other_object.create(vals) 
    @api.one
    @api.depends('rel_cleaning_unpack', 'no_urut')
    def _get_no_urut_kereta(self):
        if self.rel_cleaning_unpack and self.no_urut:
            self.no_urut_kereta = str(self.rel_cleaning_unpack.no_urut_rak_defrost)+"."+str(self.rel_cleaning_unpack.no_tengah)+"."+str(self.no_urut)
    
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
            cSQL1="delete from materialdate_unpack_wizard where unpack_id="+str(me_id.id)+""            
            self.env.cr.execute(cSQL1)   
            return models.Model.unlink(self)
        
#     @api.multi
#     def unlink(self):
#         for me_id in self :
#             cSQL1="delete from materialdate_unpack_wizard where unpack_id="+str(me_id.id)+""            
#             self.env.cr.execute(cSQL1)                           
#             return super(defrost_loin_unpacking, self).unlink()
           
class MaterialdateUnpackWizard(models.TransientModel):
    _name = 'materialdate.unpack.wizard'
    _description = 'Material Date Unpcaking Defrost Loin Wizard'
    
    new_date = fields.Date('Tanggal Produksi Bahan', required=True)
    old_date = fields.Date('Tanggal Produksi')
    unpack_id = fields.Many2one('sis.unpacking.defrost.loin', string='Unpacking Defrost Loin', required=True)
    
    def change_date_unpack(self):
        for rec in self:
            rec.unpack_id.materialdate = rec.new_date    

class sis_unpack_view_alert(models.Model):
    _name = 'sis.unpack.view.alert'
    _description = 'Data cleaning yang belum diinput'
    _auto = False
    _order = 'tgl_produksi desc'
    
    tgl_produksi = fields.Date('Tanggal Produksi')
    tgl_bongkar = fields.Date('Tanggal Bongkar')
    location = fields.Char('Lokasi')
    r_name = fields.Char('No Urut Bongkar')
    kode_loin = fields.Char('Kode Loin')
    lot = fields.Char('Lot')
    create_date = fields.Datetime('Create Date')
    
    
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_unpack_view_alert as (
        SELECT DISTINCT
        row_number() OVER () as id, 
        cl.tgl_produksi, cl.tgl_bongkar, cl.location, cl.r_name, cl.kode_loin, cl.lot, cl.create_date from sis_cleaning as cl
        left join sis_unpacking_defrost_loin unp on cl.id=unp.rel_cleaning_unpack
        where cl.tgl_produksi>='2020-11-01' and unp.id is null
        order by cl.tgl_produksi desc)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_unpack_view_alert')
        self._cr.execute(cSQL)
            
            
            