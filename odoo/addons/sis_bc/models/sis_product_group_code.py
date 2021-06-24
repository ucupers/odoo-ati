from odoo import models, fields, api
#from odoo.exceptions import UserError

class product_group_bc(models.TransientModel):
    _name  ='sis.product.group.bc'
    _description = 'Master Product Group Code NAV for BC'
    _order = 'description'
    
    temp_id             = fields.Integer(string="ID")     
    description         = fields.Char(string="Result", size=100, compute="_get_filter")
    product_group_line  = fields.One2many('sis.product.group.bc.line', 'rel_product_group', string='Product Group Line')

    @api.one
    def _get_filter(self):
        xfilter=""
        for xdetail in self.product_group_line:
            if xdetail.status_pg==True:
                if xfilter.strip()=="":
                    xfilter=xdetail.description
                else:
                    xfilter=xfilter+"|"+xdetail.description
         
#         self.description=xfilter
#         self.env.cr.execute("update sis_report_filter_bc set product_group_code='"+self.description+"' where id="+str(self.temp_id))

        self.description=xfilter
        p_item=self._update_item(xfilter)
        
        if p_item=="x?":
            p_item=""
#             self.env.cr.execute("update sis_report_filter_bc set item_category_code='"+self.description+"', product_group_code='' where id="+str(self.temp_id))
#         else:
        self.env.cr.execute("update sis_report_filter_bc set product_group_code='"+self.description+"', item_no='"+p_item+"' where id="+str(self.temp_id))
        
    def _update_item(self, xgroup):
        xWhere=""
        pgc=""
        if xgroup:            
            if xgroup.find("|")!=-1:
                koma=0
                for n in range(len(xgroup)):
                    if xgroup[n:n+1]=="|":
                        if pgc.strip()=="":
                            pgc= "'"+xgroup[koma:n].strip()+"'"
                        else:
                            pgc += ", '"+xgroup[koma:n].strip()+"'"
                         
                        koma=n+1
                    else:
                        if n+1==len(xgroup):
                            pgc += ", '"+xgroup[koma:koma+(len(xgroup)-koma)].strip()+"'"
            else:
                if pgc.strip()=="":
                    pgc = "'"+xgroup.strip()+"'"
 
        if pgc!="":
            xWhere ="where product_group_code in ("+pgc+") "
 
        self.env.cr.execute("select distinct item_no_ from sis_items_bc "+xWhere+"order by item_no_")
             
        rec_itm=self.env.cr.fetchall()
        p_item=""
        if len(rec_itm)>0:
            for itm_line in rec_itm:
                (xitm,)=itm_line
                   
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.temp_id),('item_no','like',xitm)])
                if len(rec_des)>0:
                    if p_item.strip()=="":
                        p_item=xitm
                    else:
                        p_item +="|"+xitm
                         
        if p_item=="":
            p_item="x?"
             
        return p_item
              
class product_group_bc_line(models.TransientModel):
    _name  ='sis.product.group.bc.line'
    _description = 'Master Product Group Code NAV for BC (line)'
    _order = 'description'
    
    rel_product_group   = fields.Many2one('sis.product.group.bc', string="Product Group Lines", ondelete='cascade')
    temp_id             = fields.Integer(string="ID")     
    status_pg           = fields.Boolean(string="Set as Filter") 
    description         = fields.Char(string="Description", size=20)
    
    
    