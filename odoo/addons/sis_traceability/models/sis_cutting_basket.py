from odoo import models, fields, api
from odoo.exceptions import UserError

class cutting_basket(models.Model):
    _name       ='sis.cutting.basket'
    _order      = 'label'
    _rec_name   ='label'
    
    rel_cutting       = fields.Many2one('sis.cutting', string="Basket")
    basketCooker      = fields.One2many('sis.cooker.basket', 'rel_basket_cutting', string='Basket')
    
    
    tgl_produksi      = fields.Date(string="Tanggal Produksi")
    location          = fields.Char(size=4, string='Lokasi')
    no_potong         = fields.Integer(string='No Potong')
    basket_id         = fields.Char(size=4, string='Basket ID', required=True)
    tespek            = fields.Selection([(0,'No'),(1,'Yes')], string='Test', default=0)
    label             = fields.Integer(string="Label", required="true")
    status_pnl      = fields.Boolean('Status P&L', compute='_get_pnl', store=True)
    

    @api.one
    @api.depends('rel_cutting')
    def _get_pnl(self):
        if self.rel_cutting:
            self.status_pnl = self.rel_cutting.status_pl_cut
    
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
    def create(self,vals):
        xpabrik_id,xsection_id=self._get_section_id()
        if xpabrik_id==vals['location'] or xsection_id=="Admin":
            if  xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cutting" or xsection_id=="Admin":
                res_id = models.Model.create(self, vals)
                return res_id
            else:
                raise UserError("Unauthorized User!")
        else:
                raise UserError("Data "+vals['location']+" tidak bisa di edit oleh user "+xpabrik_id)
 
    @api.multi
    def write(self, vals):
        xpabrik_id, xsection_id=self._get_section_id()
        if xpabrik_id==self.location or xsection_id=="Admin":
            if xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cutting" or xsection_id=="Admin":
                return super(cutting_basket, self).write(vals)
            else:
                raise UserError("Unauthorized User!")
        else:
                raise UserError("Data "+self.location+" tidak bisa di edit oleh user "+xpabrik_id)
    
#     @api.one
#     def refresh_label(self):
#         xbasket_label=""
#         for xdetail in self.label:
#             if xdetail.basket_label:
#                 if xbasket_label=="":
#                     xbasket_label=xdetail.basket_label
#                 else:
#                     xbasket_label=xbasket_label+", "+xdetail.basket_label
#          
#         self.list_basket_label=xbasket_label
        

    
#     @api.one
#     @api.depends('basket_id')
#     def _get_label(self):
#         if self.basket_id:
#             cSQL1 ="select MAX(label) from sis_cutting_basket where tgl_produksi='"+self.tgl_produksi+"' and location='"+self.location+"' and label is not null"
#             self.env.cr.execute(cSQL1)       
#             rc_check=self.env.cr.fetchall()
#             x = len(rc_check)
#             if x > 0:
#                 for cs_checker in rc_check:
#                     (xlabel, )=cs_checker
#                     if xlabel:
#                         self.label=xlabel+1                        
#                     else:
#                         self.label = 1
#             else:
#                 self.label=1
    
#     def open_nobasket(self):
#         return {
#             'name'      : 'No. Label',
#             'res_model' : 'sis.cutting.basket.label',
#             'type'      : 'ir.actions.act_window',
#             'view_mode' : 'tree',
#             'view_type' : 'form',
#             'views'     : [[False, "tree"], [False, "form"]],
#             'view_id'   : self.env.ref('sis_traceability.sis_cutting_basket_label_tree').id,
#             'nodestroy' : False,
#             'target'    : 'new',
#             'context'   : {'default_rel_basket_label':self.id, 'default_tgl_produksi':self.tgl_produksi, 'default_no_potong':self.no_potong, 'default_location':self.location},
#             'domain'    : [('rel_basket_label','=',self.id)],      
#             'flags'     : {'action_buttons': True}
#         }
    
#     @api.onchange('basket_id')
#     def _cari_basket(self):
#         if self.basket_id or self.basket_id!=0:
#             cSQL1="select * from sis_cutting_basket where tgl_produksi='"+self.tgl_produksi
#             cSQL2="' and basket_id='"+self.basket_id+"' and no_potong="+str(self.no_potong)
#             cSQL3=" and location='"+self.location+"'"
#             
#             self.env.cr.execute(cSQL1+cSQL2+cSQL3)
#             rec=self.env.cr.fetchall()
#             if len(rec)>0:
#                 raise UserError("No. Basket : "+self.basket_id+" sudah diinput!")
 
# class cutting_basket_label(models.Model):
#     _name       ='sis.cutting.basket.label'
#     _rec_name   ='basket_label'
#     
#     rel_basket_label = fields.Many2one('sis.cutting.basket', string="Basket ID")
#     rel_tangki_label = fields.Many2one('sis.cutting.tangki', string="No Tangki", required=True)
#     label_cooker     = fields.One2many('sis.cooker.basket', 'rel_basket_cutting', string='Label')
#     tgl_produksi= fields.Date(string="Tanggal Produksi")
#     location    = fields.Char(size=4, string='Lokasi')
#     no_potong   = fields.Integer(string='No Potong')
#     basket_label= fields.Char(size=4, string='Basket Label', required=True)
#     
#     @api.onchange('tgl_produksi')
#     def filter_defrost_tangki(self):
#         domain = []
#         domain.append(('tgl_produksi','=',self.tgl_produksi))
#         domain.append(('no_potong','=',self.no_potong))
#         domain.append(('location','=',self.location))
#         return {'domain':{'rel_tangki_label':domain}}
# 
# 
#     @api.onchange('basket_label')
#     def _cari_label(self):
#         if self.basket_label or self.basket_label!=0:
#             cSQL1="select * from sis_cutting_basket_label where tgl_produksi='"+self.tgl_produksi
#             cSQL2="' and basket_label='"+self.basket_label+"' and no_potong="+str(self.no_potong)
#             cSQL3=" and location='"+self.location+"' and rel_basket_label='"+str(self.rel_basket_label.id)+"'"
#             #print(cSQL1+cSQL2+cSQL3)
#             self.env.cr.execute(cSQL1+cSQL2+cSQL3)
#             rec=self.env.cr.fetchall()
#             if len(rec)>0:
#                 raise UserError("No. Label Basket : "+self.basket_label+" sudah diinput!")
 
