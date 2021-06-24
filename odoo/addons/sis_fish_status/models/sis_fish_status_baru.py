from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class sis_fish_status(models.Model):
    _name='sis.fish.status'
    _table='sis_fish_status'
    _auto=False
    _rec_name='barcode_no'

    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    vessel_no = fields.Char(size=100,string="Histamin",readonly=True)
    hatch_no = fields.Char(size=100,string="Histamin",readonly=True)
    voyage_no = fields.Char(size=100,string="Histamin",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    barcode_no = fields.Char(size=40,string="Barcode No",readonly=True)
    lot_no = fields.Char(size=40,string="Lot No",readonly=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)
    
class sis_fish_fresh_inv(models.Model):
    _name='sis.fish.fresh.inv'
    _table='sis_fish_fresh_inv'
    _auto=False

    entry_types = fields.Char(size=30,string="Entry Types",readonly=True)
    document_type = fields.Integer(string="Document Type",readonly=True)
    document_no = fields.Char(size=19,string="Document No.",readonly=True)
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    item_no_mix = fields.Char(size=20,string="Item No. Mix",readonly=True)
    lot_no = fields.Char(size=40,string="Lot No",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No.",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No.",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No.",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    lokasi = fields.Char(size=4,string="Lokasi",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No",readonly=True)
    purchase_document_no = fields.Char(size=15,string="Purchase Document No.",readonly=True)
    invoice_no = fields.Char(size=50,string="Invoice No",readonly=True)

class sis_nav_fish_status(models.Model):
    _name='sis.nav.fish.status'
    _table='sis_nav_fish_status'
    _auto=False

    pgc = fields.Char(size=20,string="Product Grp",readonly=True)    
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    posting_date = fields.Date(string="Posting Date", readonly=True)
    ps= fields.Char(size=30,string="P/S Type",readonly=True)
    entry_type= fields.Char(size=30,string="Entry Type",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    location_code = fields.Char(size=10,string="Location Code",readonly=True)
    bg = fields.Char(size=10,string="Business Group",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)

class sis_nav_fish_status_local(models.Model):
    _name='sis.nav.fish.status.local'

    pgc = fields.Char(size=20,string="Product Grp",readonly=True)    
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    posting_date = fields.Date(string="Posting Date", readonly=True)
    ps= fields.Char(size=30,string="P/S Type",readonly=True)
    entry_type= fields.Char(size=30,string="Entry Type",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    location_code = fields.Char(size=10,string="Location Code",readonly=True)
    bg = fields.Char(size=10,string="Business Group",readonly=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)

    def upload_from_NAV(self):
        self.env.cr.execute("delete from sis_nav_fish_status_local")
        self.env.cr.execute(" insert into sis_nav_fish_status_local(pgc,item_no,description,posting_date,ps,entry_type,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,location_code, "+\
                            " bg,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process, "+\
                            " remark_analisa,remark_process ) "+\
                            " select pgc,item_no,description,posting_date,ps,entry_type,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,location_code, "+\
                            " bg,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process, "+\
                            " remark_analisa,remark_process from sis_nav_fish_status ")

    
# class sis_fish_status_history(models.Model):
#     _name='sis.fish.status.history'
#     _rec_name='barcode_no'
#     
#     status_id = fields.Many2one('sis.fish.status.header', string="Fish Status", required=True)
#     link_id = fields.Many2one('sis.fish.status', string="Barcode No", required=True)
#     item_no = fields.Char(size=20,string="Item No.")
#     description= fields.Char(size=100,string="Description")
#     vessel_no = fields.Char(size=100,string="Vessel No.")
#     hatch_no = fields.Char(size=100,string="Hatch No.")
#     voyage_no = fields.Char(size=100,string="Voyage No.")
#     quantity = fields.Float(string='Quantity',required=True)
#     remaining_quantity = fields.Float(string='Remaining Quantity')
#     barcode_no = fields.Char(size=40,string="Barcode No", required=True)
#     lot_no = fields.Char(size=40,string="Lot No", required=True)
#     fish_box_no = fields.Char(size=20,string="Fish Box No.", required=True)
#     status = fields.Char(size=10,string="Status")
#     status_analisa = fields.Char(compute='update_history',size=10,string="Status Analisa",store=True)
#     status_process = fields.Char(size=10,string="Status Process")
#     histamin = fields.Char(size=100,string="Histamin")
#     kadar_garam = fields.Char(size=100,string="Kadar Garam")
#     orange_meat = fields.Char(size=100,string="Orange Meat")
#     blackspot = fields.Char(size=100,string="Blackspot")
#     pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus")
#     kontaminasi = fields.Char(size=100,string="Kontaminasi")
#     lain2_analisa = fields.Char(size=100,string="Lain2 Analisa")
#     lain2_process = fields.Char(size=100,string="Lain2 Process")
#     remark_analisa = fields.Char(size=100,string="Remark Analisa")
#     remark_process = fields.Char(size=100,string="Remark Process")
#     tgl_keluar = fields.Datetime(string="Tanggal Keluar CS",required=True,default=fields.Datetime.now())
#     no_potong = fields.Integer(string="No. Potong", required=True)
#     tgl_produksi = fields.Date(string="Tgl. Produksi", required=True)
#     fresh_fish = fields.Boolean(string="Fresh Fish", required=True, default=False)
#     status_def = fields.Integer(string="Status Defrost", required=True,default=0)
#   
#     @api.constrains('barcode_no')
#     def _constrains_barcode(self):
#         rec=self.env['sis.fish.status.history'].search([('barcode_no','=',self.barcode_no),('id','!=',self.id)])
#         if len(rec)>0:
#             qtyuse=0
#             for x in rec:
#                 qtyuse=qtyuse+x.quantity
#                   
#             navSQL="select quantity from sis_fish_status where barcode_no='"+self.barcode_no+"'"
#             self.env.cr.execute(navSQL)
#             navrc=self.env.cr.fetchall()
#             
#             if len(navrc)==0:
#                 qtysisa1=0
#             else:           
#                 for val_sisa1 in navrc :
#                     (qtysisa1,)=val_sisa1
#   
#                 if qtysisa1-qtyuse<self.quantity or self.quantity==0:
#                     raise UserError("Qty. barcode "+self.barcode_no+" tidak mecukupi. Sisa Qty : "+str(qtysisa1-qtyuse))
#   
#     @api.multi
#     def name_get(self):
#         result = []
#         for me in self :
#             result.append((me.id, "%s [%s]" % (me.barcode_no, me.no_potong)))
#         return result
#   
#     @api.one
#     @api.depends('barcode_no')
#     def update_history(self):
#         if self.barcode_no:
#             if self.barcode_no[:3]=="AT/" or self.barcode_no[:3]=="AT2":
#                 cSQL="select fish_box_no,lot_no,item_no,description,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process,remark_analisa,remark_process from sis_fish_status "
#                 self.env.cr.execute(cSQL+"where barcode_no='"+self.barcode_no+"'")
#                 rec_fish=self.env.cr.fetchall()
#                 if len(rec_fish)!=0:
#                     for cs_data in rec_fish:
#                         (xfish_box,xno_lot,xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xquantity,xremaining,xstatus,xstatus_analisa,xstatus_process,xhistamin,xkadargaram,xorangemeat,xblackspot,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess)=cs_data
#                 
#                     self.tgl_produksi = self.status_id.tgl_produksi
#                     self.fresh_fish = False
#                     self.item_no =  xitem_no
#                     self.description= xdescription
#                     self.vessel_no = xvessel_no
#                     self.hatch_no = xhatch_no
#                     self.voyage_no = xvoyage_no
#                     self.remaining_quantity = xremaining
#                     self.lot_no = xno_lot
#                     self.fish_box_no = xfish_box
#                     self.status = xstatus
#                     self.status_analisa = xstatus_analisa
#                     self.status_process = xstatus_process
#                     self.histamin = xhistamin
#                     self.kadar_garam = xkadargaram
#                     self.orange_meat = xorangemeat
#                     self.blackspot = xblackspot
#                     self.pemakaian = xpemakaian
#                     self.kontaminasi = xkontaminasi
#                     self.lain2_analisa = xlainanalisa
#                     self.lain2_process = xlainprocess
#                     self.remark_analisa = xremanalisa
#                     self.remark_process = xremprocess
#                     self.status_def=0
#                     
#                     qtyuse=0
#                     rec=self.env['sis.fish.status.history'].search([('barcode_no','=',self.barcode_no)])
#                     if len(rec)!=0:
#                         for x in rec:
#                             qtyuse=qtyuse+x.quantity
#                              
#                         self.quantity=xquantity-qtyuse
#                     else:
#                         self.quantity=xquantity
#                 else:
#                     raise UserError("Barcode "+self.barcode_no+" tidak ada!")
#                     
#     def _get_data_cs(self,kode):
#         if kode:
#             cSQL="select item_no,description,vessel_no,hatch_no,voyage_no,remaining_quantity,lot_no,fish_box_no,status,pemakaian,kontaminasi,lain2_analisa,lain2_process,remark_analisa,remark_process from sis_fish_status "
#             self.env.cr.execute(cSQL+"where barcode_no='"+kode+"'")
#             rec_fish=self.env.cr.fetchall()
#             if len(rec_fish)>0:
#                 for cs_data in rec_fish:
#                     (xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess)=cs_data
# 
#             return xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess
# 
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self,vals):
#             cr_data=self.env['sis.fish.status.history'].search([('barcode_no','=',vals['barcode_no']),('no_potong','=',vals['no_potong']),('tgl_produksi','=',self.status_id.tgl_produksi),('status_def','=',0)])
#             if len(cr_data)==0:
#                 if vals['fresh_fish']==False:
#                     xitem_no,xdescription,xvessel_no,xhatch_no,xvoyage_no,xremaining,xno_lot,xfish_box,xstatus,xpemakaian,xkontaminasi,xlainanalisa,xlainprocess,xremanalisa,xremprocess=self._get_data_cs(vals['barcode_no'])
#                     vals_cs={
#                         'item_no':xitem_no,
#                         'description':xdescription,
#                         'vessel_no':xvessel_no,
#                         'hatch_no':xhatch_no,
#                         'voyage_no':xvoyage_no,
#                         'remaining_quantity':xremaining,
#                         'lot_no':xno_lot,
#                         'fish_box_no':xfish_box,
#                         'status':xstatus, 
#                         'pemakaian':xpemakaian,
#                         'kontaminasi':xkontaminasi,
#                         'lain2_analisa':xlainanalisa,
#                         'lain2_process':xlainprocess,
#                         'remark_analisa':xremanalisa,
#                         'remark_process':xremprocess
#                         }
#                 else:
#                     vals_cs={
#                         'pemakaian':"",
#                         'kontaminasi':"",
#                         'lain2_analisa':"",
#                         'lain2_process':"",
#                         'remark_analisa':"",
#                         'remark_process':""
#                         }
#                        
#                 vals.update(vals_cs) 
#                 res_id = models.Model.create(self, vals)
#                 return res_id
#             else:
#                 if vals['barcode_no'][:3]=="AT/" or vals['barcode_no'][:3]=="AT2":
#                     for r in cr_data:
#                         vals_data={
#                             'quantity':r.quantity+vals['quantity']
#                             }
#                     r.write(vals_data)
#                 else:
#                     res_id = models.Model.create(self, vals)
#                     return res_id
#                     
# 
#     @api.multi
#     def unlink(self):
#         orders = self.mapped('status_id')
#         for order in orders:
#             order_lines = self.filtered(lambda x: x.status_id == order)
#             msg = ""
#             for line in order_lines:
#                 msg += "Barcode" + ": %s <b>[ <i>deleted</i> ]</b><br/>" % (line.barcode_no,)
#             order.message_post(body=msg)
#         return super(sis_fish_status_history, self).unlink()
#      
#     @api.multi
#     def write(self, vals):
#         if self.status_id.cs_id:
#             cSQL1="select b.quantity from sis_fish_status_header as a, sis_fish_status_history as b where b.status_id=a.id and b.id<>'"+str(self.id)+"' and b.status_def=0 "
#             cSQL2="and b.barcode_no='"+self.barcode_no+"' and b.no_potong='"+str(self.no_potong)+"' and b.tgl_produksi='"+self.tgl_produksi+"' and a.cs_id='"+self.status_id.cs_id+"'"
#  
#             self.env.cr.execute(cSQL1+cSQL2)
#             cr_data=self.env.cr.fetchall()
#      
#             if len(cr_data)==0:
#                 orders = self.mapped('status_id')
#                 for order in orders:
#                     order_lines = self.filtered(lambda x: x.status_id == order)
#                     msg = ""
#                     for line in order_lines:
#                         if vals.get('barcode_no'):
#                             msg += "Barcode" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (line.barcode_no, vals['barcode_no'],)
#                         if vals.get('tgl_keluar'):
#                             msg += "Tgl. Keluar" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.tgl_keluar), str(vals['tgl_keluar']),)
#                         if vals.get('no_potong'):
#                             msg += "No. Potong" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_potong), str(vals['no_potong']),)
#                         if vals.get('quantity'):
#                             msg += "Qty." + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.quantity), str(vals['quantity']),)
#                     order.message_post(body=msg)
#                      
#                     vals.update({'tgl_produksi':self.status_id.tgl_produksi})
#                     return super(sis_fish_status_history, self).write(vals)
#             else:
#                 for r in cr_data:
#                     (r_quantity,)=r
#                     vals_data={
#                        'quantity':r_quantity+self.quantity
#                     }
#                 vals.update(vals_data)            
#                 return super(sis_fish_status_history, self).write(vals)

# class fish_status_header(models.Model):
#     _inherit = ['mail.thread']
#     _name = "sis.fish.status.header"
#     _description = "Status Fish Header"
#     _order = "cs_id"
#     
#     cs_id = fields.Char(string="No. CS", size=15, default='/')
#     pabrik_id = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')], required=True, track_visibility="onchange")
#     tgl_produksi = fields.Date(string="Tanggal Produksi",required=True,default=fields.Datetime.now(), track_visibility="onchange")
#     cs_state = fields.Selection([('draft','Draft'),('confirm','Confirmed')], string='State', default='draft', track_visibility="onchange")
#     fish_status_detail = fields.One2many('sis.fish.status.history', 'status_id', string='Status ID')
#     invoice = fields.Boolean(string='Invoice')
#     invoice_no = fields.Char(string="No. Invoice", size=25)
#     
#     def get_data_fresh_fish(self):
#         if self.invoice_no:
#             self.env['sis.fish.status.history'].search([('barcode_no','=',self.invoice_no),('status_id','=',self.id)]).unlink()
#             cField="a.item_no,a.description,a.lot_no,a.vessel_no,a.hatch_no,a.voyage_no,a.quantity,a.status,a.fish_box_no"
#             cSQL1="select "+cField+" from sis_fish_fresh_inv a left join sis_fish_status_history b on a.invoice_no=b.barcode_no and a.quantity=b.quantity "
#             cSQL2=" where b.barcode_no is null and a.invoice_no='"+str(self.invoice_no)+"'"
#             self.env.cr.execute(cSQL1+cSQL2)
#             fresh_fish_data=self.env.cr.fetchall()
#             if len(fresh_fish_data)>0:
#                 new_lines = self.env['sis.fish.status.history']
#                 for ff_data in fresh_fish_data:
#                     (xitem_no,xdescription,xno_lot,xvessel_no,xhatch_no,xvoyage_no,xquantity,xstatus,xfish_box)=ff_data
#                 
#                     vals = {'barcode_no'    : self.invoice_no,
#                             'tgl_keluar'    : datetime.now(),
#                             'fresh_fish'    : True,
#                             'no_potong'     : 0,
#                             'item_no'       : xitem_no,
#                             'description'   : xdescription,
#                             'lot_no'        : xno_lot,
#                             'vessel_no'     : xvessel_no,
#                             'hatch_no'      : xhatch_no,
#                             'voyage_no'     : xvoyage_no,
#                             'quantity'      : xquantity,
#                             'status'        : xstatus,
#                             'fish_box_no'   : xfish_box,
#                             'tgl_produksi'  : self.tgl_produksi
#                             }
#                     new_lines += new_lines.new(vals)
#                 self.fish_status_detail = new_lines
#             else:
#                 raise UserError("Invoice "+str(self.invoice_no)+" tidak ada!")
#     
#     def _get_prefix(self,pabrik):
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
#                 no_prefix = "CS1/"+str(d_tahun)+str(d_bulan)+"-"
#             elif pabrik=="ATI2":
#                 no_prefix = "CS2/"+str(d_tahun)+str(d_bulan)+"-"
# 
#             rec=self.env['sis.fish.status.header'].search([('cs_id','ilike',no_prefix)])
#             if len(rec)>0:
#                 self.env.cr.execute("select max(cast(substring(cs_id,12,4) as integer)) from sis_fish_status_header where cs_id like '"+no_prefix+"%'")
#                 rc=self.env.cr.fetchall()
#                  
#                 for b in rc :
#                     (x,)=b
#                 no_urut=x+1
#                 if no_urut<10:
#                     cs_id=no_prefix+"000"+str(no_urut)
#                 elif no_urut>9 and no_urut<100:
#                     cs_id=no_prefix+"00"+str(no_urut)
#                 elif no_urut>999 and no_urut<1000:
#                     cs_id=no_prefix+"0"+str(no_urut)
#                 else:
#                     cs_id=no_prefix+str(no_urut)
#             else:
#                 no_urut=1
#                 cs_id=no_prefix+"000"+str(no_urut)
# 
#             return cs_id
#     
#     @api.model
#     @api.returns('self', lambda value:value.id)
#     def create(self,vals):
#         csid=self._get_prefix(vals['pabrik_id'])
#         vals.update({'cs_id':csid}) 
#         res_id = models.Model.create(self, vals)
#         return res_id
# 
#     @api.multi
#     def action_confirm(self):
#         for me_id in self :
#             if me_id.cs_state == 'draft':
#                 me_id.write({'cs_state':'confirm'})
#     
#     @api.multi
#     def action_unconfirm(self):
#         for me_id in self :
#             if me_id.cs_state == 'confirm':
#                 self.env.cr.execute("update sis_fish_status_header set cs_state='draft' where cs_id='"+str(me_id.cs_id)+"'")
# 
#     @api.multi
#     def action_cancel(self):
#         for me_id in self :
#             if me_id.cs_state != 'draft':
#                 me_id.write({'cs_state':'cancel'})
# 
#     
#     @api.multi
#     def unlink(self):
#         for me_id in self :
#             if me_id.cs_state != 'draft' :
#                 raise UserError("Cannot delete!")
#             else:
#                 self.env.cr.execute("delete from sis_fish_status_history where status_id='"+str(me_id.id)+"'")
# 
#         return super(fish_status_header, self).unlink()
#     
#     @api.multi
#     def write(self, vals):
#         for me_id in self :
#             if me_id.cs_state != 'draft' :
#                 if vals.get('cs_state') and vals['cs_state']=='draft':
#                     return super(fish_status_header, self).write(vals)
#                 else:
#                     raise UserError("Cannot update!")
#             return super(fish_status_header, self).write(vals)
#     
