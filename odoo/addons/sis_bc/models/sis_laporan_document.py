from odoo import models, fields, api
from odoo.exceptions import UserError
import xlsxwriter
import base64
from asn1crypto._ffi import null

class report_dokumen_bc(models.TransientModel):
    _name       ='sis.report.doc.bc'
    _rec_name   ='rpt_kode'
    _description= 'Form Report of Document BC'
    
    #rel_report_id   = fields.Many2one('sis.report.filter.bc', string="Report ID", required=True)
    rpt_kode        = fields.Char(string='Kode BC', size=255)
    rpt_tanggal1    = fields.Date(string='Tanggal BC Awal')
    rpt_tanggal2    = fields.Date(string='Tanggal BC Akhir')
    rpt_no_bc       = fields.Char(string='No Dokumen BC', size=50)
    rpt_kode_cust   = fields.Char(string='Kode Customer', size=20)
    rpt_nama_cust   = fields.Char(string='Nama Customer', size=100)
    rpt_kode_sup    = fields.Char(string='Kode Supplier', size=20)
    rpt_nama_sup    = fields.Char(string='Nama Supplier', size=100)
    rpt_no_dok      = fields.Char(string='No Dokumen', size=30)
    rpt_jenis_bc_in = fields.Selection(string="Jenis BC", selection=[('BC 2.0', 'BC 2.0'),('BC 2.1', 'BC 2.1'),('BC 2.3', 'BC 2.3'),('BC 2.6.2', 'BC 2.6.2'),('BC 2.7', 'BC 2.7'),('BC 4.0', 'BC 4.0'),('PPBKB', 'PPBKB')])
    rpt_jenis_bc_out= fields.Selection(string="Jenis BC", selection=[('BC 2.5', 'BC 2.5'),('BC 2.6.1', 'BC 2.6.1'),('BC 2.7', 'BC 2.7'),('BC 3.0', 'BC 3.0'),('BC 3.3', 'BC 3.3'),('BC 4.1', 'BC 4.1')])
    rpt_pabrik      = fields.Char(string='Factory', compute='_get_pabrik')
    rpt_init        = fields.Integer('Init Value', Default=0)
    rpt_doc_line    = fields.One2many('sis.report.doc.bc.line', 'rel_doc_line_id', string='Doc. ID')
    rpt_xlsx        = fields.Binary('File data', help='File(xlsx format)')
    hide            = fields.Boolean(string='Hide', compute="_compute_hide")    

    @api.depends('rpt_jenis_bc_in')
    def _compute_hide(self):
        # simple logic, but you can do much more here
        if self.rpt_jenis_bc_in == 'PPBKB':
            self.hide = False
        else:
            self.hide = True

    @api.depends('rpt_init')
    def _get_pabrik(self):
        if self.rpt_init>0:
            xuid = self.env.uid
            cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
             
            for def_lokasi in rc_lokasi:
                    (xpabrik_id,)=def_lokasi
             
            self.rpt_pabrik=xpabrik_id
            #self.get_data_doc_in()
            
    def clear_data_bc(self):
        self.rpt_kode=""
        self.rpt_tanggal1=""
        self.rpt_tanggal2=""
        self.rpt_no_bc=""
        self.rpt_kode_cust=""
        self.rpt_nama_cust=""
        self.rpt_kode_sup=""
        self.rpt_nama_sup=""
        self.rpt_no_dok=""
        self.rpt_jenis_bc_in=""
        self.rpt_jenis_bc_out=""
        self.get_data_doc_bc()

            
    def get_data_doc_bc(self):
        xWhere=""
        #BC27-2/20/02/000016
#         if self.rpt_no_dok:
# #             if self.rpt_init==69:
# #                 self.env.cr.execute("select bc_nomer from sis_bc_uni_line where no_dok='"+self.rpt_no_dok+"' "+\
# #                                     "and bc_jenis in ('BC 2.0','BC 2.1','BC 2.3','BC 2.6.2','BC 2.7','BC 4.0','PPBKB') limit 1")
# #             elif self.rpt_init==96:
# #                 self.env.cr.execute("select bc_nomer from sis_bc_uni_line where no_dok='"+self.rpt_no_dok+"' "+\
# #                                     "and bc_jenis in ('BC 2.5','BC 2.6.1','BC 2.7','BC 3.0','BC 4.1') limit 1")
#             self.env.cr.execute("select bc_nomer from sis_bc_uni_line where no_dok='"+self.rpt_no_dok+"' limit 1")
#             
#             drec=self.env.cr.fetchall()
#             
#             if len(drec)>0:
#                 for dbc in drec:
#                     (xbcnomer,)=dbc
#                 xWhere=" and h.bc_nomer='"+xbcnomer+"'"
            
        if self.rpt_kode:
            xWhere=" and (LOWER(h.kode_pengajuan) like '%"+self.rpt_kode+"%' or h.kode_pengajuan like '%"+self.rpt_kode+"%')"
#            xWhere=" and (LOWER(h.bc_nomer) like '%"+self.rpt_kode+"%' or h.bc_nomer like '%"+self.rpt_kode+"%')"
        if self.rpt_tanggal1 and self.rpt_tanggal2:
#             if xWhere.strip()=="":
#                 xWhere=" and bc_tanggal between '"+self.rpt_tanggal1+"' and '"+self.rpt_tanggal2+"'"
#             else:
            xWhere=xWhere+" and (h.bc_tanggal between '"+self.rpt_tanggal1+"' and '"+self.rpt_tanggal2+"')"
        else:
            if self.rpt_tanggal1:
#                 if xWhere.strip()=="":
#                     xWhere="bc_tanggal='"+self.rpt_tanggal1+"'"
#                 else:
                    xWhere=xWhere+" and h.bc_tanggal='"+self.rpt_tanggal1+"'"
            elif self.rpt_tanggal2:
#                 if xWhere.strip()=="":
#                     xWhere="bc_tanggal='"+self.rpt_tanggal2+"'"
#                 else:
                    xWhere=xWhere+" and h.bc_tanggal='"+self.rpt_tanggal2+"'"

        if self.rpt_no_bc:
#             if xWhere.strip()=="":
#                 xWhere="no_beacukai='"+self.rpt_no_bc+"'"
#             else:
                xWhere=xWhere+" and (LOWER(h.no_beacukai) like '%"+self.rpt_no_bc+"%' or h.no_beacukai like '%"+self.rpt_no_bc+"%')"
        
        if self.rpt_kode_cust:
#             if xWhere.strip()=="":
#                 xWhere="customer_kode='"+self.rpt_kode_cust+"'"
#             else:
                xWhere=xWhere+" and (LOWER(h.customer_kode) like '%"+self.rpt_kode_cust+"%' or h.customer_kode like '%"+self.rpt_kode_cust+"%')"
        
        if self.rpt_nama_cust:
#             if xWhere.strip()=="":
#                 xWhere="customer_nama='"+self.rpt_nama_cust+"'"
#             else:
                xWhere=xWhere+" and (LOWER(h.customer_nama) like '%"+self.rpt_nama_cust+"%' or h.customer_nama like '%"+self.rpt_nama_cust+"%')"
            
        if self.rpt_kode_sup:
#             if xWhere.strip()=="":
#                 xWhere="vendor_kode='"+self.rpt_kode_sup+"'"
#             else:
                xWhere=xWhere+" and (LOWER(h.vendor_kode) like '%"+self.rpt_kode_sup+"%' or h.vendor_kode like '%"+self.rpt_kode_sup+"%')"
        
        if self.rpt_nama_sup:
#             if xWhere.strip()=="":
#                 xWhere="vendor_nama='"+self.rpt_nama_sup+"'"
#             else:
                xWhere=xWhere+" and (LOWER(h.vendor_nama) like '%"+self.rpt_nama_sup+"%' or h.vendor_nama like '%"+self.rpt_nama_sup+"%')"
        
        if self.rpt_no_dok:
#              if xWhere.strip()=="":
#                  xWhere="d.no_dok='"+self.rpt_no_dok+"'"
#              else:
            xWhere=xWhere+" and (LOWER(d.no_dok) like '%"+self.rpt_no_dok+"%' or d.no_dok like '%"+self.rpt_no_dok+"%')"
        
#             if xWhere.strip()=="":
#                 xWhere="bc_jenis='"+self.rpt_jenis_bc_in+"'"
#             else:
            
        
        self.env.cr.execute("delete from sis_report_doc_bc_line where temp_id="+str(self.id))
        if self.rpt_init==69:
            
            if self.rpt_jenis_bc_in:
                xWhere=xWhere+" and h.bc_jenis='"+self.rpt_jenis_bc_in+"'"
                if self.rpt_jenis_bc_in=="BC 2.7":
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.tpb_27_tujuan='"+self.rpt_pabrik+"'"+xWhere+\
                                        " order by h.bc_tanggal desc")
                    print("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.tpb_27_tujuan='"+self.rpt_pabrik+"'"+xWhere+\
                                        " order by h.bc_tanggal desc")
                elif self.rpt_jenis_bc_in=="BC 2.6.2":
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_opt1, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer or d.bc_nomer=h.bc_nomer_asal where h.factory='"+\
                                        self.rpt_pabrik+"'"+xWhere+" order by h.bc_tanggal desc")
                else:
#                    xWhere=xWhere+" and bc_jenis='"+self.rpt_jenis_bc_in+"'"
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer or d.bc_nomer=h.bc_nomer_asal where h.factory='"+\
                                        self.rpt_pabrik+"'"+xWhere+" order by h.bc_tanggal desc")
            else:
#                 self.env.cr.execute("select bc_nomer, bc_tanggal, no_beacukai, tgl_beacukai, customer_nama, vendor_nama, bc_jenis from sis_bc_uni "+\
#                                     "where bc_jenis in ('BC 2.0','BC 2.1','BC 2.3','BC 2.6.2','BC 2.7','BC 4.0','PPBKB') and factory='"+\
#                                     self.rpt_pabrik+"'"+xWhere+" order by bc_tanggal desc")
                if xWhere.strip()!="":
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer or d.bc_nomer=h.bc_nomer_asal where h.factory='"+\
                                        self.rpt_pabrik+"' and h.bc_jenis in ('BC 2.0','BC 2.1','BC 2.3','BC 2.6.2','BC 4.0','PPBKB') "+\
                                        xWhere+" order by h.bc_tanggal desc")
                else:
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer or d.bc_nomer=h.bc_nomer_asal "+\
                                        "where (h.bc_jenis in ('BC 2.0','BC 2.1','BC 2.3','BC 2.6.2','BC 4.0','PPBKB') and "+\
                                        "h.factory='"+self.rpt_pabrik+"') or (h.bc_jenis='BC 2.7' and h.tpb_27_tujuan='"+self.rpt_pabrik+"') "+\
                                        "order by h.bc_tanggal desc")

#                 print(xWhere)
        elif self.rpt_init==96:
            if self.rpt_jenis_bc_out:
                xWhere=xWhere+" and h.bc_jenis='"+self.rpt_jenis_bc_out+"'"
                if self.rpt_jenis_bc_out=="BC 2.7":
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.tpb_27_asal='"+self.rpt_pabrik+"'"+xWhere+\
                                        " order by h.bc_tanggal desc")
                else:
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.factory='"+self.rpt_pabrik+"'"+xWhere+" order by h.bc_tanggal desc")
#                     print("select h.bc_nomer, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
#                                         "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
#                                         "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.factory='"+self.rpt_pabrik+"'"+xWhere+" order by h.bc_tanggal desc")
            else:
#                 self.env.cr.execute("select bc_nomer, bc_tanggal, no_beacukai, tgl_beacukai, customer_nama, vendor_nama, bc_jenis from sis_bc_uni "+\
#                                     "where bc_jenis in ('BC 2.5','BC 2.6.1','BC 2.7','BC 3.0','BC 4.1') and factory='"+\
#                                     self.rpt_pabrik+"'"+xWhere+" order by bc_tanggal desc")
                if xWhere.strip()!="":
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer where h.factory='"+self.rpt_pabrik+"' "+\
                                        "and h.bc_jenis in ('BC 2.5','BC 2.6.1','BC 2.7','BC 3.0','BC 3.3','BC 4.1') "+\
                                        xWhere+" order by h.bc_tanggal desc")
                else:
                    self.env.cr.execute("select h.bc_nomer, h.kode_pengajuan, h.bc_tanggal, h.no_beacukai, h.tgl_beacukai, d.no_dok, d.tgl_dok, h.customer_nama, h.vendor_nama, "+\
                                        "d.kode_barang, d.description, d.jumlah, d.satuan, d.nilai_barang, h.bc_jenis from sis_bc_uni h "+\
                                        "inner join sis_bc_uni_line d on d.bc_nomer=h.bc_nomer "+\
                                        "where (h.bc_jenis in ('BC 2.5','BC 2.6.1','BC 3.0','BC 3.3','BC 4.1') and "+\
                                        "h.factory='"+self.rpt_pabrik+"') or (h.bc_jenis='BC 2.7' and h.tpb_27_asal='"+self.rpt_pabrik+"') "+\
                                        "order by h.bc_tanggal desc")

        rec_in=self.env.cr.fetchall()
        xNomer=0
        if len(rec_in)>0:
            new_lines = self.env['sis.report.doc.bc.line']
            for ibc in rec_in:
                (xbc_nomer, xno_pengajuan, xbc_tanggal, xno_beacukai, xtgl_beacukai, xno_dok, xtgl_dok, xcust_nama, xsup_nama, xitem_no, xdescription, xqty, xuom, xnil_barang, xbc_jenis)=ibc
                xNomer=xNomer+1
#                 xnobc=''
#                 xtglbc=''

                if xno_beacukai=='':
                    xtgl_beacukai=''
                
#                 if xbc_jenis!='PPBKB':
#                     xnobc=xno_beacukai
#                     xtglbc=xtgl_beacukai
                
                vals={
                    'line_no'           :xNomer,
                    'rpt_kode'          :xbc_nomer,
                    'rpt_nopengajuan'   :xno_pengajuan,
                    'rpt_tgl_bc'        :xbc_tanggal,
#                     'rpt_no_bc'         :xno_beacukai,
#                     'rpt_tgl_no_bc'     :xtgl_beacukai,
                    'rpt_no_bc'         :xno_beacukai,
                    'rpt_tgl_no_bc'     :xtgl_beacukai,
                    'rpt_no_dok'        :xno_dok,
                    'rpt_tgl_dok'       :xtgl_dok,
                    'rpt_nama_cust'     :xcust_nama,
                    'rpt_penerima'      :xcust_nama,
                    'rpt_nama_sup'      :xsup_nama,
                    'rpt_pengirim'      :xsup_nama,
                    'rpt_item_no'       :xitem_no,
                    'rpt_description'   :xdescription,
                    'rpt_jumlah'        :xqty,
                    'rpt_satuan'        :xuom,
                    'rpt_nilai_barang'  :xnil_barang,
                    'rpt_jenis_bc'      :xbc_jenis,
                    'temp_id'           :self.id,
                    'hide'              :self.hide
                }
                new_lines += new_lines.new(vals)

            self.rpt_doc_line=new_lines
            
    @api.multi    
    def write_xlsx(self):
        xFactory, xLokasi=self._get_pabrik_id()
        xtgl=""

        if self.rpt_tanggal1:
            xtgl=self.rpt_tanggal1.replace('-','')

        if self.rpt_tanggal2:
            if xtgl=="":
                xtgl=self.rpt_tanggal2.replace('-','')
            else:
                xtgl += "-"+self.rpt_tanggal2.replace('-','')

        if xtgl=="":
            if self.rpt_init==69:
                xLaporan="ATI"+xLokasi+"-Laporan_Pemasukan_Barang_per_Dokumen_"+str(self.id)+".xlsx"
            elif self.rpt_init==96:
                xLaporan="ATI"+xLokasi+"-Laporan_Pengeluaran_Barang_per_Dokumen_"+str(self.id)+".xlsx"
        else:
            if self.rpt_init==69:
                xLaporan="ATI"+xLokasi+"-Laporan_Pemasukan_Barang_per_Dokumen_"+xtgl+"_"+str(self.id)+".xlsx"
            elif self.rpt_init==96:
                xLaporan="ATI"+xLokasi+"-Laporan_Pengeluaran_Barang_per_Dokumen_"+xtgl+"_"+str(self.id)+".xlsx"
            
#         print(self.rpt_laporan.replace(' ','_')+"_"+str(self.id)+".xlsx")
#         print(xLokasi)
        workbook = xlsxwriter.Workbook('/tmp/'+xLaporan)        
#         workbook = xlsxwriter.Workbook('/home/rusdi/Documents/shared/ati_laporan_mutasi.xlsx')        
        worksheet = workbook.add_worksheet()
        
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#BDBDDF'}) #AFAFD8
        merge_header_format = workbook.add_format({'bold': 1,'border': 1,'align': 'center','valign': 'vcenter','fg_color': '#BDBDDF'}) 
        title_format = workbook.add_format()
        title_format.set_font_size(16)
        title_format.set_bold()
        title_format2 = workbook.add_format()
        title_format2.set_font_size(16)
        title_format2.set_bold()
        title_format2.set_align('right')
        title_format3 = workbook.add_format()
        title_format3.set_font_size(16)
        title_format3.set_bold()
        date_format2 = workbook.add_format()
        date_format2.set_bold() 
        date_format2.set_align('right')
        date_format3 = workbook.add_format()
        date_format3.set_bold() 
        pabrik_format = workbook.add_format()
        pabrik_format.set_bold()
        pabrik_format.set_align('right')
        row_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        row_center_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        row_right_format = workbook.add_format({'border': 1, 'align': 'right', 'valign': 'vcenter'})
        cell_format = workbook.add_format()
        cell_format.set_border(2)
        cell_format.set_border_color('red')
        
        worksheet.insert_image('A1', '/home/logo-aja.png')
        if xLokasi=="1":
            worksheet.write(0,2,"PT Aneka Tuna Indonesia - Gempol Factory", bold)
            worksheet.write(1,2,"Jl. Raya Surabaya-Malang Km. 38 Gempol Pasuruan", bold)
        else:
            worksheet.write(0,2,"PT Aneka Tuna Indonesia - Pandaan Factory", bold)
            worksheet.write(1,2,"Jl. Gunung Gangsir RT 07/09, Nogosari, Pandaan Pasuruan", bold)

        if self.rpt_init==69:
            worksheet.write(0,8,"Laporan Pemasukan Barang per Dokumen", title_format2)
        elif self.rpt_init==96:
            worksheet.write(0,8,"Laporan Pengeluaran Barang per Dokumen", title_format2)
            
        if self.rpt_tanggal1 and self.rpt_tanggal2:
            worksheet.write(1,8,"Tanggal : "+self.rpt_tanggal1+" s/d "+self.rpt_tanggal2, date_format2)
        elif self.rpt_tanggal1:
            worksheet.write(1,8,"Tanggal : "+self.rpt_tanggal1, date_format2)
        else:
            worksheet.write(1,8,"Tanggal : -", date_format2)
            
        worksheet.merge_range('A5:B5', '', merge_header_format)
        worksheet.merge_range('C5:D5', 'Pengajuan', merge_header_format)
        worksheet.merge_range('E5:F5', 'Pendaftaran', merge_header_format)
        if self.rpt_init==69:
            worksheet.merge_range('G5:H5', 'Bukti Pemasukan', merge_header_format)
        elif self.rpt_init==96:
            worksheet.merge_range('G5:H5', 'Bukti Pengeluaran', merge_header_format)
        worksheet.merge_range('I5:N5', '', merge_header_format)
        
        worksheet.write(5,0,"No.", header_format)
        worksheet.write(5,1,"Jenis", header_format)
        worksheet.write(5,2,"Nomor", header_format)
        worksheet.write(5,3,"Tanggal", header_format)
#        worksheet.write(4,4,"No. Pendaftaran", header_format)
        worksheet.write(5,4,"Nomor", header_format)
#         worksheet.write(4,5,"Tgl. Pendaftaran", header_format)
        worksheet.write(5,5,"Tanggal", header_format)
        worksheet.write(5,6,"Nomor", header_format)
        worksheet.write(5,7,"Tanggal", header_format)
        if self.rpt_init==69:
            worksheet.write(5,8,"Pengirim", header_format)
        elif self.rpt_init==96:
            worksheet.write(5,8,"Penerima", header_format)
        worksheet.write(5,9,"Kode Barang", header_format)
        worksheet.write(5,10,"Nama Barang", header_format)
        worksheet.write(5,11,"Jumlah", header_format)
        worksheet.write(5,12,"Satuan", header_format)
        worksheet.write(5,13,"Nilai Barang", header_format)


        worksheet.set_column(0, 1, 6)
        worksheet.set_column(1, 1, 15)
        worksheet.set_column(2, 2, 30)
        worksheet.set_column(3, 7, 20)
        worksheet.set_column(8, 8, 30)
        worksheet.set_column(9, 9, 20)
        worksheet.set_column(10, 10, 40)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 10)
        worksheet.set_column(13, 13, 15)
        
#         for osheet in (workbook.worksheets()):
#             osheet.set_column('A', 12)
#             osheet.set_column('B', 12)
#             osheet.set_column('C', 12)
#             osheet.set_column('D', 12)
#             osheet.set_column('E', 12)
#             osheet.set_column('F', 12)
#             osheet.set_column('G', 12)
#             osheet.set_column('H', 12)
#             osheet.set_column('I', 12)
#             osheet.set_column('J', 12)
#             osheet.set_column('K', 12)
#             osheet.set_column('L', 12)

#         print("SELECT line_no, rpt_jenis_bc, rpt_nopengajuan, rpt_tgl_bc, rpt_no_bc, rpt_tgl_no_bc, rpt_no_dok, rpt_tgl_dok, "+\
#                             "rpt_nama_sup, rpt_nama_cust, rpt_item_no, rpt_description, rpt_jumlah, rpt_satuan, rpt_nilai_barang "
#                             "from sis_report_doc_bc_line where temp_id="+str(self.id)+" order by line_no")
#         
        self.env.cr.execute("SELECT line_no, rpt_jenis_bc, rpt_nopengajuan, rpt_tgl_bc, rpt_no_bc, rpt_tgl_no_bc, rpt_no_dok, rpt_tgl_dok, "+\
                            "rpt_nama_sup, rpt_nama_cust, rpt_item_no, rpt_description, rpt_jumlah, rpt_satuan, rpt_nilai_barang "
                            "from sis_report_doc_bc_line where temp_id="+str(self.id)+" order by line_no")
        rpt=self.env.cr.fetchall()

        xNomer=5
        if len(rpt)>0:
            for irpt in rpt:
                (xline_no, xjenis_bc, xno_pengajuan, xtgl_pengajuan, xno_daftar, xtgl_daftar, xno_bukti, xtgl_bukti, xnama_sup, xnama_cust, xitem_no, xdescription, xjumlah, xsatuan, xnilai_barang)=irpt
                xNomer=xNomer+1

                worksheet.write(xNomer,0,str(xline_no)+". ", row_right_format)
                worksheet.write(xNomer,1,xjenis_bc, row_center_format)
                worksheet.write(xNomer,2,xno_pengajuan, row_format)
                worksheet.write(xNomer,3,xtgl_pengajuan, row_center_format)
                worksheet.write(xNomer,4,xno_daftar, row_center_format)
                worksheet.write(xNomer,5,xtgl_daftar, row_center_format)
                worksheet.write(xNomer,6,xno_bukti, row_center_format)
                worksheet.write(xNomer,7,xtgl_bukti, row_center_format)
                if self.rpt_init==69:
                    worksheet.write(xNomer,8,xnama_sup, row_format)
                elif self.rpt_init==96:
                    worksheet.write(xNomer,8,xnama_cust, row_format)
                worksheet.write(xNomer,9,xitem_no, row_center_format)
                worksheet.write(xNomer,10,xdescription, row_format)
                worksheet.write(xNomer,11,xjumlah, row_format)
                worksheet.write(xNomer,12,xsatuan, row_center_format)
                worksheet.write(xNomer,13,xnilai_barang, row_format)

            worksheet.autofilter('A6:N6')
            
        workbook.close()

        rec=self.env['sis.report.doc.bc'].search([('id','=',self.id)])
        for r in rec:
            vals={ 
                    'rpt_xlsx':base64.b64encode(open("/tmp/"+xLaporan, "rb").read())
#                   'rpt_xlsx':base64.b64encode(open("/home/rusdi/Documents/shared/ati_laporan_mutasi.xlsx", "rb").read())
                }
            r.write(vals)

#         print('/web/content/sis.report.inv.bc/%s/rpt_xlsx/'+xLaporan+'?download=true')
        return {
            'type': 'ir.actions.act_url',
            'name': 'Report',
            'url': '/web/content/sis.report.doc.bc/%s/rpt_xlsx/%s?download=true' % (str(self.id), xLaporan)
#             'url': '/web/content/sis.report.inv.bc/%s/rpt_xlsx/ati_laporan_mutasi.xlsx?download=true' %(self.id),
        }

            
    def _get_pabrik_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
      
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
              
        for def_lokasi in rc_lokasi:
            (xpabrik_id,)=def_lokasi
         
        if xpabrik_id=="ATI1":
            xLokasi='1'
            xFactory='2'
        elif xpabrik_id=="ATI2":
            xLokasi='2'
            xFactory='1'
              
        return xFactory,xLokasi
            
            
class report_dokumen_bc_line(models.TransientModel):
    _name       ='sis.report.doc.bc.line'
#   _rec_name   ='rpt_laporan_doc_line'
    _description= 'Form Detail Report of Document BC'
    _order      = 'rpt_nopengajuan desc'
    
    #rel_report_id   = fields.Many2one('sis.report.filter.bc', string="Report ID", required=True)
    rel_doc_line_id = fields.Many2one('sis.report.doc.bc', string="Doc. ID")
    line_no         = fields.Integer(string="No.")
    rpt_kode        = fields.Char(string='Kode BC', size=25)
    rpt_nopengajuan = fields.Char(string='No Pengajuan', size=255)
    rpt_tgl_bc      = fields.Char(string='Tanggal BC', size=10)
    rpt_no_bc       = fields.Char(string='No Dokumen BC', size=50)
    rpt_tgl_no_bc   = fields.Char(string='Tgl Dokumen BC', size=10)
    rpt_no_dok      = fields.Char(string='No Pendaftaran', size=20)
    rpt_tgl_dok     = fields.Date('Tgl Pendaftaran')
    rpt_nama_cust   = fields.Char(string='Nama Customer', size=100)
    rpt_nama_sup    = fields.Char(string='Nama Supplier', size=100)
    rpt_item_no     = fields.Char(string='Kode Barang', size=20)
    rpt_description = fields.Char(string='Nama Barang', size=200)
    rpt_jumlah      = fields.Float(string='Jumlah')
    rpt_satuan      = fields.Char(string='Satuan', size=30)
    rpt_nilai_barang= fields.Float(string='Nilai Barang')
    rpt_jenis_bc    = fields.Char(string='Jenis BC', size=15)
    temp_id         = fields.Float(string="Temp ID")
    hide            = fields.Boolean(string='Hide')    

    def viewdata(self):
        #print(self.rpt_kode)
        self.env.cr.execute("delete from sis_bc_doc_view where temp_id="+str(self.rel_doc_line_id.id))
        self.env.cr.execute("delete from sis_bc_doc_view_line where temp_id="+str(self.rel_doc_line_id.id))
        
        if self.rpt_jenis_bc=='BC 2.0':
            return {
                'name'      : 'Laporan BC 2.0',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_20_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                        'domain'    : [('bc_nomer','=',self.rpt_kode),('bc_jenis','=',self.rpt_jenis_bc),('temp_id','=',self.rel_doc_line_id.id)]      
#                'flags'     : {'action_buttons': True}
            }
        
        if self.rpt_jenis_bc=='BC 2.1':
            return {
                'name'      : 'Laporan BC 2.1',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_21_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }
            
        if self.rpt_jenis_bc=='BC 2.3':
            return {
                'name'      : 'Laporan BC 2.3',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_23_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 2.5':
            return {
                'name'      : 'Laporan BC 2.5',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_25_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 2.6.1':
            return {
                'name'      : 'Laporan BC 2.6.1',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_261_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 2.6.2':
            return {
                'name'      : 'Laporan BC 2.6.2',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_262_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }
            
        if self.rpt_jenis_bc=='BC 2.7':
            return {
                'name'      : 'Laporan BC 2.7',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_27_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }
            
        if self.rpt_jenis_bc=='BC 3.0':
            return {
                'name'      : 'Laporan BC 3.0',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_30_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 3.3':
            return {
                'name'      : 'Laporan BC 3.3',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_33_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 4.0':
            return {
                'name'      : 'Laporan BC 4.0',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_40_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='BC 4.1':
            return {
                'name'      : 'Laporan BC 4.1',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_bc_41_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }

        if self.rpt_jenis_bc=='PPBKB':
            return {
                'name'      : 'Laporan PPBKB',
                'res_model' : 'sis.bc.doc.view',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_laporan_ppbkb_form').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_kode_pengajuan':self.rpt_nopengajuan, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
#                 'context'   : {'default_bc_nomer':self.rpt_kode, 'default_bc_jenis':self.rpt_jenis_bc, 'default_temp_id':self.temp_id}
            }
