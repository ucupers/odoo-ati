from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class cooker(models.Model):
    _name  ='sis.cooker'
    _order = "productiondate desc, nocooking"
        
    productiondate  = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now())
    nocooking       = fields.Integer(string='No Cooking', default=0, required=True)
    nocooker        = fields.Integer(string='No Cooker', default=0, required=True)
#     nobasket        = fields.Integer(string='ID Basket')
#     nourutbasket    = fields.Integer(string="No Urut Basket")
#     nopotong        = fields.Integer(string="No Potong", )     
    list_basket     = fields.Char(size=100, string='Basket ID', compute='_list_basket')
    list_label      = fields.Char(size=100, string='No. Urut / Label', compute='_list_label')
    kindoffish      = fields.Char(string='Jenis Ikan')
    size            = fields.Char(string='Ukuran')
    total_tray      = fields.Integer(string='Total Tray', required=True, default=0)
    cookingtime     = fields.Float(string='Durasi Masak', required=True, compute='_durasi_masak')
    cookingtemp     = fields.Float(string='Suhu Masak', required=True, default=100)
    steamon         = fields.Datetime(string='Steam On', required=True, default=fields.Datetime.now)
    vent_closed     = fields.Datetime(string='Lubang Angin Ditutup', required=True, compute='_vent_tutup')
    steamoff        = fields.Datetime(string='Steam Off')
    standardtemp    = fields.Float(string='Standart Suhu Pusat Setelah Dimasak', default='65', required=True)
    tempbeforetop   = fields.Float(string='Suhu Atas Ikan Sebelum Dimasak', default=0, required=True)
    tempbeforecenter= fields.Float(string='Suhu Tengah Ikan Sebelum Dimasak', default=0, required=True)
    tempbeforebottom= fields.Float(string='Suhu Bawah Ikan Sebelum Dimasak', default=0, required=True)
    tempaftertop    = fields.Float(string='Suhu Atas Ikan Sesudah Dimasak', default=0, required=True)
    tempaftercenter = fields.Float(string='Suhu Tengah Ikan Sesudah Dimasak', default=0, required=True)
    tempafterbottom = fields.Float(string='Suhu Bawah Ikan Sesudah Dimasak', default=0, required=True)
    startshowertime = fields.Datetime(string='Jam Mulai Showering')
    stopshowertime  = fields.Datetime(string='Jam Selesai Showering')
    aftershowertemp1 = fields.Float(string='Suhu Setelah Showering Atas', default=0, required=True)
    aftershowertemp2 = fields.Float(string='Suhu Setelah Showering Tengah', default=0, required=True)
    aftershowertemp3 = fields.Float(string='Suhu Setelah Showering Bawah', default=0, required=True)
    showerline      = fields.Integer(string='Jalur Shower', compute="_onchangeShowerLine", store=True)
    coolingRoomLine = fields.Integer(string='Cooling Room Line')
    remark          = fields.Char(size=50, string='Remark', required=True, default='-')
    location        = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True)   
    basket_id       = fields.One2many('sis.cooker.basket', 'rel_cooker', string='Basket ID')
    status_input    = fields.Boolean(string="Status Input", default=False)
#     list_label     =fields.Char(size=100, string='No. Basket', compute='_list_label')
    
    @api.one
    def _list_label(self):
        xlabel=""
        xbasket=""
        xtest=0
        n=0
        
        cQuery="select basket_id,label,tespek from sis_cooker_basket where rel_cooker="+str(self.id)+" order by  basket_id,tespek,label"
        self.env.cr.execute(cQuery)
        rec=self.env.cr.fetchall()
        if len(rec)>0:
            for xdata in rec:
                (xbasket_id,xbaslabel,xtespek)=xdata
                if xbaslabel:
                    if n+1<len(rec):
                        if xlabel=="":
                            if xtespek==0:
                                xlabel=str(xbaslabel)
                                xtest=0
                            else:
                                xlabel="("+str(xbaslabel)
                                xtest=1
                            xbasket=xbasket_id
                        else:
                            if xbasket_id==xbasket:
                                if xtespek==0 and xtest==0:
                                    xlabel=xlabel+", "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==0:
                                    xlabel=xlabel+", ("+str(xbaslabel)
                                    xtest=1
                                elif xtespek==0 and xtest==1:
                                    xlabel=xlabel+"), "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==1:
                                    xlabel=xlabel+", "+str(xbaslabel)
                                    xtest=1
                            else:
                                if xtespek==0 and xtest==0:
                                    xlabel=xlabel+", "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==0:
                                    xlabel=xlabel+", ("+str(xbaslabel)
                                    xtest=1
                                elif xtespek==0 and xtest==1:
                                    xlabel=xlabel+"), "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==1:
                                    xlabel=xlabel+"), ("+str(xbaslabel)
                                    xtest=1
                                    
                                xbasket=xbasket_id
    
                    elif n+1==len(rec):
                        if xlabel=="":
                            if xtespek==0:
                                xlabel=str(xbaslabel)
                                xtest=0
                            else:
                                xlabel="("+str(xbaslabel)+")"
                                xtest=1
                            xbasket=xbasket_id
                        else:
                            if xbasket_id==xbasket:
                                if xtespek==0 and xtest==0:
                                    xlabel=xlabel+", "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==0:
                                    xlabel=xlabel+", ("+str(xbaslabel)+")"
                                    xtest=1
                                elif xtespek==0 and xtest==1:
                                    xlabel=xlabel+"), "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==1:
                                    xlabel=xlabel+", "+str(xbaslabel)+")"
                                    xtest=1
                            else:
                                if xtespek==0 and xtest==0:
                                    xlabel=xlabel+", "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==0:
                                    xlabel=xlabel+", ("+str(xbaslabel)+")"
                                    xtest=1
                                elif xtespek==0 and xtest==1:
                                    xlabel=xlabel+"), "+str(xbaslabel)
                                    xtest=0
                                elif xtespek==1 and xtest==1:
                                    xlabel=xlabel+"), ("+str(xbaslabel)+")"
                                    xtest=1
                                    
                                xbasket=xbasket_id
                            
                    n=n+1
            
        #print(str(n))
        self.list_label=xlabel
    
    @api.one
    @api.depends('nocooker')
    def _onchangeShowerLine(self):
        if self.nocooker:
            self.showerline=self.nocooker

    @api.model
    def create(self,vals):
#        xpabrik_id,xsection_id=self._get_section_id()
        xsection_id=self._get_section_id()
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="Cooker":
            if vals['nocooking']==0 or vals['nocooker']==0 or vals['total_tray']==0 or vals['steamoff']==False or vals['tempbeforetop']==0 or vals['tempbeforecenter']==0 or vals['tempbeforebottom']==0 or vals['tempaftertop']==0 or vals['tempaftercenter']==0 or vals['tempafterbottom']==0  or vals['startshowertime']==False or vals['stopshowertime']==False or vals['aftershowertemp1']==0 or vals['aftershowertemp2']==0 or vals['aftershowertemp3']==0 or vals['coolingRoomLine']==0:
                vals['status_input']=False
            else:
                vals['status_input']=True
            
            if vals['tempaftertop']<vals['standardtemp'] or vals['tempaftercenter']<vals['standardtemp'] or vals['tempafterbottom']<vals['standardtemp']:
                raise UserError("Suhu atas di bawah standart")
#            if self._validasi_nopotong(vals['no_potong'], vals['productiondate'], xpabrik_id)==True:
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            raise UserError("Unauthorized User!")
    
    @api.multi
    def write(self,vals):
        xsection_id=self._get_section_id()
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="Cooker":
            if vals.get('nocooking') or vals.get('nocooker') or vals.get('total_tray') or vals.get('steamoff') or vals.get('tempbeforetop') or vals.get('tempbeforecenter') or vals.get('tempbeforebottom') or vals.get('tempaftertop') or vals.get('tempaftercenter') or vals.get('tempafterbottom')  or vals.get('startshowertime') or vals.get('stopshowertime') or vals.get('aftershowertemp1') or vals.get('aftershowertemp2') or vals.get('aftershowertemp3') or vals.get('coolingRoomLine'):
                if vals.get('nocooking')==0 or vals.get('nocooker')==0 or vals.get('total_tray')==0 or vals.get('steamoff')==False or vals.get('tempbeforetop')==0 or vals.get('tempbeforecenter')==0 or vals.get('tempbeforebottom')==0 or vals.get('tempaftertop')==0 or vals.get('tempaftercenter')==0 or vals.get('tempafterbottom')==0  or vals.get('startshowertime')==False or vals.get('stopshowertime')==False or vals.get('aftershowertemp1')==0 or vals.get('aftershowertemp2')==0 or vals.get('aftershowertemp3')==0 or vals.get('coolingRoomLine')==0:
                    self.status_input=False
            elif self.nocooking==0 or self.nocooker==0 or self.total_tray==0 or self.steamoff==False or self.tempbeforetop==0 or self.tempbeforecenter==0 or self.tempbeforebottom==0 or self.tempaftertop==0 or self.tempaftercenter==0 or self.tempafterbottom==0  or self.startshowertime==False or self.stopshowertime==False or self.aftershowertemp1==0 or self.aftershowertemp2==0 or self.aftershowertemp3==0 or self.coolingRoomLine==0:
                self.status_input=False
            else:
                self.status_input=True
                
            if vals.get('standardtemp'):
                if vals.get('tempaftertop'):
                    if vals.get('tempaftertop')<vals.get('standardtemp'):
                        raise UserError("Suhu atas setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempaftertop<vals.get('standardtemp'):
                        raise UserError("Suhu atas setelah masak di bawah suhu standard BBT")
                if vals.get('tempaftercenter'):
                    if vals.get('tempaftercenter')<vals.get('standardtemp'):
                        raise UserError("Suhu tengah setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempaftercenter<vals.get('standardtemp'):
                        raise UserError("Suhu tengah setelah masak di bawah suhu standard BBT")
                if vals.get('tempafterbottom'):
                    if vals.get('tempafterbottom')<vals.get('standardtemp'):
                        raise UserError("Suhu bawah setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempafterbottom<vals.get('standardtemp'):
                        raise UserError("Suhu bawah setelah masak di bawah suhu standard BBT")
            else:
                if vals.get('tempaftertop'):
                    if vals.get('tempaftertop')<self.standardtemp:
                        raise UserError("Suhu atas setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempaftertop<self.standardtemp:
                        raise UserError("Suhu atas setelah masak di bawah suhu standard BBT")
                if vals.get('tempaftercenter'):
                    if vals.get('tempaftercenter')<self.standardtemp:
                        raise UserError("Suhu tengah setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempaftercenter<self.standardtemp:
                        raise UserError("Suhu tengah setelah masak di bawah suhu standard BBT")
                if vals.get('tempafterbottom'):
                    if vals.get('tempafterbottom')<self.standardtemp:
                        raise UserError("Suhu bawah setelah masak di bawah suhu standard BBT")
                else:
                    if self.tempafterbottom<self.standardtemp:
                        raise UserError("Suhu bawah setelah masak di bawah suhu standard BBT")
             
            return super(cooker, self).write(vals)
#             res_id = models.Model.create(self, vals)
#             return res_id
        else:
            raise UserError("Unauthorized User!")

    def _get_section_id(self):
        xuid = self.env.uid
#        cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL1="select a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
  
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
          
        for def_lokasi in rc_lokasi:
#            (xpabrik_id,xsection_id)=def_lokasi
            (xsection_id,)=def_lokasi
          
        return xsection_id
            
#     @api.constrains('tempaftertop')
#     def _constrains_tempAfterTop(self):
#         if self.tempaftertop:
#             if self.tempaftertop < self.standardtemp and self.tempaftertop==0:
#                 raise UserError("Suhu atas di bawah standart")
#         else:
#             print(self.tempaftertop)
             
#     @api.onchange('productiondate')
#     def onchange_productiondate(self):
#         domain = []
#         if self.productiondate:
#             domain.append(('productiondate','=',self.productiondate))
#         return {'domain':{'nobasket_id':domain}}

#     @api.one
#     def _list_basket(self):
#         xbasket=""
#         for xdetail in self.basket_id:
#             if xdetail.label:
#                 if xbasket=="":
#                     xbasket=xdetail.label
#                 else:
#                     xbasket=xbasket+", "+xdetail.label
#          
#         self.list_basket=xbasket

     
    def open_nobasket(self):
        return {
            'name'      : 'Basket ID',
            'res_model' : 'sis.cooker.basket',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'tree',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_traceability.sis_cooker_basket_tree').id,
            'nodestroy' : False,
            'target'    : 'new',
            'context'   : {'default_rel_cooker':self.id, 'default_productiondate':self.productiondate, 'default_location':self.location},
            'domain'    : [('rel_cooker','=',self.id)],      
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

#     @api.constrains('nopotong')
#     def _constrains_no_potong(self):
#         if self.nopotong:
#             cSQL1="select distinct no_potong from sis_cutting where productiondate='"+self.productiondate+"' and location='"+self.location+"'"
#             cSQL2=" and no_potong="+str(self.nopotong)
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
#                     raise UserError("No. Potong : "+str(self.nopotong)+" tidak ditemukan!\nDaftar No. Potong pada Tgl. Produksi : "+self.productiondate+" :\n"+xdata_nopotong)
#             
#             else:
#                 raise UserError("No. Potong pada Tgl. Produksi : "+self.productiondate+" : tidak tersedia!\nPilih Tgl. Produksi yang lain.")

    @api.constrains('nocooking')
    def _constrains_no_cooking(self):
        if self.nocooking:
            cSQL1="select distinct nocooking from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"'"
            cSQL2=" and nocooking="+str(self.nocooking)
           
            self.env.cr.execute(cSQL1+cSQL2)
            rec=self.env.cr.fetchall()
            if len(rec)>1:
                    raise UserError("Pada Tgl. Produksi "+self.productiondate+" No. Cooking ["+str(self.nocooking)+"] sudah diinput!!")

#     @api.constrains('steamon')
#     def _constrains_steamon(self):
#         cSQL1="select max(nocooking) from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"' and nocooker="+str(self.nocooker) 
#         self.env.cr.execute(cSQL1)
#         r_data=self.env.cr.fetchall()
#         if len(r_data)>0:
#             for dt_maxcooking in r_data:
#                 (xmaxcooking,)=dt_maxcooking
#             
#             if xmaxcooking:
#                 cSQL2="select steamoff from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"' and nocooker="+str(self.nocooker)+" and nocooking="+str(xmaxcooking)
#          
#                 self.env.cr.execute(cSQL2)
#                 r_data=self.env.cr.fetchall()
#                 
#                 if len(r_data)>0:
#                     for dt_steamoff in r_data:
#                         (xsteamoff,)=dt_steamoff
#     
#                     if datetime.strptime(self.steamon, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+420) < datetime.strptime(xsteamoff, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+421):
#                         raise UserError("Periksa kolom Steam On.\nCooker : "+str(self.nocooker)+", Steam On harus di atas "+str(datetime.strptime(xsteamoff, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+421)))
# 
# 
#     @api.constrains('startshowertime')
#     def _constrains_startshowertime(self):
#         cSQL="select max(nocooking) from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"' and nocooker="+str(self.nocooker) 
#         self.env.cr.execute(cSQL)
#         r_data=self.env.cr.fetchall()
#         if len(r_data)>0:
#             for dt_maxcooking in r_data:
#                 (xmaxcooking,)=dt_maxcooking
#               
#             if xmaxcooking:
#                 cSQL="select stopshowertime from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"' and nocooker="+str(self.nocooker)+" and nocooking="+str(xmaxcooking)
#            
#                 self.env.cr.execute(cSQL)
#                 r_data=self.env.cr.fetchall()
#                   
#                 if len(r_data)>0:
#                     for dt_showeroff in r_data:
#                         (xshoweroff,)=dt_showeroff
#       
#                     if datetime.strptime(self.startshowertime, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+420) < datetime.strptime(xshoweroff, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+421):
#                         raise UserError("Periksa kolom Jam Mulai Showering.\nCooker : "+str(self.nocooker)+", Jam Mulai Showering harus di atas "+str(datetime.strptime(xshoweroff, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+421)))

                         
#     @api.one          
#     @api.depends('location')
#     def _cooking_id(self):
#         if self.location:
#             tanggal=self.productiondate
#             loc = self.location 
#             rec=self.env['sis.cooker'].search([('location','=',loc),('productiondate','=',tanggal)])
#             no_urut = len(rec)
#             self.nocooking=no_urut

    @api.one
    @api.depends('vent_closed','steamoff')
    def _durasi_masak(self):
        if self.vent_closed and self.steamoff:
            t3 = 0
            t1 = datetime.strptime(self.vent_closed, "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(self.steamoff, "%Y-%m-%d %H:%M:%S")
            if t2 > t1:
                t3 = t2-t1
            
            if t3!=0: 
                self.cookingtime = float(t3.days) * 24 + (float(t3.seconds) / 3600)

    @api.one
    @api.depends('steamon')
    def _vent_tutup(self):
        if self.steamon:
            self.vent_closed=datetime.strptime(self.steamon, "%Y-%m-%d %H:%M:%S")+relativedelta(minutes =+13)
            
    @api.multi
    def unlink(self):
        for me_id in self :
            cSQL1="delete from sis_cooker_basket where rel_cooker="+str(me_id.id)+""
            
            self.env.cr.execute(cSQL1)           
                
            return super(cooker, self).unlink()
    
    