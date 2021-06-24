from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class cooker(models.Model):
    _name  ='sis.cooker'
    _order = "productiondate desc, nocooking"
    
      
    basket_id       = fields.One2many('sis.cooker.basket', 'rel_cooker', string='Basket ID')
        
    productiondate  = fields.Date(string='Tanggal Produksi', required=True, default=fields.Datetime.now)
    nocooking       = fields.Integer(string='No Cooking', default=0, required=True)
    nocooker        = fields.Integer(string='No Cooker', default=0, required=True)  
    list_basket     = fields.Char(size=100, string='Basket ID', compute='_list_basket')
    list_label      = fields.Char(size=100, string='No. Urut / Label', compute='_list_label')
    kindoffish      = fields.Char(string='Jenis Ikan')
    size            = fields.Char(string='Ukuran')
    total_tray      = fields.Integer(string='Total Tray', required=True, default=0)
    cookingtime     = fields.Float(string='Durasi Masak', compute='_durasi_masak', store=True)
    cookingtime_real= fields.Char(string='Durasi Masak Real', compute='_durasi_masakr', store=True)
    cookingtemp     = fields.Float(string='Suhu Masak', required=True, default=105)
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
    coolingroomline = fields.Integer(string='Cooling Room Line')
    remark          = fields.Char(size=50, string='Remark', required=True, default='-')
    location        = fields.Char(size=4, string='Lokasi', compute='_get_pabrik_id', store=True) 
    status_input    = fields.Boolean(string="Status Input", default=True)
    status_pnl    = fields.Boolean(string='Status P&L', compute='_get_statuspnl', store=True)
    
    @api.one
    @api.depends('cookingtime')
    def _durasi_masakr(self):
        if self.cookingtime:
            self.cookingtime_real = '{0:02.0f}:{1:02.0f}'.format(*divmod(float(self.cookingtime) * 60, 60))
        
    @api.one
    @api.depends('vent_closed','steamoff')
    def _durasi_masak(self):
        if self.vent_closed and self.steamoff:
            t6 = 0
            t1 = datetime.strptime(self.vent_closed, "%Y-%m-%d %H:%M:%S")
            temp1 = t1.strftime("%Y-%m-%d %H:%M")
            t4 = datetime.strptime(temp1, "%Y-%m-%d %H:%M")
            t2 = datetime.strptime(self.steamoff, "%Y-%m-%d %H:%M:%S")
            temp2 = t2.strftime("%Y-%m-%d %H:%M")
            t5 = datetime.strptime(temp2, "%Y-%m-%d %H:%M")
            
            if t5 > t4:
                t6 = t5-t4            
            if t6!=0: 
                self.cookingtime = float(t6.days) * 24 + (float(t6.seconds) / 3600)
                
    @api.one
    @api.depends('basket_id')
    def _get_statuspnl(self):
        if self.basket_id:
            for rec in self.basket_id:
                self.status_pnl=rec.status_pnl
        
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
            
        self.list_label=xlabel
    
    @api.one
    @api.depends('nocooker')
    def _onchangeShowerLine(self):
        if self.nocooker:
            self.showerline=self.nocooker

    @api.model
    def create(self,vals):
        xpabrik_id, xsection_id=self._get_section_id()
#         if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cooker":
        if vals['nocooking']==0 or vals['nocooker']==0 or vals['total_tray']==0 or vals['steamoff']==False or vals['tempbeforetop']==0 or vals['tempbeforecenter']==0 or vals['tempbeforebottom']==0 or vals['tempaftertop']==0 or vals['tempaftercenter']==0 or vals['tempafterbottom']==0  or vals['startshowertime']==False or vals['stopshowertime']==False or vals['aftershowertemp1']==0 or vals['aftershowertemp2']==0 or vals['aftershowertemp3']==0 or vals['coolingroomline']==0:
            vals['status_input']=False
        else:
            vals['status_input']=True
        
        if vals['tempaftertop']<vals['standardtemp'] or vals['tempaftercenter']<vals['standardtemp'] or vals['tempafterbottom']<vals['standardtemp']:
            raise UserError("Suhu atas di bawah standart")
        res_id = models.Model.create(self, vals)
        return res_id
#         else:
#             raise UserError("Unauthorized User!"+xsection_id)
#     
    @api.multi
    def write(self,vals):
        xpabrik_id, xsection_id=self._get_section_id()
#         if xpabrik_id==self.location or xsection_id=="Admin":
#             if xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cooker" or xsection_id=="Admin":
                           
        cek=[0]
        
        if vals.get('nocooking')==0 or vals.get('nocooking'):
            if vals.get('nocooking')==0:
                cek[0]=0
            else:
                cek[0]=1
        elif self.nocooking==0:
            cek[0]=0
        else:
            cek[0]=1
             
        if vals.get('nocooker')==0 or vals.get('nocooker'):
            if vals.get('nocooker')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.nocooker==0:
            cek.append(0)
        else:
            cek.append(1)

        if vals.get('total_tray')==0 or vals.get('total_tray'):
            if vals.get('total_tray')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.total_tray==0:
            cek.append(0)
        else:
            cek.append(1)
              
        if vals.get('steamoff')==False or vals.get('steamoff'):
            if vals.get('steamoff')==False:
                cek.append(0)
            else:
                cek.append(1)
        elif self.steamoff==False:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('tempbeforetop')==0 or vals.get('tempbeforetop'):
            if vals.get('tempbeforetop')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.tempbeforetop==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('tempbeforecenter')==0 or vals.get('tempbeforecenter'):
            if vals.get('tempbeforecenter')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.tempbeforecenter==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('tempbeforebottom')==0 or vals.get('tempbeforebottom'):
            if vals.get('tempbeforebottom')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.tempbeforebottom==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('startshowertime')==False or vals.get('startshowertime'):
            if vals.get('startshowertime')==False:
                cek.append(0)
            else:
                cek.append(1)
        elif self.startshowertime==False:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('stopshowertime')==False or vals.get('stopshowertime'):
            if vals.get('stopshowertime')==False:
                cek.append(0)
            else:
                cek.append(1)
        elif self.startshowertime==False:
            cek.append(0)
        else:
            cek.append(1)
             
             
        if vals.get('aftershowertemp1')==0 or vals.get('aftershowertemp1'):
            if vals.get('aftershowertemp1')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.aftershowertemp1==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('aftershowertemp2')==0 or vals.get('aftershowertemp2'):
            if vals.get('aftershowertemp2')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.aftershowertemp2==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('aftershowertemp3')==0 or vals.get('aftershowertemp3'):
            if vals.get('aftershowertemp3')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.aftershowertemp3==0:
            cek.append(0)
        else:
            cek.append(1)
             
        if vals.get('coolingroomline')==0 or vals.get('coolingroomline'):
            if vals.get('coolingroomline')==0:
                cek.append(0)
            else:
                cek.append(1)
        elif self.coolingroomline==0:
            cek.append(0)
        else:
            cek.append(1)
        
        jml=0
             
        for i in cek: 
            jml=jml+i
            
        fullinput = "update sis_cooker set status_input=True where id="
        nofull = "update sis_cooker set status_input=False where id="
         
        if jml==13:
            self.env.cr.execute(fullinput+str(self.id))
        else:
            self.env.cr.execute(nofull+str(self.id))

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
#             else:
#                 raise UserError("Unauthorized User! "+xsection_id)
#         else:
#             raise UserError("Data "+self.location+" tidak bisa di edit oleh user "+xpabrik_id)

    def _get_section_id(self):
        xuid = self.env.uid
        cSQL1="select a.pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
  
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
          
        for def_lokasi in rc_lokasi:
            (xpabrik_id, xsection_id,)=def_lokasi
          
        return xpabrik_id, xsection_id
  

     
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

    @api.constrains('nocooking')
    def _constrains_no_cooking(self):
        if self.nocooking:
            cSQL1="select distinct nocooking from sis_cooker where productiondate='"+self.productiondate+"' and location='"+self.location+"'"
            cSQL2=" and nocooking="+str(self.nocooking)
           
            self.env.cr.execute(cSQL1+cSQL2)
            rec=self.env.cr.fetchall()
            if len(rec)>1:
                    raise UserError("Pada Tgl. Produksi "+self.productiondate+" No. Cooking ["+str(self.nocooking)+"] sudah diinput!!")

            
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
    
    