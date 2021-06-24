from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from datetime import timedelta

class pre_cleaning(models.Model):
    _name = 'sis.pre.cleaning'
    _order = "productiondate desc"    
    _rec_name   ='basket_id'
    
    line_pre = fields.One2many('sis.line.cleaning.pre', 'rel_line_cleaning', string='Line Cleaning')
    rel_pack = fields.One2many('sis.packing', 'rel_pre', string='Relasi packing')
    pcl = fields.Integer(string="Line Pre Cleaning", required=True)
    line_cleaning = fields.Char(string="Line Cleaning", required=True)
    basket_id = fields.Integer(size=4, string='Basket ID', compute="_get_basket_id", store=True)
    basket = fields.Many2one('sis.cooker.basket', string="Cooker Label")
    basket_no = fields.Integer(string="No Urut Basket", compute="_get_basket_no", store=True)
    size = fields.Char(string="Ukuran Ikan", compute="_get_ukuran_ikan", store=True)
    kindoffish = fields.Char(string="Jenis Ikan", compute="_get_jenis_ikan", store=True)
    start = fields.Float(string="Mulai", required=True)
    finish = fields.Float(string="Finish", required=True)
    nkl = fields.Selection([('N','N'),('K','K'),('L','L')], string='N-K-L', default='N')
    hc = fields.Integer(string="HC")
    pm = fields.Integer(string="PM")
    om = fields.Integer(string="OM")
    bm = fields.Integer(string="BM")
    other = fields.Integer(string="Other")
    remark = fields.Char(string="Remark")
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    productiondate = fields.Date(string="Tgl Produksi", required=True)
    shift = fields.Char(string="Shift", compute="_get_shift", store=True)
    
    @api.multi
    def my_func(self):
        self.ensure_one()            
        koma=0
        x=self.line_cleaning
        for n in range(len(x)):
            if x[n:n+1]==",":
                data=x[koma:n].strip()
                print(data+" if")
                vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id}                
                koma=n+1
                other_object = self.env['sis.line.cleaning.pre']
                other_object.create(vals)
            else:
                if n+1==len(x):
                    data=x[koma:koma+(len(x)-koma)].strip()
                    print(data+" else")
                    vals = {'line_cleaningpre': data, 'rel_line_cleaning': self.id} 
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
                    print(self.basket_no)
                    print(xremark)
                    raise UserError("No. Label : "+str(self.basket_no)+" sudah diinput!")
            
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
            self.kindoffish = xkindoffish[0].kindoffish
            print(self.kindoffish)  
            
    @api.multi             
    @api.depends('basket')
    def _get_ukuran_ikan(self):
        if self.basket:
            xsize = []
            xsize=self.basket.rel_basket_cutting.rel_cutting.tangki
            self.size = xsize[0].size
            print(self.size)        
    
    @api.onchange('productiondate')
    def onchange_label(self):
        domain = []
        domain.append(('productiondate','=',self.productiondate))
        
        return {'domain':{'basket':domain}}
    
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_line_cleaning_pre where rel_line_cleaning="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
                
            return super(pre_cleaning, self).unlink()
    
#     @api.onchange('productiondate')
#     def filter_label_basket(self):
# #        xproductiondate=self._context.get('productiondate')
# #         xnopotong      =self._context.get('nopotong')
#         xlocation      =self.location
#         
#         domain = []
#         domain.append(('productiondate','=',self.productiondate))
# #         domain.append(('no_potong','=',xnopotong))
#         domain.append(('rel_cooker.location','=',xlocation))
#         return {'domain':{'basket':domain}}
     
    def open_noLineCleaning(self):
        return {
            'name'      : 'Line Cleaning',
            'res_model' : 'sis.line.cleaning.pre',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'tree',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_traceability.sis_line_cleaning_pre_tree').id,
            'nodestroy' : False,
            'target'    : 'new',
            'context'   : {'default_rel_line_cleaning':self.id},
            'domain'    : [('rel_line_cleaning','=',self.id)],      
            'flags'     : {'action_buttons': True}
        }
        
class line_cleaning_pre(models.Model):
    _name = 'sis.line.cleaning.pre'
    
    rel_line_cleaning = fields.Many2one('sis.pre.cleaning', string="Line Cleaning")
    line_cleaningpre = fields.Integer(string="Line Cleaning")
    
    
    
    
    
    
    
    