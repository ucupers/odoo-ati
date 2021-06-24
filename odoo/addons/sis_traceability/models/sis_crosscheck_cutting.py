from odoo import models, fields, api
from odoo import tools

class sis_crosscheck_cutting(models.Model):
    _name = 'sis.crosscheck.cutting'
    _auto = False
    _order = 'productiondate Desc, label'
           
    productiondate  = fields.Date(string="Tgl. Produksi")
    no_potong       = fields.Integer(string="No. Potong")
    basket_id       = fields.Char(size=4, string='Basket ID')
    label           = fields.Integer(string="No. Label")
    kindoffish      = fields.Char(size=2, string="Jenis Ikan")
    size       = fields.Char(size=5,string="Fish Size")
    vessel       = fields.Char(size=100,string="Vessel No.")
    hatch        = fields.Char(size=100,string="Hatch No.")
    voyage       = fields.Char(size=100,string="Voyage No.")
   
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_crosscheck_cutting as (
        SELECT
        row_number() OVER () as id,
        a.productiondate, a.no_potong, b.basket_id, b.label, c.kindoffish, c.size, c.vessel, c.voyage, c.hatch 
        FROM
        sis_cutting as a 
        left join sis_cutting_basket as b on a.id = b.rel_cutting
        left join sis_cutting_tangki as c on a.id = c.rel_cutting)
        """
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_crosscheck_cutting')
        self._cr.execute(cSQL)
