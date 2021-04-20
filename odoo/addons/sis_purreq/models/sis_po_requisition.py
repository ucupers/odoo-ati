from odoo import models, fields, api
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError

import pyodbc
import re
    
SQLCONN='Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+\
                              'Server=10.0.0.12;'+\
                              'Database=NAV (9-0) ATI LIVE;'+\
                              'UID=Atidev;pwd=Ati1234;'

class sis_uom(models.Model):
    _name   = "sis.po.uom"    
    _description = 'SIS PO Requisition UOM'
    _order = "item_no"
    _rec_name="item_uom"

    item_no     = fields.Char(size=35, string="Kode")
    item_uom    = fields.Char(size=20, string="UOM")
    item_qty    = fields.Float('Qty')
    
class sis_por_items(models.Model):
    _name   = "sis.por.items"    
    _description = 'SIS PO Requisition Items'
    _order = "item_no"
    _rec_name= "item_desc"

    item_no     = fields.Char(size=20, string="Kode")
    item_desc   = fields.Char(size=200, string="Deskripsi")
    item_type   = fields.Selection([(1,'Jasa'),(2,'Item')], string='Type', default=2)

    @api.multi
    def name_get(self):
        result = []
        for me in self :
            result.append((me.id, "%s - [%s]" % (me.item_no, me.item_desc)))
        return result

class sis_por_var_items(models.Model):
    _name   = "sis.por.items.var"    
    _description = 'SIS PO Requisition Items Variant'
    _order = "item_no"
    _rec_name= "variant_code"

    item_no     = fields.Char(size=20, string="Kode")
    variant_code= fields.Char(size=20, string="Kode Variant")
    item_desc   = fields.Char(size=200, string="Deskripsi")

#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%s - [%s]" % (me.item_no, me.item_desc)))
#         return result
#     

class po_requisition(models.Model):
    _name  ='sis.po.requisition'
    _description = 'SIS PO Requisition'
    _rec_name='no_doc'
    _order = "no_doc desc"
    
    no_doc              = fields.Char(size=22, string='Doc No', default='/', track_visibility="onchange",required=True)
    tgl_doc             = fields.Date(string='Tgl Doc', default=datetime.now()+relativedelta(hours=7),required=True)
    pabrik_id           = fields.Char(string="Lokasi", size=4, compute="_get_pabrik_id", store=True, track_visibility="onchange")
    user_id             = fields.Char(string="Login", size=100, compute="_get_user_id", store=True, track_visibility="onchange")
#     pabrik_id           = fields.Selection([('ATI-1','ATI-1'),('ATI-2','ATI-2')], string='Lokasi', default='ATI-1', track_visibility="onchange")
#     section_id          = fields.Char(size=50, string='Section', compute="_get_section_id", store=True, track_visibility="onchange")
    section_id   = fields.Selection(string="Section", selection=[
        ('Admin', 'Admin'),
        ('Prod1', 'Produksi 1'),
        ('Boiler', 'Boiler'),
        ('CSD', 'Cold Storage-Defrost'),
        ('CS', 'Cold Storage'),
        ('Defrost', 'Defrost'),
        ('FJ', 'Fish Juice'),
        ('FM', 'Fish Meal'),
        ('GA', 'General Affairs'),
        ('RM', 'Raw Material'),
        ('Cutting', 'Cutting'),
        ('Cooker', 'Cooker'),
        ('HR', 'Human Resources'),
        ('IT', 'IT'),
        ('MT', 'Maintenance'),
        ('Office', 'Office'),
        ('PPIC', 'PPIC'),
        ('QT', 'Quality Technology'),
        ('Seamer', 'Seamer'),
        ('Seasoning', 'Seasoning'),
        ('QCDoc', 'Dokumen'),
        ('PreCL', 'Pre Cleaning'),
        ('CL','Cleaning'),
        ('packing','Packing'),
        ('WHUnlabeled','WH Unlabeled'),
        ('WH', 'Warehouse'),
        ('WH2', 'Warehouse 2'),
        ('Retort','Retort'),
        ('EC','Empty Can'),
        ('PNF','Purchasing'),
        ('FA','Finance Accounting'),
        ('STG1','STG GA'),
        ('HSE','HSE GA')
        ], compute="_get_section_id", store=True, track_visibility="onchange")
    item_type           = fields.Selection([(1,'Jasa'),(2,'Item')], string='Type', default=2, required=True, track_visibility="onchange")
    state_doc           = fields.Selection([('draft','Draft'),('released','Released'),('confirmed','Confirmed'),('canceled','Canceled'),('closed','Closed')], string='Status Doc', default='draft', track_visibility="onchange")
    rpt_xlsx            = fields.Binary('File data', help='File(xlsx format)')
    por_line_id         = fields.One2many('sis.po.requisition.lines', 'por_line_id', string='POR Lines')
    
    def sync_nav(self):
        self.env.cr.execute("insert into sis_po_uom(item_no, item_uom, item_qty) select a.itemno, a.code, a.qty from sis_uom_conversion a left outer join sis_po_uom b on b.item_no=a.itemno and b.item_uom=a.code and b.item_qty=a.qty where b.item_no is null and b.item_uom is null and b.item_qty is null")

        self.env.cr.execute("""insert into sis_por_items(item_no, item_desc, item_type) 
        select b.itemno, b.description, b.typpe from sis_por_items a
        right outer join
        (select itemno, description, 2 as typpe from sis_items where itc in ('GA','PKG','SS') and blocked=False
        union
        select no, name, 1 as typpe from sis_gl_account) b on b.itemno=a.item_no
        where a.item_no is null
        """)

        self.env.cr.execute("""insert into sis_por_items_var(item_no, variant_code, item_desc) 
        select b.itemno, b.variant, b.description from sis_por_items_var a
        right outer join sis_item_variants b on b.itemno=a.item_no
        where a.item_no is null and b.blocked=false        
        """)

    def _get_prefix(self):
        tanggal=datetime.now()
        d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
        d_tahun = d_to.year
        d_bulan=""
        if d_to.month<10 :
            d_bulan="0"+str(d_to.month)
        else :
            d_bulan=str(d_to.month)
        
        xlokasi,xsection=self._get_user_attribut()        
       
        no_prefix = "POR/"+xlokasi+"/"+str(d_tahun)+"/"+d_bulan+"/"
        
        rec=self.env['sis.po.requisition'].search([('no_doc','ilike',no_prefix)])
        if len(rec)>0:
            self.env.cr.execute("select max(cast(substring(no_doc,19,4) as integer)) from sis_po_requisition where no_doc like '"+no_prefix+"%'")
            rc=self.env.cr.fetchall()
              
            for b in rc :
                (x,)=b
            no_urut=x+1
            if no_urut<10:
                no_doc=no_prefix+"000"+str(no_urut)
            elif no_urut>9 and no_urut<100:
                no_doc=no_prefix+"00"+str(no_urut)
            elif no_urut>99 and no_urut<1000:
                no_doc=no_prefix+"0"+str(no_urut)
            else:
                no_doc=no_prefix+str(no_urut)
        else:
            no_urut=1
            no_doc=no_prefix+"000"+str(no_urut)
        
        return no_doc

    @api.one
    @api.depends('tgl_doc')
    def _get_pabrik_id(self):
        if self.tgl_doc:
            xuid = self.env.uid
            cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.pabrik_id=xpabrik_id

    @api.one
    @api.depends('tgl_doc')
    def _get_user_id(self):
        if self.tgl_doc:
            xuid = self.env.uid
            cSQL1="select login from res_users where" 
     
            self.env.cr.execute(cSQL1+" id="+str(xuid))
            rc_login=self.env.cr.fetchall()
             
            for def_login in rc_login:
                    (xuser_id,)=def_login
             
            self.user_id=xuser_id
        
    @api.one
    @api.depends('tgl_doc')
    def _get_section_id(self):
        if self.tgl_doc:
            xuid = self.env.uid
            cSQL1="select a.section_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_section=self.env.cr.fetchall()
             
            for def_section in rc_section:
                    (xsection_id,)=def_section
             
            self.section_id=xsection_id

    def _get_user_attribut(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id,a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
        
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
        
        return xpabrik_id,xsection_id
    
    def _close_por_nav(self):
        xstatus=False       
        conn = pyodbc.connect(SQLCONN)
        cursor = conn.cursor()
                
        row=cursor.execute("UPDATE [PT_ Aneka Tuna Indonesia$Purchase Requisition] set [Status]=3 where [Requisition No_]='"+self.no_doc+"'")
          
        if row.rowcount==0:
            xstatus=False
            raise UserError("Failed to update NAV, please try again later!")
        else:
            conn.commit()
            xstatus=True

        return xstatus
    
    def _hapus_por_nav(self):
        xstatus=False       
        conn = pyodbc.connect(SQLCONN)
        cursor = conn.cursor()
                
        row=cursor.execute("delete from [PT_ Aneka Tuna Indonesia$Purchase Requisition] where [Requisition No_]='"+self.no_doc+"'")
          
        if row.rowcount==0:
            xstatus=False
            raise UserError("Failed to update NAV, please try again later!")
        else:
            conn.commit()
            xstatus=True

        return xstatus

    def _upload_nav(self):
        xstatus=False       
        conn = pyodbc.connect(SQLCONN)
        cursor = conn.cursor()

        self.env.cr.execute("""
        select a.no_doc, b.no_line, b.item_type, b.item_no, b.item_desc, b.item_qty, b.item_uom, b.item_remark, coalesce(b.variant_code,'')
        from sis_po_requisition a 
        inner join sis_po_requisition_lines b on b.por_line_id=a.id 
        where 
        a.no_doc='"""+self.no_doc+"""' 
        order by b.no_line
        """)
        rec_por=self.env.cr.fetchall()
        
        for dat_por in rec_por:
            (xno_doc, xno_line, xitem_type, xitem_no, xitem_desc, xitem_qty, xitem_uom, xitem_remark, xvariant)=dat_por
            
            if xitem_uom:
                xsatuan=xitem_uom
            else:
                xsatuan=""
            
            if xitem_desc:
                if xitem_type==1:
                    xitemdesc=xitem_desc[16:]
                else:
                    xitemdesc=xitem_desc
            else:
                xitemdesc=""
                
            if xitem_remark:
                xremark=xitem_remark
            else:
                xremark=""

            row=cursor.execute("INSERT INTO [PT_ Aneka Tuna Indonesia$Purchase Requisition]([Requisition No_],[Line No_],"+\
            " [Type],[No_],[Description],[Unit of Measure],[Quantity],[Variant Code],Remark,[Status]) VALUES('"+xno_doc+"',"+\
            str(xno_line)+","+str(xitem_type)+",'"+xitem_no+"','"+xitemdesc+"','"+xsatuan+"',"+\
            str(xitem_qty)+",'"+xvariant+"','"+xremark+"','1')")
                
            if row.rowcount==0:
                xstatus=False
                raise UserError("Failed to update NAV, please try again later!")
                exit()
  
            conn.commit()
            xstatus=True

        return xstatus
            
    @api.multi
    def action_release(self):
        xlokasi,xsection=self._get_user_attribut()        
                
        for me_id in self :
            if me_id.pabrik_id==xlokasi and me_id.section_id==xsection:
                me_id.write({'state_doc':'released',
                             'tgl_doc':datetime.now()+relativedelta(hours=7)
                             })
            else:
                raise UserError("Unauthorized User!")
                    
    @api.multi
    def action_confirm(self):
        xlokasi,xsection=self._get_user_attribut()
                
        for me_id in self :
            if xsection=="PNF":
                if self._upload_nav()==True:
                    me_id.write({'state_doc':'confirmed'})
            else:
                raise UserError("Unauthorized User!")

    @api.multi
    def action_undo(self):
        xlokasi,xsection=self._get_user_attribut()
                
        for me_id in self :
            if me_id.state_doc=='released':
                if me_id.pabrik_id==xlokasi and me_id.section_id==xsection:
                    me_id.write({'state_doc':'draft'})
                else:
                    raise UserError("Unauthorized User!")
            
            elif me_id.state_doc=='confirmed':
                if xsection=='PNF':
                    if self._hapus_por_nav()==True:
                        me_id.write({'state_doc':'draft'})
                else:
                    raise UserError("Unauthorized User!")

    @api.multi
    def action_cancel(self):
        xlokasi,xsection=self._get_user_attribut()
                
        for me_id in self :
            if me_id.state_doc=='draft' or me_id.state_doc=='released':
                if me_id.pabrik_id==xlokasi and me_id.section_id==xsection:
                    me_id.write({'state_doc':'canceled'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.state_doc=='confirmed':
                if xsection=="PNF":
                    me_id.write({'state_doc':'canceled'})
                else:
                    raise UserError("Unauthorized User!")

    @api.multi
    def action_close(self):
        xlokasi,xsection=self._get_user_attribut()
                
        for me_id in self :
            if me_id.state_doc=='confirmed':
                if xsection=="PNF":
                    if self._close_por_nav()==True:
                        me_id.write({'state_doc':'closed'})
                else:
                    raise UserError("Unauthorized User!")
                
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        nodoc=self._get_prefix()
        vals.update({'no_doc':nodoc}) 
        res_id = models.Model.create(self, vals)
        return res_id
    
    @api.multi
    def write(self, vals):
#         for me_id in self :
            
            xpabrik_id,xsection_id=self._get_user_attribut()
            if self.state_doc=="draft":
                if xsection_id==self.section_id:
                    if xpabrik_id==self.pabrik_id:
                        return super(po_requisition, self).write(vals)
                    else:
                        raise UserError("Unauthorized User!")
                else:
                    raise UserError("Unauthorized User!")
                    
            elif self.state_doc=="released":
                if xsection_id==self.section_id:
                    if vals.get('state_doc') and vals['state_doc']=='draft':
                        return super(po_requisition, self).write(vals)
                    else:
                        if xsection_id=="PNF":
                            if vals.get('state_doc') and vals['state_doc']=='confirmed':
                                return super(po_requisition, self).write(vals)
                        else:
                            raise UserError("Cannot update!")
                else:
                    if xsection_id=="PNF":
                        return super(po_requisition, self).write(vals)
                    else:
                        raise UserError("Unauthorized User!")
            elif self.state_doc=="confirmed":
                if xsection_id=="PNF":
                    if vals.get('state_doc') and vals['state_doc']=='closed' or vals['state_doc']=='canceled' or vals['state_doc']=='draft':
                        return super(po_requisition, self).write(vals)
                    else:
                        raise UserError("Cannot update!")
                else:
                    raise UserError("Unauthorized User!")
            elif self.state_doc=="canceled" or self.state_doc=="closed":
                raise UserError("Cannot update!")
    
    @api.one
    def unlink(self):
        if self.state_doc!='draft':
            raise UserError("Cannot delete!")
        else:
            return models.Model.unlink(self)
        
    def kembali(self):
        return {'type': 'ir.actions.client', 'tag': 'history_back'}
                
class po_requisition_lines(models.Model):
    _name  ='sis.po.requisition.lines'
    _description = 'SIS PO Requisition Lines'
    _order = "no_line"
     
    por_line_id         = fields.Many2one('sis.po.requisition', string='POR Lines', ondelete='cascade')
    no_line             = fields.Integer('No Line', track_visibility="onchange")
    item_type           = fields.Selection([(1,'Jasa'),(2,'Item'),(3,'Asset')], string='Type', compute="get_type", store=True)
    item_no             = fields.Char(size=35, string='Kode', track_visibility="onchange", store=True, compute="get_kode")
#     item_desc           = fields.Char(size=50, string='Nama Barang', compute="_get_item", store=True, track_visibility="onchange")
    item_desc           = fields.Char(size=200, string='Nama Barang', track_visibility="onchange")
    item_qty            = fields.Float('Qty', default=1, required=True)
    item_uom            = fields.Char(size=20, string='Satuan', compute="_get_satuan", track_visibility="onchange", store=True)
    variant_code        = fields.Char(size=20, string='Variant', compute="_get_variant", track_visibility="onchange", store=True)
#     item_uom            = fields.Char(size=20, string='Satuan', track_visibility="onchange", required=True)
    alasan              = fields.Selection([('rutin','Rutin'),('rusak','Rusak'),('hilang','Hilang'),('spare','Spare'),('lainnya','Lainnya')], string='Alasan Order', required=True, track_visibility="onchange")
    curr_code           = fields.Char(size=5, string='Mata Uang', compute="_get_mata_uang", store=True)
#     curr_code           = fields.Char(size=5, string='Mata Uang')
#     estimasi_harga      = fields.Float('Estimasi Harga')
    estimasi_harga      = fields.Float('Estimasi Harga', compute="_get_harga", store=True)
#     estimasi_total      = fields.Float('Estimasi Total', compute="_get_total", store=True)
    no_po_nav           = fields.Char(size=20, string='No PO NAV')
    item_remark         = fields.Char(size=200, string='Remark')
    uom_line_id         = fields.Many2one('sis.po.uom', string='UOM Lines', domain="[('item_no','=',item_no)]")
    item_line_id        = fields.Many2one('sis.por.items', string='Item Lines', domain="[('item_type','=',item_type)]")
    item_var_line_id    = fields.Many2one('sis.por.items.var', string='Var Lines', domain="[('item_no','=',item_no)]")
 
    @api.one
    @api.depends("por_line_id.item_type")
    def get_type(self):
        if self.por_line_id.item_type:
            self.item_type=self.por_line_id.item_type
 
    @api.one
    @api.depends("item_line_id.item_no")
    def get_kode(self):
        if self.item_line_id:
            self.item_no=self.item_line_id.item_no

    @api.onchange("item_no")
    def _get_item(self):
        if self.item_no:
            self.item_desc=self.item_line_id.item_desc
#             if self.item_type==1:
#                 self.env.cr.execute("select name from sis_gl_account where no='"+self.item_no+"'")
#             elif self.item_type==2:    
#                 self.env.cr.execute("select description from sis_items where itc in ('GA','PKG','SS') and blocked=False and itemno='"+self.item_no+"'")
#             elif self.item_type==3:    
#                 self.env.cr.execute("select description from sis_fixed_asset where blocked=False and itemno='"+self.item_no+"'")
#                 
#             dat_ket=self.env.cr.fetchall()
#      
#             if len(dat_ket)>0:
#                 for f_ket in dat_ket:
#                     (xketerangan,)=f_ket
#                 
#                 self.item_desc=xketerangan
    
    @api.one
    @api.depends("item_no","uom_line_id")
    def _get_mata_uang(self):
        if self.item_no:
            if self.item_type==2:
                if self.item_uom:
                    self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' and item_uom='"+self.item_uom+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==1:
#                 self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==3:
#                 self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
     
            try:
                rec=self.env.cr.fetchall()
                if len(rec)>0:
                    for r in rec:
                        (xcurr_code,xharga,)=r
                     
                    if self.item_type==2:
                        self.curr_code=xcurr_code
                        self.estimasi_harga=xharga
                    else:
                        self.curr_code=""
                        self.estimasi_harga=0
            except:
                exit
                    
    @api.one
    @api.depends("uom_line_id")
    def _get_satuan(self):
        if self.uom_line_id:
            if self.item_type==2:
                self.item_uom=self.uom_line_id.item_uom

    @api.one
    @api.depends("item_var_line_id")
    def _get_variant(self):
        if self.item_var_line_id:
            if self.item_type==2:
                self.variant_code=self.item_var_line_id.variant_code
            
    @api.one
    @api.depends("item_no","uom_line_id")
    def _get_harga(self):
        if self.item_no:
            if self.item_type==2:
                if self.item_uom:
                    self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' and item_uom='"+self.item_uom+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==1:
#                 self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==3:
#                 self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
     
            try:
                rec=self.env.cr.fetchall()
                if len(rec)>0:
                    for r in rec:
                        (xcurr_code,xharga,)=r
                     
                    if self.item_type==2:
                        self.curr_code=xcurr_code
                        self.estimasi_harga=xharga
                    else:
                        self.curr_code=""
                        self.estimasi_harga=0
            except:
                exit

#     @api.one
#     @api.depends("item_qty","uom_line_id")
#     def _get_total(self):
#         if self.item_no:
#             if self.item_type==2:
#                 if self.item_uom:
#                     self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' and item_uom='"+self.item_uom+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==1:
#                 self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
#             elif self.item_type==3:
#                     self.env.cr.execute("select currency_code, direct_unit_cost from sis_purchase_last_est_price where kode_item='"+self.item_no+"' order by id desc, posting_date desc limit 1")
#                     
#             try:
#                 rec=self.env.cr.fetchall()
#                 if len(rec)>0:
#                     for r in rec:
#                         (xcurr_code,xharga,)=r
#                     
#                     self.curr_code=xcurr_code
#                     self.estimasi_total=xharga*self.item_qty
#             except:
#                 exit
                
    def close_por_line(self):
        print(self.por_line_id.no_doc)
        print(self.no_line)

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        total_len = self.env['sis.po.requisition.lines'].search_count([('por_line_id', '=',vals['por_line_id'])])
        
        if total_len==0:
            noline=1
        else:
            noline=total_len+1
        
        vals_po_line={
           'no_line':noline
        }

        vals.update(vals_po_line) 
        res_id = models.Model.create(self, vals)
        return res_id
        
    @api.multi
    def unlink(self):
        
        i=1
        for x in self.por_line_id.por_line_id:
            if x.id!=self.id:
                x.no_line=i
                i=i+1
                 
                print(x.no_line)
            
        return super(po_requisition_lines, self).unlink()
            
            
#         rec_h = self.env['sis.po.requisition'].search([('no_doc', '=', self.por_line_id.no_doc)])
#         if len(rec_h)>0:
#             
#             
#             
#             self.env.cr.execute("select id from sis_po_requisition_lines where por_line_id="+str(rec_h.id))
#             rec=self.env.cr.fetchall()
# #  
#             if len(rec)>0:            
#                 noline=0
#                 for r in rec:
#                     (xid,)=r
#                     noline=noline+1
#                     self.env.cr.execute("update sis_po_requisition_lines set no_line="+str(noline)+" where id="+str(xid))
#          
#         return super(po_requisition_lines, self).unlink()
        