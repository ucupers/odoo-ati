from odoo import models, fields, api

class sis_spec_akses(models.Model):
    _name='sis.spec.akses'
#    _rec_name='nis'
#     _rec_name='nama'
        
    section=fields.Char(size=30,string='Section',required=True)
    view_1=fields.Boolean(string="1", default=True)
    view_2=fields.Boolean(string="2", default=True)
    view_3=fields.Boolean(string="3", default=True)
    view_4=fields.Boolean(string="4", default=True)
    view_5=fields.Boolean(string="5", default=True)
    view_6=fields.Boolean(string="6", default=False)
    view_7=fields.Boolean(string="7", default=False)
    view_8=fields.Boolean(string="8", default=False)
    view_9=fields.Boolean(string="9", default=False)
    view_10=fields.Boolean(string="10", default=False)
    view_11=fields.Boolean(string="11", default=False)
    view_12=fields.Boolean(string="12", default=False)
    view_13=fields.Boolean(string="13", default=False)
    view_14=fields.Boolean(string="14", default=False)
    view_15=fields.Boolean(string="15", default=False)
    view_16=fields.Boolean(string="16", default=False)
    view_17=fields.Boolean(string="17", default=False)
    view_18=fields.Boolean(string="18", default=False)
    view_19=fields.Boolean(string="19", default=False)
    view_20=fields.Boolean(string="20", default=False)
    view_21=fields.Boolean(string="21", default=False)
    view_22=fields.Boolean(string="22", default=False)
    view_23=fields.Boolean(string="23", default=False)
    view_24=fields.Boolean(string="24", default=False)
    view_25=fields.Boolean(string="25", default=False)
    view_26=fields.Boolean(string="26", default=False)
    view_27=fields.Boolean(string="27", default=False)
    view_28=fields.Boolean(string="28", default=False)
    view_29=fields.Boolean(string="29", default=False)
    view_30=fields.Boolean(string="30", default=False)
    view_31=fields.Boolean(string="31", default=False)
    view_32=fields.Boolean(string="32", default=False)
    view_33=fields.Boolean(string="33", default=False)
    view_34=fields.Boolean(string="34", default=False)
    view_35=fields.Boolean(string="35", default=False)
    view_36=fields.Boolean(string="36", default=False)
    