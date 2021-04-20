from odoo import models, fields,api

class sis_ile_analysis_local(models.Model):
    _name='sis.ile.analysis.local'
    _rec_name='description'
        
    posting_date=fields.Date(string='Posting date', readonly=True)
    item_no=fields.Char(size=20,string="Item No.",readonly=True)
    description=fields.Char(size=200,string="Description",readonly=True)
    itemdesc=fields.Char(size=200,string="No+Description",readonly=True)    
    variant=fields.Char(size=20,string="Variant",readonly=True)
    itc=fields.Char(size=20,string="Item Cat.",readonly=True)
    pgc=fields.Char(size=20,string="Product Grp.",readonly=True)
    location_code=fields.Char(size=20,string="Location",readonly=True)
    qtyperuom=fields.Float(string="Qty/UoM",readonly=True)
    uom=fields.Char(size=30,string="UoM",readonly=True)
    entrytype=fields.Char(size=30,string="Entry Type",readonly=True)
    quantity=fields.Float(string="Qty",readonly=True)
    remaining_quantity=fields.Float(string="Remaining Qty",readonly=True)        
    bg=fields.Char(size=20,string="BG",readonly=True)

    def copy_data_from_NAV(self):
        self.env.cr.execute("delete from sis_ile_analysis_local")
        self.env.cr.execute("insert into sis_ile_analysis_local(id,posting_date,itemdesc,item_no,description,variant,itc,pgc,location_code,qtyperuom,uom,entrytype,quantity,remaining_quantity,bg) "+\
                            "select id,posting_date,concat(item_no,':',description,' @',uom),item_no,description,variant,itc,pgc,location_code,qtyperuom,uom,entrytype,quantity,remaining_quantity,bg "+\
                            "from sis_ile")
    