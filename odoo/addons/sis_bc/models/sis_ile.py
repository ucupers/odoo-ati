from odoo import models, fields, api
from odoo.exceptions import UserError
import pyodbc

SQLCONN='Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+\
                              'Server=10.0.0.12;'+\
                              'Database=NAV (9-0) ATI LIVE;'+\
                              'UID=Atidev;pwd=Ati1234;'

# class ile_nav(models.Model):
#     _name  ='sis.ile.bc'
#     _table = 'sis_ile_bc'
#     _description = 'ILE NAV for BC'
#     _auto = False
# #    _order = 'posting_date desc'
#     item_no             = fields.Char(string="Item No", size=20)
#     variant_code        = fields.Char(string="Variant Code", size=20)
#     item_category_code  = fields.Char(string="Item Category Code", size=20)
#     description         = fields.Char(string="Description", size=100)
#     description_2       = fields.Char(string="Description_2", size=100)
#     status_wip_bc       = fields.Integer(string="WIP BC")
#     location_code       = fields.Char(string="Location Code", size=20)
#     product_group_code  = fields.Char(string="Product Group Code", size=20)
#     buku_kuning         = fields.Integer(string="Buku Kuning")
#     item_not_include_bc = fields.Integer(string="Not Include BC")
#     entry_types         = fields.Integer(string="Entry Types")
#     base_uom            = fields.Char(string="Base UOM", size=10)
#     variant_uom         = fields.Char(string="Variant UOM", size=10)
#     quantity            = fields.Float(string="Quantity")
#     posting_date        = fields.Date(string="Posting Date")
#     current_datetime    = fields.Datetime(string="Current DateTime")
#.Char(string="Current DateTime", size=30)

class items_bc(models.Model):
    _name  ='sis.items.bc'
    _description = 'Master Items NAV for BC'
    _order = 'item_no'
    
    item_no_            = fields.Char(string="Item No_", size=20)
    item_no             = fields.Char(string="Item No", size=20)
    variant_code        = fields.Char(string="Variant Code", size=20)
    description         = fields.Char(string="Description", size=200)
    description_2       = fields.Char(string="Description_2", size=200)
    description_3       = fields.Char(string="Description_2", size=255)
    item_category_code  = fields.Char(string="Item Category Code", size=20)
    product_group_code  = fields.Char(string="Product Group Code", size=20)
    status_wip_bc       = fields.Integer(string="WIP BC")
    buku_kuning         = fields.Integer(string="Buku Kuning")
    exclude_bc          = fields.Integer(string="Not Include BC")

# class items_category_bc(models.Model):
#     _name  ='sis.items.category.bc'
#     _description = 'Master Items Category Code NAV for BC'
#     _order = 'description'
#     
#     description         = fields.Char(string="Description", size=20)
# 
# class items_product_group_bc(models.Model):
#     _name  ='sis.product.group.bc'
#     _description = 'Master Product Group Code NAV for BC'
#     _order = 'description'
#     
#     description         = fields.Char(string="Description", size=20)

class bc_uni(models.Model):
    _name  ='sis.bc.uni'
    _description = 'BC Universal Odoo for BC'
    _order = 'bc_nomer'

    bc_nomer                    = fields.Char(string='Nomer BC', size=25)
    bc_tanggal                  = fields.Date(string='Tanggal BC')
    vendor_kode                 = fields.Char(string='Kode Supplier', size=20)
    vendor_nama                 = fields.Char(string='Nama Supplier', size=100)
    vendor_alamat               = fields.Char(string='Alamat Supplier', size=255)
    vendor_npwp                 = fields.Char(string='NPWP supplier', size=25)
    customer_kode               = fields.Char(string='Kode Customer', size=20)
    customer_nama               = fields.Char(string='Nama Customer', size=100)
    tempat_asal                 = fields.Char(string='Tempat Asal', size=20)
    tempat_tujuan               = fields.Char(string='Tempat Tujuan', size=20)
    tujuan_pengiriman           = fields.Char(string='Tujuan Pengiriman', size=15)
    no_beacukai                 = fields.Char(string='No Dokumen BC', size=50)
    tgl_beacukai                = fields.Date(string='Tgl Dokumen BC')
    kantor_asal                 = fields.Char(string='Kantor Asal', size=30)
    kantor_tujuan               = fields.Char(string='Kantor Tujuan', size=20)
    tpb_asal_nama               = fields.Char(string='Nama TPB Asal', size=50)
    tpb_asal_alamat             = fields.Char(string='Alamat TPB Asal', size=100)
    tpb_asal_no_ijin            = fields.Char(string='No Ijin TPB Asal', size=75)
    tpb_asal_no                 = fields.Char(string='No TPB Asal', size=30)
    tpb_tujuan_nama             = fields.Char(string='Nama TPB Tujuan', size=50)
    tpb_tujuan_alamat           = fields.Char(string='Alamat TPB Tujuan', size=100)
    tpb_tujuan_no_ijin          = fields.Char(string='No Ijin TPB Tujuan', size=75)
    jenis_barang                = fields.Char(string='Jenis Barang', size=75)
    cara_pengangkut             = fields.Char(string='Cara Pengangkut', size=10)
    invoice_no                  = fields.Char(string='No Invoice', size=40)
    invoice_tgl                 = fields.Date(string='Tgl. Invoice')
    packing_list_no             = fields.Char(string='No Packing List', size=40)
    packing_list_tgl            = fields.Date(string='Tgl Packing List')
    skep_no                     = fields.Char(string='No SKEP', size=50)
    skep_tgl                    = fields.Date(string='Tgl SKEP')
    bl_no                       = fields.Char(string='No BL', size=20)
    bl_tgl                      = fields.Date(string='Tgl BL')
    no_pengajuan                = fields.Char(string='No Pengajuan', size=20)
    tempat_muat                 = fields.Char(string='Tempat Muat', size=50)
    berat_kotor                 = fields.Float(string='Berat Kotor')
    berat_bersih                = fields.Float(string='Berat Bersih')
    nilai_pabean                = fields.Float(string='Nilai Pabean')
    nilai_pabean_usd            = fields.Float(string='Nilai Pabean (USD)')
    eta_sub                     = fields.Char(string='ETA Sub', size=20)
    eta_ati                     = fields.Char(string='ETA ATI', size=30)
    bm                          = fields.Float(string='BM')
    ppn                         = fields.Float(string='PPN')
    pph                         = fields.Float(string='PPH')
    total                       = fields.Float(string='Total')
    pelabuhan_muat              = fields.Char(string='Pelabuhan Muat', size=50)
    pelabuhan_bongkar           = fields.Char(string='Pelabuhan Bongkar', size=50)
    no_container                = fields.Char(string='No Container', size=20)
    jumlah_container            = fields.Integer(string='Jumlah Container')
    nama_angkut                 = fields.Char(string='Nama Angkut', size=50)
    lokasi                      = fields.Integer(string='Factory')
    sarana_pengangkut           = fields.Char(string='Sarana Pengangkut', size=30)
    satuan                      = fields.Char(string='Satuan', size=10)
    no_contract                 = fields.Char(string='No Contract', size=10)
    nama_kapal                  = fields.Char(string='Nama Kapal', size=50)
    fcl                         = fields.Char(string='FCL', size=30)
    merk_kemasan                = fields.Char(string='Merk Kemasan', size=30)
    jenis_kemasan               = fields.Char(string='Jenis Kemasan', size=75)
    jumlah_kemasan              = fields.Float(string='Jumlah Kemasan')
    ndpdm                       = fields.Float(string='NDPDM')
    nilai_cif                   = fields.Float(string='Nilai CIF')
    harga_penyerahan            = fields.Float('Harga Penyerahan')
    kondisi_barang              = fields.Char(string='Kondisi Barang', size=10)
    ntptn_no                    = fields.Char(string='No NTPTN', size=30)
    ntptn_tgl                   = fields.Date(string='Tgl NTPTN')
    tgl_pengeluaran             = fields.Date(string='Tgl Pengeluaran')
    tgl_selesai_masuk           = fields.Date(string='Tgl Selesai Masuk')
    npe_no                      = fields.Char(string='No NPE', size=20)
    jumlah_kemasan_40           = fields.Float('Jml Kemasan')
    factory                     = fields.Char(string='Lokasi', size=10)
    tpb_asal_npwp               = fields.Char(string='NPWP TPB Asal', size=30)
    tpb_asal_tgl_ijin           = fields.Date(string='Tgl Ijin TPB Asal')
    tpb_asal_api                = fields.Char(string='API TPB Asal', size=15)
    no_bukti_penerima_jaminan   = fields.Char(string='No Bukti Penerima Jaminan', size=50)
    tgl_bukti_penerima_jaminan  = fields.Date(string='Tgl Bukti Penerima Jaminan')
    no_barang_garansi           = fields.Char(string='No Barang Garansi', size=15)
    tgl_barang_garansi          = fields.Date(string='Tgl Barang Garansi')
    valuta                      = fields.Char(string='Valuta', size=20)
    negara_asal_barang          = fields.Char(string='Negara Asal Barang', size=100)
    bc_nomer_asal               = fields.Char(string='Nomer BC Asal', size=25)
    bc_tanggal_asal             = fields.Date(string='Tanggal BC Asal')
    tpb_27_asal                 = fields.Char(string='TPB_27 Asal', size=10)
    tpb_27_tujuan               = fields.Char(string='TPB_27 Tujuan', size=10)
    bc_jenis                    = fields.Char(string='Jenis BC', size=15)
    kode_pengajuan              = fields.Char(string='Kode Pengajuan', size=255)

class bc_uni_line(models.Model):
    _name  ='sis.bc.uni.line'
    _description = 'BC Universal Line Odoo for BC'
    _order = 'bc_nomer'

    bc_nomer        = fields.Char(string='Nomer BC', size=25)
    no_dok          = fields.Char(string='No Dokumen', size=75)
    tgl_dok         = fields.Date(string='Tgl Dokumen')
    kode_barang     = fields.Char(string='Kode Barang', size=50)
    description     = fields.Char(string='Nama Barang', size=100)
    penerima        = fields.Char(string='Penerima', size=50)
    pengirim        = fields.Char(string='Pengirim', size=50)
    negara_tujuan   = fields.Char(string='Negara Tujuan', size=30)
    jumlah          = fields.Float(string='Jumlah')
    satuan          = fields.Char(string='Satuan', size=30)
    berat_bersih    = fields.Float(string='Berat Bersih')
    berat_kotor     = fields.Float(string='Berat Kotor')
    harga_fob       = fields.Float(string='Harga FOB')
    harga_cnf       = fields.Float(string='Harga CNF')
    mata_uang       = fields.Char(string='Mata Uang', size=10)
    nilai_cif       = fields.Float(string='Nilai CIF')
    nilai_barang    = fields.Float(string='Nilai Barang')
    eta_ati         = fields.Char(string='ETA ATI')
    keterangan      = fields.Char(string='Keterangan', size=100)
    segel           = fields.Char(string='Segel', size=10)
    tgl_opt1        = fields.Date(string='Tgl Opt1')
    bc_jenis        = fields.Char(string='Jenis BC', size=30)
    
class ile_bk_odoo(models.Model):
    _name  ='sis.ile.odoo.bk'
    _description = 'ILE Buku Kuning Odoo for BC'
    _order = 'current_datetime desc'
    
    item_no             = fields.Char(string="Item No", size=20)
    description         = fields.Char(string="Description", size=255)
    location_code       = fields.Char(string="Location Code", size=20)
    entry_types         = fields.Integer(string="Entry Types")
    base_uom            = fields.Char(string="Base UOM", size=10)
    quantity            = fields.Float(string="Quantity")
    posting_date        = fields.Date(string="Posting Date")
    current_datetime    = fields.Datetime(string="Current DateTime")

class ile_odoo(models.Model):
    _name  ='sis.ile.odoo.bc'
    _description = 'ILE Odoo for BC'
    _order = 'current_datetime desc'
    
    entry_no            = fields.Float(string="Entry No")
    item_no             = fields.Char(string="Item No", size=20)
    variant_code        = fields.Char(string="Variant Code", size=20)
    item_category_code  = fields.Char(string="Item Category Code", size=20)
    description         = fields.Char(string="Description", size=100)
    description_2       = fields.Char(string="Description_2", size=100)
    status_wip_bc       = fields.Integer(string="WIP BC")
    location_code       = fields.Char(string="Location Code", size=20)
    product_group_code  = fields.Char(string="Product Group Code", size=20)
    buku_kuning         = fields.Integer(string="Buku Kuning")
    item_not_include_bc = fields.Integer(string="Not Include BC")
    entry_types         = fields.Integer(string="Entry Types")
    base_uom            = fields.Char(string="Base UOM", size=10)
    variant_uom         = fields.Char(string="Variant UOM", size=10)
    quantity            = fields.Float(string="Quantity")
    bisnis_group        = fields.Char(string="Bisnis Group", size=5)
    posting_date        = fields.Date(string="Posting Date")
    current_datetime    = fields.Datetime(string="Current DateTime")
 
    def update_ile_nav_odoo(self):
        self.env.cr.execute("delete from sis_ile_odoo_bk")
        self.env.cr.execute("delete from sis_items_bc")
#         self.env.cr.execute("delete from sis_items_category_bc")
#         self.env.cr.execute("delete from sis_product_group_bc")
        self.env.cr.execute("delete from sis_bc_uni")
        self.env.cr.execute("delete from sis_bc_uni_line")

        self.env.cr.execute("insert into sis_items_bc(item_no_, variant_code, description, description_2, description_3, "+\
                            "item_category_code, product_group_code, status_wip_bc, buku_kuning, exclude_bc) select "+\
                            "(case when variant_code='' or variant_code is null then item_no else CONCAT(item_no, ' ', variant_code) "+\
                            "end) as item_no_, variant_code, description, description2, description3, itc, pgc, status_wip_bc, buku_kuning, exclude_bc "+\
                            "from sis_nav_items_bc")

        self.env.cr.execute("insert into sis_ile_odoo_bk(item_no, description, location_code, entry_types, base_uom, quantity, "+\
                            "posting_date, current_datetime) select item_no, description, location_code, entry_types, base_uom, "+\
                            "quantity, posting_date, current_datetime from sis_ile_bk")

#         self.env.cr.execute("insert into sis_items_category_bc(description) select distinct item_category_code from sis_items_bc "+\
#                             "where item_category_code<>''")
#         self.env.cr.execute("insert into sis_product_group_bc(description) select distinct product_group_code from sis_items_bc "+\
#                             "where product_group_code<>''")

        self.env.cr.execute("insert into sis_bc_uni(bc_nomer, bc_tanggal, vendor_kode, vendor_nama, vendor_alamat, vendor_npwp, customer_kode, "+\
                            "customer_nama, tempat_asal, tempat_tujuan, tujuan_pengiriman, no_beacukai, tgl_beacukai, kantor_asal, kantor_tujuan, "+\
                            "tpb_asal_nama, tpb_asal_alamat, tpb_asal_no_ijin, tpb_asal_no, tpb_tujuan_nama, tpb_tujuan_alamat, tpb_tujuan_no_ijin, "+\
                            "jenis_barang, cara_pengangkut, invoice_no, invoice_tgl, packing_list_no, packing_list_tgl, skep_no, skep_tgl, bl_no, "+\
                            "bl_tgl, no_pengajuan, tempat_muat, berat_kotor, berat_bersih, nilai_pabean, nilai_pabean_usd, eta_sub, eta_ati, bm, "+\
                            "ppn, pph, total, pelabuhan_muat, pelabuhan_bongkar, no_container, jumlah_container, nama_angkut, lokasi, "+\
                            "sarana_pengangkut, satuan, no_contract, nama_kapal, fcl, merk_kemasan, jenis_kemasan, jumlah_kemasan, ndpdm, "+\
                            "nilai_cif, harga_penyerahan, kondisi_barang, ntptn_no, ntptn_tgl, tgl_pengeluaran, tgl_selesai_masuk, npe_no, "+\
                            "jumlah_kemasan_40, factory, tpb_asal_npwp, tpb_asal_tgl_ijin, tpb_asal_api, no_bukti_penerima_jaminan, "+\
                            "tgl_bukti_penerima_jaminan, no_barang_garansi, tgl_barang_garansi, valuta, negara_asal_barang, "+\
                            "bc_nomer_asal, bc_tanggal_asal, tpb_27_asal, tpb_27_tujuan, bc_jenis, kode_pengajuan) "+\
                            "select bc_nomer, bc_tanggal, vendor_kode, vendor_nama, vendor_alamat, vendor_npwp, customer_kode, customer_nama, "+\
                            "tempat_asal, tempat_tujuan, tujuan_pengiriman, no_beacukai, tgl_beacukai, kantor_asal, kantor_tujuan, tpb_asal_nama, "+\
                            "tpb_asal_alamat, tpb_asal_no_ijin, tpb_asal_no, tpb_tujuan_nama, tpb_tujuan_alamat, tpb_tujuan_no_ijin, jenis_barang, "+\
                            "cara_pengangkut, invoice_no, invoice_tgl, packing_list_no, packing_list_tgl, skep_no, skep_tgl, bl_no, bl_tgl, "+\
                            "no_pengajuan, tempat_muat, berat_kotor, berat_bersih, nilai_pabean, nilai_pabean_usd, eta_sub, eta_ati, bm, ppn, pph, "+\
                            "total, pelabuhan_muat, pelabuhan_bongkar, no_container, jumlah_container, nama_angkut, lokasi, sarana_pengangkut, "+\
                            "satuan, no_contract, nama_kapal, fcl, merk_kemasan, jenis_kemasan, jumlah_kemasan, ndpdm, nilai_cif, harga_penyerahan, "+\
                            "kondisi_barang, ntptn_no, ntptn_tgl, tgl_pengeluaran, tgl_selesai_masuk, npe_no, jumlah_kemasan_40, factory, "+
                            "tpb_asal_npwp, tpb_asal_tgl_ijin, tpb_asal_api, no_bukti_penerima_jaminan, tgl_bukti_penerima_jaminan, "+\
                            "no_barang_garansi, tgl_barang_garansi, valuta, negara_asal_barang, bc_nomer_asal, bc_tanggal_asal, "+\
                            "tpb_27_asal, tpb_27_tujuan, bc_jenis, kode_pengajuan from sis_nav_bc_uni")

        self.env.cr.execute("insert into sis_bc_uni_line(bc_nomer, no_dok, tgl_dok, kode_barang, description, penerima, pengirim, "+\
                            "negara_tujuan, jumlah, satuan, berat_bersih, berat_kotor, harga_fob, harga_cnf, mata_uang, nilai_cif, "+\
                            "nilai_barang, eta_ati, keterangan, segel, tgl_opt1, bc_jenis) select bc_nomer, no_dok, tanggal_dok, kode_barang, "+\
                            "description, penerima, pengirim, negara_tujuan, jumlah, satuan, berat_bersih, berat_kotor, harga_fob, "+\
                            "harga_cnf, mata_uang, nilai_cif, nilai_barang, substring(eta_ati,1,10), keterangan, segel, tanggal_opt1, bc_jenis "+\
                            "from sis_nav_bc_uni_line")
        
#         self.env.cr.execute("insert into sis_ile_odoo_bc(entry_no,item_no,variant_code,item_category_code,description, description_2, status_wip_bc, "+\
#                             "location_code, product_group_code, buku_kuning, item_not_include_bc, entry_types, base_uom, variant_uom, quantity, "+\
#                             "bisnis_group, posting_date,current_datetime) select id,item_no,variant_code, item_category_code, description, "+\
#                             "description_2, status_wip_bc, location_code, product_group_code, buku_kuning, item_not_include_bc, entry_types, "+\
#                             "base_uom, variant_uom, quantity, bisnis_group, posting_date, current_datetime from sis_ile_bc")
        
#         self.env.cr.execute("select entry_no, current_datetime from sis_ile_odoo_bc order by entry_no, current_datetime desc limit 1")
#         self.env.cr.execute("select entry_no, current_datetime from sis_ile_odoo_bc where entry_no=(select max(entry_no) from sis_ile_odoo_bc)")
#         rec=self.env.cr.fetchall()
#         if len(rec)!=0:
#             for current_date in rec:
#                     (xentry_no,xcurrent_date,)=current_date
#          
#             conn = pyodbc.connect(SQLCONN)
#             cursor = conn.cursor()
#        
#             row=cursor.execute("UPDATE sis_ile_cdt set current_date_time='"+xcurrent_date+"', entry_no="+str(xentry_no))
#             if row.rowcount==0:
#                 raise UserError('Failed to update ILE NAV (2), please try again later')
#             else:
#                 conn.commit()
                            
        

        
        