from odoo import models, fields, api
from odoo.exceptions import UserError

class sis_gl_account(models.Model):
    _name='sis.gl.account'
    _table='sis_gl_account'
    _auto=False
    _order='name'

    no=fields.Char(size=20,string="Account No.",readonly=True)
    name=fields.Char(size=200,string="Description",readonly=True)
    income_balance=fields.Integer(string="Income=1/Balance=0",readonly=True)
    account_type=fields.Char(string="Account Type",readonly=True)
    
class sis_gl_entry(models.Model):
    _name='sis.gl.entry'
    _table='sis_gl_entry'
    _auto=False

    accno=fields.Char(size=20,string="Account No.",readonly=True)
    postingdate=fields.Date(string="Posting Date",readonly=True)    
    docno=fields.Char(size=50,string="Document No.",readonly=True)
    amount=fields.Float(string="Amount",readonly=True)
    addamount=fields.Float(string="Add-Amount",readonly=True)
    bg=fields.Char(size=5,string="BG",readonly=True)
    
class sis_temp_gl_entry(models.Model):
    _name='sis.temp.gl.entry'

    accno=fields.Char(size=20,string="Account No.",readonly=True)
    postingdate=fields.Date(string="Posting Date",readonly=True)    
    docno=fields.Char(size=50,string="Document No.",readonly=True)
    amount=fields.Float(string="Amount",readonly=True)
    addamount=fields.Float(string="Add-Amount",readonly=True)
    bg=fields.Char(size=5,string="BG",readonly=True)    