from odoo import models, fields, api
from odoo.exceptions import UserError

class cutting_basket(models.Model):
    _name       ='sis.cutting.basket'
    _rec_name   ='label'
    
    rel_cutting       = fields.Many2one('sis.cutting', string="Basket")
    tgl_produksi      = fields.Date(string="Tanggal Produksi")
    location          = fields.Char(size=4, string='Lokasi')
    no_potong         = fields.Integer(string='No Potong')
    basket_id         = fields.Char(size=4, string='Basket ID', required=True)
    tespek            = fields.Selection([(0,'No'),(1,'Yes')], string='Test', default=0)
    label             = fields.Integer(string="Label", required="true")
    basketCooker      = fields.One2many('sis.cooker.basket', 'rel_basket_cutting', string='Basket')
#     list_basket_label = fields.Char(size=100, string='No. Basket', compute='refresh_label')

#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%d - [%d]" % (me.basket_id, me.no_potong)))
#         return result
    
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
        
    @api.onchange('tgl_produksi')
    def filter_defrost_tangki(self):
        domain = []
        domain.append(('tgl_produksi','=',self.tgl_produksi))
        domain.append(('no_potong','=',self.no_potong))
        domain.append(('pabrik_id','=',self.location))
        return {'domain':{'rel_cutting':domain}}
    
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
 
