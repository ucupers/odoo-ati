from odoo import models, fields, api
#from odoo.exceptions import UserError

class filter_item_bc(models.TransientModel):
    _name  ='sis.item.bc'
    _description = 'Master Item NAV for BC'
    _order = 'description'
    
    temp_id    = fields.Integer(string="ID")     
    description= fields.Char(string="Result", size=255, compute="_get_filter")
    item_line  = fields.One2many('sis.item.bc.line', 'rel_item', string='Master Item Line')

    def clear_data(self):
        self.env.cr.execute("update sis_report_filter_bc set item_no='' where id="+str(self.temp_id))

    @api.one
    def _get_filter(self):
        xfilter=""
        for xdetail in self.item_line:
            if xdetail.status_item==True:
                if xfilter=="":
                    xfilter=xdetail.item_no
                else:
                    xfilter += "|"+xdetail.item_no
         
        self.description=xfilter
        self.env.cr.execute("update sis_report_filter_bc set item_no='"+self.description+"' where id="+str(self.temp_id))
              
class filter_item_bc_line(models.TransientModel):
    _name  ='sis.item.bc.line'
    _description = 'Master Item NAV for BC (line)'
    _order = 'item_no'
    
    rel_item    = fields.Many2one('sis.item.bc', string="Master Item Lines", ondelete='cascade')
    temp_id     = fields.Integer(string="ID")     
    status_item = fields.Boolean(string="Set as Filter") 
    item_no     = fields.Char(string="Item No", size=20)
    description = fields.Char(string="Description", size=255)    