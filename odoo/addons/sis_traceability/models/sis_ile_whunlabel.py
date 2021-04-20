from odoo import models, fields, api, tools

class sis_ile_whunlabel(models.Model):
    _name='sis.ile.whunlabel.loc'
    _rec_name='no_pallet'
    _order = "tanggal_produksi desc" 

    tanggal_produksi = fields.Date('Tanggal Produksi')
    item_no = fields.Char('Item No')
    no_pallet = fields.Char('No Pallet')
    gudang = fields.Char('Gudang')
    
#     def update_ile_nav_odoo(self):
#         self.env.cr.execute("delete from sis_ile_wh_unlabel_loc")
#         
#         self.env.cr.execute("""insert into sis_ile_whunlabel(tanggal_produksi, item_no, no_pallet, gudang)
#         tanggal_produksi, item_no, no_pallet, gudang from sis_ile_whunlabel""")
#         self.env.cr.fetchall()