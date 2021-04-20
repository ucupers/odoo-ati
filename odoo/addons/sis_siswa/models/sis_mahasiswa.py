from odoo import fields, models, api
from odoo.exceptions import UserError

# class Jurusan(models.Model):
#     _name = "mahasiswa.jurusan"
#     
#     nama = fields.Char(size=32, string="Nama")
#     akreditasi = fields.Char(size=1, string="Akreditasi")
#     
#     mahasiswanya  = fields.One2many('mahasiswa.mahasiswa', 'jurusannya', string='Mahasiswa')

class Mahasiswa(models.Model):
    _name = "mahasiswa.mahasiswa"
    
    nama = fields.Char(size=32, string="Nama")
    kelas= fields.Char(size=32, string="Kelas")
    alamat= fields.Char(size=32, string="Alamat")
    
#     jurusannya = fields.Many2one('mahasiswa.jurusan', string="Jurusan")
    pelajaran = fields.One2many('mahasiswa.pelajaran', 'rel_pelajaran', string='Pelajaran')
    
    def open_pelajaran(self):
        return {
            'name' : 'pelajaran',
            'res_model': 'mahasiswa.pelajaran',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_siswa.mahasiswa_pelajaran_tree').id,
            'nodestroy':False,
            'context':{'default_rel_pelajaran':self.id},
            'domain':[('rel_pelajaran','=',self.id)]
        }
        
class Pelajaran(models.Model):
    _name = 'mahasiswa.pelajaran'
    
    nama = fields.Char(size=32,string="Nama")
    sks = fields.Integer(string="SKS")
    #id_temp1=fields.Integer('id_temp')
    
    pelajaran = fields.One2many('mahasiswa.label', 'relasi', string='Relasi')
    rel_pelajaran = fields.Many2one('mahasiswa.mahasiswa', string="Mahasiswa")
    
    def open_label(self):
        return {
            'name' : 'label',
            'res_model': 'mahasiswa.label',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_siswa.mahasiswa_label_tree').id,
            'nodestroy':False,
            'domain':"[('relasi','=',"+str(self.id)+")]"
        }
        
class label(models.Model):
    _name = 'mahasiswa.label'
    
    nourutbasket = fields.Char(string='No Urut Basket')
    jenis = fields.Selection([('Test','Test'),('FG','FG')], string='Jenis', default='FG')
    relasi = fields.Many2one('mahasiswa.pelajaran', string="relasi")
    
    

