from odoo import models, fields, api, tools
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

class pre_cleaning(models.Model):
    _name = 'sis.pre.cleaning'
    _order = "productiondate desc"    
    _rec_name   ='basket_no'
    
    rel_supply_pre= fields.Many2many('sis.packing.supply', 'rel_pre_supply', string="Relasi Supply Material")
    line_pre = fields.One2many('sis.line.cleaning.pre', 'rel_line_cleaning', string='Line Cleaning')
    rel_packing_detail = fields.Many2many('sis.packing.detail','rel_pre', string="Relasi Pre Cleaning Packing")
    basket = fields.Many2one('sis.cooker.basket', string="Cooker Label")
    
    
    pcl = fields.Integer(string="Line Pre Cleaning", required=True)
    line_cleaning = fields.Char(string="Line Cleaning", required=True)
    basket_id = fields.Integer(size=4, string='Basket ID', compute="_get_basket_id", store=True)
    basket_no = fields.Integer(string="No Urut Basket", compute="_get_basket_no", store=True)
    size = fields.Char(string="Ukuran Ikan", compute="_get_ukuran_ikan", store=True)
    kindoffish = fields.Char(string="Jenis Ikan", compute="_get_jenis_ikan", store=True)
    start = fields.Float(string="Mulai", required=True)
    jamstart = fields.Char('Jam Mulai', compute="_get_start", store=True)
    jamfinish = fields.Char('Jam Selesai', compute="_get_finish", store=True)
    finish = fields.Float(string="Finish", required=True)
    jml_tray = fields.Integer(string="Jumlah Tray", required=True)
    nkl = fields.Selection([('N','N'),('K','K'),('L','L')], string='N-K-L', default='N')
    hc = fields.Integer(string="HC")
    pm = fields.Integer(string="PM")
    om = fields.Integer(string="OM")
    bm = fields.Integer(string="BM")
    other = fields.Integer(string="Other")
    remark = fields.Char(string="Remark")
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    productiondate = fields.Date(string="Tgl Produksi", required=True, default=fields.Datetime.now)
    materialdate = fields.Date(string="Tgl Produksi Bahan", compute="_get_materialdate", store=True)
    shift = fields.Char(string="Shift", compute="_get_shift", store=True)
    status_pnl = fields.Boolean('Status P&L', compute='_get_status_pnl', store=True)
    
    @api.one
    @api.depends('basket')
    def _get_status_pnl(self):
        if self.basket:
            self.status_pnl = self.basket.status_pnl
    
    @api.one
    @api.depends('productiondate')
    def _get_materialdate(self):
        if self.productiondate:
            self.materialdate=self.productiondate
    
    def simpanan_pre(self):
        return {
            'type':'ir.actions.act_window',
            'name':'Material Date Wizard',
            'res_model':'materialdate.wizard',
            'src_model':'sis.pre.cleaning',
            'view_mode':'form',
            'view_type':'form',
            'target':'new',
            'context':{
                'default_pre_id':self.id, 'default_old_date':self.productiondate
                }        
        }      
    
    def copydata(self):        
        data = {
                'productiondate' : self.productiondate,
                'line_cleaning': 0,
                'start' : 0,
                'finish' : 0,
                'nkl' : self.nkl,   
                'pcl' : 0,             
                }
        create_data = self.env['sis.pre.cleaning']
        create_data.create(data)
    
    @api.one
    @api.depends('start')
    def _get_start(self):
        if self.start:
            self.jamstart= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.start) * 60, 60))

    @api.one
    @api.depends('finish')
    def _get_finish(self):
        if self.finish:
            self.jamfinish= '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.finish) * 60, 60))
    
    @api.multi
    def my_func(self):
        self.ensure_one()            
        koma=0
        x=self.line_cleaning
        for n in range(len(x)):
            if x[n:n+1]==",":
                data=x[koma:n].strip()
                vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id, 'productiondate': self.productiondate}                
                koma=n+1
                other_object = self.env['sis.line.cleaning.pre']
                other_object.create(vals)
            else:
                if n+1==len(x):
                    data=x[koma:koma+(len(x)-koma)].strip()
                    vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id, 'productiondate': self.productiondate} 
                    other_object = self.env['sis.line.cleaning.pre']
                    other_object.create(vals) 
         
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals): 
        res = super(pre_cleaning, self).create(vals)
        res.my_func()
        return res
            
    @api.onchange('basket_no')
    def _cari_label(self):         
        if self.basket_no:
            cSQL1="select remark from sis_pre_cleaning where basket_no='"+str(self.basket_no)
            cSQL2="' and productiondate='"+self.productiondate+"' and location='"+self.location+"'"
              
            self.env.cr.execute(cSQL1+cSQL2)
            rec=self.env.cr.fetchall()
             
            if len(rec) != False:
                print("masuk len")
                
#                if len(rec2)!=0:
                for data in rec:
                    (xremark,)=data
            
                if (xremark!='MDR' and xremark!='mdr'):
                    raise UserError("No. Label : "+str(self.basket_no)+" sudah diinput! "+str(self.basket.id))
            
    @api.one
    def _list_line_cleaning(self):
        xlc=""
        for xdetail in self.line_pre:
            if xdetail.line_cleaningpre:
                if xlc=="":
                    xlc=str(xdetail.line_cleaningpre)
                else:
                    xlc=xlc+", "+str(xdetail.line_cleaningpre)
         
        self.line_cleaning=xlc
        
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
                  
    @api.one        
    @api.depends('productiondate')
    def _get_shift(self):
        if self.productiondate:
            date = datetime.now()+ timedelta(hours = 7) 
            hour = date.time().hour
            minute = date.time().minute
            time = float('%s.%s' % (hour, minute))
            
            xuid = self.env.uid
            cSQL1="select a.shift from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_shift=self.env.cr.fetchall()
             
            for def_shift in rc_shift:
                    (xshift,)=def_shift

#             if time > 5.00 and time < 13.00:
#                 self.shift="Shift "+xshift
#             else:
            self.shift="Shift "+xshift
             
    @api.one     
    @api.depends('basket')
    def _get_basket_id(self):
        if self.basket:
            self.basket_id=self.basket.basket_id
            
    @api.one     
    @api.depends('basket')
    def _get_basket_no(self):
        if self.basket:
            self.basket_no=self.basket.label
    
    @api.multi     
    @api.depends('basket')
    def _get_jenis_ikan(self):
        if self.basket:
            xkindoffish = []
            xkindoffish=self.basket.rel_basket_cutting.rel_cutting.tangki
            print(self.kindoffish)             
            if xkindoffish:
                self.kindoffish = xkindoffish[0].kindoffish
            else:
                raise UserError('Data no tangki cutting tidak ada sehingga data ikan tidak ditemukan')   
 
            
    @api.multi             
    @api.depends('basket')
    def _get_ukuran_ikan(self):
        if self.basket:
            xsize = []
            xsize=self.basket.rel_basket_cutting.rel_cutting.tangki
            
            if xsize:
                self.size = xsize[0].size
            else:
                raise UserError('Data no tangki cutting tidak ada sehingga data ikan tidak ditemukan')      
    
#     @api.onchange('productiondate')
#     def onchange_label(self):
#         domain = []
#         domain.append(('productiondate','=',self.productiondate))
#         return {'domain':{'basket':domain}}
    
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_line_cleaning_pre where rel_line_cleaning="+str(me_id.id)+""
            cSQL2="delete from materialdate_wizard where pre_id="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)  
            self.env.cr.execute(cSQL2)           
                
            return super(pre_cleaning, self).unlink()
        
class line_cleaning_pre(models.Model):
    _name = 'sis.line.cleaning.pre'
    
    rel_line_cleaning = fields.Many2one('sis.pre.cleaning', string="Line Cleaning")
    line_cleaningpre = fields.Integer(string="Line Cleaning")
    productiondate = fields.Date(string="Tgl Produksi")
    
    
class MaterialdateWizard(models.TransientModel):
    _name = 'materialdate.wizard'
    _description = 'Material Date Wizard'
    
    new_date = fields.Date('Nama Baru', required=True)
    old_date = fields.Date('Nama Lama')
    pre_id = fields.Many2one('sis.pre.cleaning', string='Pre Cleaning', required=True)
    
    def change_date_pre(self):
        for rec in self:
            rec.pre_id.materialdate = rec.new_date
            
    
class sis_pre_view_alert(models.Model):
    _name = 'sis.pre.view.alert'
    _description = 'Data Cooker yang belum diinput pre'
    _auto = False
    _order = 'productiondate desc'
    
    productiondate = fields.Date('Tanggal Produksi')
    location = fields.Char('Lokasi')
    basket_id = fields.Char('Basket ID')
    label = fields.Integer('Label')
        
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_pre_view_alert as (
        SELECT
        row_number() OVER () as id, 
        co.productiondate, co.location, co.basket_id, co.label from sis_cooker_basket as co
        left join sis_pre_cleaning as pre on pre.basket=co.id
        where co.productiondate>='2020-11-07' and pre.id is null)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_pre_view_alert')
        self._cr.execute(cSQL)
    