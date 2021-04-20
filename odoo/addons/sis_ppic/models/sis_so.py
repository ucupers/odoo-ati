from odoo import models, fields, api, _
from odoo.exceptions import UserError

    
class sis_so_header(models.Model):
    _name='sis.so.header'
    _table='sis_so_header'
    _auto=False

    no = fields.Char(size=20,string="SO No.",readonly=True)
    selltono = fields.Char(size=20,string="Sell-to No.",readonly=True)
    selltono = fields.Char(size=20,string="Sell-to No.",readonly=True)
    selltoname = fields.Char(size=200,string="Sell-to Name",readonly=True)    
    shiptoname = fields.Char(size=200,string="Ship-to Name",readonly=True)
    postingdate = fields.Date(string="Posting Date",readonly=True)
    itemrequireddate = fields.Date(string="Item Required Date",readonly=True)
    extdocno = fields.Char(size=40,string="Ext.Doc.No.",readonly=True)
    salesperson_code = fields.Char(string="Salesperson Code",readonly=True)
    discharging_port = fields.Char(size=200,string="Discharging Port",readonly=True)
    bg = fields.Char(size=5,string="Buss.Grp",readonly=True)
    whshipno = fields.Char(size=20,string="WH Ship No",readonly=True)
    currfactor= fields.Float(string="Curr Factor",readonly=True)

    detail_id=fields.One2many('sis.so.detail','header_id')
   
  
class sis_so_detail(models.Model):
    _name='sis.so.detail'
    _table='sis_so_detail'
    _auto=False
    
    header_id=fields.Many2one('sis.so.header',string='Header')
   
    docno = fields.Char(size=20,string="Doc No.",readonly=True)
    lineno = fields.Char(size=20,string="Line No.",readonly=True)
    itemno = fields.Char(size=20,string="Item No.",readonly=True)
    description = fields.Char(size=200,string="Description",readonly=True) 
    quantity = fields.Float(string="Quantity",readonly=True)
    qtyperuom = fields.Float(string="Qty/UoM",readonly=True)
    uom = fields.Char(size=20,string="UoM",readonly=True)
    qtybase = fields.Float(string="Qty Base",readonly=True)
    unitprice = fields.Float(string="Unit Price",readonly=True)

    itemnoun = fields.Char(size=20,string="Item No. Unlabeled",readonly=True)
    descriptionun = fields.Char(size=200,string="Description Unlabeled",readonly=True)
    quantity48 = fields.Float(string="Quantity/case48",readonly=True)
    
        
    itc = fields.Char(size=40,string="Item Cat.Code",readonly=True)
    pgc = fields.Char(size=20,string="Prod.Grp.Code",readonly=True)
    
    
class sis_so_buffer(models.Model):
    _name='sis.pps.so.buffer'

    itemrequireddate = fields.Date(string="Item Required Date", required=True)
    selltoname = fields.Char(size=50,string="Sell-to Name",required=True)    
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
   
    itm = fields.Many2one('sis.items.local',string='Item',domain=[('itc','=','FG')],required=True)
    variant_code = fields.Many2one('sis.item.variants.local', string='Variant')
    variant = fields.Char(related='variant_code.variant',string="Variant",store=True)
    itemno = fields.Char(related='itm.itemno',string="Item No.",store=True)
    description = fields.Char(compute='_compute_item',string="Description",store=True) 
    qtyperuom = fields.Float(compute='_compute_item',string="Qty/UoM",store=True)
    uom = fields.Char(compute='_compute_item',string="UoM",store=True)
    itc = fields.Char(related='itm.itc',string="Item Cat.Code",store=True)
    pgc = fields.Char(related='itm.pgc',string="Prod.Grp.Code",store=True)  
    uitemno = fields.Char(compute='_compute_uitemno',string="Unlabeled Item No.",store=True)     

    quantity = fields.Float(string="Quantity",required=True)
    quantity48 = fields.Float(compute="_compute_quantity48",string="Quantity/case48",store=True)
    month=fields.Integer(compute='_compute_month_year',string='Month',store=True)
    year=fields.Integer(compute='_compute_month_year',string='Year',store=True)
        
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        i=self.env['sis.items.local'].search([('id','=',vals['itm'])])        
        if not i or len(i)!=1:
            raise UserError('Error in Item Master')

        if vals['variant_code']:
            v=self.env['sis.item.variants.local'].search([('id','=',vals['variant_code'])])
            if not v or len(v)!=1:
                if len(i.refitem)>0:
                    raise UserError('Data Error in Variant ')                            
                raise UserError('Error in Variant Master')

            iv=self.env['sis.item.variants.local'].search([('itemno','=',i.itemno),('variant','=',v.variant)])
            if not iv or len(iv)!=1:
                if len(i.refitem)>0:
                    raise UserError('Error in Item Variant Master')

            if vals['variant_code']!=iv.id:
                vals.update({'variant_code':iv.id})
        return models.Model.create(self, vals)
        
    @api.one
    @api.depends('itm')
    def _compute_uitemno(self):
        if self.itm.refitem and len(self.itm.refitem)>0:
            self.uitemno=self.itm.refitem
        else:
            self.uitemno=self.itemno
    
    @api.one
    @api.depends('itm','variant_code')
    def _compute_item(self):
        if self.variant_code and len(self.variant_code)>0:
            self.description=self.variant_code.description
            self.qtyperuom=self.variant_code.qtyperuom
            self.uom=self.variant_code.uom
        else:
            self.description=self.itm.description
            self.qtyperuom=self.itm.qtyperuom
            self.uom=self.itm.salesuom
            
        
    @api.onchange('itm')
    def _onchange_variant(self):
        varr = self.env['sis.item.variants'].search([('itemno', '=', self.itm.itemno)]).ids
        return {
            'domain': {
                'variant_code': [('id', 'in', varr)]
                }} 


    @api.one
    @api.depends('itemrequireddate')
    def _compute_month_year(self):
        self.month=int(self.itemrequireddate[5:7])
        self.year=int(self.itemrequireddate[:4])

    @api.one
    @api.depends('itm','variant_code')
    def _compute_quantity48(self):
        self.quantity48=self.quantity*self.qtyperuom/48