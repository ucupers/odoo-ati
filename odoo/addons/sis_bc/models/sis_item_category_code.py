from odoo import models, fields, api
#from odoo.exceptions import UserError

class item_category_bc(models.TransientModel):
    _name  ='sis.items.category.bc'
    _description = 'Master Item Category Code NAV for BC (Header)'
    
    temp_id             = fields.Integer(string="ID")     
    description         = fields.Char(string="Result", size=100, compute="_get_filter")
    item_category_line  = fields.One2many('sis.items.category.bc.line', 'rel_items_category', string='Item Category Line')

    def clear_data(self):
        self.env.cr.execute("update sis_report_filter_bc set item_category_code='' where id="+str(self.temp_id))

    @api.one
    def _get_filter(self):
        xfilter=""
#         xupdate=""
        for xdetail in self.item_category_line:
            if xdetail.status_itc==True:
                if xfilter.strip()=="":
                    xfilter=xdetail.description
                else:
                    xfilter=xfilter+"|"+xdetail.description
         
        self.description=xfilter
        p_group=self._update_product_group(xfilter)

        if p_group=="x?":
            p_group=""

        p_item=self._update_item(xfilter, p_group)
        
        if p_item=="x?":
            p_item=""
#             self.env.cr.execute("update sis_report_filter_bc set item_category_code='"+self.description+"', product_group_code='' where id="+str(self.temp_id))
#         else:
        self.env.cr.execute("update sis_report_filter_bc set item_category_code='"+self.description+"', product_group_code='"+p_group+\
                            "', item_no='"+p_item+"' where id="+str(self.temp_id))

    def _update_product_group(self, xcategory):
        if xcategory:            
            itc=""
            if xcategory.find("|")!=-1:
                koma=0
                for n in range(len(xcategory)):
                    if xcategory[n:n+1]=="|":
                        if itc.strip()=="":
                            itc= "'"+xcategory[koma:n].strip()+"'"
                        else:
                            itc += ", '"+xcategory[koma:n].strip()+"'"
                         
                        koma=n+1
                    else:
                        if n+1==len(xcategory):
                            itc += ", '"+xcategory[koma:koma+(len(xcategory)-koma)].strip()+"'"
            else:
                if itc.strip()=="":
                    itc = "'"+xcategory.strip()+"'"
 
            self.env.cr.execute("select distinct product_group_code from sis_items_bc where product_group_code<>'' "+\
                                "and item_category_code in ("+itc+") order by product_group_code")
        else:
            self.env.cr.execute("select distinct product_group_code from sis_items_bc where product_group_code<>'' "+\
                                "order by product_group_code")
             
        rec_pgc=self.env.cr.fetchall()
#        print(len(rec_pgc))
        p_group=""
        if len(rec_pgc)>0:
            for pgc_line in rec_pgc:
                (xpgc,)=pgc_line
                  
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.temp_id),('product_group_code','like',xpgc)])
                if len(rec_des)>0:
                    if p_group.strip()=="":
                        p_group=xpgc
                    else:
                        p_group +="|"+xpgc
                        
        if p_group=="":
            p_group="x?"
            
        return p_group

    def _update_item(self, xcategory, xgroup):
        xWhere=""
        itc=""
        if xcategory:            
            if xcategory.find("|")!=-1:
                koma=0
                for n in range(len(xcategory)):
                    if xcategory[n:n+1]=="|":
                        if itc.strip()=="":
                            itc= "'"+xcategory[koma:n].strip()+"'"
                        else:
                            itc += ", '"+xcategory[koma:n].strip()+"'"
                         
                        koma=n+1
                    else:
                        if n+1==len(xcategory):
                            itc += ", '"+xcategory[koma:koma+(len(xcategory)-koma)].strip()+"'"
            else:
                if itc.strip()=="":
                    itc = "'"+xcategory.strip()+"'"
        if itc!="":
            xWhere="where item_category_code in ("+itc+") "
 
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
            if xWhere=="":
                xWhere ="where product_group_code in ("+pgc+") "
            else:
                xWhere +="and product_group_code in ("+pgc+") "
 
        print(xWhere)        
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
              
class item_category_bc_line(models.TransientModel):
    _name  ='sis.items.category.bc.line'
    _description = 'Master Item Category Code NAV for BC (line)'
    _order = 'description'
    
    rel_items_category  = fields.Many2one('sis.items.category.bc', string="Item Category Lines", ondelete='cascade')
    temp_id             = fields.Integer(string="ID")     
    status_itc          = fields.Boolean(string="Set as Filter") 
    description         = fields.Char(string="Description", size=20)