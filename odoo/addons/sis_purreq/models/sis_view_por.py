from odoo import models, fields, api
import xlsxwriter
import base64

class view_po_requisition(models.TransientModel):
    _name           = 'sis.view.por'
    _rec_name       = 'no_doc'
    _description    = 'View PO Requisition'
    
    no_doc          = fields.Char(string='No. POR')
    tanggal1_doc    = fields.Date(string='Tanggal Awal')
    tanggal2_doc    = fields.Date(string='Tanggal Akhir')
    pabrik_id       = fields.Selection([('ATI1','ATI1'),('ATI2','ATI2')], string='Factory')
    section_id      = fields.Selection(string="Section", store=True, selection=[
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
        ])
    item_type       = fields.Selection([(1,'Jasa'),(2,'Item'),(3,'Asset')], string='Type')
    item_no         = fields.Char(size=20, string='Kode')
    item_desc       = fields.Char(size=200, string='Nama Item')
    state_doc       = fields.Selection([('Open','Open'),('Close','Closed')], string='Status Doc')
    rpt_xlsx        = fields.Binary('File data', help='File(xlsx format)')
    view_por_line   = fields.One2many('sis.view.por.line', 'rel_view_por_line', string='Line ID')

    def _get_filter(self):
        xwer=""
        
        if self.no_doc:
            xwer="(LOWER(a.no_doc) like '%"+self.no_doc+"%' or a.no_doc like '%"+self.no_doc+"%')"
            
        if self.tanggal1_doc and self.tanggal2_doc:
            if xwer.strip()!="":
                xwer=xwer+" and a.tgl_doc between '"+self.tanggal1_doc+"' and '"+self.tanggal2_doc+"'"
            else:
                xwer="a.tgl_doc between '"+self.tanggal1_doc+"' and '"+self.tanggal2_doc+"'"
        else:
            if self.tanggal1_doc:
                if xwer.strip()!="":
                    xwer=xwer+" and a.tgl_doc='"+self.tanggal1_doc+"'"
                else:
                    xwer="a.tgl_doc='"+self.tanggal1_doc+"'"
        
        if self.pabrik_id:
            if xwer.strip()!="":
                xwer=xwer+" and a.pabrik_id='"+self.pabrik_id+"'"
            else:
                xwer="a.pabrik_id='"+self.pabrik_id+"'"
        
        xsection=self._get_section_id()
        if xsection=="PNF" or xsection=="Admin":
            if self.section_id:
                if xwer.strip()!="":
                    xwer=xwer+" and e.kode='"+self.section_id+"'"
                else:
                    xwer="e.kode='"+self.section_id+"'"
        else:
            if xwer.strip()!="":
                xwer=xwer+" and e.kode='"+xsection+"'"
            else:
                xwer="e.kode='"+xsection+"'"
        
        if self.item_type:
            if xwer.strip()!="":
                xwer=xwer+" and b.item_type="+str(self.item_type)
            else:
                xwer="b.item_type="+str(self.item_type)

        if self.item_no:
            temp=''
            for i in self.item_no:
                if i=='*':
                    temp=temp+'%'
                else:
                    temp=temp+i
            print(temp, self.item_no)
            if xwer.strip()!="":
#                 xwer=xwer+" and (LOWER(b.item_no) like '%"+self.item_no+"%' or b.item_no like '%"+self.item_no+"%')"
                xwer=xwer+" and (LOWER(b.item_no) like '"+temp+"' or b.item_no like '"+temp+"')"
            else:
#                 xwer="(LOWER(b.item_no) like '%"+self.item_no+"%' or b.item_no like '%"+self.item_no+"%')"
                xwer="(LOWER(b.item_no) like '"+temp+"' or b.item_no like '"+temp+"')"
        
        if self.item_desc:
            temp=''
            for i in self.item_desc:
                if i=='*':
                    temp=temp+'%'
                else:
                    temp=temp+i
            print(temp, self.item_desc)
            if xwer.strip()!="":
#                 xwer=xwer+" and (LOWER(c.description) like '%"+self.item_desc+"%' or c.description like '%"+self.item_desc+"%')"
                xwer=xwer+" and (LOWER(b.item_desc) like '"+temp+"' or b.item_desc like '"+temp+"')"
            else:
#                 xwer="(LOWER(c.description) like '%"+self.item_desc+"%' or c.description like '%"+self.item_desc+"%')"
                xwer="(LOWER(b.item_desc) like '"+temp+"' or b.item_desc like '"+temp+"')"

        if self.state_doc:
            if xwer.strip()!="":
                xwer=xwer+" and d.status_por='"+self.state_doc+"'"
            else:
                xwer="d.status_por='"+self.state_doc+"'"
        
        return xwer
    
    def _get_section_id(self):
        xsection=""
        
        xuid = self.env.uid
        cSQL1="select a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
 
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_section=self.env.cr.fetchall()
         
        for def_section in rc_section:
                (xsection_id,)=def_section
         
        xsection=xsection_id
        
        return xsection
        
    def get_data_por(self):
        self.env.cr.execute("delete from sis_view_por_line where temp_id="+str(self.id))       
        cSQL="""
            select
            a.no_doc, a.tgl_doc, a.pabrik_id, e.keterangan,
            b.item_type, b.no_line, b.item_no, b.item_desc, b.item_qty, b.item_uom, d.po_uom,
            d.no_po, d.po_date, d.vendor_no, d.vendor_desc, d.po_qty, d.por_sisa_qty, d.wh_receipt_no, d.whr_posting_date, d.no_pci, d.pci_posting_date, coalesce(d.status_por,'Open'), d.whr_qty
            
            from sis_po_requisition a
            left join sis_po_requisition_lines b on b.por_line_id=a.id
            inner join sis_section e on e.kode=a.section_id
            left  join sis_nav_por d on d.por_no=a.no_doc and d.por_line=b.no_line
        """

        if self._get_filter():
            cSQL=cSQL+" where "+self._get_filter()+" order by a.no_doc, b.no_line"
        else:
            cSQL=cSQL+" order by a.no_doc, b.no_line"

        self.env.cr.execute(cSQL)
        rec_por=self.env.cr.fetchall()
        
        if len(rec_por)>0:
            new_lines = self.env['sis.view.por.line']
            for ipor in rec_por:
                (xno_doc, xtgl_doc, xpabrik_id, xsection, xpor_type, xno_line, xitem_no, xitem_desc, xpor_qty, xpor_uom, xpo_uom, xpo_no, xpo_date, xvendor_no, xvendor_desc, 
                 xpo_qty, xpor_sisa, xwhr_no, xwhr_date, xpci_no, xpci_date, xstatus, xwhr_qty)=ipor
                
                vals={
                    'no_doc'        :xno_doc,
                    'line_no'       :xno_line,
                    'tgl_doc'       :xtgl_doc,
                    'section'       :xpabrik_id+" "+xsection,
                    'item_type'     :xpor_type,
                    'item_no'       :xitem_no,
                    'item_desc'     :xitem_desc,
                    'item_uom'      :xpor_uom,
                    'item_qty'      :xpor_qty,
                    'no_po'         :xpo_no,
                    'vendor_no'     :xvendor_no,
                    'vendor_desc'   :xvendor_desc,
                    'tgl_po'        :xpo_date,
                    'qty_po'        :xpo_qty,
                    'qty_sisa'      :xpor_sisa,
                    'po_uom'        :xpo_uom,
                    'wr_no'         :xwhr_no,
                    'wr_tgl'        :xwhr_date,
                    'inv_no'        :xpci_no,
                    'inv_tgl'       :xpci_date,
                    'wr_qty'       :xwhr_qty,
                    'state_doc'     :xstatus,
                    'temp_id'       :self.id
                }
                 
                new_lines += new_lines.new(vals)
            
            self.view_por_line=new_lines
    
    def new_data_por(self):
        return {
            'name'      : 'PO Requisition',
            'res_model' : 'sis.po.requisition',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'form',
            'view_type' : 'form',
#             'view_id'   : self.env.ref('sis_spec_product.sis_view_spec_prod').id,
#             'nodestroy' : False,
            'target'    : 'current',
#             'res_id'    : head_id,
#             'domain'    : [('temp_id','=',xtemp_id)],   
            'flags'     : {'action_buttons': True}
        }
    
    @api.multi    
    def write_xlsx(self):
        xlaporan="purchase_requisition.xlsx"

        workbook = xlsxwriter.Workbook('/tmp/'+xlaporan)        
        worksheet = workbook.add_worksheet()
        
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#BDBDDF'}) #AFAFD8
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

        worksheet.insert_image('A1', '/home/rusdi/Pictures/logo-aja.png')
        worksheet.write(0,2,"PT Aneka Tuna Indonesia", bold)
        worksheet.write(1,2,"Jl. Raya Surabaya-Malang Km. 38 Gempol Pasuruan", bold)

#         worksheet.write(0,11,self.rpt_laporan, title_format2)
#         if self.rpt_tanggal1 and self.rpt_tanggal2:
#             worksheet.write(1,11,"Tanggal : "+self.rpt_tanggal1+" s/d "+self.rpt_tanggal2, date_format2)
#         elif self.rpt_tanggal1:
#             worksheet.write(1,11,"Tanggal : "+self.rpt_tanggal1, date_format2)
#         else:
#             worksheet.write(1,11,"Tanggal : -", date_format2)

        worksheet.write(3,0,"No.", header_format)
        worksheet.write(3,1,"No. Requisition", header_format)
        worksheet.write(3,2,"Type", header_format)
        worksheet.write(3,3,"No. Line", header_format)
        worksheet.write(3,4,"Tanggal", header_format)
        worksheet.write(3,5,"Section", header_format)
        worksheet.write(3,6,"Kode Item", header_format)
        worksheet.write(3,7,"Uraian Item", header_format)
        worksheet.write(3,8,"Satuan", header_format)
        worksheet.write(3,9,"Qty", header_format)
        worksheet.write(3,10,"No. PO", header_format)
        worksheet.write(3,11,"Tgl. PO", header_format)
        worksheet.write(3,12,"Vendor", header_format)
        worksheet.write(3,13,"Qty PO", header_format)
        worksheet.write(3,14,"Qty Sisa", header_format)
        worksheet.write(3,15,"No. Receipt", header_format)
        worksheet.write(3,16,"Tgl Receipt", header_format)
        worksheet.write(3,17,"Qty Receipt", header_format)
        worksheet.write(3,18,"No. Invoice", header_format)
        worksheet.write(3,19,"Tgl Invoice", header_format)
        worksheet.write(3,20,"Status", header_format)

        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 3, 10)
        worksheet.set_column(4, 4, 10)
        worksheet.set_column(5, 5, 20)
        worksheet.set_column(6, 6, 15)
        worksheet.set_column(7, 7, 50)
        worksheet.set_column(8, 9, 10)
        worksheet.set_column(10, 10, 20)
        worksheet.set_column(11, 11, 10)
        worksheet.set_column(12, 12, 50)
        worksheet.set_column(13, 14, 10)
        worksheet.set_column(15, 15, 15)
        worksheet.set_column(16, 17, 12)
        worksheet.set_column(18, 18, 15)
        worksheet.set_column(19, 20, 10)
        
        self.env.cr.execute("""select no_doc, item_type, line_no, tgl_doc, section, item_no, item_desc, item_uom, item_qty, no_po, tgl_po, vendor_desc, qty_po, qty_sisa, 
        wr_no, wr_tgl, 0, inv_no, inv_tgl, state_doc from sis_view_por_line where temp_id="""+str(self.id)+""" order by no_doc, line_no""")
        rpt=self.env.cr.fetchall()

        xNomer=3
        xNo=0
        if len(rpt)>0:
            for irpt in rpt:
                (xno_doc, xitem_type, xline_no, xtgl_doc, xsection, xitem_no, xdescription, xitem_uom, xitem_qty, xno_po, xtgl_po, xvendor, xqty_po, xqty_sisa, xwr_no, xwr_tgl, xwr_qty, xinv_no, xinv_tgl, xstate_doc)=irpt
                xNomer=xNomer+1
                xNo=xNo+1

                worksheet.write(xNomer,0,str(xNo)+". ", row_right_format)
                worksheet.write(xNomer,1,xno_doc, row_center_format)
                if xitem_type==1:
                    worksheet.write(xNomer,2,"Jasa", row_center_format)
                elif xitem_type==2:
                    worksheet.write(xNomer,2,"Item", row_center_format)
                elif xitem_type==3:
                    worksheet.write(xNomer,2,"Fixed Asset", row_center_format)
                worksheet.write(xNomer,3,xline_no, row_right_format)
                worksheet.write(xNomer,4,xtgl_doc, row_center_format)
                worksheet.write(xNomer,5,xsection, row_format)
                worksheet.write(xNomer,6,xitem_no, row_center_format)
                worksheet.write(xNomer,7,xdescription, row_format)
                worksheet.write(xNomer,8,xitem_uom, row_center_format)
                worksheet.write(xNomer,9,xitem_qty, row_right_format)
                worksheet.write(xNomer,10,xno_po, row_center_format)
                worksheet.write(xNomer,11,xtgl_po, row_center_format)
                worksheet.write(xNomer,12,xvendor, row_format)
                worksheet.write(xNomer,13,xqty_po, row_right_format)
                worksheet.write(xNomer,14,xqty_sisa, row_right_format)
                worksheet.write(xNomer,15,xwr_no, row_center_format)
                worksheet.write(xNomer,16,xwr_tgl, row_center_format)
                worksheet.write(xNomer,17,xwr_qty, row_right_format)
                worksheet.write(xNomer,18,xinv_no, row_center_format)
                worksheet.write(xNomer,19,xinv_tgl, row_center_format)
                worksheet.write(xNomer,20,xstate_doc, row_center_format)
    
            worksheet.autofilter('A4:U4')
            
        workbook.close()

        rec=self.env['sis.view.por'].search([('id','=',self.id)])
        for r in rec:
            vals={ 
                    'rpt_xlsx':base64.b64encode(open("/tmp/"+xlaporan, "rb").read())
                }
            r.write(vals)

        return {
            'type': 'ir.actions.act_url',
            'name': 'Report',
            'url': '/web/content/sis.view.por/%s/rpt_xlsx/%s?download=true' % (str(self.id), xlaporan)
        }

class view_po_requisition_line(models.TransientModel):
    _name        ='sis.view.por.line'
    _rec_name    = 'no_doc'
    _description = 'View PO Requisition Line'

    rel_view_por_line   = fields.Many2one('sis.view.por', string="Line ID")
    no_doc              = fields.Char(string='No. POR', size=22)
    line_no             = fields.Integer(string="No. Line")
    tgl_doc             = fields.Date(string='Tanggal POR')
    section             = fields.Char(string="Section", size=50)
    item_no             = fields.Char(string="Kode", size=20)
    item_type           = fields.Selection([(1,'Jasa'),(2,'Item'),(3,'Asset')], string='Type')
    item_desc           = fields.Char(string="Nama Item", size=50)
    item_uom            = fields.Char(string="Satuan", size=20)
    item_qty            = fields.Float('Qty')
    no_po               = fields.Char(string='No. PO')
    vendor_no           = fields.Char(string="Vendor No", size=20)
    vendor_desc         = fields.Char(string="Vendor Desc", size=50)
    tgl_po              = fields.Date(string='Tanggal PO')
    qty_po              = fields.Float('Qty PO')
    qty_sisa            = fields.Float('Qty Sisa')
    po_uom              = fields.Char(string="PO UOM", size=20)
    wr_no               = fields.Char(string='WR. No.', size=20)
    wr_tgl              = fields.Date(string='Tanggal WR')
    wr_qty              = fields.Float('Qty WR')
    inv_no              = fields.Char(string='INV. No.', size=20)
    inv_tgl             = fields.Date(string='Tanggal INV')
    state_doc           = fields.Char(string='Status Doc', size=20)
    temp_id             = fields.Float(string="Temp ID")

    def viewdata(self):
        xstatus_doc=""
        
        rec=self.env['sis.po.requisition'].search([('no_doc','=',self.no_doc)])
        if len(rec)>0:
            for xfield in rec:
                head_id=xfield.id
                xstatus_doc=xfield.state_doc

        if xstatus_doc=='confirmed':
            self.env.cr.execute("select state_doc from sis_view_por_line where no_doc='"+self.no_doc+"' and temp_id="+str(self.temp_id))
            dat_por=self.env.cr.fetchall()
     
            xstate=1
            if len(dat_por)>0:
                for f_por in dat_por:
                    (xstatus,)=f_por
                    
                    if xstatus=='Open':
                        xstate=0
                        break
            
            if xstate==1:
                self.env.cr.execute("update sis_po_requisition set state_doc='closed' where no_doc='"+self.no_doc+"'")
#             rec_por=self.env['sis.po.requisition'].search([('no_doc','=',self.no_doc)])
#             for r in rec_por:
#                 vals={ 
#                       'state_doc':'closed'
#                     }
#                 r.write(vals)       
        
        return {
            'name'      : 'PO Requisition',
            'res_model' : 'sis.po.requisition',
            'type'      : 'ir.actions.act_window',
            'view_mode' : 'form',
            'view_type' : 'form',
            'view_id'   : self.env.ref('sis_purreq.sis_po_requisition_form').id,
#             'nodestroy' : False,
            'target'    : 'current',
            'res_id'    : head_id,
            'domain'    : [('no_doc','=',self.no_doc)],   
            'flags'     : {'action_buttons': True}
        }    
    
    
