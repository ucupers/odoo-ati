from odoo import models, fields

class testing1(models.Model):
    _name  ='sis.testing1'
    
    html1            = fields.Html(string="Html1")
    html2            = fields.Html(string="Html2")
    html3            = fields.Html(string="Html3")
    file_image       = fields.Binary('File data', help='File(image format)')
    
