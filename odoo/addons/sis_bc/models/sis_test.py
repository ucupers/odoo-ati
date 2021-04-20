from odoo import models, fields, api
from odoo.exceptions import UserError
import pyodbc

SQLCONN='Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+\
                              'Server=10.0.0.12;'+\
                              'Database=NAV (9-0) ATI LIVE;'+\
                              'UID=Atidev;pwd=Ati1234;'
                              
class ile_nav(models.Model):
    _name  ='sis.ile.bc'
    _table = 'sis_ile_bc'
    _description = 'ILE NAV for BC'
    _auto = False
    _order = 'posting_date desc'
    
    item_no         = fields.Char(string="Item No", size=20)
    description     = fields.Char(string="Description", size=100)
    location_code   = fields.Char(string="Location Code", size=20)
    entry_types     = fields.Integer(string="Entry Types")
    quantity        = fields.Float(string="Quantity")
    posting_date    = fields.Date(string="Posting Date")
    current_datetime= fields.Char(string="Current DateTime", size=19)
 
    def update_ile_bc(self):
        conn = pyodbc.connect(SQLCONN)
        cursor = conn.cursor()
        
        #raise UserError(fields.Datetime.now())
#        row=cursor.execute("UPDATE sis_ile_cdt set current_date_time='"+fields.Datetime.now()+"'")
        row=cursor.execute("UPDATE sis_ile_cdt set current_date_time='2020-01-14 23:59:59'")
        if row.rowcount==0:
            raise UserError('Failed to update ILE NAV (2), please try again later')
        else:
            conn.commit()
                            
        

        
        