from odoo import models, fields, api
from odoo.exceptions import UserError
import xlsxwriter

class bc_view_doc(models.TransientModel):
    _name  ='sis.bc.doc.view'
    _description = 'View Data per Document BC'
#    _order = 'bc_nomer'

    bc_nomer                    = fields.Char(string='Nomer BC', size=25)
    kode_pengajuan              = fields.Char(string='No Pengajuan', size=255)
#    bc_tanggal                  = fields.Date(string='Tanggal BC')
    bc_tanggal                  = fields.Char(string='Tanggal BC', size=10)
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
    tgl_beacukai                = fields.Char(string='Tgl Dokumen BC',size=10)
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
#    invoice_tgl                 = fields.Date(string='Tgl. Invoice')
    invoice_tgl                 = fields.Char(string='Tgl Invoice', size=10)
    packing_list_no             = fields.Char(string='No Packing List', size=40)
    packing_list_tgl            = fields.Date(string='Tgl Packing List')
    skep_no                     = fields.Char(string='No SKEP', size=50)
    skep_tgl                    = fields.Char(string='Tgl SKEP', size=10)
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
    jumlah_kemasan              = fields.Integer(string='Jumlah Kemasan')
    ndpdm                       = fields.Float(string='NDPDM')
    nilai_cif                   = fields.Float(string='Nilai CIF')
    harga_penyerahan            = fields.Float('Harga Penyerahan')
    kondisi_barang              = fields.Char(string='Kondisi Barang', size=10)
    ntptn_no                    = fields.Char(string='No NTPTN', size=30)
    ntptn_tgl                   = fields.Date(string='Tgl NTPTN')
    tgl_pengeluaran             = fields.Char(string='Tgl Pengeluaran', size=10)
    tgl_selesai_masuk           = fields.Char(string='Tgl Selesai Masuk', size=10)
    npe_no                      = fields.Char(string='No NPE', size=20)
    jumlah_kemasan_40           = fields.Float('Jml Kemasan')
    factory                     = fields.Char(string='Lokasi', size=10, compute="_get_pabrik")
    tpb_asal_npwp               = fields.Char(string='NPWP TPB Asal', size=30)
    tpb_asal_tgl_ijin           = fields.Date(string='Tgl Ijin TPB Asal')
    tpb_asal_api                = fields.Char(string='API TPB Asal', size=15)
    no_bukti_penerima_jaminan   = fields.Char(string='No Bukti Penerima Jaminan', size=50)
    tgl_bukti_penerima_jaminan  = fields.Char(string='Tgl Bukti Penerima Jaminan', size=10)
    no_barang_garansi           = fields.Char(string='No Barang Garansi', size=15)
    tgl_barang_garansi          = fields.Char(string='Tgl Barang Garansi', size=10)
    valuta                      = fields.Char(string='Valuta', size=20)
    negara_asal_barang          = fields.Char(string='Negara Asal Barang', size=100)
    bc_nomer_asal               = fields.Char(string='Nomer BC Asal', size=25)
    bc_tanggal_asal             = fields.Date(string='Tanggal BC Asal')
    bc_jenis                    = fields.Char(string='Jenis BC', size=15)
    temp_id                     = fields.Float(string="Temp ID")
    view_doc_line               = fields.One2many('sis.bc.doc.view.line', 'rel_doc_line_id', string='Doc. ID')
    
    @api.depends('kode_pengajuan','bc_jenis','temp_id')
#     @api.depends('bc_nomer','bc_jenis','temp_id')
#    @api.depends('temp_id')
    def _get_pabrik(self):
#         if self.bc_nomer and self.bc_jenis and self.temp_id:
        if self.kode_pengajuan and self.bc_jenis and self.temp_id:
            xuid = self.env.uid
            cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.factory=xpabrik_id
            self._get_data(self.kode_pengajuan,self.bc_jenis)
#             self._get_data(self.bc_nomer,self.bc_jenis)
    
    def _get_data(self, par_kode, par_jenis):
#         self.env.cr.execute("select bc_tanggal, vendor_kode, vendor_nama, vendor_alamat, vendor_npwp, customer_kode, "+\
#                             "customer_nama, tempat_asal, tempat_tujuan, tujuan_pengiriman, no_beacukai, tgl_beacukai, kantor_asal, "+\
#                             "kantor_tujuan, tpb_asal_nama, tpb_asal_alamat, tpb_asal_no_ijin, tpb_asal_no, tpb_tujuan_nama, "+\
#                             "tpb_tujuan_alamat, tpb_tujuan_no_ijin, jenis_barang, cara_pengangkut, invoice_no, invoice_tgl, "+\
#                             "packing_list_no, packing_list_tgl, skep_no, skep_tgl, bl_no, bl_tgl, no_pengajuan, tempat_muat, "+\
#                             "berat_kotor, berat_bersih, nilai_pabean, nilai_pabean_usd, eta_sub, eta_ati, bm, ppn, pph, total, "+\
#                             "pelabuhan_muat, pelabuhan_bongkar, no_container, jumlah_container, nama_angkut, lokasi, "+\
#                             "sarana_pengangkut, satuan, no_contract, nama_kapal, fcl, merk_kemasan, jenis_kemasan, jumlah_kemasan, "+\
#                             "ndpdm, nilai_cif, harga_penyerahan, kondisi_barang, ntptn_no, ntptn_tgl, tgl_pengeluaran, "+\
#                             "tgl_selesai_masuk, npe_no, jumlah_kemasan_40, factory, tpb_asal_npwp, tpb_asal_tgl_ijin, tpb_asal_api, "+\
#                             "no_bukti_penerima_jaminan, tgl_bukti_penerima_jaminan, no_barang_garansi, tgl_barang_garansi, valuta, "+\
#                             "negara_asal_barang, bc_nomer_asal, bc_tanggal_asal, kode_pengajuan from sis_bc_uni where bc_nomer='"+par_kode+\
#                             "' and bc_jenis='"+par_jenis+"'")
        self.env.cr.execute("select bc_tanggal, vendor_kode, vendor_nama, vendor_alamat, vendor_npwp, customer_kode, "+\
                            "customer_nama, tempat_asal, tempat_tujuan, tujuan_pengiriman, no_beacukai, tgl_beacukai, kantor_asal, "+\
                            "kantor_tujuan, tpb_asal_nama, tpb_asal_alamat, tpb_asal_no_ijin, tpb_asal_no, tpb_tujuan_nama, "+\
                            "tpb_tujuan_alamat, tpb_tujuan_no_ijin, jenis_barang, cara_pengangkut, invoice_no, invoice_tgl, "+\
                            "packing_list_no, packing_list_tgl, skep_no, skep_tgl, bl_no, bl_tgl, no_pengajuan, tempat_muat, "+\
                            "berat_kotor, berat_bersih, nilai_pabean, nilai_pabean_usd, eta_sub, eta_ati, bm, ppn, pph, total, "+\
                            "pelabuhan_muat, pelabuhan_bongkar, no_container, jumlah_container, nama_angkut, lokasi, "+\
                            "sarana_pengangkut, satuan, no_contract, nama_kapal, fcl, merk_kemasan, jenis_kemasan, jumlah_kemasan, "+\
                            "ndpdm, nilai_cif, harga_penyerahan, kondisi_barang, ntptn_no, ntptn_tgl, tgl_pengeluaran, "+\
                            "tgl_selesai_masuk, npe_no, jumlah_kemasan_40, factory, tpb_asal_npwp, tpb_asal_tgl_ijin, tpb_asal_api, "+\
                            "no_bukti_penerima_jaminan, tgl_bukti_penerima_jaminan, no_barang_garansi, tgl_barang_garansi, valuta, "+\
                            "negara_asal_barang, bc_nomer_asal, bc_tanggal_asal, bc_nomer from sis_bc_uni where kode_pengajuan='"+par_kode+\
                            "' and bc_jenis='"+par_jenis+"'")

        vrec=self.env.cr.fetchall()
        if len(vrec)>0:
            for data in vrec:
                (xbc_tanggal, xvendor_kode, xvendor_nama, xvendor_alamat, xvendor_npwp, xcustomer_kode, xcustomer_nama, 
                xtempat_asal, xtempat_tujuan, xtujuan_pengiriman, xno_beacukai, xtgl_beacukai, xkantor_asal, xkantor_tujuan, 
                xtpb_asal_nama, xtpb_asal_alamat, xtpb_asal_no_ijin, xtpb_asal_no, xtpb_tujuan_nama, xtpb_tujuan_alamat, 
                xtpb_tujuan_no_ijin, xjenis_barang, xcara_pengangkut, xinvoice_no, xinvoice_tgl, xpacking_list_no, xpacking_list_tgl, 
                xskep_no, xskep_tgl, xbl_no, xbl_tgl, xno_pengajuan, xtempat_muat, xberat_kotor, xberat_bersih, xnilai_pabean, 
                xnilai_pabean_usd, xeta_sub, xeta_ati, xbm, xppn, xpph, xtotal, xpelabuhan_muat, xpelabuhan_bongkar, xno_container, 
                xjumlah_container, xnama_angkut, xlokasi, xsarana_pengangkut, xsatuan, xno_contract, xnama_kapal, xfcl, xmerk_kemasan, 
                xjenis_kemasan, xjumlah_kemasan, xndpdm, xnilai_cif, xharga_penyerahan, xkondisi_barang, xntptn_no, xntptn_tgl, 
                xtgl_pengeluaran, xtgl_selesai_masuk, xnpe_no, xjumlah_kemasan_40, xfactory, xtpb_asal_npwp, xtpb_asal_tgl_ijin, 
                xtpb_asal_api, xno_bukti_penerima_jaminan, xtgl_bukti_penerima_jaminan, xno_barang_garansi, xtgl_barang_garansi, 
                xvaluta, xnegara_asal_barang, xbc_nomer2, xbc_tanggal2, xbc_nomer)=data
            
            self.bc_tanggal                 = xbc_tanggal
            self.bc_nomer                   = xbc_nomer
            self.vendor_kode                = xvendor_kode 
            self.vendor_nama                = xvendor_nama 
            self.vendor_alamat              = xvendor_alamat 
            self.vendor_npwp                = xvendor_npwp 
            self.customer_kode              = xcustomer_kode 
            self.customer_nama              = xcustomer_nama 
            self.tempat_asal                = xtempat_asal 
            self.tempat_tujuan              = xtempat_tujuan 
            self.tujuan_pengiriman          = xtujuan_pengiriman 
            self.no_beacukai                = xno_beacukai 
            self.tgl_beacukai               = xtgl_beacukai 
            self.kantor_asal                = xkantor_asal 
            self.kantor_tujuan              = xkantor_tujuan 
            self.tpb_asal_nama              = xtpb_asal_nama 
            self.tpb_asal_alamat            = xtpb_asal_alamat 
            self.tpb_asal_no_ijin           = xtpb_asal_no_ijin 
            self.tpb_asal_no                = xtpb_asal_no 
            self.tpb_tujuan_nama            = xtpb_tujuan_nama 
            self.tpb_tujuan_alamat          = xtpb_tujuan_alamat 
            self.tpb_tujuan_no_ijin         = xtpb_tujuan_no_ijin 
            self.jenis_barang               = xjenis_barang 
            self.cara_pengangkut            = xcara_pengangkut 
            self.invoice_no                 = xinvoice_no 
            self.invoice_tgl                = xinvoice_tgl 
            self.packing_list_no            = xpacking_list_no 
            self.packing_list_tgl           = xpacking_list_tgl 
            self.skep_no                    = xskep_no 
            self.skep_tgl                   = xskep_tgl 
            self.bl_no                      = xbl_no 
            self.bl_tgl                     = xbl_tgl 
            self.no_pengajuan               = xno_pengajuan 
            self.tempat_muat                = xtempat_muat 
            self.berat_kotor                = xberat_kotor 
            self.berat_bersih               = xberat_bersih 
            self.nilai_pabean               = xnilai_pabean 
            self.nilai_pabean_usd           = xnilai_pabean_usd 
            self.eta_sub                    = xeta_sub 
            self.eta_ati                    = xeta_ati 
            self.bm                         = xbm 
            self.ppn                        = xppn 
            self.pph                        = xpph 
            self.total                      = xtotal 
            self.pelabuhan_muat             = xpelabuhan_muat 
            self.pelabuhan_bongkar          = xpelabuhan_bongkar 
            self.no_container               = xno_container 
            self.jumlah_container           = xjumlah_container 
            self.nama_angkut                = xnama_angkut 
            self.lokasi                     = xlokasi 
            self.sarana_pengangkut          = xsarana_pengangkut 
            self.satuan                     = xsatuan 
            self.no_contract                = xno_contract 
            self.nama_kapal                 = xnama_kapal 
            self.fcl                        = xfcl 
            self.merk_kemasan               = xmerk_kemasan 
            self.jenis_kemasan              = xjenis_kemasan 
            self.jumlah_kemasan             = xjumlah_kemasan 
            self.ndpdm                      = xndpdm 
            self.nilai_cif                  = xnilai_cif 
            self.harga_penyerahan           = xharga_penyerahan 
            self.kondisi_barang             = xkondisi_barang 
            self.ntptn_no                   = xntptn_no 
            self.ntptn_tgl                  = xntptn_tgl 
            self.tgl_pengeluaran            = xtgl_pengeluaran 
            self.tgl_selesai_masuk          = xtgl_selesai_masuk 
            self.npe_no                     = xnpe_no 
            self.jumlah_kemasan_40          = xjumlah_kemasan_40 
            self.factory                    = xfactory 
            self.tpb_asal_npwp              = xtpb_asal_npwp 
            self.tpb_asal_tgl_ijin          = xtpb_asal_tgl_ijin 
            self.tpb_asal_api               = xtpb_asal_api 
            self.no_bukti_penerima_jaminan  = xno_bukti_penerima_jaminan 
            self.tgl_bukti_penerima_jaminan = xtgl_bukti_penerima_jaminan 
            self.no_barang_garansi          = xno_barang_garansi 
            self.tgl_barang_garansi         = xtgl_barang_garansi 
            self.valuta                     = xvaluta 
            self.negara_asal_barang         = xnegara_asal_barang
            self.bc_nomer_asal              = xbc_nomer2
            self.bc_tanggal_asal            = xbc_tanggal2 
        
            if self.bc_jenis=="BC 2.6.2":
#                 self.env.cr.execute("select bc_nomer, no_dok, kode_barang, description, penerima, pengirim, negara_tujuan, jumlah, "+\
#                                     "satuan, berat_bersih, berat_kotor, harga_fob, harga_cnf, mata_uang, nilai_cif, nilai_barang, "+\
#                                     "eta_ati, keterangan, segel, bc_jenis from sis_bc_uni_line where bc_nomer='"+self.bc_nomer_asal+"'")
                self.env.cr.execute("select bc_nomer, no_dok, kode_barang, description, penerima, pengirim, negara_tujuan, jumlah, "+\
                                    "satuan, berat_bersih, berat_kotor, harga_fob, harga_cnf, mata_uang, nilai_cif, nilai_barang, "+\
                                    "eta_ati, keterangan, segel, bc_jenis from sis_bc_uni_line where bc_nomer='"+self.bc_nomer_asal+"'")
            else:
                self.env.cr.execute("select bc_nomer, no_dok, kode_barang, description, penerima, pengirim, negara_tujuan, jumlah, "+\
                                    "satuan, berat_bersih, berat_kotor, harga_fob, harga_cnf, mata_uang, nilai_cif, nilai_barang, "+\
                                    "eta_ati, keterangan, segel, bc_jenis from sis_bc_uni_line where bc_nomer='"+self.bc_nomer+"'")
            
            vrec_line=self.env.cr.fetchall()
            if len(vrec_line)>0:
                baris_baru = self.env['sis.bc.doc.view.line']
                for data_line in vrec_line:
                    (xbc_nomer_d, xno_dok, xkode_barang, xdescription, xpenerima, xpengirim, xnegara_tujuan, xjumlah, xsatuan, 
                     xberat_bersih, xberat_kotor, xharga_fob, xharga_cnf, xmata_uang, xnilai_cif, xnilai_barang, xeta_ati, 
                     xketerangan, xsegel, xbc_jenis)=data_line
                     
                    vals_detail = {
                        'bc_nomer'      : xbc_nomer_d, 
                        'no_dok'        : xno_dok, 
                        'kode_barang'   : xkode_barang, 
                        'description'   : xdescription, 
                        'penerima'      : xpenerima,
                        'pengirim'      : xpengirim,
                        'negara_tujuan' : xnegara_tujuan,
                        'jumlah'        : xjumlah,
                        'satuan'        : xsatuan,
                        'berat_bersih'  : xberat_bersih,
                        'berat_kotor'   : xberat_kotor,
                        'harga_fob'     : xharga_fob,
                        'harga_cnf'     : xharga_cnf,
                        'mata_uang'     : xmata_uang,
                        'nilai_cif'     : xnilai_cif,
                        'nilai_barang'  : xnilai_barang,
                        'eta_ati'       : xeta_ati,
                        'keterangan'    : xketerangan,
                        'segel'         : xsegel,
                        'bc_jenis'      : xbc_jenis,
                        'temp_id'       : self.temp_id
                        }
                    
                    baris_baru += baris_baru.new(vals_detail)
                self.view_doc_line=baris_baru

    def kembali(self):
        return {'type': 'ir.actions.client', 'tag': 'history_back'}
                    
    
class bc_view_doc_line(models.TransientModel):
    _name  ='sis.bc.doc.view.line'
    _description = 'View Data Line per Document BC'

    rel_doc_line_id = fields.Many2one('sis.bc.doc.view', string="Doc. ID")
    bc_nomer        = fields.Char(string='Nomer BC', size=25)
    no_dok          = fields.Char(string='No Dokumen', size=30)
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
    bc_jenis        = fields.Char(string='Jenis BC', size=30)
    temp_id         = fields.Float(string="Temp ID")

