from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime
import psycopg2
import xlsxwriter
import base64
import html2text
from odoo.addons.point_of_sale.wizard.pos_box import PosBox

passwd="mis1.anekatuna"

class sis_ppic_dpe_xls(models.TransientModel):
    _name='sis.ppic.dpe.xls'

    report=fields.Binary (string='Report')
    
class sis_ppic_dpe(models.Model):
    _name='sis.ppic.dpe'
    _rec_name="no"
    _order='id desc'
    _inherit = ['mail.thread', 'mail.activity.mixin']


    no = fields.Char(size=20,string="No.")
    dpe_date= fields.Date(string="DPE Date") 
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    
    qca = fields.Boolean(string="QC Analisa",default=False)
    qcp = fields.Boolean(string="QC Process",default=False)
    rnd = fields.Boolean(string="RnD",default=False)
    qa = fields.Boolean(string="QA Doc.",default=False)
    seasoning = fields.Boolean(string="Seasoning",default=False)
    ec = fields.Boolean(string="Empty Can",default=False)
    packing = fields.Boolean(string="Packing",default=False)
    seamer = fields.Boolean(string="Seamer",default=False)
    retort= fields.Boolean(string="Retort",default=False)
    wh = fields.Boolean(string="WH",default=False)
    precl= fields.Boolean(string="Pre CL",default=False)
    cl = fields.Boolean(string="Cleaning",default=False)

    sj = fields.Float(string='SJ @ton',default=0)    
    yf = fields.Float(string='YF @ton',default=0)    
    yfb = fields.Float(string='YFB @ton',default=0)    
    ac = fields.Float(string='AC @ton',default=0)    
    sm = fields.Float(string='SM @ton',default=0)    
    tg = fields.Float(string='TG @ton',default=0)    
    loin = fields.Float(string='TOTAL LOIN' ,default=0)
    totalfish= fields.Float(string='TOTAL FISH',compute='_compute_totalfish')    
     
    sbo = fields.Float(string='SBO @kg',compute='_compute_oil')         
    sfo = fields.Float(string='SFO @kg',compute='_compute_oil')         
    olive = fields.Float(string='Olive @kg',compute='_compute_oil')    
    rapeseed = fields.Float(string='Rapeseed @kg',compute='_compute_oil')                  
    totaloil = fields.Float(string='TOTAL OIL',compute='_compute_totaloil')    
    totalfcl= fields.Float(string='TOTAL fcl',compute='_compute_totalfcl')    
         
    release_date= fields.Datetime(string="Release Time")  
    status = fields.Selection([('draft','Draft'),('released','RELEASED')],string="Status",default="draft")
    
    catatan= fields.Html(string="Catatan",default="1. <span style='color:red;'>Merah</span> : Product pakai ikan CC/PL<BR>"+\
               "2. <span style='color:blue;'>Biru</span> : Ganti produk dgn hari sebelumnya<BR>"+\
               "3. <span style='background-color:yellow;'>Kuning</span> : Produk baru / spek.baru / revisi<BR>"+\
               "4. <span style='background-color:lightgreen;'>Hijau</span> : Produksi hari terakhir untuk product tersebut<BR>")    


    check_access_button= fields.Boolean(compute='_check_access_button')  
    check_access_composition= fields.Boolean(compute='_check_access_composition')  
    check_access_qca= fields.Boolean(compute='_check_access_qca')  
    check_access_qcp= fields.Boolean(compute='_check_access_qcp')  
    check_access_rnd= fields.Boolean(compute='_check_access_rnd')  
    check_access_qa= fields.Boolean(compute='_check_access_qa')  
    check_access_ss= fields.Boolean(compute='_check_access_ss')  
    check_access_ec= fields.Boolean(compute='_check_access_ec')  
    check_access_pk= fields.Boolean(compute='_check_access_pk')  
    check_access_sm= fields.Boolean(compute='_check_access_sm')  
    check_access_rt= fields.Boolean(compute='_check_access_rt')  
    check_access_wh= fields.Boolean(compute='_check_access_wh')  
    check_access_precl= fields.Boolean(compute='_check_access_precl')  
    check_access_cl= fields.Boolean(compute='_check_access_cl')  
    
    detail_id = fields.One2many('sis.ppic.dpe.detail','header_id')     

    @api.constrains('dpe_date')
    def _constrains_dpe_date(self):
        for s in self:
            if self.env['sis.ppic.dpe'].search_count([('ati12','=',s.ati12),('dpe_date','=',s.dpe_date),('id','!=',s.id)])>0:
                raise UserError('Double DPE !')
    
    def add_detail(self):
        self.env['sis.ppic.dpe.detail'].create({'header_id':self.id})


    @api.depends('detail_id.oil','detail_id.qtyperuom','detail_id.itemno','detail_id.qtycase')
    def _compute_oil(self):
        sbo=0
        sfo=0
        olive=0
        rs=0
        for d in self.detail_id:
            if d.oil==0:
                continue
            pbs=self.env['sis.temp.production.bom'].search([('itemno','=',d.itemno),('variant','=',''),('lineitc','=','SS'),('linepgc','=','OIL')])
            if len(pbs)==0:
                continue
                raise UserError('There is Item in Plan without BoM')

            total=0
            for pb in pbs:
                if pb.lineitem=='SLA104' or pb.lineitem=='SMA102': #SFO
                    total+=pb.lineqty
                if pb.lineitem=='SLA101' or pb.lineitem=='SMA103' or pb.lineitem=='SMA101': #SBO
                    total+=pb.lineqty
                if pb.lineitem=='SMA104' or pb.lineitem=='SMA105' or pb.lineitem=='SMA106': #OLIVE
                    total+=pb.lineqty
                if pb.lineitem=='SMA109': #RAPESEED
                    total+=pb.lineqty

            for pb in pbs:
                if pb.lineitem=='SLA104' or pb.lineitem=='SMA102': #SFO
                    sfo+=pb.lineqty/total*d.oil*d.qtycase*d.qtyperuom
                if pb.lineitem=='SLA101' or pb.lineitem=='SMA103' or pb.lineitem=='SMA101': #SBO
                    sbo+=pb.lineqty/total*d.oil*d.qtycase*d.qtyperuom
                if pb.lineitem=='SMA104' or pb.lineitem=='SMA105' or pb.lineitem=='SMA106': #OLIVE
                    olive+=pb.lineqty/total*d.oil*d.qtycase*d.qtyperuom
                if pb.lineitem=='SMA109': #RAPESEED
                    rs+=pb.lineqty/total*d.oil*d.qtycase*d.qtyperuom
        self.sfo=sfo/1000
        self.sbo=sbo/1000
        self.olive=olive/1000
        self.rapeseed=rs/1000

    def make_excel(self):
#         sp = io.BytesIO()
        filename = ' DAILY PRODUCTION ESTIMATION '+datetime.now().strftime('%Y-%m-%d, %H:%M:%S')+'.xlsx'
        workbook = xlsxwriter.Workbook('/tmp/'+filename)
 
        # STYLE
        workbook.formats[0].set_font_size(9)
        workbook.formats[0].set_font_name('Arial')
        #################################################################################
        rtnoborder_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'right',
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        ctnoborder_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center',
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        ltnoborder_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left',
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        top_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'left',
            'border':0, 'font_name':'Arial', 'font_size':12})
        #################################################################################
        top_green_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center', 'text_wrap':1,
            'border':1, 'bg_color':'#9FE2BF','font_name':'Arial', 'font_size':9})
        #################################################################################
        blue_normal_style = workbook.add_format({'valign':'vcenter', 'border':1,
            'font_name':'Arial', 'bg_color':'#85C1E9','font_size':9})
        #################################################################################
        yellow_normal_style = workbook.add_format({'valign':'vcenter', 'border':1,
            'font_name':'Arial', 'bg_color':'yellow','font_size':9})
        #################################################################################
        lblue_normal_style = workbook.add_format({'valign':'vcenter', 'border':1,
            'font_name':'Arial', 'bg_color':'#AED6F1','font_size':9})
        #################################################################################
        normal_style = workbook.add_format({'valign':'vcenter', 'border':0,
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'font_size':9,'num_format': '#,##0.00'})
        #################################################################################
        yellow_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'bg_color':'yellow','font_size':9,'num_format': '#,##0.00'})
        #################################################################################
        green_nodec_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'bg_color':'#9FE2BF','font_size':9,'num_format': '#,##0'})
        #################################################################################
        red_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'font_color':'red','font_size':9,'num_format': '#,##0.00'})
        #################################################################################
        blue_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'font_color':'blue','font_size':9,'num_format': '#,##0.00'})
        #################################################################################
        yellow_red_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'bg_color':'yellow','font_color':'red','font_size':9,'num_format': '#,##0.00'})
        #################################################################################

        nodec_bnormal_style = workbook.add_format({'valign':'vcenter', 'border':1,'text_wrap':1,
            'font_name':'Arial', 'font_size':9,'num_format': '#,##0'})
        #################################################################################
        dec_normal_style = workbook.add_format({'valign':'vcenter', 'border':0,
            'font_name':'Arial', 'font_size':9,'num_format': '#,##0.00'})
        #################################################################################
        date_normal_style = workbook.add_format({'valign':'vcenter', 'border':1,
            'num_format': 'd/mmm/yy','font_name':'Arial', 'font_size':9 })
        #################################################################################
        bold_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'vcenter','border':1,
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        bolder_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'border':1,
            'font_name':'Arial', 'font_size':11})
        #################################################################################
        center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'font_size':9})
        #################################################################################
        date_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'num_format': 'd-mmm','font_size':9})
        #################################################################################
        red_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'font_color':'red','font_size':9})
        #################################################################################
        date_red_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'num_format': 'd-mmm','font_color':'red','font_size':9})
        #################################################################################

        blue_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'bg_color':'#85C1E9','font_size':9})
        #################################################################################
        lblue_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'bg_color':'#AED6F1','font_size':9})
        #################################################################################
        green_center_style = workbook.add_format({'valign':'vcenter', 'align':'center', 'border':1,
            'font_name':'Arial', 'bg_color':'#9FE2BF','font_size':9})
        #################################################################################
        b_center_style = workbook.add_format({'bold': 1, 'valign':'vcenter', 'align':'center',
            'border':1, 'font_name':'Arial', 'font_size':9})
        #################################################################################
        right_style = workbook.add_format({'valign':'vcenter', 'align':'right', 'border':1,
            'num_format': '###0.00', 'font_name':'Arial', 'font_size':9})
        #################################################################################
         
        worksheet = workbook.add_worksheet('Stuffing Plan')
     
        worksheet.set_column('A:AJ', 8.2)

        worksheet.write(0,0, 'DAILY PRODUCTION ESTIMATION ', top_style)
        worksheet.write(0,28, 'FORM.PIC.10.2021-03-01', normal_style)

        worksheet.write(1,0, (self.no or ''), top_style)

        worksheet.write(3,0, 'Date:', normal_style)
        worksheet.write(4,0, 'Printed:', normal_style)

        worksheet.write(3,1, self.dpe_date, normal_style)
        worksheet.write(4,1, datetime.now().strftime('%Y-%m-%d, %H:%M:%S'), normal_style)

        worksheet.write(1,8, 'SJ:', normal_style)
        worksheet.write(1,13, 'YF:', normal_style)
        worksheet.write(1,18, 'YFB:', normal_style)
        worksheet.write(1,27, 'Total FISH:', normal_style)
                
        worksheet.write(2,8, 'AC:', normal_style)
        worksheet.write(2,13, 'SM:', normal_style)
        worksheet.write(2,18, 'TG:', normal_style)
        worksheet.write(2,27, 'Total LOIN:', normal_style)

        worksheet.write(3,27, 'Total fcl:', normal_style)
        
        worksheet.write(4,8, 'SBO:', normal_style)
        worksheet.write(4,13, 'SFO:', normal_style)
        worksheet.write(4,18, 'OLIVE:', normal_style)
        worksheet.write(4,22, 'Rapeseed:', normal_style)
        worksheet.write(4,27, 'Total OIL:', normal_style)

        worksheet.write(1,10, 'ton', normal_style)
        worksheet.write(1,15, 'ton', normal_style)
        worksheet.write(1,20, 'ton', normal_style)
        worksheet.write(1,30, 'ton', normal_style)

        worksheet.write(2,10, 'ton', normal_style)
        worksheet.write(2,15, 'ton', normal_style)
        worksheet.write(2,20, 'ton', normal_style)
        worksheet.write(2,30, 'ton', normal_style)

        worksheet.write(1,9, self.sj or '', dec_normal_style)
        worksheet.write(1,14, self.yf or '', dec_normal_style)
        worksheet.write(1,19, self.yfb or '', dec_normal_style)
        worksheet.write(1,29, self.totalfish or '', dec_normal_style)
                
        worksheet.write(2,9, self.ac or '', dec_normal_style)
        worksheet.write(2,14, self.sm or '', dec_normal_style)
        worksheet.write(2,19, self.tg or '', dec_normal_style)
        worksheet.write(2,29, self.loin or '', dec_normal_style)
        
        worksheet.write(3,29, self.totalfcl or '', dec_normal_style)

        worksheet.write(4,9, self.sbo or '', dec_normal_style)
        worksheet.write(4,14, self.sfo or '', dec_normal_style)
        worksheet.write(4,19, self.olive or '', dec_normal_style)
        worksheet.write(4,24, self.rapeseed or '', dec_normal_style)
        worksheet.write(4,29, self.totaloil or '', dec_normal_style)

        worksheet.set_row(0,20)
        worksheet.set_row(1,20)
        worksheet.set_row(2,20)
        worksheet.set_row(3,20)
        worksheet.set_row(4,20)
        worksheet.set_row(5,35)

        worksheet.set_row(5,40)
        row=5
        worksheet.write(row, 0, 'LINE', top_green_style)            
        worksheet.merge_range(row, 1, row, 1+3,'PRODUCT', top_green_style)
        worksheet.merge_range(row, 5, row, 5+2,'BODY', top_green_style)
        worksheet.merge_range(row, 8, row, 8+2,'LID', top_green_style)        
        worksheet.write(row, 11, 'M', top_green_style)
        worksheet.write(row, 12, 'TOL.', top_green_style)
        worksheet.write(row, 13, 'O', top_green_style)        
        worksheet.merge_range(row, 14, row, 14+1,'REMARK OIL', top_green_style)        
        worksheet.write(row, 16, 'B', top_green_style)                                                
        worksheet.write(row, 17, 'VG', top_green_style)                                                
        worksheet.write(row, 18, 'BUMBU', top_green_style)                                                
        worksheet.write(row, 19, 'Topping', top_green_style)                                                        
        worksheet.write(row, 20, 'NW', top_green_style)                                                
        worksheet.write(row, 21, 'Target Kadar Garam', top_green_style)
        worksheet.write(row, 22, 'Qty', top_green_style)                                                
        worksheet.write(row, 23, 'Start', top_green_style)                                                
        worksheet.write(row, 24, 'Print on Body', top_green_style)                                                
        
        worksheet.merge_range(row, 25, row, 25+3,'REMARK', top_green_style)
#         worksheet.merge_range(row, 29, row, 29+1,'Format PKG', top_green_style)
        worksheet.write(row, 29, 'Format PKG', top_green_style)                                                

        worksheet.write(row, 30, 'Priority', top_green_style)                                                
        worksheet.merge_range(row, 31, row, 31+1,'No. Spec', top_green_style)
        worksheet.write(row, 33, 'Memo', top_green_style)                                                
        worksheet.write(row, 34, 'Target (fcl)', top_green_style)                                                

        row+=1
        for d in self.detail_id:
            worksheet.set_row(row,40)            
            worksheet.write(row, 0, d.line or '', bnormal_style)

            if d.baru and d.ccpl:
                worksheet.merge_range(row, 1, row, 1+3,d.product or '', yellow_red_bnormal_style)
            elif d.baru:
                worksheet.merge_range(row, 1, row, 1+3,d.product or '', yellow_bnormal_style)
            elif d.ccpl:
                worksheet.merge_range(row, 1, row, 1+3,d.product or '', red_bnormal_style)
            else:
                worksheet.merge_range(row, 1, row, 1+3,d.product or '', bnormal_style)
            
            if d.ganti:
                worksheet.merge_range(row, 5, row, 5+2,d.body or '', blue_bnormal_style)
                worksheet.merge_range(row, 8, row, 8+2,d.lid or '', blue_bnormal_style)
            else:
                worksheet.merge_range(row, 5, row, 5+2,d.body or '', bnormal_style)
                worksheet.merge_range(row, 8, row, 8+2,d.lid or '', bnormal_style)
                        
            worksheet.write(row, 11, d.meat or '', bnormal_style)
            worksheet.write(row, 12, d.toleransi or '', bnormal_style)
            worksheet.write(row, 13, d.oil or '', bnormal_style)        
            worksheet.merge_range(row, 14, row, 14+1,d.remark_oil or '', bnormal_style)        
            worksheet.write(row, 16, d.brine or '', bnormal_style)                                                
            worksheet.write(row, 17, d.vg or '', bnormal_style)                                                
            worksheet.write(row, 18, d.bumbu or '', bnormal_style)                                                
            worksheet.write(row, 19, d.topping or '', bnormal_style)                                                        
            worksheet.write(row, 20, d.nw or '', bnormal_style)                                                
            worksheet.write(row, 21, d.tkg or '', bnormal_style)
            if d.lastday:
                worksheet.write(row, 22, d.qtycase or '', green_nodec_bnormal_style)
            else:
                worksheet.write(row, 22, d.qtycase or '', nodec_bnormal_style)                                                
            jam=str(int(d.est_start))+':'+('0'+str(int((d.est_start-int(d.est_start))*60)))[-2:]
            worksheet.write(row, 23, jam or '', bnormal_style)                                                
            worksheet.write(row, 24, d.pbo or '', bnormal_style)                                                

            worksheet.merge_range(row, 25, row, 25+3,d.remark or '', bnormal_style)
#             worksheet.merge_range(row, 27, row, 27+3,d.formatpkg or '', bnormal_style)
            worksheet.write(row, 29, d.formatpkg or '', bnormal_style)                                                

            worksheet.write(row, 30, d.priority or '', bnormal_style)                                                
            worksheet.merge_range(row, 31, row, 31+1,d.spec_id.no_doc or '', bnormal_style)
            worksheet.write(row, 33, d.memo or '', bnormal_style)                              
            worksheet.write(row, 34, d.qtyfcl or '', bnormal_style)                              
            row+=1
 
        row+=1
        ftxt=self.catatan
        if ftxt:
            while len(ftxt)>0:
                i=ftxt.find('<br>')
                if i>-1:
                    txt=ftxt[:i]
                else:
                    txt=ftxt
                ftxt=ftxt[len(txt)+4:]
                txt=html2text.html2text(txt).strip()
                if len(txt)>0:
                    worksheet.merge_range(row, 0, row, 12,txt or '', normal_style)
                    row+=1            

        workbook.close()
        ids=self.env['sis.ppic.dpe.xls'].create({'report':base64.b64encode(open("/tmp/"+filename, "rb").read())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'contract',
            'url': '/web/content/sis.ppic.dpe.xls/%s/report/%s?download=true' %((ids.id),filename)
    
        }        

    def click_button(self):
        sec=self.env.context.get('check_user')
        if sec:
            if sec=='QCA':
                self.sudo().qca=True
            if sec=='RND':
                self.sudo().rnd=True
            if sec=='QCP':
                self.sudo().qcp=True
            if sec=='QA':
                self.sudo().qa=True
            if sec=='Seasoning':
                self.sudo().seasoning=True
            if sec=='EC':
                self.sudo().ec=True
            if sec=='Packing':
                self.sudo().packing=True
            if sec=='Seamer':
                self.sudo().seamer=True
            if sec=='Retort':
                self.sudo().retort=True
            if sec=='WH':
                self.sudo().wh=True
            if sec=='PreCL':
                self.sudo().precl=True
            if sec=='CL':
                self.sudo().cl=True

    
    def _compute_totalfish(self):
        for s in self:
            s.totalfish=s.sj+s.yf+s.yfb+s.ac+s.sm+s.tg

    def _compute_totaloil(self):
        for s in self:
            s.totaloil=s.sbo+s.sfo+s.olive+s.rapeseed

    @api.depends('detail_id.qtyfcl')
    def _compute_totalfcl(self):
        for s in self:
            fcl=0
            for d in s.detail_id:
                fcl+=d.qtyfcl
            s.totalfcl=fcl

    def release(self):
        for s in self:
            if s.status=='draft':
                s.status='released'
                s.release_date=datetime.now()
                users=""
                recs=self.env['res.groups'].search([('name','=','DPE / View')])
                for rec in recs:
                    for u in rec.users:
                        emps=self.env['hr.employee'].search([('user_id','=',u.id)])
                        for emp in emps:
                            if emp.work_email:
                                users=users+","+emp.work_email
                                
                        notification_ids = []
                        notification_ids.append((0,0,{
                        'res_partner_id':u.partner_id.id,
                        'notification_type':'inbox'}))
                        self.message_post(body='This receipt has been validated!', message_type='notification', author_id=self.env.user.partner_id.id, notification_ids=notification_ids)

                        
#                         self.env['mail.message'].create({'message_type':"notification",
#                                 "subtype": self.env.ref("mail.mt_comment").id,
#                                 'body': s.no+' Date '+s.dpe_date+' RELEASED ',
#                                 'subject': s.no+' Date '+s.dpe_date+' RELEASED ',
#                                 'needaction_partner_ids': [(4, u.partner_id.id)],
#                                 'model': self._name,
#                                 'res_id': self.id,
#                                 })                
                if len(users)>0:
                    users=users[1:]
                     
                    body="<HTML> <head> </head> <BR/><BR/>Regards,<BR/>No Reply</HTML>"
                    template_obj = self.env['mail.mail']
                    template_data = {
                                    'subject': s.no+' Date '+s.dpe_date+' RELEASED ',
                                    'body_html': body,
                                    'email_from': 'no-reply@ati.id',
                                    'email_to': users
                                    }
                    template_id = template_obj.create(template_data)
                    template_obj.send(template_id)                             

    def draft(self):
        for s in self:
            if s.status=='released':
                s.write({'status':'draft',
                         'qca':False,
                         'qcp':False,
                         'rnd':False,
                         'qa':False,
                         'seasoning':False,
                         'ec':False,
                         'packing':False,
                         'seamer':False,
                         'retort':False,
                         'wh':False,
                         'precl':False,
                         'cl':False})
    
    @api.multi
    def unlink(self):
        for s in self:
            if s.check_access_button==False:
                raise UserError('Cannot Delete')
            if s.status=='released':
                raise UserError('Cannot Delete !')
        return models.Model.unlink(self)

    @api.multi
    def write(self, vals):
        cont=True
        for v in vals:
            if v not in ['qca','qcp','qa','seasoning','ec','packing','seamer','retort','wh','precl','cl','rnd']:
                cont=False
        if self.check_access_button==False and not cont:
            raise UserError('Cannot Edit')
        return models.Model.write(self, vals)
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if self.env['sis.ppic.dpe'].search_count([('ati12','=',vals['ati12']),('dpe_date','=',vals['dpe_date'])])>0:
            raise UserError('Double DPE !')
        section,pabrik,dpe_view = self._get_section()
        user_dept=['PPIC']
        check_access_button=self.access_check(section,user_dept,'---')
        if check_access_button==False:
            raise UserError('Cannot Create')
        postingdate=datetime.now().strftime("%Y-%m-%d")
        no='DPE/'+vals['ati12'].upper()+'/'+postingdate[2:4]+postingdate[5:7]+'/'
        rec=self.env['sis.ppic.dpe'].search([('no','ilike',no)],limit=1,order='no desc')
        if len(rec)==0:
            seq='0001'
        else:
            seq=str(int(rec['no'][-4:])+1).zfill(4)
        no+=seq              
        vals.update({'no':no})
        return models.Model.create(self, vals)

    def get_data(self):
        if self.status=='released':
            raise UserError('Cannot get data if RELEASED')
        self.detail_id.write({'exist':False})
        SQL=" select ph.id,line_id,item_no, description,qtyperuom,t"+str(int(self.dpe_date[8:10]))+\
            " from sis_pps_header ph inner join sis_pps_detail pd on ph.id=pd.header_id and pd.type='production' "+\
            " where ph.month="+str(int(self.dpe_date[5:7]))+" and ph.year="+str(int(self.dpe_date[0:4]))+" and t"+str(int(self.dpe_date[8:10]))+">0 and ph.ati12='"+self.ati12+"'"
        conn = psycopg2.connect(
            host="localhost",
            database="PT_ATI",
            user="odoo",
            password=passwd)
        cur = conn.cursor()

        cur.execute(SQL)
        recs=cur.fetchall()
        for rec in recs:
            (phid,line,item_no,desc,qtyperuom,qty)=rec
            vals={'header_id':self.id}
            mitem=self.env['sis.pps.item'].search([('item_no','=',item_no),('ati12','=',self.ati12)])
            if len(mitem)==0:
                raise UserError("No SIS Master Item error for "+item_no)
            item=self.env['sis.items.local'].search([('itemno','=',item_no)])
            if item.qtyperfcl==0:
                raise UserError('Qty/fcl = 0 for '+item_no)
            if not item or len(item)!=1:
                raise UserError ('NAV Master Item error for '+item_no)            

            qtyperfcl=mitem.qtyperfcl
            if qtyperfcl==0:
                qtyperfcl=item.qtyperfcl
            
            caseitem=self.env['sis.pgc.case48'].search_count([('pgc','=',item.pgc)])
            if caseitem>0:
                qtyper=48
            else:
                qtyper=item.purchqtyperuom
            #CAN and POUCH
            pbs=self.env['sis.temp.production.bom'].search([('itemno','=',item_no),('variant','=',''),('lineitc','=','PKG'),'|',('linepgc','=','CAN'),('linepgc','=','POUCH')])
            if len(pbs)==0:
                continue
                raise UserError('There is Item in Plan without BoM')

            can=False
            lid=False
            for pb in pbs:
                if pb.linepgc=='CAN':
                    if pb.lineitem[:3]=='ELB' or pb.lineitem[:3]=='EMB':
                        if can:
                            q=self.env['sis.pps.material'].search([('header_id','=',phid),('item_no','=',pb.lineitem),('type','=','inventory')],limit=1)
                            if q['t'+str(int(self.dpe_date[8:10]))]<=0:
                                continue
                        if pb.lineitem[:3]=='ELB' :
                            vals.update({'body':pb.lineitem+':'+pb.linedesc})
                        else:
                            vals.update({'body':pb.lineitem+': '+pb.linedesc})
                        can=pb.lineitem                            
                    if pb.lineitem[:3]=='ELE' or pb.lineitem[:3]=='EME':
                        if lid:
                            q=self.env['sis.pps.material'].search([('header_id','=',phid),('item_no','=',pb.lineitem),('type','=','inventory')],limit=1)
                            if q['t'+str(int(self.dpe_date[8:10]))]<=0:
                                continue
                        if pb.lineitem[:3]=='ELE':
                            vals.update({'lid':pb.lineitem+': '+pb.linedesc})
                        else:
                            vals.update({'lid':pb.lineitem+': '+pb.linedesc})                            
                        lid=pb.lineitem                            
                else:
                    vals.update({'body':pb.lineitem+': '+pb.linedesc,
                                 'lid':''})
                    
            sps=self.env['sis.spec.prod'].search([('item_no','=',item_no),('spec_state','=','confirm')],order='id desc',limit=1)
            if len(sps)==1:
                vals.update({'spec_id':sps.id})

            vals.update({'line':line,
                  'itemno':item_no,
                  'product':desc,
                  'exist':True,
                  'qtycase':qty,
                  'qtyperuom':qtyper,
                  'qtyperfcl':qtyperfcl,
                  'qtyperuomsale':qtyperuom,
                  'factor':mitem.fclfactor})
            
            r=self.env['sis.ppic.dpe.detail'].search([('product','=',desc),('header_id','=',self.id)])
            if len(r)>0:
                r.write(vals)
            else:
                self.env['sis.ppic.dpe.detail'].create(vals)
        self.detail_id.filtered(lambda x:x.exist==False).unlink()

    def _get_section(self):
        xuid = self.env.uid
        cSQL1="select a.section_spec,a.dpe_view_only,a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_section=self.env.cr.fetchall()
        
        xsection_spec="NOT OK"
        dpe_view_only=False
        for def_section in rc_section:
            (xsection_spec,dpe_view_only,pabrik)=def_section

        return xsection_spec,pabrik,dpe_view_only

    def access_check(self,section,user_dept,pabrik):
        if section == 'Admin':
            return True
        if section in user_dept and pabrik=='---':
            return True
       
        if section in user_dept and self.ati12.upper()==pabrik:
            return True
        else:
            return False

    def _check_access_rnd(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_rnd=False
            else:
                s.check_access_rnd=s.access_check(section,['RND'],pabrik)
    
    def _check_access_qca(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_qca=False
            else:
                if s.access_check(section,['QC'],pabrik):
                    s.check_access_qca=not(s.qca)

    def _check_access_qcp(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_qcp=False
            else:
                if s.access_check(section,['QC'],pabrik):
                    s.check_access_qcp=not(s.qcp)

    
    def _check_access_qa(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_qa=False
            else:
                s.check_access_qa=s.access_check(section,['QA'],pabrik)

    def _check_access_ss(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_ss=False
            else:
                s.check_access_ss=s.access_check(section,['Seasoning'],pabrik)

    def _check_access_ec(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_ec=False
            else:
                s.check_access_ec=s.access_check(section,['EC'],pabrik)

    def _check_access_pk(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_pk=False
            else:
                s.check_access_pk=s.access_check(section,['Packing'],pabrik)

    def _check_access_sm(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_sm=False
            else:
                s.check_access_sm=s.access_check(section,['Seamer'],pabrik)

    def _check_access_rt(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_rt=False
            else:
                s.check_access_rt=s.access_check(section,['Retort'],pabrik)

    def _check_access_wh(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_wh=False
            else:
                s.check_access_wh=s.access_check(section,['WH'],pabrik)

    def _check_access_precl(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_precl=False
            else:
                s.check_access_precl=s.access_check(section,['PreCL'],pabrik)

    def _check_access_cl(self):
        section,pabrik,dpe_view_only = self._get_section()
        for s in self:
            if dpe_view_only==True:
                s.check_access_cl=False
            else:
                s.check_access_cl=s.access_check(section,['CL'],pabrik)

    
    def _check_access_button(self):
        section,pabrik,dpe_view_only = self._get_section()
        user_dept=['PPIC']
        for s in self:
            s.check_access_button=s.access_check(section,user_dept,'---')

    def _check_access_composition(self):
        section,pabrik,dpe_view_only = self._get_section()
        user_dept=['SS','QA','QC','PPIC','Seasoning','Seamer','RND']
        for s in self:
            s.check_access_composition=s.access_check(section,user_dept,'---')

class sis_ppic_dpe_detail(models.Model):
    _name='sis.ppic.dpe.detail'
    _order='line'

    header_id=fields.Many2one('sis.ppic.dpe')
    status=fields.Selection(related='header_id.status')

    line = fields.Char(string="Line")
    itemno= fields.Char(string="itemno")
    product = fields.Char(string="Product")
    body = fields.Char(string="Body")
    lid = fields.Char(string="Lid")
    meat = fields.Float(string="Meat")
    toleransi= fields.Char(string="Toleransi")
    oil= fields.Float(string="Oil")
    remark_oil= fields.Char(string="Remark Oil")
    brine = fields.Float(string="Brine")
    vg = fields.Float(string="VG")
    bumbu = fields.Float(string="Bumbu")

    topping = fields.Char(string='Topping')    
    nw = fields.Float(string='NW',compute='_compute_nw')    
    tkg = fields.Float(string='Target Kadar Garam')    
    qtycase = fields.Integer(string='Qty')    
    est_start = fields.Float(string='Est.Start')    
    pbo = fields.Char(string='Print Body On')
    remark = fields.Char(string='Remark')    
    formatpkg= fields.Char(string='Format PKG')    
    priority = fields.Integer(string='Priority')
    spec_id=fields.Many2one('sis.spec.prod',string='No.Spec',domain=[('spec_state','=','confirm')])                
    memo= fields.Char(string='Memo')    
    qtyperfcl= fields.Integer(string='Qty per fcl')
    qtyperuom= fields.Integer(string='Qty per UoM')
    qtyperuomsale= fields.Integer(string='Qty per UoM Sale')
    qtyfcl = fields.Float(string='Qty in fcl',compute='_compute_qtyfcl')
    factor = fields.Float(string='Factor')

    spec= fields.Char(string="No.Spec",compute='_compute_spec',store=True)

    baru = fields.Boolean(string='Prod BARU/REV')
    ganti = fields.Boolean(string='GANTI dgn hr.sblm')
    ccpl = fields.Boolean(string='Ikan CC/PL')
    lastday = fields.Boolean(string='Hari Terakhir')

    exist= fields.Boolean(string='Ikan CC/PL',default=False)
            
    check_access_button= fields.Boolean(compute='_check_access_button')        
    check_access_composition= fields.Boolean(compute='_check_access_composition')        

    @api.depends('spec_id')
    def _compute_spec(self):
        for s in self:
            if s.spec_id.no_doc: 
                s.spec=s.spec_id.no_doc+' rev '+str(s.spec_id.no_rev)
            else:
                s.spec='-- not found --'

    
    @api.depends('meat','oil','brine','vg','bumbu','topping')
    def _compute_nw(self):
        for s in self:
            topping=0
            if s.topping and len(s.topping)>0:
                try:
                    topping=eval(s.topping)
                except Exception as e:
                    raise UserError(e)

                    raise UserError('Topping formula error !')

            s.nw=s.meat+s.oil+s.brine+s.vg+s.bumbu+topping

    def open_spec(self):
        sps=self.env['sis.spec.prod'].search([('item_no','=',self.itemno),('spec_state','=','confirm')],order='id desc',limit=1)
        if len(sps)==0:
            raise UserError('No Confirmed Product Specification, please contact RnD')
        return sps.view_spec()
#         return {
#             'name': 'Product specification',
#             'res_model': 'sis.spec.prod',
#             'type': 'ir.actions.act_window',
#             'context': {},
#             'view_mode': 'form',
#             'view_type': 'form',
#             'view_id': self.env.ref('sis_spec_product.sis_view_spec_prod').id,
#             'target': 'new',
#             'nodestroy':True,
#             'domain':"[('id','=',"+str(sps.id)+")]"
#         }
            
    @api.multi
    def unlink(self):
        for s in self:
            if s.check_access_button==False:
                raise UserError('Cannot Delete')
            if s.status=='released':
                raise UserError('Cannot Delete, status should be draft !')
        return models.Model.unlink(self)
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        for s in self:
            if s.check_access_button==False:
                raise UserError('Cannot Create')            
            if 'product' not in vals:
                raise UserError('')            
            if s.status=='released':
                raise UserError('Cannot Create, status should be draft !')  
        return models.Model.create(self, vals)
    
    @api.multi
    def write(self, vals):
        for s in self:
            if s.check_access_button==False:
                raise UserError('Cannot Edit')
            if s.status=='released':
                raise UserError('Cannot Edit, status should be draft !')
        return models.Model.write(self, vals)
    
    def _check_access_button(self):
        for s in self:
            s.check_access_button=s.header_id.check_access_button
        
    def _check_access_composition(self):
        for s in self:
            s.check_access_composition=s.header_id.check_access_composition
        
    def _compute_qtyfcl(self):
        for s in self:
            if s.qtyperfcl>0 and s.qtyperuom>0 and s.qtyperuomsale>0:
                s.qtyfcl=s.qtycase/(s.qtyperfcl*s.qtyperuomsale/s.qtyperuom)*s.factor
            else:
                s.qtyfcl=0
