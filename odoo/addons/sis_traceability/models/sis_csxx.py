from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import tools

class sis_cs_header(models.Model):
    _inherit = ['mail.thread']
    _name = "sis.cs.header"
    _rec_name = "cs_id"
    _description = "Cold Storage"
    _order = "tgl_produksi desc, no_potong"

    cs_id = fields.Char(string="No. CS", size=15, default='/')
    tgl_produksi = fields.Date(string="Tanggal Produksi",required=True,default=datetime.now()+relativedelta(hours=7), track_visibility="onchange")
    pabrik_id = fields.Char(string="Lokasi", size=4, compute="_get_pabrik_id", store=True)
    cs_state = fields.Selection([('draft','Draft'),('confirm','Confirmed')], string='State', default='draft', track_visibility="onchange")
    no_potong=fields.Integer(string="No. Potong", default=0, required=True)
    total_tonase=fields.Float(string="Tonase", compute="_save_tonase")
#    invoice = fields.Boolean(string="Invoice", track_visibility="onchange")
    invoice = fields.Selection([('1','Fresh Fish'),('2','Frozen Fish'),('3','Frozen Loin/Flake')], default='2', string='Kategori', track_visibility="onchange")
#    invoice = fields.Selection([('1','Fish'),('2','Loin/Flake')], string='Kategori', track_visibility="onchange")
    fresh_fish = fields.Boolean(string="Fresh", track_visibility="onchange")
    invoice_no = fields.Char(string="No. Invoice", size=25, track_visibility="onchange")
    user_checker = fields.Boolean(string="Checker", compute="_checker")
    user_unchecker = fields.Boolean(string="Unchecker", compute="_unchecker")
    cs_line_id = fields.One2many('sis.cs.detail', 'cs_line_id', string='CS Lines')
    
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

    @api.depends('tgl_produksi')
    def _get_pabrik_id(self):
        if self.tgl_produksi:
            xuid = self.env.uid
            cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.pabrik_id=xpabrik_id

    @api.one
    def _save_tonase(self):
        xtonase=0
        for xdetail in self.cs_line_id:
            if xdetail.quantity and xdetail.quantity>0:
                xtonase=xtonase+xdetail.quantity
         
        self.total_tonase=xtonase

    def _get_save_pabrik_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id,a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
        
        for def_lokasi in rc_lokasi:
                (xpabrik_id,xsection_id)=def_lokasi
        
        return xpabrik_id,xsection_id
     
    def get_data_fresh_fish(self):
        if self.invoice_no:
            self.env['sis.cs.detail'].search([('barcode_no','=',self.invoice_no),('cs_line_id','=',self.id)]).unlink()
            cField="a.item_no,a.description,a.lot_no,a.vessel_no,a.hatch_no,a.voyage_no,a.quantity,a.status,a.fish_box_no, a.po"
            cSQL1="select "+cField+" from sis_fish_fresh_inv a left join sis_cs_detail b on a.invoice_no=b.barcode_no and a.quantity=b.quantity "
            cSQL2=" where b.barcode_no is null and a.invoice_no='"+str(self.invoice_no)+"'"
            self.env.cr.execute(cSQL1+cSQL2)
            fresh_fish_data=self.env.cr.fetchall()
            if len(fresh_fish_data)>0:
                new_lines = self.env['sis.cs.detail']
                for ff_data in fresh_fish_data:
                    (xitem_no,xdescription,xno_lot,xvessel_no,xhatch_no,xvoyage_no,xquantity,xstatus,xfish_box,xpo)=ff_data
                    vals = {'barcode_no'    : self.invoice_no,
                            'tgl_keluar'    : datetime.now(),
                            'fresh_fish'    : '1',
                            'no_potong'     : self.cs_line_id.no_potong,
                            'item_no'       : xitem_no,
                            'description'   : xdescription,
                            'lot_no'        : xno_lot,
                            'vessel_no'     : xvessel_no,
                            'hatch_no'      : xhatch_no,
                            'voyage_no'     : xvoyage_no,
                            'quantity'      : xquantity,
                            'status'        : xstatus,
                            'fish_box_no'   : xfish_box,
                            'tgl_produksi'  : self.tgl_produksi,
                            'pabrik_id'     : self.pabrik_id,
                            'po'            : xpo
                            }
                    new_lines += new_lines.new(vals)
#                self.fish_status_detail = new_lines
                self.cs_line_id = new_lines
            else:
                raise UserError("Invoice "+str(self.invoice_no)+" tidak ada!")
        else:
            self.cs_line_id.ids()
     
    def _get_prefix(self,pabrik):
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
                no_prefix = "CS1/"+str(d_tahun)+str(d_bulan)+"-"
            elif pabrik=="ATI2":
                no_prefix = "CS2/"+str(d_tahun)+str(d_bulan)+"-"
 
            rec=self.env['sis.cs.header'].search([('cs_id','ilike',no_prefix)])
            if len(rec)>0:
                self.env.cr.execute("select max(cast(substring(cs_id,12,4) as integer)) from sis_cs_header where cs_id like '"+no_prefix+"%'")
                rc=self.env.cr.fetchall()
                  
                for b in rc :
                    (x,)=b
                no_urut=x+1
                if no_urut<10:
                    cs_id=no_prefix+"000"+str(no_urut)
                elif no_urut>9 and no_urut<100:
                    cs_id=no_prefix+"00"+str(no_urut)
                elif no_urut>999 and no_urut<1000:
                    cs_id=no_prefix+"0"+str(no_urut)
                else:
                    cs_id=no_prefix+str(no_urut)
            else:
                no_urut=1
                cs_id=no_prefix+"000"+str(no_urut)
 
            return cs_id
     
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        xpabrik_id,xsection_id=self._get_save_pabrik_id()
        #xtonase=self._save_tonase()
        if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="CS":
            csid=self._get_prefix(xpabrik_id)
            vals.update({'cs_id':csid, 'pabrik_id':xpabrik_id}) 
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            raise UserError("Unauthorized User!")
 
    @api.multi
    def action_confirm(self):
        for me_id in self :
            if me_id.cs_state == 'draft':
                me_id.write({'cs_state':'confirm'})
     
    @api.multi
    def action_unconfirm(self):
        for me_id in self :
            if me_id.cs_state == 'confirm':
                me_id.write({'cs_state':'draft'})
#                self.env.cr.execute("update sis_cs_header set cs_state='draft' where cs_id='"+str(me_id.cs_id)+"'")
 
    @api.multi
    def unlink(self):
        for me_id in self :
            trace_id=0
            if me_id.cs_state != 'draft' :
                raise UserError("Cannot delete!")
            else:
#                 self.env.cr.execute("select distinct trace_detail_id from sis_cs_detail where cs_line_id='"+str(me_id.id)+"'")
#                 cs=self.env.cr.fetchall()
#                 for rec_cs in cs :
#                     (trace_id,)=rec_cs
                
                self.env.cr.execute("delete from sis_cs_detail where cs_line_id='"+str(me_id.id)+"'")
#                rec=self.env['sis.cs.detail'].search([('cs_line_id','=',me_id.id)])
                rec=self.env['sis.cs.detail'].search([('tgl_produksi','=',me_id.tgl_produksi)])
                if len(rec)==0:
                    self.env.cr.execute("delete from sis_trace_header where id="+str(trace_id))
 
        return super(sis_cs_header, self).unlink()
     
    @api.multi
    def write(self, vals):
        for me_id in self :
            xpabrik_id,xsection_id=self._get_save_pabrik_id()
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="CS":
                if me_id.cs_state != 'draft' :
                    if vals.get('cs_state') and vals['cs_state']=='draft':
                        return super(sis_cs_header, self).write(vals)
                    else:
                        raise UserError("Cannot update!")
                else:
                        if vals.get('no_potong') and vals.get('no_potong')>0:                
                            self.env.cr.execute("update sis_cs_detail set no_potong="+str(vals['no_potong'])+" where cs_line_id='"+str(me_id.id)+"'")
                        super(sis_cs_header, self).write(vals)
            else:
                    raise UserError("Unauthorized User!")

                

class sis_cs_detail(models.Model):
    _name='sis.cs.detail'
    _rec_name='fish_box_no'
    
    cs_line_id = fields.Many2one('sis.cs.header', string="CS Lines", ondelete='cascade', required=True)
    defrost_detail = fields.One2many('sis.defrost.detail', 'defrost_link_id', string='Defrost Lines')
    noUrutLoin = fields.One2many('sis.cs.no.loin', 'rel_cs_detail', string='No Urut Loin')
    cleaning = fields.One2many('sis.cleaning', 'rel_cs_detail', string='No Fish Box')
#     trace_detail_id = fields.Many2one('sis.trace.header', string="Detail CS", required=True)
    tgl_produksi = fields.Date(string="Tgl. Produksi", required=True)
#    fresh_fish = fields.Selection(string="Fish Type", selection=[(True, 'Fresh'),(False, 'Frozen')])
    fresh_fish = fields.Selection([('1','Fresh Fish'),('2','Frozen Fish'),('3','Frozen Loin/Flake')], string='Kategori', default='2')
#     tgl_keluar = fields.Datetime(string="Tanggal Keluar CS",required=True,default=datetime.now()+relativedelta(minutes=200))
    tgl_keluar = fields.Datetime(string="Tanggal Keluar CS",required=True, default=fields.Datetime.now)
    no_potong = fields.Integer(string="No. Potong", required=True)
    pabrik_id = fields.Char(string="Lokasi", size=4)
    barcode_no = fields.Char(size=40,string="Barcode No", required=True)
    item_no = fields.Char(size=20,string="Item No.")
    description= fields.Char(size=100,string="Description")
    vessel_no = fields.Char(size=100,string="Vessel No.")
    hatch_no = fields.Char(size=100,string="Hatch No.")
    voyage_no = fields.Char(size=100,string="Voyage No.")
    quantity = fields.Float(string='Quantity', required=True)
    remaining_quantity = fields.Float(string='Remaining Quantity')
    lot_no = fields.Char(size=40,string="Lot No", required=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No.", required=True)
    status = fields.Char(size=10,string="Status")
    status_analisa = fields.Char(compute='update_history',size=10,string="Status Analisa",store=True)
    status_process = fields.Char(size=10,string="Status Process")
    histamin = fields.Char(size=100,string="Histamin")
    kadar_garam = fields.Char(size=100,string="Kadar Garam")
    orange_meat = fields.Char(size=100,string="Orange Meat")
    blackspot = fields.Char(size=100,string="Blackspot")
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus")
    kontaminasi = fields.Char(size=100,string="Kontaminasi")
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa")
    lain2_process = fields.Char(size=100,string="Lain2 Process")
    remark_analisa = fields.Char(size=100,string="Remark Analisa")
    remark_process = fields.Char(size=100,string="Remark Process")
    status_def = fields.Integer(string="Status Defrost", required=True,default=0)
    status_pl = fields.Boolean(string="Pole & Line", compute="update_history", store=True)
    real_item_no = fields.Char(size=5,string="Fish Size")
    product_group_code = fields.Char(size=2, string="Product Group Code")
    real_itemno = fields.Char(size=20,string="real_item_no")
    po = fields.Char(size=20, string="Purchase Order")
    no_urut = fields.Char(string="No Urut", compute="_list_no_urut_loin")
    quantity_loin = fields.Float(string='Qty. Loin', compute="_hitung_qty_loin")
    
#     @api.one
#     def _qty_loin(self):
#         if self.fresh_fish == 3:
#             if self.noUrutLoin:
#                 self.quantity = 200
                
    @api.one
    def _list_no_urut_loin(self):
        xno=""
        for xdetail in self.noUrutLoin:
            if xdetail.no_urut:
                if xno=="":
                    xno=str(xdetail.no_urut)
                else:
                    xno=xno+", "+str(xdetail.no_urut)
          
        self.no_urut=xno
        
    def open_nourut(self):
        return {
            'name'      : 'No Urut',
            'res_model' : 'sis.cs.no.loin',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'tree',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_traceability.sis_cs_no_loin_tree').id,
            'nodestroy' : False,
            'target'    : 'new',
            'context'   : {'default_rel_cs_detail':self.id},
            'domain'    : [('rel_cs_detail','=',self.id)],      
            'flags'     : {'action_buttons': True}
        }

        xtonase=0
        for xdetail in self.cs_line_id:
            if xdetail.quantity and xdetail.quantity>0:
                xtonase=xtonase+xdetail.quantity
         
        self.total_tonase=xtonase

        
    @api.one
    def _hitung_qty_loin(self):
        if self.fresh_fish=='3':
            total=0
            for xdetail in self.noUrutLoin:
                if xdetail.qty:
                    if total==0:
                        total=xdetail.qty
                    else:
                        total=total+xdetail.qty
        else:
            total=0
        self.quantity_loin=total
          
    @api.constrains('barcode_no')
    def _constrains_barcode(self):
        rec=self.env['sis.cs.detail'].search([('barcode_no','=',self.barcode_no),('id','!=',self.id)])
        if len(rec)>0:
            qtyuse=0
            for x in rec:
                qtyuse=qtyuse+x.quantity
                   
            navSQL="select quantity from sis_fish_status where barcode_no='"+self.barcode_no+"'"
            self.env.cr.execute(navSQL)
            navrc=self.env.cr.fetchall()
             
            if len(navrc)==0:
                qtysisa1=0
            else:           
                for val_sisa1 in navrc :
                    (qtysisa1,)=val_sisa1
   
                if qtysisa1-qtyuse<self.quantity or self.quantity==0:
                    raise UserError("Qty. barcode "+self.barcode_no+" tidak mecukupi. Sisa Qty : "+str(qtysisa1-qtyuse))
   
#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%s [%s]" % (me.barcode_no, me.no_potong)))
#         return result
   
    @api.one
    @api.depends('barcode_no')
    def update_history(self):
        if self.barcode_no:
            if self.barcode_no[:3]=="AT/" or self.barcode_no[:3]=="AT2":
                cSQL="select fish_box_no,lot_no,item_no,description,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process,remark_analisa,remark_process,real_item_no,product_group_code,po,real_item_no from sis_fish_status "
                self.env.cr.execute(cSQL+"where barcode_no='"+self.barcode_no+"'")
                rec_fish=self.env.cr.fetchall()
                if len(rec_fish)!=0:
                    for cs_data in rec_fish:
                        (xfish_box,xno_lot,xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xquantity,xremaining,xstatus,xstatus_analisa,xstatus_process,xhistamin,xkadargaram,xorangemeat,xblackspot,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess,xrealitem,xproductgroup,xpo,xrealitemno)=cs_data
                 
                    self.tgl_produksi = self.cs_line_id.tgl_produksi
                    self.pabrik_id = self.cs_line_id.pabrik_id
                    if self.cs_line_id.invoice=='1':
                        if self.cs_line_id.fresh_fish==True:
                            self.fresh_fish='1'
                        else:
                            self.fresh_fish='2'
                    else:
                        self.fresh_fish='3'
                    #self.fresh_fish = self.cs_line_id.invoice
                    self.item_no =  xitem_no
                    self.description= xdescription
                    self.vessel_no = xvessel_no
                    self.hatch_no = xhatch_no
                    self.voyage_no = xvoyage_no
                    self.remaining_quantity = xremaining
                    self.lot_no = xno_lot
                    self.fish_box_no = xfish_box
                    self.status = xstatus
                    self.status_analisa = xstatus_analisa
                    self.status_process = xstatus_process
                    self.histamin = xhistamin
                    self.kadar_garam = xkadargaram
                    self.orange_meat = xorangemeat
                    self.blackspot = xblackspot
                    self.pemakaian = xpemakaian
                    self.kontaminasi = xkontaminasi
                    self.lain2_analisa = xlainanalisa
                    self.lain2_process = xlainprocess
                    self.remark_analisa = xremanalisa
                    self.remark_process = xremprocess
                    self.no_potong=self.cs_line_id.no_potong
                    self.status_def=0
                    self.po=xpo
                    self.real_itemno=xrealitemno
                    if self.hatch_no[-3:]=="P&L":
                        self.status_pl=True
                    self.product_group_code=xproductgroup
                    
                    if xproductgroup=='BE':
                        self.real_item_no=xrealitem[6:].strip()
                    else:
                        self.real_item_no=xrealitem[5:].strip()
                            
                    qtyuse=0
                    rec=self.env['sis.cs.detail'].search([('barcode_no','=',self.barcode_no)])
                    if len(rec)!=0:
                        for x in rec:
                            qtyuse=qtyuse+x.quantity
                              
                        self.quantity=xquantity-qtyuse
                    else:
                        self.quantity=xquantity

    def _get_data_cs(self,kode):
        if kode:
            cSQL="select item_no,description,vessel_no,hatch_no,voyage_no,remaining_quantity,lot_no,fish_box_no,status,pemakaian,kontaminasi,lain2_analisa,lain2_process,remark_analisa,remark_process,real_item_no,product_group_code,po,real_item_no from sis_fish_status "
            self.env.cr.execute(cSQL+"where barcode_no='"+kode+"'")
            rec_fish=self.env.cr.fetchall()
            if len(rec_fish)>0:
                for cs_data in rec_fish:
                    (xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess,xrealitem,xproductgroup,xpo,xrealitemno)=cs_data

                    if xproductgroup=='BE':
                        yrealitem=xrealitem[6:].strip()
                    else:
                        yrealitem=xrealitem[5:].strip()
 
            return xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess,yrealitem,xproductgroup,xpo,xrealitemno
 
    def get_data_fresh(self,kode):
        if kode:
#            cField="a.item_no,a.description,a.lot_no,a.vessel_no,a.hatch_no,a.voyage_no,a.quantity,a.status,a.fish_box_no,a.real_item_no,a.product_group_code"
            cField="a.real_item_no,a.product_group_code,a.real_item_no"
            cSQL1="select "+cField+" from sis_fish_fresh_inv a left join sis_cs_detail b on a.invoice_no=b.barcode_no and a.quantity=b.quantity "
            cSQL2=" where b.barcode_no is null and a.invoice_no='"+str(self.invoice_no)+"'"
            self.env.cr.execute(cSQL1+cSQL2)
            fresh_fish_data=self.env.cr.fetchall()
            if len(fresh_fish_data)>0:
                for ff_data in fresh_fish_data:
                    (xrealitem,xproductgroup,xrealitemno)=ff_data

                    if xproductgroup=='BE':
                        yrealitem=xrealitem[6:].strip()
                    else:
                        yrealitem=xrealitem[5:].strip()
            
            return yrealitem,xproductgroup,xrealitemno  

 
    def _get_trace_id(self,pabrik,tgl_produksi):
        if pabrik and tgl_produksi:
#            tanggal=datetime.now()
            tanggal=tgl_produksi
#            d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
            d_to = datetime.strptime(tanggal,"%Y-%m-%d")
            d_tahun = d_to.year
            d_bulan=""
            d_tanggal=""
#            no_prefix=""
            if d_to.month<10 :
                d_bulan="0"+str(d_to.month)
            else :
                d_bulan=str(d_to.month)

            if d_to.day<10 :
                d_tanggal="0"+str(d_to.day)
            else :
                d_tanggal=str(d_to.day)
         
#             if pabrik=="ATI1":
#                 no_prefix = "T1/"+str(d_tahun)+str(d_bulan)+"-"
#             elif pabrik=="ATI2":
#                 no_prefix = "T2/"+str(d_tahun)+str(d_bulan)+"-"

            if pabrik=="ATI1":
                trace_id = "T1/"+str(d_tahun)+str(d_bulan)+"-"+str(d_tanggal)
            elif pabrik=="ATI2":
                trace_id = "T2/"+str(d_tahun)+str(d_bulan)+"-"+str(d_tanggal)
 
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
 
            return trace_id

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        
        self._list_no_urut_loin()
        xproses=100*(1/10)
#         cr_th=self.enver'].search([('tgl_produksi','=',vals['tgl_produksi']),('pabrik_id','=',vals['pabrik_id'])])
#         if len(cr_th)==0:
#             trace_id=self._get_trace_id(vals['pabrik_id'],vals['tgl_produksi'])
#             vals_th={
#                 'trace_id':trace_id,
#                 'tgl_produksi':vals['tgl_produksi'],
#                 'pabrik_id':vals['pabrik_id'],
#                 'trace_proses':xproses,
#                 'proses_desc': 'Cold Storage'
#                 }
#             self.env['sis.trace.header'].create(vals_th)
#  
#         cr_th=self.env['sis.trace.header'].search([('tgl_produksi','=',vals['tgl_produksi']),('pabrik_id','=',vals['pabrik_id'])])
#         if len(cr_th)>0:
#             xth_id=cr_th.id
 
        cr_data=self.env['sis.cs.detail'].search([('barcode_no','=',vals['barcode_no']),('no_potong','=',vals['no_potong']),('tgl_produksi','=',vals['tgl_produksi']),('status_def','=',0)])
        if len(cr_data)==0:
            if vals['fresh_fish']!='1':
                xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess,xrealitem,xproductgroup,xpo,xrealitemno=self._get_data_cs(vals['barcode_no'])
                vals_cs={
#                    'trace_detail_id':xth_id,
                   'item_no':xitem_no,
                   'description':xdescription,
                   'vessel_no':xvessel_no,
                   'hatch_no':xhatch_no,
                   'voyage_no':xvoyage_no,
                   'remaining_quantity':xremaining,
                   'lot_no':xno_lot,
                   'fish_box_no':xfish_box,
                   'status':xstatus, 
                   'pemakaian':xpemakaian,
                   'kontaminasi':xkontaminasi,
                   'lain2_analisa':xlainanalisa,
                   'lain2_process':xlainprocess,
                   'remark_analisa':xremanalisa,
                   'remark_process':xremprocess,
                   'real_item_no':xrealitem,
                   'product_group_code':xproductgroup,
                   'po':xpo,
                   'real_itemno':xrealitemno
                }
            else:
                xrealitem,xproductgroup=self._get_data_fresh(vals['barcode_no'])                
                vals_cs={
                   'pemakaian':"",
                   'kontaminasi':"",
                   'lain2_analisa':"",
                   'lain2_process':"",
                   'remark_analisa':"",
                   'remark_process':"",
                   'real_item_no':xrealitem,
                   'product_group_code':xproductgroup,
                   'real_itemno':xrealitemno
                }
                        
            vals.update(vals_cs) 
            res_id = models.Model.create(self, vals)
            return res_id
        else:
            if vals['barcode_no'][:3]=="AT/" or vals['barcode_no'][:3]=="AT2":
                for r in cr_data:
                    vals_data={
                       'quantity':r.quantity+vals['quantity']
                            }
                r.write(vals_data)
            else:
                res_id = models.Model.create(self, vals)
                return res_id
 
    @api.multi
    def unlink(self):
        cr_def=self.env['sis.defrost.detail'].search([('tgl_produksi','=',self.tgl_produksi),('pabrik_id','=',self.pabrik_id),('no_potong','=',self.no_potong),('barcode_no','=',self.barcode_no)])
        if len(cr_def)!=0:
            raise UserError('Barcode : '+self.barcode_no+' sudah diinput Defrost. Data tidak bisa didelete!')
 
        orders = self.mapped('cs_line_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.cs_line_id == order)
            msg = ""
            for line in order_lines:
                msg += "Barcode" + ": %s <b>[ <i>deleted</i> ]</b><br/>" % (line.barcode_no,)
            if msg!="":
                order.message_post(body=msg)
        return super(sis_cs_detail, self).unlink()
      
    @api.multi
    def write(self, vals):
        if self.cs_line_id.cs_id:
            if vals.get('status_def')==0 or vals.get('status_def')==1:
                exit
            else:
                cr_def=self.env['sis.cs.detail'].search([('tgl_produksi','=',self.tgl_produksi),('pabrik_id','=',self.pabrik_id),('no_potong','=',self.no_potong),('barcode_no','=',self.barcode_no),('status_def','=',1)])
                if len(cr_def)!=0:
                    raise UserError('Barcode : '+self.barcode_no+' sudah diinput Defrost. Data tidak bisa diupdate!')
                
            cSQL1="select b.quantity from sis_cs_header as a, sis_cs_detail as b where b.cs_line_id=a.id and b.id<>'"+str(self.id)+"' and b.status_def=0 "
            cSQL2="and b.barcode_no='"+self.barcode_no+"' and b.no_potong='"+str(self.no_potong)+"' and b.tgl_produksi='"+self.tgl_produksi+"' and a.cs_id='"+self.cs_line_id.cs_id+"'"
  
            self.env.cr.execute(cSQL1+cSQL2)
            cr_data=self.env.cr.fetchall()
      
            if len(cr_data)==0:
                orders = self.mapped('cs_line_id')
                for order in orders:
                    order_lines = self.filtered(lambda x: x.cs_line_id == order)
                    msg = ""
                    for line in order_lines:
                        if vals.get('barcode_no'):
                            msg += "Barcode" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (line.barcode_no, vals['barcode_no'],)
                        if vals.get('tgl_keluar'):
                            msg += "Tgl. Keluar" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.tgl_keluar), str(vals['tgl_keluar']),)
                        if vals.get('no_potong'):
                            msg += "No. Potong" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_potong), str(vals['no_potong']),)
                        if vals.get('quantity'):
                            msg += "Qty." + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.quantity), str(vals['quantity']),)

                    if msg!="":
                        order.message_post(body=msg)
                      
                    vals.update({'tgl_produksi':self.cs_line_id.tgl_produksi})
                    return super(sis_cs_detail, self).write(vals)
            else:
                for r in cr_data:
                    (r_quantity,)=r
                    vals_data={
                       'quantity':r_quantity+self.quantity
                    }
                vals.update(vals_data)            
                return super(sis_cs_detail, self).write(vals)

class sis_cs_view(models.Model):
    _name = "sis.cs.view"
    _auto = False

    cs_id        = fields.Integer(string="ID")
    tgl_produksi = fields.Date(string="Tanggal Produksi")
    pabrik_id    = fields.Char(string="Lokasi")
    no_potong    = fields.Integer(string="No. Potong")
    total_tonase = fields.Float(string="Tonase")
    barcode_no   = fields.Char(size=40,string="Barcode No")
    fish_box_no  = fields.Char(size=20,string="Fish Box No.")
    quantity     = fields.Float(string='Quantity')
    
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_cs_view as (
        SELECT
        row_number() OVER () as id, 
        h.id as cs_id, h.tgl_produksi, h.pabrik_id, h.no_potong, d.barcode_no, d.fish_box_no, d.quantity, sum(d.quantity) as total_tonase
        
        FROM 
        sis_cs_header as h, sis_cs_detail as d
        
        WHERE
        d.cs_line_id=h.id
        
        GROUP BY h.id, d.barcode_no, d.fish_box_no, d.quantity)
        """
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_cs_view')
        self._cr.execute(cSQL)
    
class sis_cs_no_loin(models.Model):
    _name = "sis.cs.no.loin"
    
    no_urut = fields.Integer(String="No Urut")
    qty     = fields.Float(string='Quantity', required=True)
    qty_fish = fields.Float(string='Qty. Fish', store=False)
    jambongkar = fields.Datetime(String="Jam Bongkar", default=fields.Datetime.now)
    rel_cs_detail = fields.Many2one('sis.cs.detail', string="CS Detail Lines")

    @api.constrains('no_urut')
    def _constrains_qty(self):
        #total_qty=self.rel_cs_detail.quantity
        rec=self.env['sis.cs.no.loin'].search([('rel_cs_detail','=',self.rel_cs_detail.id)])
        if len(rec)>0:
            qtyuse=0
            for x in rec:
                qtyuse=qtyuse+x.qty
                   
#             navSQL="select quantity from sis_fish_status where barcode_no='"+self.barcode_no+"'"
#             self.env.cr.execute(navSQL)
#             navrc=self.env.cr.fetchall()
             
#             if len(navrc)==0:
#                 qtysisa1=0
#             else:           
#                 for val_sisa1 in navrc :
#                     (qtysisa1,)=val_sisa1
   
            if qtyuse>self.rel_cs_detail.quantity or self.rel_cs_detail.quantity==0:
                raise UserError("Qty. No. Urut "+str(self.no_urut)+" tidak mecukupi. Sisa Qty : "+str(self.rel_cs_detail.quantity-(qtyuse-self.qty)))

     
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self,vals):
#         

#     @api.one
#     @api.onchange('qty')
#     def _qty_sum(self):
#         if self.qty:
#             relasi = self.env['sis.cs.detail'].search([('id', '=', self.rel_cs_detail.id)])
#             if relasi:
#                 relasi['quantity'] = 200
#         if self.qty:
#             total=0
#             for xdetail in self.rel_cs_detail.noUrutLoin:
#                 if xdetail.qty:
#                     if total==0:
#                         total=xdetail.qty
#                     else:
#                         total=total+xdetail.qty
#             
#             self.rel_cs_detail.quantity=total
    
