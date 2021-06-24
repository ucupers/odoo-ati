from odoo import models, fields, api
from odoo import tools

class sis_trace_view(models.Model):
    _name = 'sis.trace.view'
    _order = "tgl_produksi desc"    
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
    no_line         = fields.Char(string="No. Line")
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
    pcl             = fields.Integer(string="Line Pre Cleaning")
    jamstart        = fields.Char(string="Jam Mulai Pre")
    jamfinish       = fields.Char(string="Jam Selesai Pre")
#     line_group_cl   = fields.Char(string="Line Group Cl")
#     kind_of_product = fields.Char(string="Jenis Produk")
#     jam_cl          = fields.Char(string="Jam Cleaning")
#     fish            = fields.Char(string="Basket Fish")
#     loin            = fields.Char(string="Basket Loin")
#     shreded         = fields.Char(string="Basket Shreded")
#     line            = fields.Char(string="Line")

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
        cs.item_no, cs.description, cs.vessel_no, cs.hatch_no, cs.voyage_no, cs.status_pl, pre.pcl, pre.jamstart, pre.jamfinish
         
         
         
        FROM 
        sis_cs_detail cs 
        left join sis_defrost_detail def on def.barcode_no=cs.barcode_no and def.tgl_produksi=cs.tgl_produksi and def.pabrik_id=cs.pabrik_id and def.no_potong=cs.no_potong
        left join sis_cutting_tangki cuttangki on cuttangki.tgl_produksi=def.tgl_produksi and cuttangki.location=def.pabrik_id and cuttangki.no_potong=def.no_potong and cuttangki.no_tangki=def.no_tangki
        left join sis_cutting cut on cut.id=cuttangki.rel_cutting
        left join sis_cutting_basket cutbasket on cutbasket.rel_cutting=cut.id
        left join sis_cooker_basket cookbasket on cookbasket.productiondate=cuttangki.tgl_produksi and cookbasket.location=cuttangki.location and cookbasket.basket_id=cutbasket.basket_id and cookbasket.label=cutbasket.label
        left join sis_cooker cook on cook.id=cookbasket.rel_cooker
        left join sis_pre_cleaning pre on cookbasket.id=pre.basket)
        """
         
        cSQL2="""
        CREATE OR REPLACE VIEW sis_trace_view as (
        SELECT
        row_number() OVER () as id, 
        csd.tgl_produksi, csd.pabrik_id, csd.no_potong, csd.fresh_fish, csd.barcode_no, csd.fish_box_no, csd.quantity, csd.product_group_code as fish_type, csd.real_item_no as fish_size,
        defd.no_tangki, defd.no_line,
        cutb.basket_id, cutb.label, cutb.tespek,
        cook.nocooking, cook.nocooker, cook.steamon, cook.steamoff, cook.startshowertime, cook.stopshowertime, cook.showerline, cook.coolingroomline,
        csd.po, csd.status, csd.tgl_keluar, defd.suhu_before, defd.tgl_start, defd.suhu_after, defd.tgl_finish, defd.tgl_tuang, defd.remark,
        csd.item_no, csd.description, csd.vessel_no, csd.hatch_no, csd.voyage_no, csd.status_pl, pre.pcl, pre.jamstart, pre.jamfinish,
        pack.kind_of_product, pack_de.line_group_cl, pack_de.jam_cl, pack_de.fish, pack_de.loin, pack_de.shreded
         
        FROM 
        sis_cs_header csh
        left join sis_cs_detail csd on csd.cs_line_id=csh.id
        left join sis_defrost_detail defd on defd.defrost_link_id=csd.id
        left join sis_defrost_header defh on defh.id=defd.detail_id
        left join sis_cutting_tangki cutt on cutt.rel_defrost=defd.id
        left join sis_cutting cut on cut.id=cutt.rel_cutting
        left join sis_cutting_basket cutb on cutb.rel_cutting=cut.id
        left join sis_cooker_basket cookb on cookb.rel_basket_cutting=cutb.id
        left join sis_cooker cook on cook.id=cookb.rel_cooker
        left join sis_pre_cleaning pre on cookb.id=pre.basket
        left join pack_pre_rel rel on pre.id=rel.pre_id
        left join sis_packing_detail pack_de on pack_de.id=rel.pack_id
        left join sis_packing pack on pack.id=pack_de.rel_header)
        """
        
        cSQL3="""
        CREATE OR REPLACE VIEW sis_trace_view as (
        SELECT
        row_number() OVER () as id, 
        cs.tgl_produksi, cs.pabrik_id, cs.no_potong, cs.fresh_fish, cs.barcode_no, cs.fish_box_no, cs.quantity, cs.product_group_code as fish_type, cs.real_item_no as fish_size,
        def.no_tangki, def.no_line,
        cutbasket.basket_id, cutbasket.label, cutbasket.tespek,
        cook.nocooking, cook.nocooker, cook.steamon, cook.steamoff, cook.startshowertime, cook.stopshowertime, cook.showerline, cook.coolingroomline,
        cs.po, cs.status, cs.tgl_keluar, def.suhu_before, def.tgl_start, def.suhu_after, def.tgl_finish, def.tgl_tuang, def.remark,
        cs.item_no, cs.description, cs.vessel_no, cs.hatch_no, cs.voyage_no, cs.status_pl, pre.pcl, pre.jamstart, pre.jamfinish
        ,pack_de.line_group_cl
          
        FROM 
        sis_cs_detail cs 
        left join sis_defrost_detail def on def.barcode_no=cs.barcode_no and def.tgl_produksi=cs.tgl_produksi and def.pabrik_id=cs.pabrik_id and def.no_potong=cs.no_potong
        left join sis_cutting_tangki cuttangki on cuttangki.tgl_produksi=def.tgl_produksi and cuttangki.location=def.pabrik_id and cuttangki.no_potong=def.no_potong and cuttangki.no_tangki=def.no_tangki
        left join sis_cutting cut on cut.id=cuttangki.rel_cutting
        left join sis_cutting_basket cutbasket on cutbasket.rel_cutting=cut.id
        left join sis_cooker_basket cookbasket on cookbasket.productiondate=cuttangki.tgl_produksi and cookbasket.location=cuttangki.location and cookbasket.basket_id=cutbasket.basket_id and cookbasket.label=cutbasket.label
        left join sis_cooker cook on cook.id=cookbasket.rel_cooker
        left join sis_pre_cleaning pre on cookbasket.id=pre.basket
        left join pack_pre_rel rel on pre.id=rel.pre_id
        left join sis_packing_detail pack_de on pack_de.id=rel.pack_id)
        """
#         pack.kind_of_product, pack_de.jam_cl, pack.line
#         inner join pack_pre_rel rel on pre.id=rel.pre_id
#         inner join sis_packing_detail pack_de on pack_de.id=rel.pack_id
#         inner join sis_packing pack on pack.id=pack_de.rel_header)

        
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_trace_view')
        self._cr.execute(cSQL)
#         print(cSQL3)
        



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


class sis_trace_backward(models.TransientModel):
    _name = 'sis.trace.backward'
    _description = 'Tracing Backward'
    
    detail_id = fields.One2many('sis.trace.backward.detail', 'head_id', string='Detail ID')
    
    productiondate = fields.Date('Tanggal Produksi ATI')
    produk = fields.Char('Nama Produk')
    jam_mulai_bongkar = fields.Float('Jam Mulai Bongkar (WH Unlabeled)')
    jam_mulai_bongkar_real = fields.Float('jam Mulai Bongkar Real', compute="_get_jam_mulai_real", store=True)
    line = fields.Integer('Line Unlabeled')
    
    @api.one
    @api.depends('jam_mulai_bongkar')
    def _get_jam_mulai_real(self):
        if self.jam_mulai_bongkar:
            self.jam_mulai_bongkar_real='{0:02.0f}.{1:02.0f}'.format(*divmod(float(self.jam_mulai_bongkar) * 60, 60))
    
    def caridata(self):
#         ssql="""select wh_d.jam_mulai, wh_d.jam_selesai, wh_d.jam_mulai_real, wh_d.jam_selesai_real from sis_wh_bongkar_produk as wh_h
#                 left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
#                 where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)
#         print(ssql)
#         self.env.cr.execute(ssql)
#         datata=self.env.cr.fetchall()
#         print(datata)
        unl = self.env['sis.trace.backward.detail'].search([('head_id','=',self.id)])
        unl.unlink()
        
        csql="""select relo_d.jam_mulai, relo_d.jam_selesai

                from sis_wh_bongkar_produk as wh_h 
                left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
                
                left join sis_retort_loading_basket_detail as relo_d on wh_d.retort_loading_id=relo_d.id
                left join basket_retort_ids as rel_rt_load on rel_rt_load.sis_retort_loading_basket_detail_id=relo_d.id
                left join sis_retort_detail as rt_d on rel_rt_load.sis_retort_detail_id=rt_d.id
                left join sis_retort_header as rt_h on rt_d.retort_header_id=rt_h.id
                
                where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)
        print(csql)
        self.env.cr.execute(csql)
        datas=self.env.cr.fetchall()
        print(datas)
        delsql="delete from sis_tb_packing_bt"
        self.env.cr.execute(delsql)
        if datas: 
            for data in datas:
                (mulai, selesai,)=data
                ccsql="""insert into sis_tb_packing_bt(productiondate, produk, jam_packing, pkd_id, pk_id)
                        (select pk.productiondate, pk.kind_of_product, pk_d.jam_packing, pk_d.id, pk.id from sis_packing_detail pk_d
                        left join sis_packing pk on pk.id=pk_d.rel_header
                        where pk_d.productiondate='"""+self.productiondate+"' and pk.kind_of_product='"+self.produk+"' and pk_d.jam_packing>="""+str(mulai)+""" 
                        and pk_d.jam_packing<="""+str(selesai)+""")
                        union                        
                        (select pk.productiondate, pk.kind_of_product, pk_d.jam_packing, pk_d.id, pk.id from sis_packing_detail pk_d
                        left join sis_packing pk on pk.id=pk_d.rel_header
                        where pk_d.productiondate='"""+self.productiondate+"' and pk.kind_of_product='"+self.produk+"""' and pk_d.jam_packing<"""+str(mulai)+"""
                        order by pk_d.jam_packing desc
                        limit 2)                
                        """
                print(ccsql)
                self.env.cr.execute(ccsql)
        realsql = """
                    select wh_h.produk, wh_h.productiondate, wh_d.jam_mulai_real, wh_d.basket_no, wh_d.pallet,
                    rt_h.no_retort, rt_d.no_siklus, rt_d.steam_on_real, rt_d.jam_basket_keluar_real, relo_d.jam_mulai_real,
                    relo_d.jam_selesai_real,
                    pk_d.jam_cl_real, pk_d.jam_packing_real,
                    pre.jamstart, pre.jamfinish,
                    cook.nocooking, cook.nocooker,
                    cut_b.basket_id, cut_b.label,
                    def_d.no_tangki, def_d.fish_box_no, def_d.barcode_no,
                    csd.item_no, csd.description, csd.vessel_no, csd.hatch_no, csd.voyage_no, csd.lot_no
                    
                    from sis_wh_bongkar_produk as wh_h 
                    left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
                    
                    left join sis_retort_loading_basket_detail as relo_d on wh_d.retort_loading_id=relo_d.id
                    left join basket_retort_ids as rel_rt_load on rel_rt_load.sis_retort_loading_basket_detail_id=relo_d.id
                    left join sis_retort_detail as rt_d on rel_rt_load.sis_retort_detail_id=rt_d.id
                    left join sis_retort_header as rt_h on rt_d.retort_header_id=rt_h.id
                    left join sis_retort_loading_basket as relo_h on relo_h.id=relo_d.header_id
                    left join sis_tb_packing_bt as tbp on tbp.pk_id=relo_h.packing_id
                    left join sis_packing_detail as pk_d on tbp.pkd_id=pk_d.id
                    left join pack_pre_rel as rel_rm on rel_rm.pack_id=pk_d.id
                    left join sis_pre_cleaning as pre on pre.id=rel_rm.pre_id
                    left join sis_cooker_basket as cook_b on cook_b.id=pre.basket
                    left join sis_cooker as cook on cook.id=cook_b.rel_cooker
                    left join sis_cutting_basket as cut_b on cut_b.id=cook_b.rel_basket_cutting
                    left join sis_cutting as cut on cut.id=cut_b.rel_cutting
                    left join sis_cutting_tangki as cut_t on cut_t.rel_cutting=cut.id
                    left join sis_defrost_detail as def_d on cut_t.rel_defrost=def_d.id
                    left join sis_cs_detail as csd on csd.id=def_d.defrost_link_id
                    
                    where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)+" and cut_b.label is not null"
        
        self.env.cr.execute(realsql)
        result =self.env.cr.fetchall()
        
        if result:
            for dt in result:
                (xproduk, xproductiondate, xjammulaibongkarwh, xbasketre, xpallet, xno_retort, xno_siklus, 
                xsteam_on_retort, xjam_basket_keluar, xjam_mulai_muat_rt, xjam_selesai_muat_rt, xjam_cl, 
                xjam_pack, xstartpre, sfinishpre, xnocooking, xnocooker, xbasketcut, xlabelcut, xnotangki,
                xfishboxno, xbarcodeno, csditemno, csddescription, csdvessel_no, csdhatch_no, csdvoyage_no, csdlot_no)= dt
                        
                vals_detail = {
                    'head_id' : self.id,
                    'produk' : xproduk,
                    'productiondate' : xproductiondate,
                    'jam_mulai_bongkar_wh' : xjammulaibongkarwh,
                    'basket_retort' : xbasketre,
                    'pallet' : xpallet,
                    'no_retort' : xno_retort,
                    'no_siklus' : xno_siklus,
                    'steam_on_retort' : xsteam_on_retort,
                    'jam_basket_keluar' : xjam_basket_keluar,
                    'jam_mulai_muat_rt' : xjam_mulai_muat_rt,
                    'jam_selesai_muat_rt' : xjam_selesai_muat_rt,
                    'jam_cl' : xjam_cl,
                    'jam_pack' : xjam_pack, 
                    'jamstartpre' : xstartpre,
                    'jamfinishpre' : sfinishpre,
                    'nocooking' : xnocooking,
                    'nocooker' : xnocooker,
                    'basket_cutting' : xbasketcut,
                    'label_cutting' : xlabelcut,
                    'no_tangki' : xnotangki,
                    'fish_box_no' : xfishboxno,
                    'barcode_no' : xbarcodeno,
                    'item_no'  : csditemno,
                    'description' : csddescription,
                    'vessel_no' : csdvessel_no,
                    'hatch_no' : csdhatch_no,
                    'voyage_no' : csdvoyage_no,
                    'lot_no' : csdlot_no,
                    'status_ikan' : 'fish'
                    }
                create_detail = self.env['sis.trace.backward.detail']
                create_detail.create(vals_detail)
                
        realsql2="""select wh_h.produk, wh_h.productiondate, wh_d.jam_mulai_real, wh_d.basket_no, wh_d.pallet,
                    rt_h.no_retort, rt_d.no_siklus, rt_d.steam_on_real, rt_d.jam_basket_keluar_real, relo_d.jam_mulai_real,
                    relo_d.jam_selesai_real,
                    pk_d.jam_cl_real, pk_d.jam_packing_real,
                    unpk.jam_bongkar_real, unpk.no_urut_kereta,
                    cl.tgl_bongkar, cl.kode_produksi, cl.jambongkar_real, cl.start_thawing_real, cl.fish_box_no, 
                    csd.barcode_no, csd.item_no, csd.description, csd.vessel_no, csd.hatch_no, csd.voyage_no, csd.lot_no
                                        
                    from sis_wh_bongkar_produk as wh_h 
                    left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
                                        
                    left join sis_retort_loading_basket_detail as relo_d on wh_d.retort_loading_id=relo_d.id
                    left join basket_retort_ids as rel_rt_load on rel_rt_load.sis_retort_loading_basket_detail_id=relo_d.id
                    left join sis_retort_detail as rt_d on rel_rt_load.sis_retort_detail_id=rt_d.id
                    left join sis_retort_header as rt_h on rt_d.retort_header_id=rt_h.id
                    left join sis_retort_loading_basket as relo_h on relo_h.id=relo_d.header_id
                    left join sis_tb_packing_bt as tbp on tbp.pk_id=relo_h.packing_id
                    left join sis_packing_detail as pk_d on tbp.pkd_id=pk_d.id
                    left join rel_unpack_pack as rel_fz on rel_fz.sis_packing_detail_id=pk_d.id
                    left join sis_unpacking_defrost_loin as unpk on unpk.id=rel_fz.sis_unpacking_defrost_loin_id
                    left join sis_cleaning as cl on cl.id=unpk.rel_cleaning_unpack
                    left join sis_cs_detail as csd on csd.id=cl.rel_cs_detail
                    
                    where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)+" and unpk.no_urut_kereta is not null"
        
        self.env.cr.execute(realsql2)
        result2 =self.env.cr.fetchall()
        
        if result2:
            for dt2 in result2:
                (xproduk, xproductiondate, xjammulaibongkarwh, xbasketre, xpallet,
                 xno_retort, xno_siklus, xsteam_on_retort, xjam_basket_keluar, xjam_mulai_muat_rt, xjam_selesai_muat_rt, xjam_cl, 
                xjam_pack, unpkjambongkar_real, unpkno_urut_kereta, cltanggal_bongkar, clkode_produksi, cljam_bongkar, clstart_thawing, 
                xfishboxno, xbarcodeno, csditemno, csddescription, csdvessel_no, csdhatch_no, csdvoyage_no, csdlot_no)= dt2
                        
                vals_detail = {
                    'head_id' : self.id,
                    'produk' : xproduk,
                    'productiondate' : xproductiondate,
                    'jam_mulai_bongkar_wh' : xjammulaibongkarwh,
                    'basket_retort' : xbasketre,
                    'pallet' : xpallet,
                    'no_retort' : xno_retort,
                    'no_siklus' : xno_siklus,
                    'steam_on_retort' : xsteam_on_retort,
                    'jam_basket_keluar' : xjam_basket_keluar,
                    'jam_mulai_muat_rt' : xjam_mulai_muat_rt,
                    'jam_selesai_muat_rt' : xjam_selesai_muat_rt,
                    'jam_cl' : xjam_cl,
                    'jam_pack' : xjam_pack, 
                    'jam_bongkar_unpacking' : unpkjambongkar_real,
                    'no_urut_kereta' : unpkno_urut_kereta,
                    'tgl_bongkar_fz' : cltanggal_bongkar,
                    'kode_produksi_loin' : clkode_produksi,
                    'jam_bongkar_fz' : cljam_bongkar,
                    'start_thawing_fz' : clstart_thawing,
                    'fish_box_no' : xfishboxno,
                    'barcode_no' : xbarcodeno,
                    'item_no'  : csditemno,
                    'description' : csddescription,
                    'vessel_no' : csdvessel_no,
                    'hatch_no' : csdhatch_no,
                    'voyage_no' : csdvoyage_no,
                    'lot_no' : csdlot_no,
                    'status_ikan' : 'loin'
                    }
                create_detail = self.env['sis.trace.backward.detail']
                create_detail.create(vals_detail)
        
        realsql3 = """
                    select wh_h.produk, wh_h.productiondate, wh_d.jam_mulai_real, wh_d.basket_no, wh_d.pallet,
                    rt_h.no_retort, rt_d.no_siklus, rt_d.steam_on_real, rt_d.jam_basket_keluar_real, relo_d.jam_mulai_real,
                    relo_d.jam_selesai_real,
                    pk_d.jam_cl_real, pk_d.jam_packing_real,
                    pksup.jam_packing_real as jam_supply, pksup.material,
                    pre.jamstart, pre.jamfinish,
                    cook.nocooking, cook.nocooker,
                    cut_b.basket_id, cut_b.label,
                    def_d.no_tangki, def_d.fish_box_no, def_d.barcode_no,
                    csd.item_no, csd.description, csd.vessel_no, csd.hatch_no, csd.voyage_no, csd.lot_no
                    
                    from sis_wh_bongkar_produk as wh_h 
                    left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
                    
                    left join sis_retort_loading_basket_detail as relo_d on wh_d.retort_loading_id=relo_d.id
                    left join basket_retort_ids as rel_rt_load on rel_rt_load.sis_retort_loading_basket_detail_id=relo_d.id
                    left join sis_retort_detail as rt_d on rel_rt_load.sis_retort_detail_id=rt_d.id
                    left join sis_retort_header as rt_h on rt_d.retort_header_id=rt_h.id
                    left join sis_retort_loading_basket as relo_h on relo_h.id=relo_d.header_id
                    left join sis_tb_packing_bt as tbp on tbp.pk_id=relo_h.packing_id
                    left join sis_packing_detail as pk_d on tbp.pkd_id=pk_d.id
                    left join rel_packing_detail_sup as relsup on relsup.sis_packing_detail_id=pk_d.id
                    left join sis_packing_supply_basket as supbas on supbas.id=relsup.sis_packing_supply_basket_id
                    left join sis_packing_supply as pksup on supbas.rel_supply=pksup.id
                    left join rel_supply_pre as presup on presup.sis_packing_supply_id=pksup.id
                    left join sis_pre_cleaning as pre on pre.id=presup.sis_pre_cleaning_id
                    left join sis_cooker_basket as cook_b on cook_b.id=pre.basket
                    left join sis_cooker as cook on cook.id=cook_b.rel_cooker
                    left join sis_cutting_basket as cut_b on cut_b.id=cook_b.rel_basket_cutting
                    left join sis_cutting as cut on cut.id=cut_b.rel_cutting
                    left join sis_cutting_tangki as cut_t on cut_t.rel_cutting=cut.id
                    left join sis_defrost_detail as def_d on cut_t.rel_defrost=def_d.id
                    left join sis_cs_detail as csd on csd.id=def_d.defrost_link_id
                    
                    where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)+" and cut_b.label is not null"
        
        self.env.cr.execute(realsql3)
        result3 =self.env.cr.fetchall()
        
        if result3:
            for dt3 in result3:
                (xproduk, xproductiondate, xjammulaibongkarwh, xbasketre, xpallet, xno_retort, xno_siklus, 
                xsteam_on_retort, xjam_basket_keluar, xjam_mulai_muat_rt, xjam_selesai_muat_rt, xjam_cl, 
                xjam_pack, xjam_supply, xmaterial, xstartpre, sfinishpre, xnocooking, xnocooker, xbasketcut, xlabelcut, xnotangki,
                xfishboxno, xbarcodeno, csditemno, csddescription, csdvessel_no, csdhatch_no, csdvoyage_no, csdlot_no)= dt3
                        
                vals_detail = {
                    'head_id' : self.id,
                    'produk' : xproduk,
                    'productiondate' : xproductiondate,
                    'jam_mulai_bongkar_wh' : xjammulaibongkarwh,
                    'basket_retort' : xbasketre,
                    'pallet' : xpallet,
                    'no_retort' : xno_retort,
                    'no_siklus' : xno_siklus,
                    'steam_on_retort' : xsteam_on_retort,
                    'jam_basket_keluar' : xjam_basket_keluar,
                    'jam_mulai_muat_rt' : xjam_mulai_muat_rt,
                    'jam_selesai_muat_rt' : xjam_selesai_muat_rt,
                    'jam_cl' : xjam_cl,
                    'jam_pack' : xjam_pack, 
                    'jam_supply' : xjam_supply,
                    'material' : xmaterial,
                    'jamstartpre' : xstartpre,
                    'jamfinishpre' : sfinishpre,
                    'nocooking' : xnocooking,
                    'nocooker' : xnocooker,
                    'basket_cutting' : xbasketcut,
                    'label_cutting' : xlabelcut,
                    'no_tangki' : xnotangki,
                    'fish_box_no' : xfishboxno,
                    'barcode_no' : xbarcodeno,
                    'item_no'  : csditemno,
                    'description' : csddescription,
                    'vessel_no' : csdvessel_no,
                    'hatch_no' : csdhatch_no,
                    'voyage_no' : csdvoyage_no,
                    'lot_no' : csdlot_no,
                    'status_ikan' : 'sh-fish'
                    }
                create_detail = self.env['sis.trace.backward.detail']
                create_detail.create(vals_detail)
                
        realsql4="""select wh_h.produk, wh_h.productiondate, wh_d.jam_mulai_real, wh_d.basket_no, wh_d.pallet,
                    rt_h.no_retort, rt_d.no_siklus, rt_d.steam_on_real, rt_d.jam_basket_keluar_real, relo_d.jam_mulai_real,
                    relo_d.jam_selesai_real,
                    pk_d.jam_cl_real, pk_d.jam_packing_real,
                    pksup.jam_packing_real as jam_supply, pksup.material, 
                    unpk.jam_bongkar_real, unpk.no_urut_kereta,
                    cl.tgl_bongkar, cl.kode_produksi, cl.jambongkar_real, cl.start_thawing_real, cl.fish_box_no, 
                    csd.barcode_no, csd.item_no, csd.description, csd.vessel_no, csd.hatch_no, csd.voyage_no, csd.lot_no
                                        
                    from sis_wh_bongkar_produk as wh_h 
                    left join sis_wh_bongkar_produk_detail as wh_d on wh_d.header_id=wh_h.id
                                        
                    left join sis_retort_loading_basket_detail as relo_d on wh_d.retort_loading_id=relo_d.id
                    left join basket_retort_ids as rel_rt_load on rel_rt_load.sis_retort_loading_basket_detail_id=relo_d.id
                    left join sis_retort_detail as rt_d on rel_rt_load.sis_retort_detail_id=rt_d.id
                    left join sis_retort_header as rt_h on rt_d.retort_header_id=rt_h.id
                    left join sis_retort_loading_basket as relo_h on relo_h.id=relo_d.header_id
                    left join sis_tb_packing_bt as tbp on tbp.pk_id=relo_h.packing_id
                    left join sis_packing_detail as pk_d on tbp.pkd_id=pk_d.id
                    left join rel_packing_detail_sup as relsup on relsup.sis_packing_detail_id=pk_d.id
                    left join sis_packing_supply_basket as supbas on supbas.id=relsup.sis_packing_supply_basket_id
                    left join sis_packing_supply as pksup on supbas.rel_supply=pksup.id
                    left join rel_supply_unpack as suppk on suppk.sis_packing_supply_id=pksup.id
                    left join sis_unpacking_defrost_loin as unpk on unpk.id=suppk.sis_unpacking_defrost_loin_id
                    left join sis_cleaning as cl on cl.id=unpk.rel_cleaning_unpack
                    left join sis_cs_detail as csd on csd.id=cl.rel_cs_detail
                    
                    where wh_h.productiondate='"""+self.productiondate+"' and wh_h.produk='"+self.produk+"' and wh_d.jam_mulai_real<="+str(self.jam_mulai_bongkar_real)+" and wh_d.jam_selesai_real>="+str(self.jam_mulai_bongkar_real)+" and unpk.no_urut_kereta is not null"
        
        self.env.cr.execute(realsql4)
        result4 =self.env.cr.fetchall()
        
        if result4:
            for dt4 in result4:
                (xproduk, xproductiondate, xjammulaibongkarwh, xbasketre, xpallet,
                 xno_retort, xno_siklus, xsteam_on_retort, xjam_basket_keluar, xjam_mulai_muat_rt, xjam_selesai_muat_rt, xjam_cl, 
                 xjam_pack, xjam_supply, xmaterial, unpkjambongkar_real, unpkno_urut_kereta, cltanggal_bongkar, clkode_produksi, cljam_bongkar, clstart_thawing, 
                 xfishboxno, xbarcodeno, csditemno, csddescription, csdvessel_no, csdhatch_no, csdvoyage_no, csdlot_no)= dt4
                        
                vals_detail = {
                    'head_id' : self.id,
                    'produk' : xproduk,
                    'productiondate' : xproductiondate,
                    'jam_mulai_bongkar_wh' : xjammulaibongkarwh,
                    'basket_retort' : xbasketre,
                    'pallet' : xpallet,
                    'no_retort' : xno_retort,
                    'no_siklus' : xno_siklus,
                    'steam_on_retort' : xsteam_on_retort,
                    'jam_basket_keluar' : xjam_basket_keluar,
                    'jam_mulai_muat_rt' : xjam_mulai_muat_rt,
                    'jam_selesai_muat_rt' : xjam_selesai_muat_rt,
                    'jam_cl' : xjam_cl,
                    'jam_pack' : xjam_pack,  
                    'jam_supply' : xjam_supply,
                    'material' : xmaterial,
                    'jam_bongkar_unpacking' : unpkjambongkar_real,
                    'no_urut_kereta' : unpkno_urut_kereta,
                    'tgl_bongkar_fz' : cltanggal_bongkar,
                    'kode_produksi_loin' : clkode_produksi,
                    'jam_bongkar_fz' : cljam_bongkar,
                    'start_thawing_fz' : clstart_thawing,
                    'fish_box_no' : xfishboxno,
                    'barcode_no' : xbarcodeno,
                    'item_no'  : csditemno,
                    'description' : csddescription,
                    'vessel_no' : csdvessel_no,
                    'hatch_no' : csdhatch_no,
                    'voyage_no' : csdvoyage_no,
                    'lot_no' : csdlot_no,
                    'status_ikan' : 'sh-loin'
                    }
                create_detail = self.env['sis.trace.backward.detail']
                create_detail.create(vals_detail)
                      
class sis_trace_backward_detail(models.TransientModel):
    _name = 'sis.trace.backward.detail'
    _description = 'Tracing Backward Detail'
    
    head_id = fields.Many2one('sis.trace.backward', string='Header ID')
    
    productiondate = fields.Date('Tanggal Produksi')
    produk = fields.Char('Nama Produk')
    jam_mulai_bongkar_wh = fields.Float('Jam Mulai Bongkar WH')
    basket_retort = fields.Char('Basket Retort')    
    pallet= fields.Char('Pallet WH')
    no_retort = fields.Integer('Nomor Retort')    
    no_siklus = fields.Integer('Siklus Retort')     
    steam_on_retort = fields.Char('Steam On Retort')
    jam_basket_keluar = fields.Char('Jam Basket Keluar')    
    jam_mulai_muat_rt = fields.Char('Jam Mulai Muat Retort')
    jam_selesai_muat_rt = fields.Char('Jam Selesai Muat Retort')    
    jam_cl = fields.Char('Jam Cleaning')
    jam_pack = fields.Char('Jam Packing')    
    jamstartpre = fields.Char('Jam Mulai pre')
    jamfinishpre = fields.Char('Jam Selesai pre')
    nocooking = fields.Integer('No Cooking')
    nocooker = fields.Integer('No Cooker')
    basket_cutting = fields.Char('Basket ID')
    label_cutting = fields.Integer('Basket Label')
    no_tangki = fields.Char('No Tangki')
    fish_box_no = fields.Char('No Fish Box')
    barcode_no = fields.Char('Barcode No')
    item_no = fields.Char(size=20,string="Item No.")
    description= fields.Char(size=100,string="Description")
    vessel_no = fields.Char(size=100,string="Vessel No.")
    hatch_no = fields.Char(size=100,string="Hatch No.")
    voyage_no = fields.Char(size=100,string="Voyage No.")
    lot_no = fields.Char(size=40,string="Lot No")
    jam_bongkar_unpacking = fields.Char('jam Bongkar Unpacking')
    no_urut_kereta = fields.Char('No Urut Kereta')
    tgl_bongkar_fz = fields.Char('Tgl Bongkar FZ')
    kode_produksi_loin = fields.Char('Kode Produksi Loin')
    jam_bongkar_fz = fields.Char('jam Bongkar FZ')
    start_thawing_fz = fields.Char('Start Thawing FZ')
    jam_supply = fields.Char('Jam Supply')
    material = fields.Char('Material')
    status_ikan = fields.Char('Status ikan')
                    

class sis_tb_packing_bt(models.Model):
    _name = 'sis.tb.packing.bt'
    _description = 'Packing Tracing Backward - Between'
    
    pk_id = fields.Integer('Packing ID')
    productiondate = fields.Date('Tanggal Produksi')
    produk = fields.Char('Nama Produk')
    jam_packing = fields.Float('Jam packing')
    pkd_id = fields.Integer('Packing Deatil ID')
    
class sis_trace_can_lot(models.TransientModel):
    _name = 'sis.trace.can.lot'
    _description = 'Trace Can Lot per tanggal produksi supplier'
    
    productiondate_ati = fields.Date('Tanggal Produksi ATI')
    kind_of_product = fields.Many2one('sis.master.product', string='Jenis Product')
    kind_of_pkg = fields.Many2one('sis.items.ec', string = 'Kind of Packaging')
    desc_pkg = fields.Char('Description PKG', compute='_get_desc', store=True)
    
    
    @api.one
    @api.depends('kind_of_pkg')
    def _get_desc(self):
        if self.kind_of_pkg:
            self.desc_pkg = self.kind_of_pkg.deskripsi_barang

class sis_trace_can_lot_detail(models.TransientModel):
    _name = 'sis.trace.can.lot.detail'
    _description = 'Trace Can Lot per tanggal produksi supplier detail'
    
    productiondate_sup = fields.Date('Tanggal Produksi Supplier')
    supplier = fields.Char('Supplier')
    incoming_date = fields.Date('Tanggal kedatangan')
    qty_pemakaian = fields.Integer('Qty Pemakaian')
    qty_reject = fields.Integer('Qty Reject')
    qty_sample = fields.Integer('Qty Sample')   


