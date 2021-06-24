from odoo import models, fields, api
from odoo.exceptions import UserError

class cooker_basket(models.Model):
    _name       ='sis.cooker.basket'
    _order      = "label"    
    _rec_name   ='basket_id'
    
    rel_cooker         = fields.Many2one('sis.cooker', string="Cooker ID")
    rel_basket_cutting = fields.Many2one('sis.cutting.basket', string="ID Basket", required=True)
    productiondate     = fields.Date(string='Tanggal Produksi', required=True)
    location           = fields.Char(size=4, string='Lokasi')
#    basket_id          = fields.Char(size=4, string='Basket ID', related="rel_basket_cutting.basket_id", store=True)
    basket_id          = fields.Char(size=4, string='Basket ID', compute="_get_basket_id", store=True)
    tespek             = fields.Integer(string='Test', compute="_get_test", store=True)
    tespek_desc        = fields.Char(size=3, string='Test Desc', compute="_get_test", store=True)
    label              = fields.Integer(string='Label', compute="_get_label", store=True)
#    label              = fields.Char(size=100, string='Label', related="rel_basket_cutting.label")
    label_pre          = fields.One2many('sis.pre.cleaning', 'basket', string='Label ID')

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
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="Cooker":
#            if self._validasi_nopotong(vals['no_potong'], vals['productiondate'], xpabrik_id)==True:
            xtespek=self._get_tespek(vals['rel_basket_cutting'])
            vals.update({'tespek':xtespek}) 
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            raise UserError("Unauthorized User!")

    @api.one     
    @api.depends('rel_basket_cutting')
    def _get_basket_id(self):
        if self.rel_basket_cutting:
            self.basket_id=self.rel_basket_cutting.basket_id
            #self.tespek=self.rel_basket_cutting.tespek

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
                

#            self.label=self.rel_basket_cutting.label

    
#     @api.one     
#     @api.depends('basket_id')
#     def _list_basket_label(self):
#         if self.basket_id:
#             
#             cSQL1="select basket_label from sis_cutting_basket_label "
#             cSQL2="where rel_basket_label="+str(self.rel_basket_cutting.id) 
#      
#             self.env.cr.execute(cSQL1+cSQL2)
#             rec=self.env.cr.fetchall()
#             if len(rec)>0:
#                 xbasket_label=""
#                 for label in rec:
#                     (xlabel,)=label
#                     if xbasket_label=="":
#                         xbasket_label=xlabel
#                     else:
#                         xbasket_label=xbasket_label+", "+xlabel
#                 self.label=xbasket_label
        
    @api.onchange('label')
    def _cari_label(self):
        xid=self._context.get('default_productiondate')
         
        if self.basket_id or self.basket_id!=0:
            cSQL1="select * from sis_cooker_basket where label='"+str(self.label)
            cSQL2="' and productiondate='"+xid+"'"
              
            self.env.cr.execute(cSQL1+cSQL2)
            rec=self.env.cr.fetchall()
            if len(rec)>0:
                raise UserError("No. Label : "+str(self.label)+" sudah diinput!")
            
#     @api.onchange('basket_id')
#     def _cari_jumlah_basket(self):
#         if self.basket_id:
#             cSQL1="select count(*) basket_id from sis_cooker_basket group by basket_id"
#             self.env.cr.execute(cSQL1)
#             rec=self.env.cr.fetchall()
#             if len(rec)>6:
#                 raise UserError("Basket Mencapai Maksimum")
            
#     @api.one
#     @api.depends('label')
#     def _label(self):
#         if self.label:
#             self.basket_id = self.rel_basket_cutting.rel_basket_label.basket_id
#     @api.one        
#     @api.depends('label')
#     def _test(self):
#         if self.label:
#             self.tespek = self.rel_basket_cutting.rel_basket_label.tespek            
            
                         
    @api.onchange('productiondate')
    def filter_cutting_basket(self):
#        xproductiondate=self._context.get('productiondate')
#         xnopotong      =self._context.get('nopotong')
#        xlocation      =self._context.get('location')
        
        domain = []
        domain.append(('tgl_produksi','=',self.productiondate))
#         domain.append(('no_potong','=',xnopotong))
        domain.append(('location','=',self.location))
        return {'domain':{'rel_basket_cutting':domain}}
    
#     @api.onchange('label')
#     def _cari_label(self):
#         if self.label or self.label!=0:
#             cSQL1="select * from sis_cooker_basket where productiondate='"+self.productiondate
#             cSQL2="' and label='"+self.label+"'"
#             #print(cSQL1+cSQL2+cSQL3)
#             self.env.cr.execute(cSQL1+cSQL2)
#             rec=self.env.cr.fetchall()
#             if len(rec)>0:
#                 raise UserError("No. Label Basket : "+self.label+" sudah diinput!")

