import re
from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class sis_thawing_header(models.Model):
    _inherit    = ['mail.thread']
    _name       ='sis.defrost.header'
    _rec_name    ='defrost_id'
    _order      ='tgl_produksi desc'

    defrost_id      = fields.Char(string="Defrost ID", size=16, default='/')
    tgl_produksi    = fields.Date(string="Tanggal Produksi",required=True, default=fields.Datetime.now())
#    tgl_produksi = fields.Selection(lambda self: self._get_tgl_produksi(),string="Tgl. Produksi", required=True)
    pabrik_id       = fields.Char(string="Lokasi", size=4, compute="_get_pabrik_id", store=True)
    nopotong_header = fields.Char(string="No Potong", size=4, compute="_get_nopotong", store=True)
#    pabrik_id = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')], required=True, track_visibility="onchange")
#     tgl_start       = fields.Datetime(string="Tanggal Mulai", required=True, default=fields.Datetime.now(), track_visibility="onchange")
#     tgl_finish      = fields.Datetime(string="Tanggal Selesai", required=True, default=fields.Datetime.now(), track_visibility="onchange")
#     shift           = fields.Selection(string="Shift", selection=[('1', 'Pagi'),('2', 'Malam')], required=True, track_visibility="onchange")
    defrost_state   = fields.Selection([('draft','Draft'),('confirm','Confirmed')], string='State', default='draft')
    user_checker = fields.Boolean(string="Checker", compute="_checker")
    user_unchecker = fields.Boolean(string="Unchecker", compute="_unchecker")
    defrost_detail  = fields.One2many('sis.defrost.detail', 'detail_id', string='Detail ID')
    header_status = fields.Boolean(string="status", default=0)
    #no_potong = fields.Selection(lambda self: self._get_potong(),string="No. Potong", required=True, store=True)
    #no_potong = fields.Integer(string="No. Potong", required=True)

    @api.one
    def _get_nopotong(self):
        xnopotong=""
        for xdetail in self.defrost_detail:
            if xdetail.no_potong:
                if xnopotong=="":
                    xnopotong=str(xdetail.no_potong)
                    temp = xdetail.no_potong
                else:
                    if temp != xdetail.no_potong:                        
                        temp = xdetail.no_potong
                        xnopotong=xnopotong+", "+str(xdetail.no_potong)
         
        self.nopotong_header=xnopotong
        
    @api.depends('tgl_produksi')
    def _checker(self):
        self.user_checker=False

        xuid = self.env.uid
        cSQL1="select d.checker from hr_employee as a, res_users as b, res_partner as c, hr_employee as d "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id and d.name=c.name " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_check=self.env.cr.fetchall()
        if len(rc_check)==0:
            self.user_checker=False
        else:
            for cs_checker in rc_check:
                    (xchecker,)=cs_checker
            self.user_checker=xchecker
                
                
    @api.depends('tgl_produksi')
    def _unchecker(self):
        xuid = self.env.uid
        cSQL1="select d.unchecker from hr_employee as a, res_users as b, res_partner as c, hr_employee as d "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id and d.name=c.name " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_uncheck=self.env.cr.fetchall()
        if len(rc_uncheck)==0:
            self.user_unchecker=False
        else:
            for cs_unchecker in rc_uncheck:
                (xunchecker,)=cs_unchecker
            self.user_unchecker=xunchecker

    @api.one
    @api.depends('tgl_produksi')
    def _get_pabrik_id(self):
        if self.tgl_produksi:
            xuid = self.env.uid
            cSQL1="select a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
    
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
            
            for def_lokasi in rc_lokasi:
                (xpabrik_id,)=def_lokasi
            
            self.pabrik_id=xpabrik_id
        
        
    @api.model
    def _get_tgl_produksi(self):
        lst_tglprod=list()
        
#        self.env.cr.execute("select distinct tgl_produksi from sis_fish_status_header")
        cSQL1="select distinct a.tgl_produksi from sis_fish_status_header as a, sis_cs_detail as b, sis_fish_status as c "
        cSQL2="where b.status_id=a.id and c.barcode_no=b.barcode_no and (c.quantity-b.quantity)>0"
        self.env.cr.execute(cSQL1+cSQL2)
        rc_tglprod=self.env.cr.fetchall()
        
        if len(rc_tglprod)==0:
            raise UserError("Tanggal Produksi belum diinput!")
        else:
            for def_tglprod in rc_tglprod:
                (xtglprod,)=def_tglprod
                lst_tglprod.append((xtglprod, xtglprod))
            
            return lst_tglprod

#     @api.model
#     def _get_potong(self):
#         lst_potong=list()
#         
#         self.env.cr.execute("select * from sis_defrost_detail")
#         rc_def=self.env.cr.fetchall()
#         
#         if len(rc_def)==0:
#             self.env.cr.execute("select distinct no_potong from sis_fish_status_history order by no_potong")
#             rc_potong=self.env.cr.fetchall()
#         else:
#             self.env.cr.execute("select distinct a.no_potong from sis_fish_status_history as a, sis_defrost_detail as b where a.barcode_no<>b.barcode_no order by a.no_potong")
#             rc_potong=self.env.cr.fetchall()
# 
#                   
#         for def_potong in rc_potong:
#             (xpotong,)=def_potong
#             lst_potong.append((xpotong, xpotong))
#         
#         return lst_potong
            
    def _get_defrost_id(self,pabrik):
        if pabrik:
            tanggal=datetime.now()
            d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
            d_tahun = d_to.year
            d_bulan=""
            no_prefix=""
            if d_to.month<10 :
                d_bulan="0"+str(d_to.month)
            else :
                d_bulan=str(d_to.month)
         
            if pabrik=="ATI1":
                no_prefix = "DEF1/"+str(d_tahun)+str(d_bulan)+"-"
            elif pabrik=="ATI2":
                no_prefix = "DEF2/"+str(d_tahun)+str(d_bulan)+"-"
 
            rec=self.env['sis.defrost.header'].search([('defrost_id','ilike',no_prefix)])
            if len(rec)>0:
                self.env.cr.execute("select max(cast(substring(defrost_id,13,4) as integer)) from sis_defrost_header where defrost_id like '"+no_prefix+"%'")
                rc=self.env.cr.fetchall()
                  
                for def_max in rc :
                    (x,)=def_max
                
                no_urut=x+1
                if no_urut<10:
                    defros_id=no_prefix+"000"+str(no_urut)
                elif no_urut>9 and no_urut<100:
                    defros_id=no_prefix+"00"+str(no_urut)
                elif no_urut>999 and no_urut<1000:
                    defros_id=no_prefix+"0"+str(no_urut)
                else:
                    defros_id=no_prefix+str(no_urut)
            else:
                no_urut=1
                defros_id=no_prefix+"000"+str(no_urut)
 
            return defros_id

    @api.model
#    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        xpabrik_id, xsection_id=self._get_save_pabrik_id()
        
        z=self._get_save_barcode(vals['tgl_produksi'],xpabrik_id)
        if z==True:
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":
                no_defrost=self._get_defrost_id(xpabrik_id)
                vals.update({'defrost_id':no_defrost})
                
#                 self._get_nopotong()
                
                res_id = models.Model.create(self, vals)
                return res_id
            else:
                raise UserError("Unauthorized User!")
        else:
            raise UserError("Data CS pada tanggal Produksi "+vals['tgl_produksi']+" tidak ada/sudah diinput ke defrost")

    @api.multi
    def write(self, vals):
        for me_id in self :
            xpabrik_id, xsection_id=self._get_save_pabrik_id()
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":

                if me_id.defrost_state != 'draft' :
                    if vals.get('defrost_state') and vals['defrost_state']=='draft':
                        return super(sis_thawing_header, self).write(vals)
                    else:
                        raise UserError("Cannot update!")
                else:
                    vals_defrost={}
                
                    if vals.get('tgl_produksi'):
                        if vals.get('tgl_produksi')!=self.tgl_produksi:
                            raise UserError("Tgl. Produksi : "+self.tgl_produksi+" can not update!")
                    if vals.get('shift'):
                        vals_defrost.update({'shift':vals['shift']})
                    if vals.get('tgl_start'):             
                        vals_defrost.update({'tgl_start':vals['tgl_start']})
                    if vals.get('tgl_finish'):             
                        vals_defrost.update({'tgl_finish':vals['tgl_finish']})
                
                    cr_data=self.env['sis.defrost.header'].search([('defrost_id','=',self.defrost_id)])
                    if len(cr_data)>0:
                        xdef_id=cr_data.id
                            
                    cr_data2=self.env['sis.defrost.detail'].search([('detail_id','=',xdef_id)])
                    if len(cr_data2)>0:
                        for x in cr_data2:
                            x.write(vals_defrost)
                
                    return super(sis_thawing_header, self).write(vals)
        else:
            raise UserError("Unauthorized User!")
    
    @api.multi
    def unlink(self):
        for me_id in self :
            if me_id.defrost_state != 'draft' :
                raise UserError("Cannot delete!")
            else:
                rs=self.env['sis.defrost.detail'].search([('detail_id','=',me_id.id)])
                for defrost in rs:
                    defrost.unlink()
                
                return super(sis_thawing_header, self).unlink()

    @api.multi
    def action_confirm(self):
        for me_id in self :
            if me_id.defrost_state == 'draft':
                me_id.write({'defrost_state':'confirm'})
     
    @api.multi
    def action_unconfirm(self):
        for me_id in self :
            if me_id.defrost_state == 'confirm':
                me_id.write({'defrost_state':'draft'})


    def _get_save_pabrik_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
        
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
        
        return xpabrik_id,xsection_id

    def _get_save_barcode(self, tgl_produksi, pabrik_id):
        cSQL1="select distinct a.barcode_no, a.no_potong, a.fish_box_no, a.quantity, a.tgl_keluar, a.hatch_no "
        cSQL2="from sis_cs_detail a left join sis_defrost_detail b on b.barcode_no=a.barcode_no and b.quantity=a.quantity "
        cSQL3="where b.no_tangki is null and b.quantity is null and a.tgl_produksi='"+tgl_produksi+"' and a.pabrik_id='"+pabrik_id+"'"
        self.env.cr.execute(cSQL1+cSQL2+cSQL3)
        the_barcode=self.env.cr.fetchall()
        if len(the_barcode)==0:
            return False
        else:
            return True

    def get_barcode(self):
        if self.tgl_produksi:
            cSQL1="select distinct a.barcode_no, a.no_potong, a.fish_box_no, a.quantity, a.tgl_keluar, a.hatch_no "
            cSQL2="from sis_cs_detail a left join sis_defrost_detail b on b.barcode_no=a.barcode_no and b.quantity=a.quantity "
            cSQL3="where b.no_tangki is null and b.quantity is null and a.tgl_produksi='"+self.tgl_produksi+"' and a.pabrik_id='"+self.pabrik_id+"' and a.real_itemno not like '%L' and a.real_itemno not like '%F'"
            self.env.cr.execute(cSQL1+cSQL2+cSQL3)
            the_barcode=self.env.cr.fetchall()
            if len(the_barcode)>0:
                new_lines = self.env['sis.defrost.detail']
                for ff_data in the_barcode:
                    (xbarcode,xnopotong,xfish_box_no,xquantity, xtgl_keluar, xhatch)=ff_data
#                     for x in range(2):
                    if xhatch[-3:]=="P&L":
                        xstatus_pl=True
                    else:
                        xstatus_pl=False
                    if xhatch[-3:]=="P&L":
                        xstatus_pl=True
                    else:
                        xstatus_pl=False
                     
                    vals = {'barcode_no'    : xbarcode,
                            'tgl_keluar'    : xtgl_keluar,
                            'quantity'      : xquantity,
                            'no_potong'     : xnopotong,
                            'fish_box_no'   : xfish_box_no,
                            'no_tangki'     : "-",
                            'suhu_before'   : 0,
                            'suhu_after'    : 0,
                            'tgl_produksi'  : self.tgl_produksi,
                            'pabrik_id'     : self.pabrik_id,
                            'hatch_no'      : xhatch,
                            'status_pl'     : xstatus_pl
                            }
                    new_lines += new_lines.new(vals)
                self.defrost_detail = new_lines
                self.header_status = 1

class sis_thawing_detail(models.Model):
    _name='sis.defrost.detail'
    _rec_name    ='no_tangki'
    _order      ='no_potong, barcode_no'

    detail_id       = fields.Many2one('sis.defrost.header', string="Detail ID")
    defrost_link_id = fields.Many2one('sis.cs.detail', string="Defrost Link ID")
    #trace_detail_id = fields.Many2one('sis.trace.header', string="Detail Defrost")
    tgl_produksi    = fields.Date(string="Tanggal Produksi")
    pabrik_id       = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')])
    fresh_fish      = fields.Selection(string="Fish Type", selection=[(True, 'Fresh'),(False, 'Frozen')])
    tgl_keluar      = fields.Datetime(string="Tanggal Keluar CS")
    barcode_no      = fields.Char(string="Barcode No",size=40,required=True)
    no_tangki       = fields.Char(string="No. Tangki", size=7, required=True)
    no_line         = fields.Integer(string="No. Line")
    no_potong       = fields.Integer(related="defrost_link_id.no_potong",string="No. Potong", store=True)
    fish_box_no     = fields.Char(size=20,string="Fish Box No.",store=True)
    hatch_no        = fields.Char(size=100,string="Hatch No.")
    quantity        = fields.Float(compute="update_qty_cs",string='Quantity',store=True)
    suhu_before     = fields.Float(string="Suhu Before", required=True)     
    tgl_start       = fields.Datetime(string="Tanggal Mulai", default=fields.Datetime.now, required=True)
    suhu_after      = fields.Float(string="Suhu Before", required=True)     
    tgl_finish      = fields.Datetime(string="Tanggal Selesai", default=fields.Datetime.now, required=True)
    tgl_tuang       = fields.Datetime(string="Tanggal Tuang Hoper", default=fields.Datetime.now, required=True)
    remark          = fields.Char(string="Remark",size=100, default='-', required=True)
    durasi_jam      = fields.Float(string="Durasi", compute="_get_durasi", store=True)
    status_pl       = fields.Boolean(string="Pole & Line", compute="_update_hatch", store=True)
    #cutting_id      = fields.One2many('sis.cutting','notangki_id', string="No Tangki")
    tangki_cut      = fields.One2many('sis.cutting.tangki', 'rel_defrost', string='Tangki')
#    cutting_id      = fields.One2many('sis.cutting2','no_potong_def', string="no_potong_def")

    @api.one
    @api.depends('tgl_keluar','tgl_tuang')
    def _get_durasi(self):
        if self.tgl_keluar and self.tgl_tuang:
            t1 = datetime.strptime(self.tgl_keluar, "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(self.tgl_tuang, "%Y-%m-%d %H:%M:%S")
            if t2 > t1:
                t3 = t2-t1
            else:
                t3 = t1 - t2
             
            self.durasi_jam = float(t3.days) * 24 + (float(t3.seconds) / 3600)
            #float(t3.days) * 24 + (float(t3.seconds) / 3600)

    @api.onchange('barcode_no')
    def onchange_barcode_no(self):
        if self.barcode_no:
            rec=self.env['sis.cs.detail'].search([('barcode_no','=',self.barcode_no),('no_potong','=',self.no_potong),('tgl_produksi','=',self.detail_id.tgl_produksi)])
            if len(rec)==0:
                raise UserError("Barcode : "+self.barcode_no+" tidak untuk Tanggal Produksi "+self.detail_id.tgl_produksi)
            

    @api.onchange('tgl_produksi')
    def onchange_defrost_line(self):
        domain = []
        domain.append(('tgl_produksi','=',self.detail_id.tgl_produksi))
        return {'domain':{'defrost_link_id':domain}}


    @api.onchange('no_tangki')
    def regexnotangki(self):
        if self.no_tangki:
            regex = '^[0-9]*$'
            if(re.search(regex, self.no_tangki)):
                exit 
            else:
                raise UserError('No Tangki harus menggunakan Angka')
            
    
    @api.onchange('barcode_no')
    def _get_header_data(self):
        if self.barcode_no:
            self.tgl_produksi=self.detail_id.tgl_produksi
            self.pabrik_id=self.detail_id.pabrik_id

#             self.tgl_start=self.detail_id.tgl_start
#             self.tgl_finish=self.detail_id.tgl_finish
#             self.shift=self.detail_id.shift
    
   
            
#     def _get_pabrik_id(self):
#         xuid = self.env.uid
#         cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
#         cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
# 
#         self.env.cr.execute(cSQL1+cSQL2+"and b.id="+xuid)
#         rc_lokasi=self.env.cr.fetchall()
#         
#         for def_lokasi in rc_lokasi:
#                 (xpabrik_id,)=def_lokasi
#         
#         return xpabrik_id
        
#     @api.one
#     @api.depends('defrost_link_id')
#     def update_qty_cs(self):
#         xqty=0
#         if self.no_potong and self.detail_id.tgl_produksi:
#             cSQL="select quantity from sis_cs_detail "
#             self.env.cr.execute(cSQL+"where barcode_no='"+self.barcode_no+"' and no_potong='"+str(self.no_potong)+"' and tgl_produksi='"+self.detail_id.tgl_produksi+"'")
#             rec_fish=self.env.cr.fetchall()
#             for qty_data in rec_fish:
#                 (xqty,)=qty_data
#                 
#             self.quantity=xqty
# 
#     @api.one
#     @api.depends('hatch_no')
#     def _update_hatch(self):
#         if self.hatch_no[-3:]=="P&L":
#             self.status_pl=True
#         else:
#             self.status_pl=False
                        
#     def get_def1(self, n):
#         count = n-1
#         prime = True
#         while(count>1):
#             if n % count==0:
#                 prime=False
#                 break
#             count=count-1
#         
#         return prime
# 
#     def get_def2(self, n):
#         count = 2
#         xfaktor=0
#         faktor=""
#         while(count<n):
#             if n % count==0:
#                 if faktor.strip()=="":
#                     faktor=str(count)
#                 else:    
#                     faktor=faktor+", "+str(count)
#                     
#                 if xfaktor==0:
#                     xfaktor=count
#                 else:
#                     if count<xfaktor:
#                         xfaktor=count
#                 
#             count=count+1
#         
#         raise UserError("Faktor : "+faktor+" - FPK : "+str(xfaktor))

#     def _get_trace_id(self,pabrik):
#         if pabrik:
#             tanggal=datetime.now()
#             d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
#             d_tahun = d_to.year
#             d_bulan=""
#             no_prefix=""
#             if d_to.month<10 :
#                 d_bulan="0"+str(d_to.month)
#             else :
#                 d_bulan=str(d_to.month)
#          
#             if pabrik=="ATI1":
#                 no_prefix = "T1/"+str(d_tahun)+str(d_bulan)+"-"
#             elif pabrik=="ATI2":
#                 no_prefix = "T2/"+str(d_tahun)+str(d_bulan)+"-"
#  
#             rec=self.env['sis.trace.header'].search([('trace_id','ilike',no_prefix)])
#             if len(rec)>0:
#                 self.env.cr.execute("select max(cast(substring(trace_id,11,2) as integer)) from sis_trace_header where trace_id like '"+no_prefix+"%'")
#                 rc=self.env.cr.fetchall()
#                   
#                 for def_max in rc :
#                     (x,)=def_max
#                 
#                 no_urut=x+1
#                 if x<10:
#                     trace_id=no_prefix+"0"+str(no_urut)
#                 else:
#                     trace_id=no_prefix+str(no_urut)
#             else:
#                 no_urut=1
#                 trace_id=no_prefix+"0"+str(no_urut)
#  
#             return trace_id

    
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self,vals):
#         if vals.get('defrost_link_id'):
#             cr_data=self.env['sis.cs.detail'].search([('id','=',vals.get('defrost_link_id'))])
#             if len(cr_data)>0:
                #for cs in cr_data:
                #self.env.cr.execute("update sis_cs_detail set status_def=0 where id="+str(vals.get('defrost_link_id')))
                    
#                    vals_data={'status_def':0}
#                    cs.write(vals_data)
                
#                 vals_defrost={
#                     'no_potong':cr_data.no_potong,
#                     'fish_box_no':cr_data.fish_box_no
#                     }
#                 vals.update(vals_defrost) 
                
#                 cr_th=self.env['sis.trace.header'].search([('tgl_produksi','=',cr_data.tgl_produksi),('pabrik_id','=',cr_data.pabrik_id)])
#                 if len(cr_th)>0:
#                     
#                     vals_defrost={
#                         'trace_detail_id':cr_th.id
#                         }
#                     vals.update(vals_defrost) 
#            res_id = models.Model.create(self, vals)
                #self.env.cr.execute("update sis_cs_detail set status_def=0 where id="+str(vals.get('defrost_link_id')))
    
#                 for cs in cr_data:
#                     vals_data={'status_def':1}
#                     cs.write(vals_data)
#            return res_id
        
    @api.multi
    def write(self, vals):
#         if self.detail_id.defrost_id:
#             cSQL1="select b.quantity from sis_fish_status_header as a, sis_cs_detail as b where b.cs_line_id=a.id and b.id<>'"+str(self.id)+"' and b.status_def=0 "
#             cSQL2="and b.barcode_no='"+self.barcode_no+"' and b.no_potong='"+str(self.no_potong)+"' and b.tgl_produksi='"+self.tgl_produksi+"' and a.cs_id='"+self.cs_line_id.cs_id+"'"
#   
#             self.env.cr.execute(cSQL1+cSQL2)
#             cr_data=self.env.cr.fetchall()
#       
#             if len(cr_data)==0:
                orders = self.mapped('detail_id')
                for order in orders:
                    order_lines = self.filtered(lambda x: x.detail_id == order)
                    msg = ""
                    for line in order_lines:
                        if vals.get('barcode_no'):
                            msg += "Barcode" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (line.barcode_no, vals['barcode_no'],)
                        if vals.get('no_tangki'):
                            msg += "No. Tangki" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_tangki), str(vals['no_tangki']),)
                        if vals.get('no_line'):
                            msg += "Line" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_line), str(vals['no_line']),)
                    
                    if msg!="":
                        order.message_post(body=msg)
                      
#                    vals.update({'tgl_produksi':self.cs_line_id.tgl_produksi})
                    return super(sis_thawing_detail, self).write(vals)
#             else:
#                 for r in cr_data:
#                     (r_quantity,)=r
#                     vals_data={
#                        'quantity':r_quantity+self.quantity
#                     }
#                 vals.update(vals_data)            
#                 return super(sis_cs_detail, self).write(vals)

    @api.multi
    def unlink(self):
#         cr_def=self.env['sis.defrost.detail'].search([('tgl_produksi','=',self.tgl_produksi),('pabrik_id','=',self.pabrik_id),('no_potong','=',self.no_potong),('barcode_no','=',self.barcode_no),('id','!=',self.id)])
#         if len(cr_def)==0:
#               
#             cr_data=self.env['sis.cs.detail'].search([('id','=',self.defrost_link_id.id),('tgl_produksi','=',self.tgl_produksi),('pabrik_id','=',self.pabrik_id),('no_potong','=',self.no_potong),('barcode_no','=',self.barcode_no)])
#             if len(cr_data)>0:
#                 for cs in cr_data:
#                     vals_data={'status_def':0}
#                     cs.write(vals_data)
#                
    
        orders = self.mapped('detail_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.detail_id == order)
            msg = ""
            for line in order_lines:
                msg += "Barcode" + ": %s <b>[ <i>deleted</i> ]</b><br/>" % (line.barcode_no,)
            if msg!="":
                order.message_post(body=msg)
        return super(sis_thawing_detail, self).unlink()

#     @api.multi
#     def name_get(self):
#         #print(self._context.get('notangki'))
#         result = []
#         for me in self :
#             if self._context.get('notangki')==1:
#                 _rec_name='no_tangki'
#                 result.append((me.id, "%s" % (me.no_tangki)))
# #                result.append((me.id, "%s [%s]" % (me.no_tangki, me.no_potong)))
#             else:
#                 _rec_name='no_potong'
#                 result.append((me.id, "%s" % (me.no_potong)))
#         return result
    
    def copydata(self):
        rdef=self.env['sis.defrost.detail'].search([('id','=',self.id)])
        if len(rdef)>0:
            self.env.cr.execute("select id from sis_cs_detail where tgl_produksi='"+rdef.tgl_produksi+"' and barcode_no='"+rdef.barcode_no+"' and no_potong="+str(rdef.no_potong)+" and pabrik_id='"+rdef.pabrik_id+"'")
            cs=self.env.cr.fetchall()
            if len(cs)>0:
                for def_data in cs:
                    (xid,)=def_data
 
                vals = {'tgl_produksi'   : rdef.tgl_produksi,
                        'pabrik_id'      : rdef.pabrik_id,
                        'fresh_fish'     : rdef.fresh_fish,
                        'tgl_keluar'     : rdef.tgl_keluar,
                        'barcode_no'     : rdef.barcode_no,
                        'no_tangki'      : rdef.no_tangki,
                        'no_line'        : rdef.no_line,
                        'no_potong'      : rdef.no_potong,
                        'fish_box_no'    : rdef.fish_box_no,
                        'quantity'       : rdef.quantity,
                        'suhu_before'    : rdef.suhu_before,
                        'tgl_start'      : rdef.tgl_start,
                        'suhu_after'     : rdef.suhu_after,
                        'tgl_finish'     : rdef.tgl_finish,
                        'tgl_tuang'      : rdef.tgl_tuang,
                        'remark'         : rdef.remark,
                        'durasi_jam'     : rdef.durasi_jam,
                        'status_pl'      : rdef.status_pl,
                        'defrost_link_id': xid,
                        'detail_id'      : self.detail_id.id
                    }
                self.env['sis.defrost.detail'].create(vals)
