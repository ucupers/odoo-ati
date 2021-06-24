from odoo import models, fields, api
from odoo.exceptions import ValidationError

    
class sis_raport(models.Model):
    _name='sis.raport'

    nis=fields.Char(size=20,string='No Induk',required=True)    
    nama=fields.Char(size=100,string='Nama',required=True)
    rata2=fields.Float(string='Rata2')        
    
class sis_siswa(models.Model):
    _name='sis.siswa'
#    _rec_name='nis'
    _rec_name='nama'
        
    nis=fields.Char(size=20,string='No Induk',required=True)
    nama=fields.Char(size=100,string='Nama',required=True)
    tinggi=fields.Float(string='Tinggi',default=100)
    bmi=fields.Integer(string='BMI',compute='_compute_bmi',store=True)
    rata2=fields.Float(compute='_compute_rata2',string='Rata2')
    nilai_id=fields.One2many('sis.nilai','siswa_id',string="Nilai")
    
    @api.multi
    def name_get(self):
        result = []
        for me in self :
            result.append((me.id, "%s - %s" % (me.nama, me.tinggi)))
        return result
    
    def genraport(self):
        total=0
        for rec in self.nilai_id:
            total=total+rec.nilai
        rata2=total/len(self.nilai_id)

        rec=self.env['sis.raport'].search([('nis','=',self.nis)])
        for r in rec:
            vals={ 
                  'nama':self.nama,
                  'rata2':rata2
                }
            r.write(vals)
        if len(rec)==0:
            vals={ 'nis':self.nis,
                  'nama':self.nama,
                  'rata2':rata2
                }
            self.env['sis.raport'].create(vals)
        
        
    @api.one
    def _compute_rata2(self):
        
        total=0
        for rec in self.nilai_id:
            total=total+rec.nilai
        if len(self.nilai_id)>0:
            self.rata2=total/len(self.nilai_id)
        else:
            self.rata2=0
            
    @api.constrains('nis')
    def _constrains_nis(self):
        rec=self.env['sis.siswa'].search([('nis','=',self.nis),('id','!=',self.id)])
        if len(rec)>0:
            raise ValidationError('NIS Double!!')
        rec._compute_bmi

    @api.one
    @api.depends('tinggi')    
    def _compute_bmi(self):
        self.bmi=self.tinggi-100
        self._constrains_nis()

        
        
        