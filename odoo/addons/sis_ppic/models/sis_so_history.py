from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import timedelta, datetime

    
class sis_pps_so_history(models.Model):
    _name='sis.pps.so.history'

    header_id=fields.Many2one('sis.pps.detail',string="Header")

    no = fields.Char(size=20,string="SO No.")
    selltono = fields.Char(size=20,string="Sell-to No.")
    selltoname = fields.Char(size=200,string="Sell-to Name")    
    shiptoname = fields.Char(size=200,string="Ship-to Name")
    postingdate = fields.Date(string="Posting Date")
    itemrequireddate = fields.Date(string="Item Required Date")
    extdocno = fields.Char(size=40,string="Ext.Doc.No.")
    bg = fields.Char(size=5,string="BG")
    lineno = fields.Char(size=20,string="Line No.")
    itemno = fields.Char(size=20,string="Item No.")
    description = fields.Char(size=200,string="_______________Item________________")
    variant = fields.Char(size=20,string="Variant")
    quantity = fields.Float(string="Quantity")
    qtyperuom = fields.Float(string="Qty/UoM")
    uom = fields.Char(size=20,string="__UoM__")
    qtyppic = fields.Float(string="Qty PPIC")    
    uomppic = fields.Char(size=20,string="UoM PPIC")
    qtyperuomppic = fields.Float(string="Qty/UoM PPIC")
    whshipno = fields.Char(size=20,string="Wh.Ship No")
    
    ati1qty = fields.Float(string='ATI1 Qty')
    ati1qtyppic = fields.Float(string='ATI1 Qty PPIC')
    ati1date = fields.Date(string='ATI1 Date')
    ati2qty = fields.Float(string='ATI2 Qty')
    ati2qtyppic = fields.Float(string='ATI2 Qty PPIC')
    ati2date = fields.Date(string='ATI2 Date')
    remark = fields.Char(size=200,string="Remark")
        
    existnav = fields.Boolean(string="in NAV")
    
    curr_id=fields.Many2one('sis.pps.so.current', string='Current ID')
    changetime=fields.Datetime(string='Change Time')
    changetimeUTC7=fields.Datetime(compute='_compute_changetimeUTC7',string='Change Time')

    @api.one
    @api.depends('changetime')
    def _compute_changetimeUTC7(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        changetime = datetime.strptime(self.changetime, DATETIME_FORMAT)
        self.changetimeUTC7=changetime+timedelta(hours=7)

    @api.multi
    def unlink(self):
        raise UserError('Cannot Delete !')
        return models.Model.unlink(self)

class sis_pps_so_current(models.Model):
    _name='sis.pps.so.current'

    header_id=fields.Many2one('sis.pps.detail',string="Header")

    no = fields.Char(size=20,string="SO No.")
    selltono = fields.Char(size=20,string="Sell-to No.")
    selltoname = fields.Char(size=200,string="Sell-to Name")    
    shiptoname = fields.Char(size=200,string="Ship-to Name")
    postingdate = fields.Date(string="Posting Date")
    itemrequireddate = fields.Date(string="Item Required Date")
    extdocno = fields.Char(size=40,string="Ext.Doc.No.")
    bg = fields.Char(size=5,string="BG")
    lineno = fields.Char(size=20,string="Line No.")
    itemno = fields.Char(size=20,string="Item No.")
    description = fields.Char(size=200,string="_______________Item________________")
    variant = fields.Char(size=20,string="Variant")
    quantity = fields.Float(string="Qty Sales")
    qtyperuom = fields.Float(string="Qty/UoM Sales")
    qtyperuomppic = fields.Float(string="Qty/UoM PPIC")
    uom = fields.Char(size=20,string="UoM Sales")
    qtyppic = fields.Float(compute='compute_qtyppic',string="Qty PPIC")    
    uomppic = fields.Char(size=20,string="UoM PPIC")
    whshipno = fields.Char(size=20,string="Wh.Ship No")

    ati1qty = fields.Float(compute='compute_qty1sales',string='ATI1 Qty Sales')
    ati1qtyppic = fields.Float(string='ATI1 Qty')
    ati1date = fields.Date(string='ATI1 Date')
    ati2qty = fields.Float(compute='compute_qty2sales',string='ATI2 Qty Sales')
    ati2qtyppic = fields.Float(string='ATI2 Qty')
    ati2date = fields.Date(string='ATI2 Date')
    remark = fields.Char(size=200,string="Remark")
    
    existnav = fields.Boolean(string="in Update")
    fbg = fields.Boolean(compute="_compute_fbg",string="Buss.Grp")    

    changetimeUTC7=fields.Datetime(compute='_compute_changetimeUTC7',string='Change Time')

    @api.one
    @api.depends('write_date')
    def _compute_changetimeUTC7(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        changetime = datetime.strptime(self.write_date, DATETIME_FORMAT)
        self.changetimeUTC7=changetime+timedelta(hours=7)
    
    @api.depends('bg')
    def _compute_fbg(self):
        for s in self:
            if s.bg=='':
                s.fbg=False
            else:
                s.fbg=True
    
    def open_historyview(self): 
        if self.variant:
            variant=self.variant
        else:
            variant=''
        return {
            'name': self.description + ' - '+variant,
            'res_model': 'sis.pps.so.history',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_so_history_tree').id,
            'target': 'new',
            'nodestroy':True,
            'domain':"[('curr_id','=',"+str(self.id)+")]"
        }
        
    @api.multi
    def unlink(self):
        raise UserError('Cannot Delete !')
        return models.Model.unlink(self)
    
    @api.one
    @api.depends('ati1qtyppic')
    def compute_qty1sales(self):
        self.ati1qty=self.ati1qtyppic*self.qtyperuomppic/self.qtyperuom
        
    @api.one
    @api.depends('ati2qtyppic')
    def compute_qty2sales(self):
        self.ati2qty=self.ati2qtyppic*self.qtyperuomppic/self.qtyperuom
        
    @api.one    
    @api.depends('quantity')
    def compute_qtyppic(self):
        if self.qtyperuomppic!=0:
            self.qtyppic=self.quantity*self.qtyperuom/self.qtyperuomppic
        
        