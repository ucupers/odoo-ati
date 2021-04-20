from odoo import models, fields, api
#from odoo.exceptions import UserError

class location_code_bc(models.TransientModel):
    _name  ='sis.location.bc'
    _description = 'Master Location Code NAV for BC'
    _order = 'description'
    
    temp_id        = fields.Integer(string="ID")     
    description    = fields.Char(string="Result", size=100, compute="_get_filter")
    location_line  = fields.One2many('sis.location.bc.line', 'rel_location', string='Location Line')

    def clear_data(self):
        self.env.cr.execute("update sis_report_filter_bc set location_code='' where id="+str(self.temp_id))

    @api.one
    def _get_filter(self):
        xfilter=""
        for xdetail in self.location_line:
            if xdetail.status_location==True:
                if xfilter.strip()=="":
                    xfilter=xdetail.description
                else:
                    xfilter=xfilter+"|"+xdetail.description
         
        self.description=xfilter
        self.env.cr.execute("update sis_report_filter_bc set location_code='"+self.description+"' where id="+str(self.temp_id))
              
class location_code_bc_line(models.TransientModel):
    _name  ='sis.location.bc.line'
    _description = 'Master Locaton Code NAV for BC (line)'
    _order = 'description'
    
    rel_location    = fields.Many2one('sis.location.bc', string="Location Lines", ondelete='cascade')
    temp_id         = fields.Integer(string="ID")     
    status_location = fields.Boolean(string="Set as Filter") 
    description     = fields.Char(string="Description", size=20)