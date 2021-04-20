from odoo import models, fields, api
#from odoo.exceptions import UserError

class report_filter_bc(models.Model):
    _name        = 'sis.report.filter.bc'
    _description = 'Master filter for BC'
    _order       = "rpt_name, factory_code, location_code"
    
    rpt_name            = fields.Char(string="Laporan", size=200)
    item_no             = fields.Char(string="Item No.", size=255)
    description_2       = fields.Char(string="Description 2 (NAV)", size=100)
    item_category_code  = fields.Char(string="Item Category Code", size=100)
#     itc                 = fields.Char(string="Item Category Code", size=100)
    product_group_code  = fields.Char(string="Product Group Code", size=100)
    location_code       = fields.Char(string="Location Code", size=200)
    factory_code        = fields.Selection([('1','ATI1'),('2','ATI2'),('3','None')], string='Factory', default='3')
    wip_bc              = fields.Selection([('False','False'),('True','True')], string='WIP BC')
    inc_bk              = fields.Boolean(string="Include Buku Kuning", default=False)
    bisnis_group        = fields.Boolean(string="Bisnis Group", default=False)
    set_active          = fields.Boolean(string="Active")
#    item_category_line  = fields.One2many('sis.items.category.bc', 'rel_items_category', string='Item Category Line')
#    product_group_line  = fields.One2many('sis.product.group.bc', 'rel_product_group', string='Product Group Line')
#    report_id           = fields.One2many('sis.report.inv.bc', 'rel_report_id', string='Report ID')

    @api.one
    def _get_itc(self):
        xitc=""
        for xdetail in self.item_category_line:
            if xdetail.status_itc:
                if xitc.strip()=="":
                    xitc=xdetail.description.strip()
                else:
                    xitc=xitc+"|"+xdetail.description.strip()
         
        self.item_category_code=xitc
#         self.itc=xitc
    
    def add_category_code(self):
        self.env.cr.execute("delete from sis_items_category_bc where temp_id="+str(self.id))
        self.env.cr.execute("delete from sis_items_category_bc_line where temp_id="+str(self.id))
         
        self.env.cr.execute("select distinct item_category_code from sis_items_bc where item_category_code<>'' order by item_category_code")
        rec_itc=self.env.cr.fetchall()
        if len(rec_itc)>0:
            head_id=0
            itc_head = {
                'temp_id'       : self.id,
                'description'   : ''
                }
            self.env['sis.items.category.bc'].create(itc_head)

            rec=self.env['sis.items.category.bc'].search([('temp_id','=',self.id)])
            if len(rec)>0:
                for xfield in rec:
                    head_id=xfield.id
 
            for itc_line in rec_itc:
                (xitc,)=itc_line
                
                status_itc=False
                    
#=================Cara Manual
#                xItem_Category_Code=""
#                 if self.item_category_code.find("|")!=-1:
#                     koma=0
#                     for n in range(len(self.item_category_code)):
#                         if self.item_category_code[n:n+1]=="|":
#                             xItem_Category_Code=self.item_category_code[koma:n].strip()
#                             koma=n+1
#                         else:
#                             if n+1==len(self.item_category_code):
#                                 xItem_Category_Code =self.item_category_code[koma:koma+(len(self.item_category_code)-koma)].strip()
#             
#                         if xitc==xItem_Category_Code:
#                             status_itc=True
#                             break
#                 else:
#                     if xitc==self.item_category_code:
#                         status_itc=True

#==============Cara Ringkas
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.id),('item_category_code','like',xitc)])
                if len(rec_des)>0:
                    status_itc=True
                                  
                itc_vals = {
                    'rel_items_category'    : head_id,
                    'temp_id'               : self.id,
                    'status_itc'            : status_itc,
                    'description'           : xitc
                    }
                 
                self.env['sis.items.category.bc.line'].create(itc_vals)
        
            return {
                'name'      : 'Item Category Code',
                'res_model' : 'sis.items.category.bc',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_bc_items_category').id,
                'nodestroy' : False,
                'target'    : 'new',
                'res_id'    : head_id,
                'domain'    : [('temp_id','=',self.id)],      
                'flags'     : {'action_buttons': True}
            }
    
    def add_product_group(self):
        self.env.cr.execute("delete from sis_product_group_bc where temp_id="+str(self.id))
        self.env.cr.execute("delete from sis_product_group_bc_line where temp_id="+str(self.id))

        if self.item_category_code:            
            itc=""
            if self.item_category_code.find("|")!=-1:
                koma=0
                for n in range(len(self.item_category_code)):
                    if self.item_category_code[n:n+1]=="|":
                        if itc.strip()=="":
                            itc= "'"+self.item_category_code[koma:n].strip()+"'"
                        else:
                            itc += ", '"+self.item_category_code[koma:n].strip()+"'"
 
                        koma=n+1
                    else:
                        if n+1==len(self.item_category_code):
                            itc += ", '"+self.item_category_code[koma:koma+(len(self.item_category_code)-koma)].strip()+"'"
            else:
                if itc.strip()=="":
                    itc = "'"+self.item_category_code.strip()+"'"

            self.env.cr.execute("select distinct product_group_code from sis_items_bc where product_group_code<>'' "+\
                                "and item_category_code in ("+itc+") order by product_group_code")
#            self.env.cr.execute("select pgc from sis_bc_product_group where pgc<>'' "+\
#                                "and itc in ("+itc+") order by pgc")
        else:
            self.env.cr.execute("select distinct product_group_code from sis_items_bc where product_group_code<>'' "+\
                                "order by product_group_code")
#            self.env.cr.execute("select pgc from sis_bc_product_group where pgc<>'' order by pgc")

        rec_pgc=self.env.cr.fetchall()
        if len(rec_pgc)>0:
            head_id=0
            pgc_head = {
                'temp_id'       : self.id,
                'description'   : ''
                }
            self.env['sis.product.group.bc'].create(pgc_head)
 
            rec=self.env['sis.product.group.bc'].search([('temp_id','=',self.id)])
            if len(rec)>0:
                for xfield in rec:
                    head_id=xfield.id
  
            for pgc_line in rec_pgc:
                (xpgc,)=pgc_line
                 
                status_pgc=False
 
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.id),('product_group_code','like',xpgc)])
                if len(rec_des)>0:
                    status_pgc=True
                                   
                pgc_vals = {
                    'rel_product_group'     : head_id,
                    'temp_id'               : self.id,
                    'status_pg'            : status_pgc,
                    'description'           : xpgc
                    }
                  
                self.env['sis.product.group.bc.line'].create(pgc_vals)
         
            return {
                'name'      : 'Product Group Code',
                'res_model' : 'sis.product.group.bc',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_bc_product_group').id,
                'nodestroy' : False,
                'target'    : 'new',
                'res_id'    : head_id,
                'domain'    : [('temp_id','=',self.id)],      
                'flags'     : {'action_buttons': True}
            }
    
    def add_location_code(self):
        self.env.cr.execute("delete from sis_location_bc where temp_id="+str(self.id))
        self.env.cr.execute("delete from sis_location_bc_line where temp_id="+str(self.id))

        self.env.cr.execute("select distinct location_code from sis_ile_odoo_bc where location_code<>'' and location_code not "+\
                            "like '%INTRAN%' order by location_code")
        
        rec_itc=self.env.cr.fetchall()
        if len(rec_itc)>0:
            head_id=0
            loc_head = {
                'temp_id'       : self.id,
                'description'   : ''
                }
            self.env['sis.location.bc'].create(loc_head)

            rec=self.env['sis.location.bc'].search([('temp_id','=',self.id)])
            if len(rec)>0:
                for xfield in rec:
                    head_id=xfield.id
 
            for itc_line in rec_itc:
                (xlocation,)=itc_line
                
                status_location=False
                    
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.id),('location_code','like',xlocation)])
                if len(rec_des)>0:
                    status_location=True
                                  
                loc_vals = {
                    'rel_location'    : head_id,
                    'temp_id'         : self.id,
                    'status_location' : status_location,
                    'description'     : xlocation
                    }
                 
                self.env['sis.location.bc.line'].create(loc_vals)
         
            return {
                'name'      : 'Location Code',
                'res_model' : 'sis.location.bc',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_bc_location').id,
                'nodestroy' : False,
                'target'    : 'new',
                'res_id'    : head_id,
                'domain'    : [('temp_id','=',self.id)],      
                'flags'     : {'action_buttons': True}
            }
            
    def add_item_no(self):
        self.env.cr.execute("delete from sis_item_bc where temp_id="+str(self.id))
        self.env.cr.execute("delete from sis_item_bc_line where temp_id="+str(self.id))
        
        xWhere=""
        itc=""
        if self.item_category_code:            
            if self.item_category_code.find("|")!=-1:
                koma=0
                for n in range(len(self.item_category_code)):
                    if self.item_category_code[n:n+1]=="|":
                        if itc.strip()=="":
                            itc= "'"+self.item_category_code[koma:n].strip()+"'"
                        else:
                            itc += ", '"+self.item_category_code[koma:n].strip()+"'"
                        
                        koma=n+1
                    else:
                        if n+1==len(self.item_category_code):
                            itc += ", '"+self.item_category_code[koma:koma+(len(self.item_category_code)-koma)].strip()+"'"
            else:
                if itc.strip()=="":
                    itc = "'"+self.item_category_code.strip()+"'"
        if itc!="":
            xWhere=" item_category_code in ("+itc+") "

        pgc=""
        if self.product_group_code:            
            if self.product_group_code.find("|")!=-1:
                koma=0
                for n in range(len(self.product_group_code)):
                    if self.product_group_code[n:n+1]=="|":
                        if pgc.strip()=="":
                            pgc= "'"+self.product_group_code[koma:n].strip()+"'"
                        else:
                            pgc += ", '"+self.product_group_code[koma:n].strip()+"'"
                        
                        koma=n+1
                    else:
                        if n+1==len(self.product_group_code):
                            pgc += ", '"+self.product_group_code[koma:koma+(len(self.product_group_code)-koma)].strip()+"'"
            else:
                if pgc.strip()=="":
                    pgc = "'"+self.product_group_code.strip()+"'"

        if pgc!="":
            if xWhere=="":
                xWhere=" product_group_code in ("+pgc+") "
            else:
                xWhere +=" and product_group_code in ("+pgc+") "
        
        xWhere=" where "+xWhere

        self.env.cr.execute("select distinct item_no_, description_3 from sis_items_bc "+xWhere+"order by item_no_")
        print(xWhere)
            
        rec_itm=self.env.cr.fetchall()
        if len(rec_itm)>0:
            head_id=0
            itm_head = {
                'temp_id'       : self.id,
                'description'   : ''
                }
            self.env['sis.item.bc'].create(itm_head)
 
            rec=self.env['sis.item.bc'].search([('temp_id','=',self.id)])
            if len(rec)>0:
                for xfield in rec:
                    head_id=xfield.id
  
            for itm_line in rec_itm:
                (xitem_no,xdescription)=itm_line
                 
                status_itm=False
 
                rec_des=self.env['sis.report.filter.bc'].search([('id','=',self.id),('item_no','like',xitem_no)])
                if len(rec_des)>0:
                    status_itm=True
                                   
                itm_vals = {
                    'rel_item'      : head_id,
                    'temp_id'       : self.id,
                    'status_item'   : status_itm,
                    'item_no'       : xitem_no,
                    'description'   : xdescription 
                    }
                  
                self.env['sis.item.bc.line'].create(itm_vals)
         
            return {
                'name'      : 'Master Item',
                'res_model' : 'sis.item.bc',
                'type'      : 'ir.actions.act_window',
                'view_mode' : 'form',
                'view_type' : 'form',
                'view_id'   : self.env.ref('sis_bc.sis_bc_item').id,
                'nodestroy' : False,
                'target'    : 'new',
                'res_id'    : head_id,
                'domain'    : [('temp_id','=',self.id)],      
                'flags'     : {'action_buttons': True}
            }
            
    
