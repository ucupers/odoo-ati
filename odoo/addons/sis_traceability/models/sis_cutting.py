from odoo import models, fields, api
from odoo.exceptions import UserError
#from datetime import datetime

class cutting(models.Model):
    _name       ='sis.cutting'
    _order      = "productiondate desc, no_potong"
     
    
    basket = fields.One2many('sis.cutting.basket', 'rel_cutting', string='Tangki')
    tangki = fields.One2many('sis.cutting.tangki', 'rel_cutting', string='Tangki')
    

    productiondate = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now())
    no_potong = fields.Integer(string='No Potong', required=True)
    jam_potong = fields.Datetime(string='Jam Potong', required=True)
    suhu = fields.Float(string='Suhu Punggung Awal', required=True)
    suhu_akhir = fields.Float(string='Suhu Punggung Akhir', required=True)
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
    pic = fields.Selection([('Yudianto','Yudianto'),('Abd Ghopar','Abd Ghopar'),('undik','Undik'),('M Farid','M Farid')], string='PIC', track_visibility="onchange")    
    location = fields.Char(size=4, string='Lokasi', compute="_get_pabrik_id", store=True)
    list_tangki=fields.Char(size=100, string='No. Tangki', compute='_list_tangki')
    list_basket=fields.Char(size=100, string='No. Basket', compute='_list_basket')
    data_ok = fields.Boolean(string="Kesesuaian Data", required=True, default=True)
    status_pl_cut   = fields.Boolean(string="Pole & Line", compute="update_hatch", store=True)
    
    @api.one
    @api.depends('tangki')
    def update_hatch(self):
        if self.tangki:
            for data in self.tangki:
                self.status_pl_cut = data.status_pl
    
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
            
            else:
                raise UserError("No. Potong pada Tgl. Produksi : "+self.productiondate+" : tidak tersedia!\nPilih Tgl. Produksi yang lain.")
     
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
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cutting":
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            raise UserError("Unauthorized User!")
 
    @api.multi
    def write(self, vals):
        xpabrik_id, xsection_id=self._get_section_id()
        if xpabrik_id==self.location or xsection_id=="Admin":
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cutting":
                if self.data_ok==False:
                    raise UserError("Kesesuain Data : False.\n Data tidak bisa diupdate!")
                else:
                    return super(cutting, self).write(vals)
            else:
                raise UserError("Unauthorized User!")
        else:
            raise UserError("Data "+self.location+" tidak bisa di edit oleh user "+xpabrik_id)
            
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_cutting_basket where rel_cutting="+str(me_id.id)+""
            cSQL2="delete from sis_cutting_tangki where rel_cutting="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
            self.env.cr.execute(cSQL2)

            return super(cutting, self).unlink()