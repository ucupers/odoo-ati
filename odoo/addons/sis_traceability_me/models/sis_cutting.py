from odoo import models, fields, api
from odoo.exceptions import UserError
#from datetime import datetime

class cutting(models.Model):
    _name       ='sis.cutting'
    _order      = "productiondate desc, no_potong"
     
    productiondate = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now())
#    no_potong = fields.Integer(string='No Potong', related='notangki_id.no_potong', store=True)
    no_potong = fields.Integer(string='No Potong', required=True)
    jam_potong = fields.Datetime(string='Jam Potong', required=True)
    suhu = fields.Float(string='Suhu', required=True)
    qty_reject = fields.Integer(string='Quantity Reject', required=True)
    eyes = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Mata', default='B', track_visibility="onchange")
    gill = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Insang', default='B', track_visibility="onchange")
    skin = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Kulit', default='B', track_visibility="onchange")
    physical_damage = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Kerusakan Fisik', default='B', track_visibility="onchange")
    texture = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Tekstur', default='B', track_visibility="onchange")
    belly_cavity = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Rongga Perut', default='B', track_visibility="onchange")
    odour = fields.Char(size=5, string='Bau', default='B', required=True)
    grade_assigned = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Nilai', default='B', track_visibility="onchange")
    parasite = fields.Selection([('OK','OK'),('L','L'),('X','X')], string='Parasite', default='OK', track_visibility="onchange")
    remark = fields.Char(size=50, string='Remark', required=True, default='-')    
    pic = fields.Selection([('bayu','Bayu'),('nayaka','Nayaka')], string='PIC', default='bayu', track_visibility="onchange")    
    #notangki_id=fields.Many2one('sis.defrost.detail',string="No Potong", required=True) 
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    tangki = fields.One2many('sis.cutting.tangki', 'rel_cutting', string='Tangki')
    list_tangki=fields.Char(size=100, string='No. Tangki', compute='_list_tangki')
    list_basket=fields.Char(size=100, string='No. Basket', compute='_list_basket')
    basket = fields.One2many('sis.cutting.basket', 'rel_cutting', string='Tangki')
    data_ok = fields.Boolean(string="Kesesuaian Data", required=True, default=True)

    @api.one
    def _list_tangki(self):
        xtangki=""
        for xdetail in self.tangki:
            if xdetail.no_tangki:
                if xtangki=="":
                    xtangki=xdetail.no_tangki
                else:
                    xtangki=xtangki+", "+xdetail.no_tangki
         
        self.list_tangki=xtangki
        
    
    @api.one
    def _list_basket(self):
        xbasket=""
        for xdetail in self.basket:
            if xdetail.label:
                if xbasket=="":
                    xbasket=xdetail.label
                else:
                    xbasket=str(xbasket)+", "+str(xdetail.label)
         
        self.list_basket=xbasket
    
#     @api.onchange('no_potong')
#     def _check_nopotong(self):
#         if self.no_potong:
#             cSQL1="select distinct no_potong from sis_defrost_detail where tgl_produksi='"+self.productiondate+"' and pabrik_id='"+self.location+"'"
#             cSQL2=" and no_potong="+str(self.no_potong)
#            
#             self.env.cr.execute(cSQL1)
#             rec=self.env.cr.fetchall()
#             if len(rec)>0:
#                 xdata_nopotong=""
#                 for data in rec :
#                     (xnopotong,)=data
#                     if xdata_nopotong=="":
#                         xdata_nopotong=str(xnopotong)
#                     else:
#                         xdata_nopotong=xdata_nopotong+", "+str(xnopotong)
# 
#                 self.env.cr.execute(cSQL1+cSQL2)
#                 rec2=self.env.cr.fetchall()
#                 if len(rec2)==0:
#                     raise UserError("No. Potong : "+str(self.no_potong)+" tidak ditemukan!\nDaftar No. Potong pada Tgl. Produksi : "+self.productiondate+" :\n"+xdata_nopotong)
#             
#             else:
#                 raise UserError("No. Potong pada Tgl. Produksi : "+self.productiondate+" : tidak tersedia!")

    @api.constrains('no_potong')
    def _constrains_no_potong(self):
        if self.no_potong:
            cSQL1="select distinct no_potong from sis_defrost_detail where tgl_produksi='"+self.productiondate+"' and pabrik_id='"+self.location+"'"
            cSQL2=" and no_potong="+str(self.no_potong)
            cSQL3="select distinct no_potong from sis_cutting where productiondate='"+self.productiondate+"' and location='"+self.location+"'"
                       
            self.env.cr.execute(cSQL1)
            rec=self.env.cr.fetchall()
            if len(rec)>0:
                xdata_nopotong=""
                for data in rec :
                    (xnopotong,)=data
                    if xdata_nopotong=="":
                        xdata_nopotong=str(xnopotong)
                    else:
                        xdata_nopotong=xdata_nopotong+", "+str(xnopotong)

                self.env.cr.execute(cSQL1+cSQL2)
                rec2=self.env.cr.fetchall()
                if len(rec2)==0:
                    raise UserError("No. Potong : "+str(self.no_potong)+" tidak ditemukan!\nDaftar No. Potong pada Tgl. Produksi : "+self.productiondate+" :\n"+xdata_nopotong)

#                 else:                    
#                     self.env.cr.execute(cSQL3+cSQL2)
#                     rec3=self.env.cr.fetchall()
#                     if len(rec3)!=0:
#                         raise UserError("Pada Tgl. Produksi "+self.productiondate+" No. Potong ["+str(self.no_potong)+"] sudah diinput!!")
            
            else:
                raise UserError("No. Potong pada Tgl. Produksi : "+self.productiondate+" : tidak tersedia!\nPilih Tgl. Produksi yang lain.")
            
#     @api.onchange('productiondate')
#     def filter_no_tangki(self):
#         domain = []
#         self.notangki_id=0
#         if self.productiondate:
#             domain.append(('tgl_produksi','=',self.productiondate))
#         return {'domain':{'notangki_id':domain}}
     
    def open_notangki(self):
        return {
            'name'      : 'No. Tangki Defrost',
            'res_model' : 'sis.cutting.tangki',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'tree',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_traceability.sis_cutting_tangki_tree').id,
            'nodestroy' : False,
            'target'    : 'new',
            'context'   : {'default_rel_cutting':self.id, 'default_tgl_produksi':self.productiondate, 'default_no_potong':self.no_potong, 'default_location':self.location},
            'domain'    : [('rel_cutting','=',self.id)],      
            'flags'     : {'action_buttons': True}
        }

    def open_nobasket(self):
        return {
            'name'      : 'Basket ID',
            'res_model' : 'sis.cutting.basket',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'tree',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_traceability.sis_cutting_basket_tree').id,
            'nodestroy' : False,
            'target'    : 'new',
            'context'   : {'default_rel_cutting':self.id, 'default_tgl_produksi':self.productiondate, 'default_no_potong':self.no_potong, 'default_location':self.location},
            'domain'    : [('rel_cutting','=',self.id)],      
            'flags'     : {'action_buttons': True}
        }

#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%d-%d [%d]" % (me.basket_id, me.no_urut_basket, me.no_potong)))
#         return result
#      
#     def copydata(self):
#         rcutting=self.env['sis.cutting'].search([('id','=',self.id)])
#         if len(rcutting)>0:
#             self.env.cr.execute("select id from sis_defrost_detail where tgl_produksi='"+rcutting.productiondate+"' and no_tangki='"+rcutting.notangki+"' and no_potong="+str(rcutting.no_potong)+" and pabrik_id='"+rcutting.location+"'")
#             rdefrost=self.env.cr.fetchall()
#             if len(rdefrost)>0:
#                 for def_data in rdefrost:
#                     (xid,)=def_data
#  
#                 vals = {'productiondate' : rcutting.productiondate,
#                         #'notangki'       : self.notangki,
#                         'basket_id'      : rcutting.basket_id,
#                         'no_urut_basket' : rcutting.no_urut_basket,
#                         #'no_potong'     : self.no_potong,
#                         'jam_potong'     : rcutting.jam_potong,
#                         'suhu'           : rcutting.suhu,
#                         'qty_reject'     : rcutting.qty_reject,
#                         'eyes'           : rcutting.eyes,
#                         'gill'           : rcutting.gill,
#                         'skin'           : rcutting.skin,
#                         'physical_damage': rcutting.physical_damage,
#                         'texture'        : rcutting.texture,
#                         'belly_cavity'   : rcutting.belly_cavity,
#                         'odour'          : rcutting.odour,
#                         'grade_assigned' : rcutting.grade_assigned,
#                         'parasite'       : rcutting.parasite,
#                         'remark'         : rcutting.remark,
#                         'notangki_id'    : xid
#                         }
#                 self.env['sis.cutting'].create(vals)
     
     
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
        xpabrik_id,xsection_id=self._get_section_id()
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="Cutting":
#            if self._validasi_nopotong(vals['no_potong'], vals['productiondate'], xpabrik_id)==True:
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            raise UserError("Unauthorized User!")
 
    @api.multi
    def write(self, vals):
        xpabrik_id, xsection_id=self._get_section_id()
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="Cutting":
            if self.data_ok==False:
                raise UserError("Kesesuain Data : False.\n Data tidak bisa diupdate!")
            else:
#            if self._validasi_nopotong(self.no_potong, self.productiondate, xpabrik_id)==True:
                return super(cutting, self).write(vals)
        else:
            raise UserError("Unauthorized User!")
        
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_cutting_basket where rel_cutting="+str(me_id.id)+""
            cSQL2="delete from sis_cutting_tangki where rel_cutting="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)
#             basket=self.env.cr.fetchall()
            
            self.env.cr.execute(cSQL2)
#             tangki=self.env.cr.fetchall()
            
                
            return super(cutting, self).unlink()
             
#================================================cutting lama

# class cutting(models.Model):
#     _name       ='sis.cutting'
#     _order      ='productiondate'
#      
#     productiondate = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now())
#     notangki = fields.Char(size=7, string='No. Tangki', related='notangki_id.no_tangki', store=True)
#     basket_id = fields.Integer(string='ID Basket', required=True)
#     no_urut_basket = fields.Integer(string='No Urut Basket', required=True)
#     no_potong = fields.Integer(string='No Potong', related='notangki_id.no_potong', store=True)
#     kindoffish = fields.Char(string="Jenis Ikan", compute="_jenisikan", store=True)
#     size = fields.Char(string="Ukuran", compute="_size", store=True)
#     vessel = fields.Char(string="Vessel", compute="_vessel", store=True)
#     voyage = fields.Char(string="Voyage", compute="_voyage", store=True)
#     hatch = fields.Char(string="Hatch", compute="_hatch", store=True)
#     jam_potong = fields.Datetime(string='Jam Potong', required=True)
#     suhu = fields.Float(string='Suhu', required=True)
#     qty_reject = fields.Integer(string='Quantity Reject', required=True)
#     eyes = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Mata', default='B', track_visibility="onchange")
#     gill = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Insang', default='B', track_visibility="onchange")
#     skin = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Kulit', default='B', track_visibility="onchange")
#     physical_damage = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Kerusakan Fisik', default='B', track_visibility="onchange")
#     texture = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Tekstur', default='B', track_visibility="onchange")
#     belly_cavity = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Rongga Perut', default='B', track_visibility="onchange")
#     odour = fields.Char(size=5, string='bau', default='B', required=True)
#     grade_assigned = fields.Selection([('A','A'),('B','B'),('C','C'),('D','D')], string='Nilai', default='B', track_visibility="onchange")
#     parasite = fields.Selection([('OK','OK'),('L','L'),('X','X')], string='Parasite', default='OK', track_visibility="onchange")
#     remark = fields.Char(size=50, string='Remark', required=True, default='-')    
#     pic = fields.Selection([('bayu','Bayu'),('nayaka','Nayaka')], string='PIC', default='bayu', track_visibility="onchange")    
#     notangki_id=fields.Many2one('sis.defrost.detail',string="No Tangki", required=True) 
#     location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
#     durasi_jam = fields.Float(string="Durasi", compute="_get_durasi", store=True)
#     jam_potong_def = fields.Datetime(string='Jam Potong Defrost', related='notangki_id.tgl_tuang')
#     durasi_def = fields.Float(string="Durasi Defrost", related='notangki_id.durasi_jam')
#       
#     @api.onchange('productiondate')
#     def filter_no_tangki(self):
#         domain = []
#         self.notangki_id=0
#         if self.productiondate:
#             domain.append(('tgl_produksi','=',self.productiondate))
#         return {'domain':{'notangki_id':domain}}
#      
#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%d-%d [%d]" % (me.basket_id, me.no_urut_basket, me.no_potong)))
#         return result
#      
#     def copydata(self):
#         rcutting=self.env['sis.cutting'].search([('id','=',self.id)])
#         if len(rcutting)>0:
#             self.env.cr.execute("select id from sis_defrost_detail where tgl_produksi='"+rcutting.productiondate+"' and no_tangki='"+rcutting.notangki+"' and no_potong="+str(rcutting.no_potong)+" and pabrik_id='"+rcutting.location+"'")
#             rdefrost=self.env.cr.fetchall()
#             if len(rdefrost)>0:
#                 for def_data in rdefrost:
#                     (xid,)=def_data
#  
#                 vals = {'productiondate' : rcutting.productiondate,
#                         #'notangki'       : self.notangki,
#                         'basket_id'      : rcutting.basket_id,
#                         'no_urut_basket' : rcutting.no_urut_basket,
#                         #'no_potong'     : self.no_potong,
#                         'jam_potong'     : rcutting.jam_potong,
#                         'suhu'           : rcutting.suhu,
#                         'qty_reject'     : rcutting.qty_reject,
#                         'eyes'           : rcutting.eyes,
#                         'gill'           : rcutting.gill,
#                         'skin'           : rcutting.skin,
#                         'physical_damage': rcutting.physical_damage,
#                         'texture'        : rcutting.texture,
#                         'belly_cavity'   : rcutting.belly_cavity,
#                         'odour'          : rcutting.odour,
#                         'grade_assigned' : rcutting.grade_assigned,
#                         'parasite'       : rcutting.parasite,
#                         'remark'         : rcutting.remark,
#                         'notangki_id'    : xid
#                         }
#                 self.env['sis.cutting'].create(vals)
#      
#     @api.depends('notangki_id')
#     def _jenisikan(self):
#         xuid = self.notangki
#         tglprod = self.productiondate
#         nopot = self.no_potong
#         cSQL1="select distinct c.product_group_code from sis_defrost_detail as b, sis_cs_detail as c "
#         cSQL2="where b.tgl_produksi='"
#         cSQL3="' and b.no_tangki='"
#         cSQL4="' and b.no_potong='"
#         cSQL5="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
#       
#         self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5)
#         rc_check=self.env.cr.fetchall()
#         if len(rc_check)>0:
#             for cs_checker in rc_check:
#                 (xproductgroupcode, )=cs_checker
#             self.kindoffish = xproductgroupcode
#              
#     @api.depends('notangki_id')
#     def _size(self):
#         xuid = self.notangki
#         tglprod = self.productiondate
#         nopot = self.no_potong
#         cSQL1="select distinct c.real_item_no from sis_defrost_detail as b, sis_cs_detail as c "
#         cSQL2="where b.tgl_produksi='"
#         cSQL3="' and b.no_tangki='"
#         cSQL4="' and b.no_potong='"
#         cSQL5="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
#       
#         self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5)
#         rc_check=self.env.cr.fetchall()
#         if len(rc_check)>0:
#             for cs_checker in rc_check:
#                 (xrealitemno, )=cs_checker
#             self.size = xrealitemno
#      
#     @api.depends('notangki_id')
#     def _vessel(self):
#         xuid = self.notangki
#         tglprod = self.productiondate
#         nopot = self.no_potong
#         cSQL1="select distinct c.vessel_no from sis_defrost_detail as b, sis_cs_detail as c "
#         cSQL2="where b.tgl_produksi='"
#         cSQL3="' and b.no_tangki='"
#         cSQL4="' and b.no_potong='"
#         cSQL5="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
#       
#         self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5)
#         rc_check=self.env.cr.fetchall()
#         if len(rc_check)>0:
#             for cs_checker in rc_check:
#                 (xvessel, )=cs_checker
#             self.vessel = xvessel
#              
#      
#     @api.depends('notangki_id')
#     def _voyage(self):
#         xuid = self.notangki
#         tglprod = self.productiondate
#         nopot = self.no_potong
#         cSQL1="select distinct c.voyage_no from sis_defrost_detail as b, sis_cs_detail as c "
#         cSQL2="where b.tgl_produksi='"
#         cSQL3="' and b.no_tangki='"
#         cSQL4="' and b.no_potong='"
#         cSQL5="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
#       
#         self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5)
#         rc_check=self.env.cr.fetchall()
#         if len(rc_check)>0:
#             for cs_checker in rc_check:
#                 ( xvoyage, )=cs_checker
#             self.voyage = xvoyage
#              
#      
#     @api.depends('notangki_id')
#     def _hatch(self):
#         xuid = self.notangki
#         tglprod = self.productiondate
#         nopot = self.no_potong
#         cSQL1="select distinct c.hatch_no from sis_defrost_detail as b, sis_cs_detail as c "
#         cSQL2="where b.tgl_produksi='"
#         cSQL3="' and b.no_tangki='"
#         cSQL4="' and b.no_potong='"
#         cSQL5="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
#       
#         self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5)
#         rc_check=self.env.cr.fetchall()
#         if len(rc_check)>0:
#             for cs_checker in rc_check:
#                 (xhatch, )=cs_checker
#             self.hatch = xhatch
#      
#     @api.one        
#     @api.depends('productiondate')
#     def _get_pabrik_id(self):
#         if self.productiondate:
#             xuid = self.env.uid
#             cSQL1="select a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
#             cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
#      
#             self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
#             rc_lokasi=self.env.cr.fetchall()
#              
#             for def_lokasi in rc_lokasi:
#                     (xpabrik_id,)=def_lokasi
#              
#             self.location=xpabrik_id
#  
#     def _get_section_id(self):
#         xuid = self.env.uid
#         cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
#         cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
#  
#         self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
#         rc_lokasi=self.env.cr.fetchall()
#          
#         for def_lokasi in rc_lokasi:
#             (xpabrik_id,xsection_id)=def_lokasi
#          
#         return xpabrik_id,xsection_id
#  
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self,vals):
#         xpabrik_id,xsection_id=self._get_section_id()
#         if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":
#             res_id = models.Model.create(self, vals)
#             return res_id
#         else:
#             raise UserError("Unauthorized User!")
#  
#     @api.multi
#     def write(self, vals):
#         xpabrik_id, xsection_id=self._get_section_id()
#         if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":
#             return super(cutting, self).write(vals)
#         else:
#             raise UserError("Unauthorized User!")

