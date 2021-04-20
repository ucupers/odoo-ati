from odoo import models, fields, api
from odoo.exceptions import UserError

class cutting_tangki(models.Model):
    _name       ='sis.cutting.tangki'
    _rec_name   = 'no_tangki'
    
    rel_cutting = fields.Many2one('sis.cutting', string="Tangki")
    rel_defrost = fields.Many2one('sis.defrost.detail', string="No. Tangki", required=True)
#     label      = fields.One2many('sis.cutting.basket.label', 'rel_tangki_label', string='Tangki')
    tgl_produksi= fields.Date(string="Tanggal Produksi")
    location    = fields.Char(size=4, string='Lokasi')
    no_potong   = fields.Integer(string='No Potong')
    no_tangki   = fields.Char(string="No. Tangki", related="rel_defrost.no_tangki", store=True)
    kindoffish  = fields.Char(string="Jenis Ikan", compute="_jenisikan", store=True)
    size        = fields.Char(string="Ukuran", compute="_size", store=True)
    vessel      = fields.Char(string="Vessel", compute="_vessel", store=True)
    voyage      = fields.Char(string="Voyage", compute="_voyage", store=True)
    hatch       = fields.Char(string="Hatch", compute="_hatch", store=True)
    status_pl   = fields.Boolean(string="Pole & Line", compute="_update_hatch", store=True)

    @api.onchange('tgl_produksi')
    def filter_defrost_tangki(self):
        domain = []
        domain.append(('tgl_produksi','=',self.tgl_produksi))
        domain.append(('no_potong','=',self.no_potong))
        domain.append(('pabrik_id','=',self.location))
        domain.append(('no_tangki','!=','-'))
        return {'domain':{'rel_defrost':domain}}
    
    @api.one
    @api.depends('rel_defrost')
    def _jenisikan(self):
        if self.rel_defrost:
            xlokasi=self.location
            xuid = self.no_tangki
            tglprod = self.tgl_produksi
            nopot = self.no_potong
            cSQL1="select distinct c.product_group_code from sis_defrost_detail as b, sis_cs_detail as c "
            cSQL2="where b.tgl_produksi='"
            cSQL3="' and b.no_tangki='"
            cSQL4="' and b.no_potong='"
            cSQL5="' and b.pabrik_id='"
            cSQL6="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
           
            self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5+xlokasi+cSQL6)
            rc_check=self.env.cr.fetchall()
            if len(rc_check)>0:
                for cs_checker in rc_check:
                    (xproductgroupcode, )=cs_checker
                self.kindoffish = xproductgroupcode
                
    @api.one          
    @api.depends('rel_defrost')
    def _size(self):
        if self.rel_defrost:
            xlokasi=self.location
            xuid = self.no_tangki
            tglprod = self.tgl_produksi
            nopot = self.no_potong
            cSQL1="select distinct c.real_item_no from sis_defrost_detail as b, sis_cs_detail as c "
            cSQL2="where b.tgl_produksi='"
            cSQL3="' and b.no_tangki='"
            cSQL4="' and b.no_potong='"
            cSQL5="' and b.pabrik_id='"
            cSQL6="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
           
            self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5+xlokasi+cSQL6)
       
            rc_check=self.env.cr.fetchall()
            if len(rc_check)>0:
                for cs_checker in rc_check:
                    (xrealitemno, )=cs_checker
                self.size = xrealitemno
    
    @api.one  
    @api.depends('rel_defrost')
    def _vessel(self):
        if self.rel_defrost:
            xlokasi=self.location
            xuid = self.no_tangki
            tglprod = self.tgl_produksi
            nopot = self.no_potong
            cSQL1="select distinct c.vessel_no from sis_defrost_detail as b, sis_cs_detail as c "
            cSQL2="where b.tgl_produksi='"
            cSQL3="' and b.no_tangki='"
            cSQL4="' and b.no_potong='"
            cSQL5="' and b.pabrik_id='"
            cSQL6="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
           
            self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5+xlokasi+cSQL6)
            rc_check=self.env.cr.fetchall()
            if len(rc_check)>0:
                for cs_checker in rc_check:
                    (xvessel, )=cs_checker
                self.vessel = xvessel
              
      
    @api.depends('rel_defrost')
    def _voyage(self):
        if self.rel_defrost:
            xlokasi=self.location
            xuid = self.no_tangki
            tglprod = self.tgl_produksi
            nopot = self.no_potong
            cSQL1="select distinct c.voyage_no from sis_defrost_detail as b, sis_cs_detail as c "
            cSQL2="where b.tgl_produksi='"
            cSQL3="' and b.no_tangki='"
            cSQL4="' and b.no_potong='"
            cSQL5="' and b.pabrik_id='"
            cSQL6="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
           
            self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5+xlokasi+cSQL6)
            rc_check=self.env.cr.fetchall()
            if len(rc_check)>0:
                for cs_checker in rc_check:
                    ( xvoyage, )=cs_checker
                self.voyage = xvoyage
              
    @api.one  
    @api.depends('rel_defrost')
    def _hatch(self):
        if self.rel_defrost:
            xlokasi=self.location
            xuid = self.no_tangki
            tglprod = self.tgl_produksi
            nopot = self.no_potong
            cSQL1="select distinct c.hatch_no from sis_defrost_detail as b, sis_cs_detail as c "
            cSQL2="where b.tgl_produksi='"
            cSQL3="' and b.no_tangki='"
            cSQL4="' and b.no_potong='"
            cSQL5="' and b.pabrik_id='"
            cSQL6="' and c.tgl_produksi=b.tgl_produksi and c.no_potong=b.no_potong and c.barcode_no=b.barcode_no" 
           
            self.env.cr.execute(cSQL1+cSQL2+str(tglprod)+cSQL3+str(xuid)+cSQL4+str(nopot)+cSQL5+xlokasi+cSQL6)
            rc_check=self.env.cr.fetchall()
            if len(rc_check)>0:
                for cs_checker in rc_check:
                    (xhatch, )=cs_checker
                self.hatch = xhatch

    @api.one
    @api.depends('hatch')
    def _update_hatch(self):
        if self.hatch:
            if self.hatch[-3:]=="P&L":
                self.status_pl=True
            else:
                self.status_pl=False
    
    @api.onchange('no_tangki')
    def _cari_notangki(self):
        if self.no_tangki or self.no_tangki!=0:
#            rec=self.env['sis.cutting.tangki'].search([('tgl_produksi','=',self.tgl_produksi),('no_potong','=',self.no_potong),('location','=',self.location),('no_tangki','=',self.no_tangki),('id','!=',self.id)])
            cSQL1="select * from sis_cutting_tangki where tgl_produksi='"+self.tgl_produksi
            cSQL2="' and no_tangki='"+self.no_tangki+"' and no_potong="+str(self.no_potong)
            cSQL3=" and location='"+self.location+"'"
           
            self.env.cr.execute(cSQL1+cSQL2+cSQL3)
            rec=self.env.cr.fetchall()
            if len(rec)>0:
                raise UserError("No. Tangki : "+self.no_tangki+" sudah diinput!")

    @api.multi
    def write(self, vals):
        raise UserError("No. Tangki : "+self.no_tangki+" tidak bisa diupdate!\nDelete No. Tangki : "+self.no_tangki+", kemudian buat data baru.")

