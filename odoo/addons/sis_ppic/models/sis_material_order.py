from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pyodbc

class sis_pps_material_order(models.Model):
    _name='sis.pps.material.order'

    pono = fields.Char(size=20,string="PO No")
    posting_date = fields.Date(string="Date")
    purchasercode = fields.Char(size=20,string="Purchaser")
    bg = fields.Char(size=20,string="BG")
    line_no = fields.Char(size=20,string="Line No")
    item_no = fields.Char(size=20,string="Item No")
    description= fields.Char(size=200,string="Description")
    location_code = fields.Char(size=20,string="Location")
    estimated_time_departure = fields.Date(string="Estimated Time Departure")
    expected_receipt_date = fields.Date(string="Expc.Rcpt.Date\n/ETA Sby")
    expected_date = fields.Date(string="Expected Date")
    requested_receipt_date = fields.Date(string="Req.Rcpt.Date\n/ETA ATI")
    requested_date = fields.Date(string="Requested Date")
    date_warning = fields.Integer(compute="_compute_date_warning",String="Warning")
    remark = fields.Char(size=50,string="Remark")
    quantity = fields.Float(string="Qty")
    outstanding_quantity = fields.Float(string="Outstanding")
    uom = fields.Char(size=20,string="UoM")
    inupdate = fields.Boolean(string="In\nUpdate")
    demurrage_warning = fields.Integer(compute="_compute_demurrage_warning",String="Warning")
    itc = fields.Char(size=20,string="Item Cat.Cd")
    pgc = fields.Char(size=20,string="Prd.Grp.Cd")        
    purchasing_team=fields.Boolean(string='Purchasing Team',compute='_compute_purchasing_team')


    @api.one
    def _compute_purchasing_team(self):
        if self.env.user.login in ['stephanus@ati.id','etik@ati.id','mukhtar@ati.id','admin']:
            self.purchasing_team=True
            return True
        else:
            self.purchasing_team=False
            return False

    def _purchasing_team(self):
        if self.env.user.login in ['stephanus@ati.id','etik@ati.id','mukhtar@ati.id','admin']:
            return True
        else:
            return False

    
    @api.one
    def _compute_date_warning(self):
        if self.requested_receipt_date!=self.requested_date:
            self.date_warning=1
        else:
            self.date_warning=0

    @api.one
    def _compute_demurrage_warning(self):
        if self.requested_date and self.requested_receipt_date:
            if datetime.strptime(self.requested_date,'%Y-%m-%d')>datetime.strptime(self.requested_receipt_date,'%Y-%m-%d')+relativedelta(days=20):
                self.demurrage_warning=1
                return
        self.demurrage_warning=0

            
    def get_material_order(self):
        self.env.cr.execute("DROP TABLE IF EXISTS sis_purchase_order_mat")
        self.env.cr.execute("CREATE TEMP TABLE sis_purchase_order_mat AS SELECT * FROM sis_purchase_order; ")                

#        n=datetime.now()+relativedelta(months=4)
#        p=datetime.now()-relativedelta(months=1)
        now=datetime.now()-relativedelta(months=1)

        self.env.cr.execute("update sis_pps_material_order set inupdate=False ")
        self.env.cr.execute("select pono,posting_date,purchasercode,bg,line_no,item_no,description,location_code,expected_receipt_date,requested_receipt_date,estimated_time_departure,quantity,outstanding_quantity,uom,itc,pgc from sis_purchase_order_mat "+ \
                        " where itc in ('SS','PKG') "+\
                        #" and extract(year from requested_receipt_date)*100+extract(month from requested_receipt_date)>="+str(p.year*100+p.month)+\
                        #" and extract(year from requested_receipt_date)*100+extract(month from requested_receipt_date)<="+str(n.year*100+n.month))
                        " and (extract(year from requested_receipt_date)*100+extract(month from requested_receipt_date)>="+str(now.year*100+now.month)+\
                        " or (outstanding_quantity>0 and extract(year from requested_receipt_date)>2019) )")
        ordpos=self.env.cr.fetchall()

        for ordpo in ordpos:        
            (pono,posting_date,purchasercode,bg,line_no,item_no,description,location_code,expected_receipt_date,requested_receipt_date,estimated_time_departure,quantity,outstanding_quantity,uom,itc,pgc)=ordpo
  
            valsord={'pono':pono,
                     'posting_date':posting_date,
                     'purchasercode':purchasercode,
                     'bg':bg,
                     'line_no':line_no,
                     'item_no':item_no,
                     'description':description,
                     'location_code':location_code,
                     'estimated_time_departure':estimated_time_departure,
                     'expected_receipt_date':expected_receipt_date,
                     'expected_date':expected_receipt_date,
                     'requested_receipt_date':requested_receipt_date,
                     'requested_date':requested_receipt_date,
                     'quantity':quantity,
                     'outstanding_quantity':outstanding_quantity,
                     'uom':uom ,
                     'itc':itc,
                     'pgc':pgc,
                     'inupdate':True
                     }
            
            rec=self.env['sis.pps.material.order'].search([('pono','=',pono),('line_no','=',line_no)])
            if len(rec)==0:
                self.env['sis.pps.material.order'].create(valsord)
            else:
                if len(rec)==1:
                    rec.write(valsord)
                else:
                    raise ValidationError('Material Calc: Error in Order Data')
        pass

    def update_and_notif(self):

        conn = pyodbc.connect('Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+
                              'Server=10.0.0.12;'+
                              'Database=NAV (9-0) ATI LIVE;'+
                              'UID=Atidev;pwd=Ati1234;')
        cursor = conn.cursor()
        if self._purchasing_team():
            body="<HTML> <head> <style> table, th, td { border-collapse: collapse; border: 1px solid black; } </style> </head> Requested date change in : <BR/> "+\
                "<table border=""1""><tbody><tr><td>No.</td><td>PO Number</td><td>Line No.</td><td>Item No.</td><td>Description</td><td>Quantity</td><td>Outstanding Qty</td><td>UoM</td><td>Change To</td><td>Original</td><td>Remark</td></tr>"
        else:
            body="<HTML> <head> <style> table, th, td { border-collapse: collapse; border: 1px solid black; } </style> </head> Expected date change in : <BR/> "+\
                "<table border=""1""><tbody><tr><td>No.</td><td>PO Number</td><td>Line No.</td><td>Item No.</td><td>Description</td><td>Quantity</td><td>Outstanding Qty</td><td>UoM</td><td>Change To</td><td>Original</td><td>Remark</td></tr>"
        no=0
        recs=self.search([])
        if self._purchasing_team():
            for rec in recs:
                if rec.expected_receipt_date!=rec.expected_date:
                    rrd=rec.expected_receipt_date
                    if rec.expected_receipt_date==False or len(rec.expected_receipt_date)==0:
                        rrd='-'
                    if rec.remark==False or len(rec.remark)==0:
                        rem='-'                        
                    if rec.expected_date==False or len(rec.expected_date)==0:
                        raise UserError('Expected date cannot be empty !')
                    no+=1
                    body+="<tr><td>"+str(no)+"</td><td>"+rec.pono+"</td><td>"+str(rec.line_no)+"</td><td>"+rec.item_no+"</td><td>"+rec.description+"</td><td>"+str(rec.quantity)+"</td><td>"+str(rec.outstanding_quantity)+"</td><td>"+rec.uom+"</td><td>"+rec.expected_date+"</td><td>"+rrd+"</td><td>"+rem+"</td></tr>"
                    row=cursor.execute(" update [PT_ Aneka Tuna Indonesia$Purchase Line] set [Expected Receipt Date]='"+rec.expected_date+"' "+\
                                   " where [Document No_]='"+rec.pono+"' and [Line No_]="+str(rec.line_no)+" and [Document Type]='1'")
                    if row.rowcount==0:
                        raise UserError('Failed to update NAV, please try again later')                
        else:
            for rec in recs:
                if rec.requested_receipt_date!=rec.requested_date:
                    rrd=rec.requested_receipt_date
                    if rec.requested_receipt_date==False or len(rec.requested_receipt_date)==0:
                        rrd='-'
                    if rec.remark==False or len(rec.remark)==0:
                        rem='-'                        
                    if rec.requested_date==False or len(rec.requested_date)==0:
                        raise UserError('Request date cannot be empty !')
                    no+=1
                    body+="<tr><td>"+str(no)+"</td><td>"+rec.pono+"</td><td>"+str(rec.line_no)+"</td><td>"+rec.item_no+"</td><td>"+rec.description+"</td><td>"+str(rec.quantity)+"</td><td>"+str(rec.outstanding_quantity)+"</td><td>"+rec.uom+"</td><td>"+rec.requested_date+"</td><td>"+rrd+"</td><td>"+rem+"</td></tr>"
                    row=cursor.execute(" update [PT_ Aneka Tuna Indonesia$Purchase Line] set [Requested Receipt Date]='"+rec.requested_date+"' "+\
                                   " where [Document No_]='"+rec.pono+"' and [Line No_]="+str(rec.line_no)+" and [Document Type]='1'")
                    if row.rowcount==0:
                        raise UserError('Failed to update NAV, please try again later')                
        if no>0:
            conn.commit()
            if self._purchasing_team:
                tag='EXPECTED'
            else:
                tag='REQUESTED'                                
            body+="</tbody></table><BR/><BR/>Thank you<BR/>Note : No reply needed<BR/><BR/>"+\
            "Regards,<BR/>No Reply</HTML>"
            template_obj = self.env['mail.mail']
            template_data = {
                            'subject': tag+' Receipt Date change at '+(datetime.now()+timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S'),
                            'body_html': body,
                            'email_from': 'no-reply@ati.id',
                            'email_to': 'stephanus@ati.id, etik@ati.id, mukhtar@ati.id, iswatul@ati.id, siti@ati.id, hamim@ati.id'
                            }
            template_id = template_obj.create(template_data)
            template_obj.send(template_id)
        self.get_material_order()
            