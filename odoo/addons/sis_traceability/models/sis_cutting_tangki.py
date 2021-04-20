from odoo import models, fields, api, tools
from odoo.exceptions import UserError

class cutting_tangki(models.Model):
    _name       ='sis.cutting.tangki'
    _rec_name   = 'no_tangki'
    
    rel_cutting = fields.Many2one('sis.cutting', string="Tangki")
    rel_defrost = fields.Many2one('sis.defrost.detail', string="No. Tangki", required=True, domain="[('tgl_produksi','=', tgl_produksi),('no_potong','=',no_potong),('pabrik_id', '=', location),('no_tangki', '!=', '-')]")


    tgl_produksi= fields.Date(string="Tanggal Produksi")
    location    = fields.Char(size=4, string='Lokasi')
    location_notangki    = fields.Char(size=4, string='Lokasi', compute="_lokasi", store=True)
    no_potong   = fields.Integer(string='No Potong')
    no_tangki   = fields.Char(string="No. Tangki", related="rel_defrost.no_tangki", store=True)
    kindoffish  = fields.Char(string="Jenis Ikan", compute="_jenisikan", store=True)
    size        = fields.Char(string="Ukuran", compute="_size", store=True)
    vessel      = fields.Char(string="Vessel", compute="_vessel", store=True)
    voyage      = fields.Char(string="Voyage", compute="_voyage", store=True)
    hatch       = fields.Char(string="Hatch", compute="_hatch", store=True)
    status_pl   = fields.Boolean(string="Pole & Line", compute="_update_hatch", store=True)
    
    @api.one
    @api.depends('rel_defrost')
    def _lokasi(self):
        if self.rel_defrost:
            self.location_notangki=self.rel_defrost.pabrik_id
    
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
#                 self.rel_cutting.status_pl_cut=False
    
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
    
        
    @api.model
    def create(self,vals):
        xpabrik_id,xsection_id=self._get_section_id()
        if xpabrik_id==vals['location']:
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="RM" or xsection_id=="Cutting":
                res_id = models.Model.create(self, vals)
                return res_id
            else:
                raise UserError("Unauthorized User!")
        else:
                raise UserError("Data "+vals['location']+" tidak bisa di edit oleh user "+xpabrik_id)
    
    def _get_section_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
 
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
         
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
         
        return xpabrik_id,xsection_id

class sis_cutting_view_alert(models.Model):
    _name = 'sis.cutting.view.alert'
    _description = 'Data No tangki yang belum diiput Cutting'
    _auto = False
    _order = 'tgl_produksi desc'
    
    tgl_produksi = fields.Date('Tanggal Produksi')
    pabrik_id = fields.Char('Lokasi')
    no_tangki = fields.Char('No Tangki')
    no_potong = fields.Integer('No Potong')
    item_no = fields.Char('Item No')
    description =  fields.Char('Description')
    vessel_no =   fields.Char('Vessel No')
    hatch_no =   fields.Char('Hatch No')
    create_date =   fields.Datetime('Create Date')

    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_cutting_view_alert as (
        SELECT
        row_number() OVER () as id, 
        def.tgl_produksi, def.pabrik_id, def.no_tangki, def.no_potong, cs.item_no, cs.description, cs.vessel_no, cs.hatch_no, def.create_date
        from sis_defrost_detail as def
        left join sis_cutting_tangki as cut on def.id=cut.rel_defrost
        left join sis_cs_detail as cs on def.defrost_link_id=cs.id
        where def.tgl_produksi>='2020-11-9' and cut.id is null and def.no_tangki !='-')"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_cutting_view_alert')
        self._cr.execute(cSQL)


