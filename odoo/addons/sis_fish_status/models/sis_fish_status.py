from odoo import models, fields, api
from odoo.exceptions import UserError

class sis_fish_status(models.Model):
    _name='sis.fish.status'
    _table='sis_fish_status'
    _auto=False
    _rec_name='barcode_no'

    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    vessel_no = fields.Char(size=100,string="Histamin",readonly=True)
    hatch_no = fields.Char(size=100,string="Histamin",readonly=True)
    voyage_no = fields.Char(size=100,string="Histamin",readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    barcode_no = fields.Char(size=40,string="Barcode No",readonly=True)
    lot_no = fields.Char(size=40,string="Lot No",readonly=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)
    real_item_no = fields.Char(size=20,string="Real Item No",readonly=True)
    product_group_code = fields.Char(size=2, string="Product Group Code",readonly=True)

class sis_fish_fresh_inv(models.Model):
    _name='sis.fish.fresh.inv'
    _table='sis_fish_fresh_inv'
    _auto=False

    entry_types = fields.Char(size=30,string="Entry Types",readonly=True)
    document_type = fields.Integer(string="Document Type",readonly=True)
    document_no = fields.Char(size=19,string="Document No.",readonly=True)
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    item_no_mix = fields.Char(size=20,string="Item No. Mix",readonly=True)
    lot_no = fields.Char(size=40,string="Lot No",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No.",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No.",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No.",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    lokasi = fields.Char(size=4,string="Lokasi",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    fish_box_no = fields.Char(size=20,string="Fish Box No",readonly=True)
    purchase_document_no = fields.Char(size=15,string="Purchase Document No.",readonly=True)
    invoice_no = fields.Char(size=50,string="Invoice No",readonly=True)
    real_item_no = fields.Char(size=20,string="Real Item No",readonly=True)
    product_group_code = fields.Char(size=2, string="Product Group Code",readonly=True)
        
class sis_nav_fish_status(models.Model):
    _name='sis.nav.fish.status'
    _table='sis_nav_fish_status'
    _auto=False

    pgc = fields.Char(size=20,string="Product Grp",readonly=True)    
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    posting_date = fields.Date(string="Posting Date", readonly=True)
    ps= fields.Char(size=30,string="P/S Type",readonly=True)
    entry_type= fields.Char(size=30,string="Entry Type",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    location_code = fields.Char(size=10,string="Location Code",readonly=True)
    bg = fields.Char(size=10,string="Business Group",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)

class sis_nav_fish_status_local(models.Model):
    _name='sis.nav.fish.status.local'

    pgc = fields.Char(size=20,string="Product Grp",readonly=True)    
    item_no = fields.Char(size=20,string="Item No.",readonly=True)
    description= fields.Char(size=100,string="Description",readonly=True)
    posting_date = fields.Date(string="Posting Date", readonly=True)
    ps= fields.Char(size=30,string="P/S Type",readonly=True)
    entry_type= fields.Char(size=30,string="Entry Type",readonly=True)
    vessel_no = fields.Char(size=100,string="Vessel No",readonly=True)
    hatch_no = fields.Char(size=100,string="Hatch No",readonly=True)
    voyage_no = fields.Char(size=100,string="Voyage No",readonly=True)
    quantity = fields.Float(string='Quantity', readonly=True)
    remaining_quantity = fields.Float(string='Remaining Quantity', readonly=True)
    location_code = fields.Char(size=10,string="Location Code",readonly=True)
    bg = fields.Char(size=10,string="Business Group",readonly=True)
    status = fields.Char(size=10,string="Status",readonly=True)
    status_analisa = fields.Char(size=10,string="Status Analisa",readonly=True)
    status_process = fields.Char(size=10,string="Status Process",readonly=True)
    histamin = fields.Char(size=100,string="Histamin",readonly=True)
    kadar_garam = fields.Char(size=100,string="Kadar Garam",readonly=True)
    orange_meat = fields.Char(size=100,string="Orange Meat",readonly=True)
    blackspot = fields.Char(size=100,string="Blackspot",readonly=True)
    pemakaian = fields.Char(size=100,string="Pemakaian karena Kasus Khusus",readonly=True)
    kontaminasi = fields.Char(size=100,string="Kontaminasi",readonly=True)
    lain2_analisa = fields.Char(size=100,string="Lain2 Analisa",readonly=True)
    lain2_process = fields.Char(size=100,string="Lain2 Process",readonly=True)
    remark_analisa = fields.Char(size=100,string="Remark Analisa",readonly=True)
    remark_process = fields.Char(size=100,string="Remark Process",readonly=True)

    def upload_from_NAV(self):
        self.env.cr.execute("delete from sis_nav_fish_status_local")
        self.env.cr.execute(" insert into sis_nav_fish_status_local(pgc,item_no,description,posting_date,ps,entry_type,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,location_code, "+\
                            " bg,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process, "+\
                            " remark_analisa,remark_process ) "+\
                            " select pgc,item_no,description,posting_date,ps,entry_type,vessel_no,hatch_no,voyage_no,quantity,remaining_quantity,location_code, "+\
                            " bg,status,status_analisa,status_process,histamin,kadar_garam,orange_meat,blackspot,pemakaian,kontaminasi,lain2_analisa,lain2_process, "+\
                            " remark_analisa,remark_process from sis_nav_fish_status ")

    
class sis_fish_status_history(models.Model):
    _name='sis.fish.status.history'
    _rec_name='lot_no'

    link_id = fields.Many2one('sis.fish.status', string="Barcode No", required=True)
    item_no = fields.Char(compute='update_history',size=20,string="Item No.",store=True)
    description= fields.Char(compute='update_history',size=100,string="Description",store=True)
    vessel_no = fields.Char(compute='update_history',size=100,string="Vessel No.",store=True)
    hatch_no = fields.Char(compute='update_history',size=100,string="Hatch No.",store=True)
    voyage_no = fields.Char(compute='update_history',size=100,string="Voyage No.",store=True)
    remaining_quantity = fields.Float(compute='update_history',string='Remaining Quantity',store=True)
    barcode_no = fields.Char(compute='update_history',size=40,string="Barcode No",store=True)
    lot_no = fields.Char(compute='update_history',size=40,string="Lot No",store=True)
    status = fields.Char(compute='update_history',size=10,string="Status",store=True)
    status_analisa = fields.Char(compute='update_history',size=10,string="Status Analisa",store=True)
    status_process = fields.Char(compute='update_history',size=10,string="Status Process",store=True)
    histamin = fields.Char(compute='update_history',size=100,string="Histamin",store=True)
    kadar_garam = fields.Char(compute='update_history',size=100,string="Kadar Garam",store=True)
    orange_meat = fields.Char(compute='update_history',size=100,string="Orange Meat",store=True)
    blackspot = fields.Char(compute='update_history',size=100,string="Blackspot",store=True)
    pemakaian = fields.Char(compute='update_history',size=100,string="Pemakaian karena Kasus Khusus",store=True)
    kontaminasi = fields.Char(compute='update_history',size=100,string="Kontaminasi",store=True)
    lain2_analisa = fields.Char(compute='update_history',size=100,string="Lain2 Analisa",store=True)
    lain2_process = fields.Char(compute='update_history',size=100,string="Lain2 Process",store=True)
    remark_analisa = fields.Char(compute='update_history',size=100,string="Remark Analisa",store=True)
    remark_process = fields.Char(compute='update_history',size=100,string="Remark Process",store=True)
  
    @api.one
    @api.depends('link_id')
    def update_history(self):
        self.item_no = self.link_id.item_no
        self.description= self.link_id.description
        self.vessel_no = self.link_id.vessel_no
        self.hatch_no = self.link_id.hatch_no
        self.voyage_no = self.link_id.voyage_no
        self.remaining_quantity = self.link_id.remaining_quantity
        self.barcode_no = self.link_id.barcode_no
        self.lot_no = self.link_id.lot_no
        self.status = self.link_id.status
        self.status_analisa = self.link_id.status_analisa
        self.status_process = self.link_id.status_process
        self.histamin = self.link_id.histamin
        self.kadar_garam = self.link_id.kadar_garam
        self.orange_meat = self.link_id.orange_meat
        self.blackspot = self.link_id.blackspot
        self.pemakaian = self.link_id.pemakaian
        self.kontaminasi = self.link_id.kontaminasi
        self.lain2_analisa = self.link_id.lain2_analisa
        self.lain2_process = self.link_id.lain2_process
        self.remark_analisa = self.link_id.remark_analisa
        self.remark_process = self.link_id.remark_process

    
    @api.multi
    def unlink(self):
        raise UserError('Cannot delete!')
    
    @api.multi
    def write(self, vals):
        raise UserError('Cannot update!')        