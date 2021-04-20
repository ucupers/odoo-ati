from odoo import models, fields, api, _
from odoo.exceptions import UserError

    
class sis_budomari(models.Model):
    _name='sis.budomari'
    _order='year desc,month desc,ati12,fish'    

    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    fish = fields.Char(size=20,string="Kind of Fish",required=True)
    budomari = fields.Float(string="Budomari %",required=True)
  
class sis_line_capacity(models.Model):
    _name='sis.line.capacity'
    _order='year desc,month desc,ati12'    

    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    line = fields.Char(size=10,string="Line",required=True)
    capacity = fields.Float(string="Capacity",required=True)

class sis_clean_capacity(models.Model):
    _name='sis.clean.capacity'
    _order='year desc,month desc,ati12'    
    
    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    capacity = fields.Float(string="Capacity(KG)/day",required=True)

class sis_pgc_case48(models.Model):
    _name='sis.pgc.case48'

    pgc = fields.Char(size=5,string="Item Case 48",required=True)

class sis_pps_option(models.Model):
    _name='sis.pps.option'

    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    montothu = fields.Float(string="Mon-Thu hours/day",required=True)
    fri = fields.Float(string="Fri hours/day",required=True)
    sat = fields.Float(string="Sat hours/day",required=True)


class sis_pps_exhour(models.Model):
    _name='sis.pps.exhour'
    _order='workdate desc'    
    
    workdate=fields.Date(string="Date", required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    hours = fields.Float(string="# hours/day",required=True)
    
class sis_pps_line(models.Model):
    _name='sis.pps.line'

    name=fields.Char(size=10,string='Line',required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    line1 = fields.Char(size=5,string="Line#1",required=True)
    line2 = fields.Char(size=5,string="Line#2")
    line3 = fields.Char(size=5,string="Line#3") 
    line4 = fields.Char(size=5,string="Line#4")
    line5 = fields.Char(size=5,string="Line#5")
    linenum=fields.Integer(compute='_compute_linenum',string='Line Num')
    
    
    @api.constrains('name')
    def _constrain_name(self):
        if self.env['sis.pps.line'].search_count([('name','=',self.name),('id','!=',self.id)])!=0:
            raise UserError('Duplicate Name !')
    
    @api.one
    @api.depends('line1','line2','line3','line4','line5')
    def _compute_linenum(self):
        num=0
        if self.line1 and self.line1!='':
            num+=1
        if self.line2 and self.line2!='':
            num+=1
        if self.line3 and self.line3!='':
            num+=1
        if self.line4 and self.line4!='':
            num+=1
        if self.line5 and self.line5!='':
            num+=1
        self.linenum=num

class sis_pps_item(models.Model):
    _name='sis.pps.item'
    _rec_name='line'

    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    item_no = fields.Char(size=20,string="Item No.")
    description = fields.Char(compute='_compute_item',size=200,string="Description",store=True)
    line = fields.Char(size=20,string='Def.Line')#Many2one('sis.pps.line',string=' Def.Line',required=True)
    capacity= fields.Float(string="Cap.case/Line/Hour")     
    altline = fields.Char(size=20,string='Alt.Line')#Many2one('sis.pps.line',string=' Def.Line',required=True)
    altcapacity= fields.Float(string="Alt Cap.cs/Line/Hr")     
    #fz = fields.Char(size=10,string='Frozen')
    fz = fields.Selection([('ACS DC','ACS DC'),('SJS SC','SJS SC'),('SJS DC','SJS DC'),('SJP DC','SJP DC'),('YFS SC','YFS SC'),('YFS DC','YFS DC'),('YFP DC','YFP DC')],string="Frozen")
    fzcode = fields.Char(size=10,string='Fz NAV Code')
    #fishmaterial= fields.Char(size=10,string='Fish Material')
    fishmaterial=fields.Selection([('SJS','SJS'),('SJP','SJP'),('YFS','YFS'),('YFP','YFP'),('SM','SM'),('AC','AC'),('BT','BT'),('TG','TG')],string="Fish Material")
    fzsign = fields.Char(size=10,string='Fz NAV Remark Sign')    
    fzpercent= fields.Float(string="% FZ")
    priority=fields.Integer(string="Priority FZ Use")     
    fclfactor= fields.Float(string="FCL factor", default=1)
    bepercent= fields.Float(string="%YFB")
    qtyperfcl= fields.Float(string="QTY per FCL")

    def update_from_nav_item(self):
        rs=self.env['sis.items'].search([('itc','=','FG')])
        for r in rs:
            for ati in ['ati1','ati2']:
                item=self.env['sis.pps.item'].search_count([('item_no','=',r.itemno),('ati12','=',ati)])
                if item==1:
                    continue                
                if item>1:                
                    raise UserError('Double item '+r.itemno+ 'in SIS Master Item')
                self.env['sis.pps.item'].create({ 'ati12':ati, 'item_no':r.itemno})

    @api.one
    @api.depends('item_no')
    def _compute_item(self):
        rs=self.env['sis.items'].search([('itemno','=',self.item_no)])
        if len(rs)==1:
            if rs.ensure_one():
                self.description=rs.description
            else:
                raise UserError('Error in NAV Item Master')

#     @api.one
#     @api.constrains('fishmaterial')
#     def _constrains_fishmaterial(self):
#         rs=self.env['sis.items'].search([('itemno','=',self.item_no)])
#         if rs and len(rs)==1:
#             if rs.itc=='FG':
#                 if self.fishmaterial == False or self.fishmaterial =='':
#                     raise UserError('Please fill Fish Material for FG item')                
#         else:
#             raise UserError('Item code does not exist in NAV')

    @api.one
    @api.constrains('fz','fzpercent')
    def _constrains_frozen(self):
        if self.priority!=0:
            if self.fz==False or self.fz=='' or self.fzpercent==0:
                raise UserError('Please fill Forzen and PZ Percent if item has priority')                

 
#     @api.one
#     @api.constrains('fzcode')
#     def _constrains_fzcode(self):
#         rs=self.env['sis.items'].search([('itemno','=',self.item_no),('fishmaterial','=',self.fzcode)])
#         if rs and len(rs)==1:
#             pass
#         else:
#             raise UserError('Error in Frozen Loin Code, Please cross check with NAV data')

class sis_pps_packingline(models.Model):
    _name='sis.pps.packingline'
    _rec_name='line'
    _order='ati12,line'    

    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    line = fields.Char(size=20,string='Packing Line',required=True)#Many2one('sis.pps.line',string=' Def.Line',required=True)
    linenum = fields.Integer(compute='_compute_linenum',string='Line num')

    @api.one
    @api.depends('line')
    def _compute_linenum(self):
        if self.line:        
            self.linenum=len(self.line.split(','))
            
            
class sis_num_work_days(models.Model):
    _name='sis.pps.num.work.days'
    _order='year desc,month desc'    

    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    num_work_days= fields.Integer(string="Num Work Days",required=True)            