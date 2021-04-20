from odoo import models, fields, api, tools
from odoo.exceptions import UserError

class cooker_basket(models.Model):
    _name       ='sis.cooker.basket'
    _order      = "label"    
    _rec_name   ='label'
    
    rel_cooker         = fields.Many2one('sis.cooker', string="Cooker ID")
    rel_basket_cutting = fields.Many2one('sis.cutting.basket', string="ID Basket", required=True, domain="[('tgl_produksi','=', productiondate),('location', '=', location)]")
    label_pre          = fields.One2many('sis.pre.cleaning', 'basket', string='Label ID')
    
    productiondate     = fields.Date(string='Tanggal Produksi', required=True)
    location           = fields.Char(size=4, string='Lokasi')
    location_nobasket    = fields.Char(size=4, string='Lokasi', compute="_lokasi", store=True)
    basket_id          = fields.Char(size=4, string='Basket ID', compute="_get_basket_id", store=True)
    tespek             = fields.Integer(string='Test', compute="_get_test", store=True)
    tespek_desc        = fields.Char(size=3, string='Test Desc', compute="_get_test", store=True)
    label              = fields.Integer(string='Label', compute="_get_label", store=True)
    status_basket      = fields.Boolean('cari tangki', compute='list_domain', store=True)
    status_pnl      = fields.Boolean('Status P&L', compute='_get_statuspnl', store=True)
    combination = fields.Char(string='Combination', compute='_compute_fields_combination')
    
    @api.one
    @api.depends('rel_basket_cutting')
    def _get_statuspnl(self):
        if self.rel_basket_cutting:
            self.status_pnl=self.rel_basket_cutting.status_pnl
            
    @api.one
    @api.depends('rel_basket_cutting')
    def _lokasi(self):
        if self.rel_basket_cutting:
            self.location_nobasket=self.rel_basket_cutting.location
            
    @api.depends('label', 'basket_id')
    def _compute_fields_combination(self):
        for test in self:
            test.combination = str(test.label) + ' - ' + str(test.basket_id)
        
    @api.one
    def list_domain(self):
        xkindoffish=self.rel_basket_cutting.rel_cutting.tangki
        if xkindoffish:
            self.status_basket=True
            
    def _get_section_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
 
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
         
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
         
        return xpabrik_id,xsection_id
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        xpabrik_id, xsection_id=self._get_section_id()
#         if vals['location']==xpabrik_id or xsection_id=="Admin":
#             if  xsection_id=="Prod1" or xsection_id=="Cooker" or xsection_id=="RM" or xsection_id=="Admin":
        xtespek=self._get_tespek(vals['rel_basket_cutting'])
        vals.update({'tespek':xtespek}) 
        res_id = models.Model.create(self, vals)
        return res_id
#             else:
#                 raise UserError("Unauthorized User!")
#         else:
#             raise UserError("Data "+vals['location']+" tidak bisa di edit oleh user "+xpabrik_id)

    @api.one     
    @api.depends('rel_basket_cutting')
    def _get_basket_id(self):
        if self.rel_basket_cutting:
            self.basket_id=self.rel_basket_cutting.basket_id

    @api.one     
    @api.depends('rel_basket_cutting')
    def _get_label(self):
        if self.rel_basket_cutting:
            self.env.cr.execute("select label from sis_cutting_basket where id="+str(self.rel_basket_cutting.id))
            xrec=self.env.cr.fetchall()
            
            if len(xrec)>0:
                for label in xrec:
                    (xlabel,)=label
                self.label=xlabel

    @api.one     
    @api.depends('rel_basket_cutting')
    def _get_test(self):
        if self.rel_basket_cutting:
            self.env.cr.execute("select tespek from sis_cutting_basket where id="+str(self.rel_basket_cutting.id))
            xrec=self.env.cr.fetchall()
             
            if len(xrec)>0:
                for tespek in xrec:
                    (xtespek,)=tespek
                self.tespek=xtespek
                if xtespek==0:
                    self.tespek_desc="No"
                else:
                    self.tespek_desc="Yes"

    def _get_tespek(self, cut_id):
        if cut_id:
            self.env.cr.execute("select tespek from sis_cutting_basket where id="+str(cut_id))
            xrec=self.env.cr.fetchall()
            
            if len(xrec)>0:
                for tespek in xrec:
                    (xtespek,)=tespek
                    
                return xtespek
        
    @api.onchange('label')
    def _cari_label(self):
        xid=self._context.get('default_productiondate')
         
        if self.basket_id or self.basket_id!=0:
            cSQL1="select * from sis_cooker_basket where label='"+str(self.label)
            cSQL2="' and productiondate='"+xid+"' and location='"+self.location+"'"
            
            print(cSQL1+cSQL2)
              
            self.env.cr.execute(cSQL1+cSQL2)
            rec=self.env.cr.fetchall()
            if len(rec)>0:
                raise UserError("No. Label : "+str(self.label)+" sudah diinput!")

#     @api.multi
#     def write(self, vals):
#         xpabrik_id, xsection_id=self._get_section_id()
#         if xpabrik_id==self.location or xsection_id=="Admin":
#             if xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cooker" or xsection_id=="Admin":
#                 return super(cooker_basket, self).write(vals)
#             else:
#                 raise UserError("Unauthorized User!")
#         else:
#                 raise UserError("Data "+self.location+" tidak bisa di edit oleh user "+xpabrik_id)
            
class sis_cooker_view_alert(models.Model):
    _name = 'sis.cooker.view.alert'
    _description = 'Data Basket yang sudah diinput Cutting'
    _auto = False
    _order = 'tgl_produksi desc, label'
    
    tgl_produksi = fields.Date('Tanggal Produksi')
    location = fields.Char('Lokasi')
    basket_id          = fields.Char(size=4, string='Basket ID')
    label              = fields.Integer(string='Label')
    tespek             = fields.Integer(string='Test')
    create_date =   fields.Datetime('Create Date')

    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_cooker_view_alert as (
        SELECT
        row_number() OVER () as id, 
        cut.tgl_produksi, cut.location, cut.basket_id, cut.label, cut.tespek, cut.create_date from sis_cutting_basket as cut
        left join sis_cooker_basket as co on co.rel_basket_cutting=cut.id
        where tgl_produksi >='2020-11-01' and co.id is null order by tgl_produksi desc)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_cooker_view_alert')
        self._cr.execute(cSQL)
