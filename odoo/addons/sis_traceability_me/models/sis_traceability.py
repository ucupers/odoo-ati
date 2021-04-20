from odoo import models, fields, api
from odoo import tools

class sis_trace_view(models.Model):
    _name = 'sis.trace.view'
    _order = "tgl_produksi desc, no_potong desc"    
    _auto = False

    tgl_produksi    = fields.Date(string="Tgl. Produksi")
    pabrik_id       = fields.Char(string="Lokasi", size=4)
    no_potong       = fields.Integer(string="No. Potong")
    fresh_fish      = fields.Boolean(string="Fresh Fish")
    barcode_no      = fields.Char(size=40,string="Barcode No")
    fish_box_no     = fields.Char(size=20,string="Fish Box No.")
    quantity        = fields.Float(string='Quantity')
    fish_type       = fields.Char(size=2, string="Jenis Ikan")
    fish_size       = fields.Char(size=5,string="Fish Size")
    no_tangki       = fields.Char(string="No. Tangki", size=7)
    no_line         = fields.Integer(string="No. Line")
    basket_id       = fields.Char(size=4, string='Basket ID')
    label           = fields.Integer(string="No. Label")
    tespek          = fields.Selection([(0,'No'),(1,'Yes')], string='Test', default=0)
    nocooking       = fields.Integer(string="No. Cooking")
    nocooker        = fields.Integer(string="No. Cooker")
    steamon         = fields.Datetime(string='Steam On')
    steamoff        = fields.Datetime(string='Steam Off')
    startshowertime = fields.Datetime(string='Mulai Showering')
    stopshowertime  = fields.Datetime(string='Selesai Showering')
    showerline      = fields.Integer(string='Shower Line')
    coolingroomline = fields.Integer(string='Cooling Line')
    po              = fields.Char(size=20,string="PO No.")
    status          = fields.Char(size=10,string="Status QC")
    tgl_keluar      = fields.Datetime(string="Tanggal Keluar CS")
    suhu_before     = fields.Float(string="Suhu Awal")     
    tgl_start       = fields.Datetime(string="Start Defrost")
    suhu_after      = fields.Float(string="Suhu Akhir")     
    tgl_finish      = fields.Datetime(string="Finish Defrost")
    tgl_tuang       = fields.Datetime(string="Jam Potong")
    remark          = fields.Char(string="Remark Defrost")
    item_no         = fields.Char(size=20,string="Item No.")
    description     = fields.Char(size=100,string="Description")
    vessel_no       = fields.Char(size=100,string="Vessel No.")
    hatch_no        = fields.Char(size=100,string="Hatch No.")
    voyage_no       = fields.Char(size=100,string="Voyage No.")
    status_pl       = fields.Boolean(string="Pole & Line")

    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_trace_view as (
        SELECT
        row_number() OVER () as id, 
        cs.tgl_produksi, cs.pabrik_id, cs.no_potong, cs.fresh_fish, cs.barcode_no, cs.fish_box_no, cs.quantity, cs.product_group_code as fish_type, cs.real_item_no as fish_size,
        def.no_tangki, def.no_line,
        cutbasket.basket_id, cutbasket.label, cutbasket.tespek,
        cook.nocooking, cook.nocooker, cook.steamon, cook.steamoff, cook.startshowertime, cook.stopshowertime, cook.showerline, cook.coolingroomline,
        cs.po, cs.status, cs.tgl_keluar, def.suhu_before, def.tgl_start, def.suhu_after, def.tgl_finish, def.tgl_tuang, def.remark,
        cs.item_no, cs.description, cs.vessel_no, cs.hatch_no, cs.voyage_no, cs.status_pl
        
        FROM 
        sis_cs_detail cs 
        left join sis_defrost_detail def on def.barcode_no=cs.barcode_no and def.tgl_produksi=cs.tgl_produksi and def.pabrik_id=cs.pabrik_id and def.no_potong=cs.no_potong
        left join sis_cutting_tangki cuttangki on cuttangki.tgl_produksi=def.tgl_produksi and cuttangki.location=def.pabrik_id and cuttangki.no_potong=def.no_potong and cuttangki.no_tangki=def.no_tangki
        left join sis_cutting cut on cut.id=cuttangki.rel_cutting
        left join sis_cutting_basket cutbasket on cutbasket.rel_cutting=cut.id
        left join sis_cooker_basket cookbasket on cookbasket.productiondate=cuttangki.tgl_produksi and cookbasket.location=cuttangki.location and cookbasket.basket_id=cutbasket.basket_id and cookbasket.label=cutbasket.label
        left join sis_cooker cook on cook.id=cookbasket.rel_cooker)
        """
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_trace_view')
        self._cr.execute(cSQL)




# class sis_trace_header(models.Model):
#     _name='sis.trace.header'
#     _rec_name='trace_id'
#     
#     trace_id        = fields.Char(string="Trace ID", size=12, default='/')
#     tgl_produksi    = fields.Date(string="Tanggal Produksi", required=True, default=fields.Datetime.now())
#     pabrik_id       = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')], required=True)
#     produk_id       = fields.Char(string="Product", size=100)
#     trace_proses    = fields.Float(string="Progress")
#     proses_desc     = fields.Char(string="Step", size=50)
#     status          = fields.Selection(string="Status", selection=[('1', 'OK'),('0', 'NOT OK')])
#     status_desc     = fields.Char(string="Keterangan", size=100)
#     detail_cs       = fields.One2many('sis.cs.detail', 'trace_detail_id', string='Trace Detail ID')
    #detail_defrost  = fields.One2many('sis.defrost.detail', 'trace_detail_id', string='Trace Detail ID')

# class sis_cs_detail(models.Model):
#     _name='sis.cs.detail'
#     
#     trace_detail_id = fields.Many2one('sis.trace.header', string="Detail CS", required=True)
#     no_potong       = fields.Integer(string="No. Potong", required=True)
#     fresh_fish      = fields.Boolean(string="Fresh Fish", required=True)
#     barcode_no      = fields.Char(size=40,string="Barcode No", required=True)
#     tgl_produksi    = fields.Date(string="Tanggal Produksi",required=True)
#     tgl_keluar      = fields.Datetime(string="Tanggal Keluar CS",required=True)
#     fish_box_no     = fields.Char(size=20,string="Fish Box No.", required=True)
#     item_no         = fields.Char(size=20,string="Item No.")
#     description     = fields.Char(size=100,string="Description")
#     vessel_no       = fields.Char(size=100,string="Vessel No.")
#     hatch_no        = fields.Char(size=100,string="Hatch No.")
#     voyage_no       = fields.Char(size=100,string="Voyage No.")
#     quantity        = fields.Float(string='Quantity',required=True)
#     remaining_quantity = fields.Float(string='Remaining Quantity')
#     lot_no          = fields.Char(size=40,string="Lot No", required=True)
#     status          = fields.Char(size=10,string="Status")
