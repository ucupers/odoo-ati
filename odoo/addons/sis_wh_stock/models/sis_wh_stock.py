from odoo import models, fields,api

class sis_fgstock_remaining_quantity(models.Model):
    _name='sis.fgstock.remaining.quantity'
    _table='sis_fgstock_remaining_quantity'
    _auto=False

    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(size=20,string="Document No",readonly=True)
    gitem_no =fields.Char(size=20,string="Global Item No",readonly=True) 
    gdescription =fields.Char(size=200,string="Global Description",readonly=True)
    item_no =fields.Char(size=20,string="Item No",readonly=True) 
    description =fields.Char(size=200,string="Description",readonly=True)
    category =fields.Char(size=20,string="Category",readonly=True)
    location_code =fields.Char(size=20,string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    entry_type =fields.Char(size=30,string="Entry Type",readonly=True)    
    lot_no =fields.Char(size=20,string="Lot No",readonly=True)
    lot_prod_date =fields.Char(size=20,string="Lot Production Date",readonly=True)
    lot_prod_month =fields.Char(size=20,string="Lot Production Month",readonly=True)
    no_contract =fields.Char(size=20,string="No Contract",readonly=True)
    inkjet_print =fields.Char(size=250,string="Inkjet Print",readonly=True)    
    uom_code=fields.Char(size=20,string="UoM Code",readonly=True)
    qty_per_unit =fields.Char(size=20,string="Qty per UoM",readonly=True)
    qty_per_fcl =fields.Char(size=20,string="Qty per FCL",readonly=True)                
    labeled_unlabeled=fields.Char(size=20,string="Labeled/Unlabeled",readonly=True)
    qty_in_unit = fields.Float(string='Qty in UoM',readonly=True)
    qty_in_fcl = fields.Float(string='Qty in FCL',readonly=True)    
    prodqty_in_unit = fields.Float(string='Prod Qty in UoM',readonly=True)
    prodqty_in_fcl = fields.Float(string='Prod Qty in FCL',readonly=True)    
    prodqty_per_fcl =fields.Char(size=30,string="Prod Qty per FCL",readonly=True)                
    produom_code=fields.Char(size=30,string="Prod UoM Code",readonly=True)

#     @api.model
#     def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
#         res = models.Model.read_group(self, domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
#         if 'qty_in_unit' in fields:
#             for line in res:
#                 if '__domain' in line:
#                     lines = self.search(line['__domain'])
#                     total = 0.0
#                     qty_per_uom=0
#                     for current in lines:
#                         total += current.remaining_quantity
#                         qty_per_uom=current.qty_per_unit
#                     line['qty_in_unit'] = (total // qty_per_uom) + (total % qty_per_uom / 100)

class sis_fgstock_remaining_quantity_local(models.Model):
    _name='sis.fgstock.remaining.quantity.local'

    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(size=20,string="Document No",readonly=True)
    gitem_no =fields.Char(size=20,string="Global Item No",readonly=True) 
    gdescription =fields.Char(size=200,string="Global Description",readonly=True)
    item_no =fields.Char(size=20,string="Item No",readonly=True) 
    description =fields.Char(size=200,string="Description",readonly=True)
    category =fields.Char(size=20,string="Category",readonly=True)
    location_code =fields.Char(size=20,string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    entry_type =fields.Char(size=30,string="Entry Type",readonly=True)    
    lot_no =fields.Char(size=40,string="Lot No",readonly=True)
    lot_prod_date =fields.Char(size=20,string="Lot Production Date",readonly=True)
    lot_prod_month =fields.Char(size=20,string="Lot Production Month",readonly=True)
    no_contract =fields.Char(size=20,string="No Contract",readonly=True)
    inkjet_print =fields.Char(size=250,string="Inkjet Print",readonly=True)    
    uom_code=fields.Char(size=20,string="UoM Code",readonly=True)
    qty_per_unit =fields.Char(size=20,string="Qty per UoM",readonly=True)
    qty_per_fcl =fields.Char(size=20,string="Qty per FCL",readonly=True)                
    labeled_unlabeled=fields.Char(size=30,string="Labeled/Unlabeled",readonly=True)
    qty_in_unit = fields.Float(string='Qty in UoM',readonly=True)
    qty_in_fcl = fields.Float(string='Qty in FCL',readonly=True)
    prodqty_in_unit = fields.Float(string='Prod Qty in UoM',readonly=True)
    prodqty_in_fcl = fields.Float(string='Prod Qty in FCL',readonly=True)     
    prodqty_per_fcl =fields.Char(size=30,string="Prod Qty per FCL",readonly=True)                
    produom_code=fields.Char(size=30,string="Prod UoM Code",readonly=True)

        
#     @api.model
#     def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
#         res = models.Model.read_group(self, domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
#         if 'qty_in_unit' in fields:
#             for line in res:
#                 if '__domain' in line:
#                     lines = self.search(line['__domain'])
#                     total = 0.0
#                     qty_per_uom=0
#                     for current in lines:
#                         total += current.remaining_quantity
#                         qty_per_uom=current.qty_per_unit
#                     line['qty_in_unit'] = (total // qty_per_uom) + (total % qty_per_uom / 100)
    @api.one
    def _compute_qty_in_unit(self):
        #satuan  = self.remaining_quantity//self.qty_per_unit
        #pecahan = self.remaining_quantity%self.qty_per_unit
        #self.qty_in_unit = satuan + pecahan/100
        self.qty_in_unit = self.remaining_quantity/self.qty_per_unit

    @api.one
    def _compute_qty_in_fcl(self):
        if self.qty_per_fcl>0:
            self.qty_in_fcl = self.qty_in_unit / self.qty_per_fcl
            
    def copy_data_from_NAV(self):
        self.env.cr.execute("delete from sis_fgstock_remaining_quantity_local")
        self.env.cr.execute("insert into sis_fgstock_remaining_quantity_local(id,posting_date,document_no,gitem_no,gdescription,item_no,description,category,location_code,quantity,remaining_quantity,entry_type, prodqty_in_unit, prodqty_in_fcl, "+\
                            "lot_no,lot_prod_date,lot_prod_month,no_contract,inkjet_print,uom_code,qty_per_unit,qty_per_fcl,labeled_unlabeled,qty_in_unit,qty_in_fcl, produom_code, prodqty_per_fcl) "+\
                            "select id,posting_date,document_no,gitem_no,gdescription,item_no,description,category,location_code,quantity,remaining_quantity,entry_type,prodqty_in_unit, prodqty_in_fcl, "+\
                            "lot_no,lot_prod_date,lot_prod_month,no_contract,inkjet_print,uom_code,qty_per_unit,qty_per_fcl,labeled_unlabeled,qty_in_unit,qty_in_fcl, produom_code, prodqty_per_fcl "+\
                            "from sis_fgstock_remaining_quantity")
    