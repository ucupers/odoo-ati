from odoo import models, fields, api
from datetime import datetime, date
from odoo.exceptions import UserError

import re
import base64
from odoo.models import TransientModel

# from odoo.exceptions import ValidationError

class sis_spec_prod(models.Model):
    _inherit = ['mail.thread']
    _name='sis.spec.prod'
    _rec_name='item_desc2'
        
    tgl_buat = fields.Datetime(string="Tanggal Create", default=fields.Datetime.now, track_visibility="onchange")
    temp_id=fields.Char(string="temp_id", compute='_get_temp_id', store=True)
    no_doc=fields.Char(size=30,string='Doc No', track_visibility="onchange",required=True)
    no_rev=fields.Integer(string='Rev No', default=0)
    tgl_efektif=fields.Date(string='Tanggal Efektif', track_visibility="onchange",required=True)
    tgl_mulai=fields.Char(size=255, string='Tanggal Mulai', track_visibility="onchange",required=True)
    creator_name=fields.Char(size=30,string='Disiapkan Oleh', track_visibility="onchange")
    item_no=fields.Char(size=50,string='Item No')
    item_desc=fields.Html(string='Kode Produk',default='-',required=True, track_visibility="onchange")
    item_desc2=fields.Text(string='Kode Produk', compute='_kode_produk', store=True)
    buyer_produk=fields.Html(string='Kode Produk Buyer',default='-',required=True, track_visibility="onchange")
    buyer_no=fields.Char(size=10,string='Kode Buyer')
    buyer_name=fields.Html(string='Nama Buyer',default='-',required=True, track_visibility="onchange")
    buyer_brand=fields.Html(string='Brand',default='-',required=True, track_visibility="onchange")
    nama_produk=fields.Html(string='Nama Produk',default='-',required=True, track_visibility="onchange")
    can_size=fields.Html(string='Ukuran Kaleng',default='-',required=True, track_visibility="onchange")
    lid=fields.Html(string='Tutup Kaleng',default='-',required=True, track_visibility="onchange")
    jenis_ikan=fields.Html(string='Jenis Ikan',default='-',track_visibility="onchange")
    ukuran_ikan=fields.Html(string='Ukuran Ikan',default='-',required=True, track_visibility="onchange")
    netto=fields.Html(string='Berat Netto',default='-',required=True, track_visibility="onchange")
    hampa_udara=fields.Html(string='Hampa Udara',default='-',required=True, track_visibility="onchange")
    sisa_udara=fields.Html(string='Sisa Udara',default='-',required=True, track_visibility="onchange")
    komposisi=fields.Html(string='Komposisi',default='-',required=True, track_visibility="onchange")
    formulasi=fields.Html(string='Formulasi',default='-',required=True, track_visibility="onchange")
    jenis_minyak=fields.Html(default='-',required=True,string='Jenis Minyak', track_visibility="onchange")
    bumbu=fields.Html(string='Bumbu',default='-',required=True, track_visibility="onchange")
    rasio_air=fields.Html(string='Rasio Air : Likuid',default='-',required=True, track_visibility="onchange")
    berat_tekan=fields.Html(string='Berat Tekan',default='-',required=True, track_visibility="onchange")
    berat_tuntas=fields.Html(string='Berat Tuntas',default='-',required=True, track_visibility="onchange")
    tingkat_bersih=fields.Html(string='Tingkat Pembersihan',default='-',required=True, track_visibility="onchange")
    serpihan=fields.Html(string='Serpihan',default='-',required=True, track_visibility="onchange")
    ukuran_serpihan=fields.Html(string='Ukuran Serpihan',default='-',required=True, track_visibility="onchange")
    jenis_packing=fields.Html(string='Jenis Packing',default='-',required=True, track_visibility="onchange")
    kebersihan_produk=fields.Html(string='Kebersihan Produk',default='-',required=True, track_visibility="onchange")
    ph_produk_air=fields.Html(string='PH Produk Akhir',default='-',required=True, track_visibility="onchange")
    kadar_garam=fields.Html(string='Kadar Garam',default='-',required=True, track_visibility="onchange")
    histamin=fields.Html(string='Histamin',default='-',required=True, track_visibility="onchange")
    analisa_proximat=fields.Html(string='Analisa Proximat',default='-',required=True, track_visibility="onchange")
    proses_produksi=fields.Html(string='Proses Produksi',default='-',required=True, track_visibility="onchange")
    sterilisasi=fields.Html(string='Sterilisasi', default='-',track_visibility="onchange")
    pendinginan=fields.Html(string='Pendinginan',default='-',required=True, track_visibility="onchange")
    kode_kaleng=fields.Html(string='Kode Kaleng',default='-',required=True, track_visibility="onchange")
    kadaluarsa=fields.Html(string='Kadaluarsa',default=0,required=True, track_visibility="onchange")
    etiket=fields.Html(string='Etiket',default='-',required=True, track_visibility="onchange")
    kaleng_dus=fields.Html(string='Kaleng/Dus',default=0,required=True, track_visibility="onchange")
    keterangan=fields.Html(string='Keterangan',default='-',required=True, track_visibility="onchange")
    status_spec = fields.Boolean(string="Status") 
    spec_state = fields.Selection([('draft','Draft'),('confirm','Confirmed'),('obselete','Obselete')], string='State', default='draft', track_visibility="onchange")
    user_checker = fields.Boolean(string="Checker", compute="_checker")
    user_unchecker = fields.Boolean(string="Unchecker", compute="_unchecker")
    spec_line_id = fields.One2many('sis.spec.prod.line', 'spec_line_id', string='Spec Lines')
    signature_id = fields.Integer(string="Signature ID", default=0, track_visibility="onchange")

    ttd_jabatan1= fields.Char(size=50,string='Jabatan1')
    ttd_jabatan2= fields.Char(size=50,string='Jabatan2')
    ttd_jabatan3= fields.Char(size=50,string='Jabatan3')
    ttd_nama1   = fields.Char(size=50,string='Nama1')
    ttd_nama2   = fields.Char(size=50,string='Nama2')
    ttd_nama3   = fields.Char(size=50,string='Nama3')
    file_apendix= fields.Binary('File data')

    @api.one
    @api.depends('item_desc')
    def _kode_produk(self):
        if self.item_desc:
            TAG_RE = re.compile('<.*?>')
            self.item_desc2=TAG_RE.sub('', self.item_desc)
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        self.env.cr.execute("select ttd_jabatan1,ttd_jabatan2,ttd_jabatan3,ttd_nama1,ttd_nama2,ttd_nama3 from sis_spec_signature where id="+str(vals['signature_id']))
        r_sign=self.env.cr.fetchall()
        if len(r_sign)!=0:
            for spec_sign in r_sign:
                (xttd_jabatan1,xttd_jabatan2,xttd_jabatan3,xttd_nama1,xttd_nama2,xttd_nama3)=spec_sign        
                vals.update({'ttd_jabatan1':xttd_jabatan1, 'ttd_jabatan2':xttd_jabatan2, 'ttd_jabatan3':xttd_jabatan3, 'ttd_nama1':xttd_nama1, 'ttd_nama2':xttd_nama2, 'ttd_nama3':xttd_nama3}) 

        return models.Model.create(self, vals)   

    @api.depends('tgl_buat')
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
            for spec_checker in rc_check:
                    (xchecker,)=spec_checker
                    
            self.user_checker=xchecker

    @api.depends('tgl_buat')
    def _unchecker(self):
        xuid = self.env.uid
        cSQL1="select d.unchecker from hr_employee as a, res_users as b, res_partner as c, hr_employee as d "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id and d.name=c.name " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_uncheck=self.env.cr.fetchall()
        if len(rc_uncheck)==0:
            self.user_unchecker=False
        else:
            for spec_unchecker in rc_uncheck:
                    (xunchecker,)=spec_unchecker
                    
            self.user_unchecker=xunchecker
    
#     @api.depends('item_no')
#     def _get_bom(self):
#         if self.item_no:
#             self.env.cr.execute("select description, lineitem, linedesc, lineitc, linepgc, lineuom from sis_production_bom where linerouting='UNLABEL' and itemno='"+self.item_no+"' order by itemno")
#             rc_bom=self.env.cr.fetchall()
#             if len(rc_bom)>0:
#                 for bom_data in rc_bom:
#                     (xdesc, xlineitem, xlinedesc, xlineitc, xlinepgc, xlineuom)=bom_data
#                     self.item_desc=xdesc
#                     if xlineitc=='PKG' and xlinepgc=='CAN' and xlineitem[2:3]=='B':
#                         print('kaleng')
#                         
#                         print(xlinedesc)
#                         self.can_size=xlinedesc+" ("+xlineitem+")"
#                     if xlineitc=='PKG' and xlinepgc=='CAN' and xlineitem[2:3]=='E':
#                         print('lid')
#                         self.lid=xlinedesc+" ("+xlineitem+")"

#     def print_spec(self):
#         return {
#             'type'          :'ir.actions.report',
#             'report_name'   :'sis_spec_product.sis_spec_report',
#             'model'         :'sis.spec.prod',
#             'report_type'   :"qweb-pdf",
#         }         
# 

    @api.multi
    def action_confirm(self):
        for me_id in self :
            if me_id.spec_state == 'draft':
#                 result = re.sub("<.*?>", "", self.kode_kaleng)
#                 print(result)
                self.env.cr.execute("update sis_spec_prod set spec_state='obselete' where spec_state='confirm' and no_doc like '"+self.no_doc[:6]+"%' and no_rev!="+str(self.no_rev))
                me_id.write({'spec_state':'confirm'})
     
    @api.multi
    def action_draft(self):
        for me_id in self :
            if me_id.spec_state == 'obselete':
#                 result = re.sub("<.*?>", "", self.kode_kaleng)
#                 print(result)
                me_id.write({'spec_state':'draft'})

    @api.multi
    def action_unconfirm(self):
        for me_id in self :
            if me_id.spec_state == 'confirm':
                me_id.write({'spec_state':'draft'})
#                self.env.cr.execute("update sis_cs_header set cs_state='draft' where cs_id='"+str(me_id.cs_id)+"'")
    
    @api.depends('tgl_buat')
    def _get_temp_id(self):
#         print(str(datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.',''))
        self.temp_id=str(datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')

#         if self.item_desc:
        xuid = self.env.uid
        cSQL1="select c.name from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
 
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_user=self.env.cr.fetchall()
         
        for def_user in rc_user:
            (xname,)=def_user
        
        self.creator_name=xname

    def copy_spec(self):
#         xno_rev=0
        xtanggal=datetime.now()
        xtemp_id=str(datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        
#         self.env.cr.execute("update sis_spec_prod set spec_state='draft' where no_doc='"+self.no_doc+"'")
        self.env.cr.execute("select max(no_rev) from sis_spec_prod where item_no='"+self.item_no+"'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xno_rev,)=spec_line
        
        vals={'tgl_buat'            : xtanggal,
              'temp_id'             : xtemp_id,
              'no_doc'              : self.no_doc,
              'no_rev'              : xno_rev+1,
              'tgl_efektif'         : xtanggal,
              'tgl_mulai'           : self.tgl_mulai,
              'creator_name'        : self.creator_name,
              'item_no'             : self.item_no,
              'item_desc'           : self.item_desc,
              'buyer_produk'        : self.buyer_produk,
              'buyer_no'            : self.buyer_no,
              'buyer_name'          : self.buyer_name,
              'buyer_brand'         : self.buyer_brand,
              'nama_produk'         : self.nama_produk,
              'can_size'            : self.can_size,
              'lid'                 : self.lid,
              'jenis_ikan'          : self.jenis_ikan,
              'ukuran_ikan'         : self.ukuran_ikan,
              'netto'               : self.netto,
              'hampa_udara'         : self.hampa_udara,
              'sisa_udara'          : self.sisa_udara,
              'komposisi'           : self.komposisi,
              'formulasi'           : self.formulasi,
              'jenis_minyak'        : self.jenis_minyak,
              'bumbu'               : self.bumbu,
              'rasio_air'           : self.rasio_air,
              'berat_tekan'         : self.berat_tekan,
              'berat_tuntas'        : self.berat_tuntas,
              'tingkat_bersih'      : self.tingkat_bersih,
              'serpihan'            : self.serpihan,
              'ukuran_serpihan'     : self.ukuran_serpihan,
              'jenis_packing'       : self.jenis_packing,
              'kebersihan_produk'   : self.kebersihan_produk,
              'ph_produk_air'       : self.ph_produk_air,
              'kadar_garam'         : self.kadar_garam,
              'histamin'            : self.histamin,
              'analisa_proximat'    : self.analisa_proximat,
              'proses_produksi'     : self.proses_produksi,
              'sterilisasi'         : self.sterilisasi,
              'pendinginan'         : self.pendinginan,
              'kode_kaleng'         : self.kode_kaleng,
              'kadaluarsa'          : self.kadaluarsa,
              'etiket'              : self.etiket,
              'kaleng_dus'          : self.kaleng_dus,
              'keterangan'          : self.keterangan,
              'signature_id'        : self.signature_id,
              'spec_state'          : "draft"
            }
        self.env['sis.spec.prod'].create(vals)

        self.env.cr.execute("select id from sis_spec_prod where item_no='"+self.item_no+"' and no_rev="+str(xno_rev+1)+" and no_doc='"+self.no_doc+"'")
        rc=self.env.cr.fetchall()
         
        for def_id in rc:
            (xid,)=def_id
        
        self.env.cr.execute("select b.no_item, b.no_rev, b.tgl_efektif, b.alasan from sis_spec_prod a inner join sis_spec_prod_line b on b.spec_line_id=a.id where a.item_no='"+self.item_no+"' and a.no_rev="+str(xno_rev)+" and a.no_doc='"+self.no_doc+"'")
        rc_line=self.env.cr.fetchall()
        if len(rc_line)>0:
            for def_line in rc_line:
                (xno_item,xno_rev,xtgl_efektif,xalasan)=def_line

                self.env.cr.execute("insert into sis_spec_prod_line (spec_line_id, no_item, no_rev, tgl_efektif, alasan) values ('"+str(xid)+"','"+str(xno_item)+"','"+xno_rev+"','"+xtgl_efektif+"','"+xalasan+"')")
            
#         self.env.cr.execute("update sis_spec_prod set spec_state='confirm' where no_doc='"+self.no_doc+"'")

                
    def view_spec(self):
        xuid = self.env.uid
        cSQL1="select a.section_spec from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_section=self.env.cr.fetchall()
        
        for def_section in rc_section:
            (xsection_spec,)=def_section

        cSQL="""
        select a.no_doc, a.no_rev, a.tgl_efektif, a.tgl_mulai, a.creator_name, a.item_desc, a.buyer_produk, a.buyer_name, a.buyer_brand, a.nama_produk, a.can_size, b.view_6, a.lid, b.view_7, a.jenis_ikan, b.view_8, a.ukuran_ikan, 
        b.view_9, a.netto, b.view_10, a.hampa_udara, b.view_11, a.sisa_udara, b.view_12, a.komposisi, b.view_13, a.formulasi, b.view_14, a.jenis_minyak, b.view_15, a.bumbu, b.view_16, 
        a.rasio_air, b.view_17, a.berat_tekan, b.view_18, a.berat_tuntas, b.view_19, a.tingkat_bersih, b.view_20, a.serpihan, b.view_21, a.ukuran_serpihan, b.view_22, a.jenis_packing, 
        b.view_23, a.kebersihan_produk, b.view_24, a.ph_produk_air, b.view_25, a.kadar_garam, b.view_26, a.histamin, b.view_27, a.analisa_proximat, b.view_28, a.proses_produksi, b.view_29,
        a.sterilisasi, b.view_30, a.pendinginan, b.view_31, a.kode_kaleng, b.view_32, a.kadaluarsa, b.view_33, a.etiket, b.view_34, a.kaleng_dus, b.view_35, a.keterangan, b.view_36, a.id
        from sis_spec_prod a, sis_spec_akses b
        where a.item_no='"""+self.item_no+"""' and a.no_doc='"""+self.no_doc+"""' and a.no_rev="""+str(self.no_rev)+""" and b.section='"""+xsection_spec+"""'
        """

        self.env.cr.execute(cSQL)
        rs=self.env.cr.fetchall()
        for rs_view in rs:
            (xno_doc, xno_rev, xtgl_efektif, xtgl_mulai, xcreator_name, xitem_desc, xbuyer_produk, xbuyer_name, xbuyer_brand, xnama_produk, xcan_size, xview_6, xlid, xview_7, xjenis_ikan, xview_8, xukuran_ikan, 
            xview_9, xnetto, xview_10, xhampa_udara, xview_11, xsisa_udara, xview_12, xkomposisi, xview_13, xformulasi, xview_14, xjenis_minyak, xview_15, xbumbu, xview_16, 
            xrasio_air, xview_17, xberat_tekan, xview_18, xberat_tuntas, xview_19, xtingkat_bersih, xview_20, xserpihan, xview_21, xukuran_serpihan, xview_22, xjenis_packing, 
            xview_23, xkebersihan_produk, xview_24, xph_produk_air, xview_25, xkadar_garam, xview_26, xhistamin, xview_27, xanalisa_proximat, xview_28, xproses_produksi, xview_29,
            xsterilisasi, xview_30, xpendinginan, xview_31, xkode_kaleng, xview_32, xkadaluarsa, xview_33, xetiket, xview_34, xkaleng_dus, xview_35, xketerangan, xview_36, xid)=rs_view

        xVHTML="""
            <script type="text/javascript">
                document.oncontextmenu = new Function("return false;");
                
                $(window).bind('keydown', 'ctrl+s', function () {
                    $('#save').click(); return false;
                });                
                $(window).bind('keydown', 'ctrl+p', function () {
                    $('#print').click(); return false;
                });                
            </script>
        
            <style>
                .disable-select {
                    -webkit-touch-callout: none; /* iOS Safari */
                    -webkit-user-select: none;   /* Chrome/Safari/Opera */
                    -khtml-user-select: none;    /* Konqueror */
                    -moz-user-select: none;      /* Firefox */
                    -ms-user-select: none;       /* Internet Explorer/Edge */
                    user-select: none;           /* Non-prefixed version, currently supported by any browser but < IE9 */
                }
            </style>        
        
            <center>
            <table class="disable-select" border="1" width="60%">
                <tr>
                    <td colspan="2" rowspan="2" width="45%" valign="middle" align="center" style="font-size:20px">
                    <table class="table" border="0" width="100%"><tr>
                        <td width=20%" align="center"><img class="img" src="/sis_testing/static/src/img/logo-aja.png"/></td>
                        <td align="center"><b>PT. ANEKA TUNA INDONESIA</b></td>
                    </tr></table>
                    </td>
                    <td width="15%" height="30px" style="font-size:15px" valign="middle">&nbsp;Doc No. """+xno_doc+"""</td>
                </tr>
                <tr>
                    <td width="12%" height="30px" style="font-size:15px" valign="middle">&nbsp;Rev No. """+str(xno_rev)+"""</td>
                </tr>
                <tr>
                    <td height="50px" width="13%" style="font-size:15px" valign="top">&nbsp;disiapkan oleh <br/>&nbsp;"""+str(xcreator_name)+"""</td>
                    <td align="center" valign="middle" align="center"><font size="4"><b>PRODUCT SPECIFICATION</b></font></td>
                    <td width="15%" style="font-size:15px" valign="top">&nbsp;Tanggal Efektif """+datetime.strptime(xtgl_efektif, "%Y-%m-%d").strftime("%d-%m-%Y")+"""</td>
                </tr>
            </table><br/>

            <table class="disable-select" border="1" width="60%">
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">1.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Nomor Seri / <i>Serial Number</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xno_doc+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">2.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Tanggal Mulai / <i>Starting Date</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xtgl_mulai+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">3.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kode Produk / <i>Product Code</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xitem_desc+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kode Produk Buyer/ <i>Buyer Product Code</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xbuyer_produk+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">4.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Nama Pembeli / <i>Buyer Name </i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xbuyer_name+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Nama Brand / <i>Buyer Brand</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xbuyer_brand+"""</td></tr></table></td>
                </tr>
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">5.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Nama Produk / <i>Product Name</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xnama_produk+"""</td></tr></table></td>
                </tr>
            
        """

        if xview_6==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">6.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Ukuran Kaleng / <i>Can Size</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xcan_size+"""</td></tr></table></td>
                </tr>
            """
        
        if xview_7==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">7.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Tutup Kaleng / <i>Lid</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xlid+"""</td></tr></table></td>
                </tr>
            """

        if xview_8==True:
            if xjenis_ikan.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">8.&nbsp;</td>
                        <td height="30px" style="font-size:15px;" width="300px">&nbsp;Jenis Ikan / <i>Kind of Fish</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xjenis_ikan+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">8.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Jenis Ikan / <i>Kind of Fish</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xjenis_ikan+"""</td></tr></table></td>
                    </tr>
                """

        if xview_9==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">9.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Ukuran Ikan / <i>Fish Size</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xukuran_ikan+"""</td></tr></table></td>
                </tr>
            """
        if xview_10==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">10.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Berat Netto / <i>Net Weight</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xnetto+"""</td></tr></table></td>
                </tr>
            """

        if xview_11==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">11.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Hampa Udara / <i>Vacuum</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xhampa_udara+"""</td></tr></table></td>
                </tr>
            """

        if xview_12==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">12.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Sisa Udara / <i>Residual Air</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xsisa_udara+"""</td></tr></table></td>
                </tr>
            """
            
        if xview_13==True:
            if xkomposisi.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">13.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Komposisi / <i>Ingredient</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkomposisi+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">13.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Komposisi / <i>Ingredient</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkomposisi+"""</td></tr></table></td>
                    </tr>
                """

        if xview_14==True:
            if xformulasi.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">14.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Formulasi / <i>Filling Weight</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xformulasi+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">14.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Formulasi / <i>Filling Weight</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xformulasi+"""</td></tr></table></td>
                    </tr>
                """


        if xview_15==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">15.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Jenis Minyak / <i>Kind of Oil</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xjenis_minyak+"""</td></tr></table></td>
                </tr>
            """
        
        if xview_16==True:
            if xbumbu.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">16.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Bumbu / <i>Seasoning</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xbumbu+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">16.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Bumbu / <i>Seasoning</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xbumbu+"""</td></tr></table></td>
                    </tr>
                """

        if xview_17==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">17.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Rasio Air : Liquid / <i>Aqueous Component</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xrasio_air+"""</td></tr></table></td>
                </tr>
            """

        if xview_18==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">18.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Berat Tekan / <i>Press Weight</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xberat_tekan+"""</td></tr></table></td>
                </tr>
            """

        if xview_19==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">19.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Berat Tuntas / <i>Drain Weight</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xberat_tuntas+"""</td></tr></table></td>
                </tr>
            """

        if xview_20==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">20.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Tingkat Pembersihan / <i>Level Cleaning</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xtingkat_bersih+"""</td></tr></table></td>
                </tr>
            """

        if xview_21==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">21.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Serpihan / <i>Flakes</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xserpihan+"""</td></tr></table></td>
                </tr>
            """

        if xview_22==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">22.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Ukuran Serpihan / <i>Flake Size</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xukuran_serpihan+"""</td></tr></table></td>
                </tr>
            """

        if xview_23==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">23.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Jenis Packing / <i>Pack Style</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xjenis_packing+"""</td></tr></table></td>
                </tr>
            """

        if xview_24==True:
            if xkebersihan_produk.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">24.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kebersihan Produk / <i>Cleaning Defect</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkebersihan_produk+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">24.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Kebersihan Produk / <i>Cleaning Defect</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkebersihan_produk+"""</td></tr></table></td>
                    </tr>
                """

        if xview_25==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">25.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;pH Produk Akhir / <i>pH End Product</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xph_produk_air+"""</td></tr></table></td>
                </tr>
            """

        if xview_26==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">26.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kadar Garam / <i>Salt Content</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkadar_garam+"""</td></tr></table></td>
                </tr>
            """

        if xview_27==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">27.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Histamin / <i>Histamine</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xhistamin+"""</td></tr></table></td>
                </tr>
            """

        if xview_28==True:
            if xanalisa_proximat.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">28.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Analisa Proximat / <i>Proximate analysis</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xanalisa_proximat+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:15px; width:40px">28.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Analisa Proximat / <i>Proximate analysis</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xanalisa_proximat+"""</td></tr></table></td>
                    </tr>
                """

        if xview_29==True:
            if xproses_produksi.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">29.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Proses Produksi / <i>Processing Method</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xproses_produksi+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">29.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Proses Produksi / <i>Processing Method</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xproses_produksi+"""</td></tr></table></td>
                    </tr>
                """
    
        if xview_30==True:
            if xsterilisasi.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">30.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Sterilisasi / <i>Sterilization</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xsterilisasi+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">30.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Sterilisasi / <i>Sterilization</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xsterilisasi+"""</td></tr></table></td>
                    </tr>
                """

        if xview_31==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">31.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Pendinginan / <i>Cooling</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xpendinginan+"""</td></tr></table></td>
                </tr>
            """

        if xview_32==True:
            if xkode_kaleng.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">32.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kode di Kaleng / <i>Can Code</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkode_kaleng+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">32.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Kode di Kaleng / <i>Can Code</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkode_kaleng+"""</td></tr></table></td>
                    </tr>
                """
            
        if xview_33==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">33.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Kadaluarsa / <i>Expiry</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkadaluarsa+"""</td></tr></table></td>
                </tr>
            """
            
        if xview_34==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">34.&nbsp;</td>
                    <td height="30px" style="font-size:15px;" width="300px"&nbsp;Etiket / <i>Label</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xetiket+"""</td></tr></table></td>
                </tr>
            """

        if xview_35==True:
            xVHTML +="""
                <tr valign="middle">
                    <td align="right" height="30px" style="font-size:14px; width:40px">35.&nbsp;</td>
                    <td height="30px" style="font-size:14px;" width="300px">&nbsp;Jumlah Produk Perdus / <i>Qty Product Per Case</i></td>
                    <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xkaleng_dus+"""</td></tr></table></td>
                </tr>
            """

        if xview_36==True:
            if xketerangan.find("<br")==-1:
                xVHTML +="""
                    <tr valign="middle">
                        <td align="right" height="30px" style="font-size:14px; width:40px">36.&nbsp;</td>
                        <td height="30px" style="font-size:14px;" width="300px">&nbsp;Keterangan / <i>Remark</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xketerangan+"""</td></tr></table></td>
                    </tr>
                """
            else:
                xVHTML +="""
                    <tr>
                        <td valign="top" align="right" height="30px" style="font-size:14px; width:40px">36.&nbsp;</td>
                        <td valign="top" height="30px" style="font-size:14px;" width="300px">&nbsp;Keterangan / <i>Remark</i></td>
                        <td height="30px"><table class="disable-select" border="0" width="100%"><tr><td width="10">&nbsp;</td><td>"""+xketerangan+"""</td></tr></table></td>
                    </tr>
                """
        
        xVHTML +="</table><br/>"
        
        cSQL="select no_item, no_rev, tgl_efektif, keterangan, alasan from sis_spec_prod_line where spec_line_id="+str(xid)+" order by no_rev"
        
        self.env.cr.execute(cSQL)
        rs2=self.env.cr.fetchall()
        if len(rs2)>0:        
            xVHTML +="""
            <table class="disable-select" border="1" width="60%">
                <tr>
                    <td style="font-size:13px; font-weight:normal" align="center" width="5%"><b><i>No.</i></b></td>
                    <td style="font-size:13px; font-weight:normal" align="center" width="5%"><b><i>Rev</i></b></td>
                    <td style="font-size:13px; font-weight:normal" align="center" width="10%"><b><i>Tgl. Efektif</i></b></td>
                    <td style="font-size:13px; font-weight:normal" align="center"><b><i>Alasan Revisi</i></b></td>
                    <td style="font-size:13px; font-weight:normal" align="center" width="30%"><b><i>Keterangan</i></b></td>
                </tr>
            """
            for rs_view2 in rs2:
                (xno_item, xno_rev, xtgl_efektif, xketerangan, xalasan)=rs_view2
                
                if xketerangan:
                    xket=xketerangan
                else:
                    xket=""
                
                xVHTML +="""
                    <tr>
                        <td style="font-size:12px; font-weight:normal" align="center">"""+xno_item+"""</td>
                        <td style="font-size:12px; font-weight:normal" align="center">"""+xno_rev+"""</td>
                        <td style="font-size:12px; font-weight:normal" align="center">"""+xtgl_efektif+"""</td>
                        <td style="font-size:12px; font-weight:normal">&nbsp;&nbsp;"""+xalasan+"""</td>
                    
                        <td style="font-size:12px; font-weight:normal">&nbsp;&nbsp;"""+xket+"""</td>
                    </tr>
                """
                
        
            xVHTML +="""</table>"""

            
#         xtanggal=datetime.now()
        xtemp_id=str(datetime.now()).replace('-','').replace(' ','').replace(':','').replace('.','')
        vals={'temp_id'             : xtemp_id,
              'no_doc'              : xno_doc,
              'no_rev'              : xno_rev,
              'tgl_efektif'         : xtgl_efektif,
              'creator_name'        : xcreator_name,
              'item_desc'           : xitem_desc,
              'buyer_produk'        : xbuyer_produk,
              'buyer_name'          : xbuyer_name,
              'buyer_brand'         : xbuyer_brand,
              'nama_produk'         : xnama_produk,
              'can_size'            : xcan_size,
              'view_6'              : xview_6,
              'lid'                 : xlid,
              'view_7'              : xview_7,
              'jenis_ikan'          : xjenis_ikan,
              'view_8'              : xview_8,
              'ukuran_ikan'         : xukuran_ikan,
              'view_9'              : xview_9,
              'netto'               : xnetto,
              'view_10'             : xview_10,
              'hampa_udara'         : xhampa_udara,
              'view_11'             : xview_11,
              'sisa_udara'          : xsisa_udara,
              'view_12'             : xview_12,
              'komposisi'           : xkomposisi,
              'view_13'             : xview_13,
              'formulasi'           : xformulasi,
              'view_14'             : xview_14,
              'jenis_minyak'        : xjenis_minyak,
              'view_15'             : xview_15,
              'bumbu'               : xbumbu,
              'view_16'             : xview_16,
              'rasio_air'           : xrasio_air,
              'view_17'             : xview_17,
              'berat_tekan'         : xberat_tekan,
              'view_18'             : xview_18,
              'berat_tuntas'        : xberat_tuntas,
              'view_19'             : xview_19,
              'tingkat_bersih'      : xtingkat_bersih,
              'view_20'             : xview_20,
              'serpihan'            : xserpihan,
              'view_21'             : xview_21,
              'ukuran_serpihan'     : xukuran_serpihan,
              'view_22'             : xview_22,
              'jenis_packing'       : xjenis_packing,
              'view_23'             : xview_23,
              'kebersihan_produk'   : xkebersihan_produk,
              'view_24'             : xview_24,
              'ph_produk_air'       : xph_produk_air,
              'view_25'             : xview_25,
              'kadar_garam'         : xkadar_garam,
              'view_26'             : xview_26,
              'histamin'            : xhistamin,
              'view_27'             : xview_27,
              'analisa_proximat'    : xanalisa_proximat,
              'view_28'             : xview_28,
              'sterilisasi'         : xproses_produksi,
              'view_29'             : xview_29,
              'sterilisasi'         : xsterilisasi,
              'view_29'             : xview_30,
              'pendinginan'         : xpendinginan,
              'view_30'             : xview_31,
              'kode_kaleng'         : xkode_kaleng,
              'view_31'             : xview_32,
              'kadaluarsa'          : xkadaluarsa,
              'view_32'             : xview_33,
              'etiket'              : xetiket,
              'view_33'             : xview_34,
              'kaleng_dus'          : xkaleng_dus,
              'view_34'             : xview_35,
              'keterangan'          : xketerangan,
              'view_35'             : xview_36,
              'view_html'           : xVHTML
            }
        
        self.env['sis.spec.prod.view'].create(vals)
        
        rec=self.env['sis.spec.prod.view'].search([('temp_id','=',xtemp_id)])
        if len(rec)>0:
            for xfield in rec:
                head_id=xfield.id

        return {
            'name'      : 'Product Specification',
            'res_model' : 'sis.spec.prod.view',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'form',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_spec_product.sis_view_spec_prod').id,
            'nodestroy' : False,
            'target'    : 'inline',
            'res_id'    : head_id,
            'domain'    : [('temp_id','=',xtemp_id)],   
            'flags'     : {'action_buttons': True}
        }    
        
        
    def get_nama_produk(self):
        self.env.cr.execute("select it.description2 from sis_production_bom bom inner join sis_nav_items_bc it on it.item_no=bom.itemno where bom.itemno='"+self.item_no+"'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xnama_produk,)=spec_line
        
        if self.no_rev==0:
            self.nama_produk=xnama_produk
        else:
            self.nama_produk="""<font style="background-color: rgb(255, 255, 0);">"""+xnama_produk+"""</font>"""
        
    def get_ukuran_kaleng(self):
        xcan=""
        self.env.cr.execute("select lineitem, linedesc from sis_production_bom where itemno='"+self.item_no+"' and lineitc='PKG' and (linepgc='CAN' or linepgc='POUCH')")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlineitem, xlinedesc)=spec_line
                
                if xlineitem[2:3]=='B':
                    if xcan.strip()=="":
                        xcan=xlinedesc+" ("+xlineitem+")"
                    else:
                        xcan=xcan+", "+xlinedesc+" ("+xlineitem+")"
                        
        if self.no_rev==0:
            self.can_size=xcan
        else:
            self.can_size="""<font style="background-color: rgb(255, 255, 0);">"""+xcan+"""</font>"""
        
    def get_lid(self):
        xlid=""
        self.env.cr.execute("select lineitem, linedesc from sis_production_bom where itemno='"+self.item_no+"' and lineitc='PKG' and linepgc='CAN'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlineitem, xlinedesc)=spec_line
                
                if xlineitem[2:3]=='E':
                    if xlid.strip()=="":
                        xlid=xlinedesc+" ("+xlineitem+")"
                    else:
                        xlid=xlid+", "+xlinedesc+" ("+xlineitem+")"
                        
        if self.no_rev==0:
            self.lid=xlid
        else:
            self.lid="""<font style="background-color: rgb(255, 255, 0);">"""+xlid+"""</font>"""

    def get_fish(self):
        xfish=""
        self.env.cr.execute("select lineitem, linedesc from sis_production_bom where itemno='"+self.item_no+"' and lineitc='WIP'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlineitem, xlinedesc)=spec_line
                
                if xfish.strip()=="":
                    xfish=xlinedesc
                else:
                    xfish=xfish+", "+xlinedesc
                        
        if self.no_rev==0:
            self.jenis_ikan=xfish
        else:
            self.jenis_ikan="""<font style="background-color: rgb(255, 255, 0);">"""+xfish+"""</font>"""

    def get_komposisi(self):
        xkomposisi=""
        self.env.cr.execute("select linedesc from sis_production_bom where itemno='"+self.item_no+"' and lineitc!='PKG' order by linepgc")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlinedesc,)=spec_line
                
                if xkomposisi.strip()=="":
                    xkomposisi=xlinedesc
                else:
                    xkomposisi=xkomposisi+", "+xlinedesc
                        
        self.komposisi=self.komposisi+"""<br>"""+xkomposisi

    def get_formulasi(self):
        xtotal_desc=""
        xtotal_qty=0
        xformulasi="-"
        self.env.cr.execute("""
        select sum(bom.lineqty) as Meat, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+self.item_no+"""' and bom.lineitc='WIP' group by bom.lineuom""")
        
        rc_meat=self.env.cr.fetchall()
        if len(rc_meat)>0:
            for meat_data in rc_meat:
                (meat_qty, meat_uom)=meat_data
                xformulasi="""<tr><td style="font-size:13px;border:0">Meat</td><td align="right" style="font-size:13px;border:0">"""+str(meat_qty)+" "+meat_uom+"""&nbsp;&nbsp;</td></tr>"""
                xtotal_desc="Meat"
                xtotal_qty=meat_qty
                    
        self.env.cr.execute("""
        select bom.linedesc, bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+self.item_no+"""' and bom.lineitc='SS' and bom.linepgc='VEGNFRT' order by bom.lineqty desc        
        """)
                
        rc_ss=self.env.cr.fetchall()
        if len(rc_ss)>0:
            xnomer=0
            for ss_data in rc_ss:
                (xssdesc, xssqty, xssuom)=ss_data
                xnomer=xnomer+1
                
                if xtotal_desc.strip()=="":
                    xtotal_desc=xssdesc
                else:
                    xtotal_desc +=", "+xssdesc
                
                xtotal_qty +=xssqty
                
                if xnomer==len(rc_ss):
                    xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xssdesc+"""</td><td align="right" style="font-size:13px;border:0"><u>"""+str(xssqty)+" "+xssuom+"""</u>&nbsp;&nbsp;</td></tr>"""
                else:
                    xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xssdesc+"""</td><td align="right" style="font-size:13px;border:0">"""+str(xssqty)+" "+xssuom+"""&nbsp;&nbsp;</td></tr>"""
            
            xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xtotal_desc+"""</td><td align="right" style="font-size:13px;border:0">"""+str(xtotal_qty)+" "+xssuom+"""&nbsp;&nbsp;</td></tr>"""

            xformulasi="""<p><br></p><p align="center"><table border="0" width="60%"><tbody>"""+xformulasi+"""</tbody></table></p><p><br></p>"""
            
        xformulasi +="""<p><br></p><p align="center"><table border="0" width="60%">"""
        
        self.env.cr.execute("""
        select bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+self.item_no+"""' and bom.lineitc='SS' and bom.linepgc='OIL' order by bom.lineqty desc        
        """)
 
        xoil=0                
        rc_oil=self.env.cr.fetchall()
        if len(rc_oil)>0:
            for oil_data in rc_oil:
                (xoilqty, xoiluom)=oil_data
                xoil+=xoilqty
            
            if xoil!=0:
                xformulasi +="""
                <tr><td style="font-size:13px;border:0">Minyak/Oil</td><td width="20%" align="right" style="font-size:13px;border:0">"""+str(xoil)+""" """+xoiluom+"""&nbsp;&nbsp;</td></tr>
                """

        self.env.cr.execute("""
        select bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+self.item_no+"""' and 
        (bom.linedesc like '%Garam%' or bom.linedesc like '%garam%' or bom.linedesc like '%GARAM%' or bom.linedesc like '%Salt%' or bom.linedesc like '%salt%' or bom.linedesc like '%SALT%')
        """)
        xsalt=0                
        rc_salt=self.env.cr.fetchall()
        if len(rc_salt)>0:
            for salt_data in rc_salt:
                (xsaltqty, xsaltuom)=salt_data
                xsalt +=xsaltqty
            
            if xsalt!=0:
                xformulasi +="""
                <tr><td style="font-size:13px;border:0">Air Garam/Brine</td><td width="20%" align="right" style="font-size:13px;border:0">"""+str(xsalt)+""" """+xsaltuom+"""&nbsp;&nbsp;</td></tr>
                """
        xformulasi +="</table></p>"
        
        self.formulasi +="<br>------------------<br>synced formulasi<br>------------------<br>"+xformulasi
        
    def get_jenis_minyak(self):
        xoil=""
        
        self.env.cr.execute("select linedesc from sis_production_bom where itemno='"+self.item_no+"' and lineitc='SS' and linepgc='OIL' order by linedesc")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlinedesc,)=spec_line
                if xoil.strip()=="":
                    xoil="""<font style="background-color: rgb(255, 255, 0);">"""+xlinedesc+"""</font>"""
                else:
                    xoil=xoil+""", <font style="background-color: rgb(255, 255, 0);">"""+xlinedesc+"""</font>"""
        else:
            xoil="""<font style="background-color: rgb(255, 255, 0);">-</font>"""
        
        self.jenis_minyak=xoil
    
    def get_bumbu(self):
        xseas=""
        xseas_head="""
        <p><br></p>
        <table border="1">
            <tbody>
                <tr><td colspan="2" align="center"><b>Brine (g)/tin</b></td></tr>
        """
        xseas_foot="</tbody></table><p><br></p>"

        self.env.cr.execute("select linedesc, lineqty, lineuom from sis_production_bom where itemno='"+self.item_no+"' and lineitc='SS' and linepgc not in ('OIL','VEGNFRT') order by lineqty desc")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlinedesc, xlineqty, xlineuom)=spec_line

                if xseas.strip()=="":
                    xseas="""<tr><td>"""+xlinedesc+"""</td><td align="center">"""+str(xlineqty)+"""</td></tr>"""
                else:
                    xseas=xseas+"""<tr><td>"""+xlinedesc+"""</td><td align="center">"""+str(xlineqty)+"""</td></tr>"""
        
        if xseas.strip()!="" or xseas.strip()!="-":
            self.bumbu=self.bumbu+"<br>------------------<br>synced bumbu<br>------------------<br>"+xseas_head+xseas+xseas_foot
        else:
            self.bumbu="-"    
    
    def get_product_bom(self):
        self.env.cr.execute("delete from sis_bom where temp_id='"+self.temp_id+"'")
        self.env.cr.execute("delete from sis_bom_line where temp_id='"+self.temp_id+"'")
         
        if self.temp_id:
            return {
                'name'      : 'B O M',
                'res_model' : 'sis.bom',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_spec_product.sis_bom_filter').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_temp_id':self.temp_id, 'default_selected_bom':self.item_desc},
            }    

    def get_buyer(self):
        self.env.cr.execute("delete from sis_spec_buyer where temp_id='"+self.temp_id+"'")
        self.env.cr.execute("delete from sis_spec_buyer_line where temp_id='"+self.temp_id+"'")
         
        if self.temp_id:
            return {
                'name'      : 'Buyer',
                'res_model' : 'sis.spec.buyer',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_spec_product.sis_buyer_filter').id,
                'nodestroy' : False,
                'target'    : 'inline',
                'context'   : {'default_temp_id':self.temp_id, 'default_selected_buy':self.buyer_name},
            }
            
#     def set_status(self):
#         if self.status_spec==False:
#             self.status_spec=True
#         else:
#             self.status_spec=False
# 
#         self.env.cr.execute("update sis_spec_prod set status_spec=false where no_doc='"+self.no_doc+"' and item_no='"+self.item_no+"' and no_rev!="+str(self.no_rev))
        
    def write(self, vals):
        msg="" 
        for me in self:
            if me.spec_state != 'draft' :
                if vals.get('spec_state') and vals['spec_state']=='draft':
                    return super(sis_spec_prod, self).write(vals)
                else:
                    raise UserError("Cannot update!")
            else:
                if vals.get('item_desc'):
                    msg += "Kode Produk" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.item_desc, vals['item_desc'],)                

                if vals.get('buyer_produk'):
                    msg += "Kode Produk Buyer" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.buyer_produk, vals['buyer_produk'],)                

                if vals.get('buyer_name'):
                    msg += "Nama Pembeli" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.buyer_name, vals['buyer_name'],)                

                if vals.get('buyer_brand'):
                    msg += "Nama Brand" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.buyer_brand, vals['buyer_brand'],)                

                if vals.get('nama_produk'):
                    msg += "Nama Produk" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.nama_produk, vals['nama_produk'],)                

                if vals.get('can_size'):
                    msg += "Ukuran Kaleng" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.can_size, vals['can_size'],)                

                if vals.get('lid'):
                    msg += "Tutup Kaleng" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.lid, vals['lid'],)                

                if vals.get('jenis_ikan'):
                    msg += "Jenis Ikan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.jenis_ikan, vals['jenis_ikan'],)                

                if vals.get('ukuran_ikan'):
                    msg += "Ukuran Ikan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.ukuran_ikan, vals['ukuran_ikan'],)                

                if vals.get('netto'):
                    msg += "Berat Netto" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.netto, vals['netto'],)                

                if vals.get('hampa_udara'):
                    msg += "Hampa Udara" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.hampa_udara, vals['hampa_udara'],)                

                if vals.get('sisa_udara'):
                    msg += "Sisa Udara" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.sisa_udara, vals['sisa_udara'],)                

                if vals.get('komposisi'):
                    msg += "Komposisi" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.komposisi, vals['komposisi'],)                
    
                if vals.get('formulasi'):
                    msg += "Formulasi" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.formulasi, vals['formulasi'],)                
    
                if vals.get('jenis_minyak'):
                    msg += "Jenis Minyak" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.jenis_minyak, vals['jenis_minyak'],)                
    
                if vals.get('bumbu'):
                    msg += "Bumbu" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.bumbu, vals['bumbu'],)                
                    
                if vals.get('rasio_air'):
                    msg += "Rasio Air : Liquid" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.rasio_air, vals['rasio_air'],)                
    
                if vals.get('berat_tekan'):
                    msg += "Berat Tekan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.berat_tekan, vals['berat_tekan'],)                

                if vals.get('berat_tuntas'):
                    msg += "Berat Tuntas" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.berat_tuntas, vals['berat_tuntas'],)                

                if vals.get('tingkat_bersih'):
                    msg += "Tingkat Pembersihan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.tingkat_bersih, vals['tingkat_bersih'],)                

                if vals.get('serpihan'):
                    msg += "Serpihan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.serpihan, vals['serpihan'],)                

                if vals.get('ukuran_serpihan'):
                    msg += "Ukuran Serpihan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.ukuran_serpihan, vals['ukuran_serpihan'],)                

                if vals.get('jenis_packing'):
                    msg += "Jenis Packing" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.jenis_packing, vals['jenis_packing'],)                

                if vals.get('kebersihan_produk'):
                    msg += "Kebersihan Produk" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.kebersihan_produk, vals['kebersihan_produk'],)                

                if vals.get('ph_produk_air'):
                    msg += "PH Produk Akhir" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.ph_produk_air, vals['ph_produk_air'],)                

                if vals.get('kadar_garam'):
                    msg += "Kadar Garam" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.kadar_garam, vals['kadar_garam'],)                

                if vals.get('histamin'):
                    msg += "Histamin" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.histamin, vals['histamin'],)                

                if vals.get('analisa_proximat'):
                    msg += "Analisa Proximat" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.analisa_proximat, vals['analisa_proximat'],)                
    
                if vals.get('proses_produksi'):
                    msg += "Proses Produksi" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.proses_produksi, vals['proses_produksi'],)                

                if vals.get('sterilisasi'):
                    msg += "Sterilisasi" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.sterilisasi, vals['sterilisasi'],)                

                if vals.get('pendinginan'):
                    msg += "Pendinginan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.pendinginan, vals['pendinginan'],)                

                if vals.get('kode_kaleng'):
                    msg += "Kode Kaleng" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.kode_kaleng, vals['kode_kaleng'],)                

                if vals.get('kadaluarsa'):
                    msg += "Kadaluarsa" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.kadaluarsa, vals['kadaluarsa'],)                

                if vals.get('etiket'):
                    msg += "Etiket" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.etiket, vals['etiket'],)                

                if vals.get('kaleng_dus'):
                    msg += "Jumlah Produk per Dus" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.kaleng_dus, vals['kaleng_dus'],)                

                if vals.get('keterangan'):
                    msg += "Keterangan" + ": <br/><b>Before :</b> %s<br/><b>After :</b> %s" % (me.keterangan, vals['keterangan'],)                

                if msg!="":
                    me.message_post(body=msg)
                
                if vals.get('signature_id'):
                    self.env.cr.execute("select ttd_jabatan1,ttd_jabatan2,ttd_jabatan3,ttd_nama1,ttd_nama2,ttd_nama3 from sis_spec_signature where id="+str(vals['signature_id']))
                    r_sign=self.env.cr.fetchall()
                    if len(r_sign)!=0:
                        for spec_sign in r_sign:
                            (xttd_jabatan1,xttd_jabatan2,xttd_jabatan3,xttd_nama1,xttd_nama2,xttd_nama3)=spec_sign        
                            vals.update({'ttd_jabatan1':xttd_jabatan1, 'ttd_jabatan2':xttd_jabatan2, 'ttd_jabatan3':xttd_jabatan3, 'ttd_nama1':xttd_nama1, 'ttd_nama2':xttd_nama2, 'ttd_nama3':xttd_nama3})                     
        
                return super(sis_spec_prod, self).write(vals)

    @api.multi
    def unlink(self):
        for me in self :
            if me.spec_state != 'draft' :
                raise UserError("Cannot delete!")
            else:
                return super(sis_spec_prod, self).unlink()

class sis_spec_prod_line(models.Model):
    _name='sis.spec.prod.line'
    _rec_name='no_item'
    
    spec_line_id = fields.Many2one('sis.spec.prod', string="Spec Lines", ondelete='cascade', required=True)
    no_item=fields.Char(string='No Item', size=20, default="0", required=True)
    no_rev=fields.Char(size=3,string='Rev No', compute="get_data_header", store=True)
    tgl_efektif=fields.Date(string='Tanggal Efektif', compute="get_data_header", store=True)
    keterangan=fields.Char(size=50,string='Keterangan')
    alasan=fields.Char(size=255,string='Alasan Revisi')
    
    @api.one
    @api.depends('no_item')
    def get_data_header(self):
        if self.no_item and self.no_item!=0:
            self.no_rev=self.spec_line_id.no_rev
            self.tgl_efektif=self.spec_line_id.tgl_efektif            
            
class sis_spec_prod_view(models.TransientModel):
    _name='sis.spec.prod.view'
#    _rec_name='nis'
    _rec_name='item_desc2'
        
    temp_id= fields.Float(string="Temp ID")
    no_doc=fields.Char(size=30,string='Doc No')
    no_rev=fields.Integer(string='Rev No')
    tgl_efektif=fields.Date(string='Tanggal Efektif')
    tgl_mulai=fields.Char(size=255, string='Tanggal Mulai')
    creator_name=fields.Char(size=30,string='Disiapkan Oleh')
#     item_no=fields.Char(size=50,string='Item No',required=True)
    item_desc=fields.Html(string='Kode Produk')
    item_desc2=fields.Text(string='Kode Produk', compute='_kode_produk')
#     buyer_no=fields.Char(size=10,string='Kode Buyer',required=True)
    buyer_produk=fields.Html(string='Kode Produk Buyer')
    buyer_name=fields.Html(string='Nama Buyer')
    buyer_brand=fields.Html(string='Brand')
    nama_produk=fields.Html(string='Nama Produk')
    can_size=fields.Html(string='Ukuran Kaleng')
    view_6=fields.Boolean(string="view_6")
    lid=fields.Html(string='Tutup Kaleng')
    view_7=fields.Boolean(string="view_7")
    jenis_ikan=fields.Html(string='Jenis Ikan')
    view_8=fields.Boolean(string="view_8")
    ukuran_ikan=fields.Html(string='Ukuran Ikan')
    view_9=fields.Boolean(string="view_9")
    netto=fields.Html(string='Berat Netto')
    view_10=fields.Boolean(string="view_10")
    hampa_udara=fields.Html(string='Hampa Udara')
    view_11=fields.Boolean(string="view_11")
    sisa_udara=fields.Html(string='Sisa Udara')
    view_12=fields.Boolean(string="view_12")
    komposisi=fields.Html(string='Komposisi')
    view_13=fields.Boolean(string="view_13")
    formulasi=fields.Html(string='Formulasi')
    view_14=fields.Boolean(string="view_14")
    jenis_minyak=fields.Html(string='Jenis Minyak')
    view_15=fields.Boolean(string="view_15")
    bumbu=fields.Html(string='Bumbu')
    view_16=fields.Boolean(string="view_16")
    rasio_air=fields.Html(string='Rasio Air : Likuid')
    view_17=fields.Boolean(string="view_17")
    berat_tekan=fields.Html(string='Berat Tekan')
    view_18=fields.Boolean(string="view_18")
    berat_tuntas=fields.Html(string='Berat Tuntas')
    view_19=fields.Boolean(string="view_19")
    tingkat_bersih=fields.Html(string='Tingkat Pembersihan')
    view_20=fields.Boolean(string="view_20")
    serpihan=fields.Html(string='Serpihan')
    view_21=fields.Boolean(string="view_21")
    ukuran_serpihan=fields.Html(string='Ukuran Serpihan')
    view_22=fields.Boolean(string="view_22")
    jenis_packing=fields.Html(string='Jenis Packing')
    view_23=fields.Boolean(string="view_23")
    kebersihan_produk=fields.Html(string='Kebersihan Produk')
    view_24=fields.Boolean(string="view_24")
    ph_produk_air=fields.Html(string='Kebersihan Produk')
    view_25=fields.Boolean(string="view_25")
    kadar_garam=fields.Html(string='Kadar Garam')
    view_26=fields.Boolean(string="view_26")
    histamin=fields.Html(string='Histamin')
    view_27=fields.Boolean(string="view_27")
    analisa_proximat=fields.Html(string='Analisa Proximat')
    view_28=fields.Boolean(string="view_28")
    proses_produksi=fields.Html(string='Proses Produksi')
    view_29=fields.Boolean(string="view_29")
    sterilisasi=fields.Html(string='Sterilisasi')
    view_30=fields.Boolean(string="view_30")
    pendinginan=fields.Html(string='Pendinginan')
    view_31=fields.Boolean(string="view_31")
    kode_kaleng=fields.Html(string='Koden Kaleng')
    view_32=fields.Boolean(string="view_32")
    kadaluarsa=fields.Html(string='Kadaluarsa (Bulan)')
    view_33=fields.Boolean(string="view_33")
    etiket=fields.Html(string='Etiket')
    view_34=fields.Boolean(string="view_34")
    kaleng_dus=fields.Html(string='Kaleng/Dus')
    view_35=fields.Boolean(string="view_35")
    keterangan=fields.Html(string='Keterangan')
    view_36=fields.Boolean(string="view_36")
    view_html=fields.Html(string="View HTML", sanitize=False)
    
    @api.one
    @api.depends('item_desc')
    def _kode_produk(self):
        if self.item_desc:
            TAG_RE = re.compile('<.*?>')
            self.item_desc2=TAG_RE.sub('', self.item_desc)
    
    def kembali(self):
        return {'type': 'ir.actions.client', 
                'tag': 'history_back'
                }
        