from odoo import models, fields, api

class master_buyer(models.TransientModel):
    _name  ='sis.spec.buyer'
    _description = 'Master Buyer NAV for Spec'
    _rec_name='filter'
    
    temp_id     = fields.Char(string="ID")     
    filter      = fields.Char(string="Buyer", size=100)
    selected_buy= fields.Char(size=200,string='Selected Buyer',compute="_get_filter")
    buyer_line  = fields.One2many('sis.spec.buyer.line', 'rel_buyer', string='rel_buyer')

    @api.one
    def _get_filter(self):
        xitem_desc=""
        if self.filter:
            self.env.cr.execute("select description from sis_spec_buyer_line where rel_buyer="+str(self.id)+" and status_buyer=true")
            rec_buyer=self.env.cr.fetchall()
            for buyer_line in rec_buyer:
                (xitem_desc,)=buyer_line
            
        self.selected_buy=xitem_desc    

    def find_buyer(self):
        
        self.env.cr.execute("delete from sis_spec_buyer_line where temp_id='"+self.temp_id+"'")
        if self.filter: 
            self.env.cr.execute("select ship_to_code, customer_name from sis_customer where LOWER(customer_name) like '%"+self.filter+"%' or customer_name like '%"+self.filter+"%' or UPPER(customer_name) like '%"+self.filter+"%' order by customer_name")
        else:
            self.env.cr.execute("select ship_to_code, customer_name from sis_customer order by customer_name")

        rec_buyer=self.env.cr.fetchall()
        if len(rec_buyer)>0:
            new_lines = self.env['sis.spec.buyer.line']
            for buyer_line in rec_buyer:
                (xbuyer_no, xbuyer_desc)=buyer_line
                
                buyer_vals = {
                    'temp_id'       : self.temp_id,
                    'buyer_no'      : xbuyer_no,
                    'description'   : xbuyer_desc
                    }
                 
                new_lines += new_lines.new(buyer_vals)
            
            self.buyer_line=new_lines

    def kembali(self):
        return {'type': 'ir.actions.client', 
                'tag': 'history_back'
#                 'context'   : {'default_item_desc':self.temp_id} 
                }
              
class master_buyer_line(models.TransientModel):
    _name  ='sis.spec.buyer.line'
    _description = 'Master Buyer NAV for Spec (line)'
    _order = 'buyer_no'
    
    rel_buyer     = fields.Many2one('sis.spec.buyer', string="Buyer Lines", ondelete='cascade')
    temp_id       = fields.Char(string="ID")     
#     status_itc    = fields.Boolean(string="Set as Filter")
    buyer_no      = fields.Char(string="Buyer No", size=20)
    description   = fields.Char(string="Description")
    status_buyer  = fields.Boolean(string="Set as Filter") 
    
    def select_buyer(self):
        xbuyer=""
        self.env.cr.execute("update sis_spec_buyer_line set status_buyer=false")
        self.env.cr.execute("update sis_spec_buyer_line set status_buyer=true where buyer_no='"+self.buyer_no+"'")
        
#         self.env.cr.execute("select ship_to_code, customer_name from sis_customer where ship_to_code='"+self.buyer_no+"'")
#                 
#         rc_buyer=self.env.cr.fetchall()
#         if len(rc_buyer)>0:
#             for buyer_data in rc_buyer:
#                 (xkode, xnama)=buyer_data
        self.env.cr.execute("select no_rev from sis_spec_prod where temp_id='"+self.temp_id+"'")
        rec_rev=self.env.cr.fetchall()
        if len(rec_rev)>0:
            for rev_data in rec_rev:
                (xnorev, )=rev_data

        if xnorev==0:
            xbuyer=self.description
        else:
            xbuyer="""<font style="background-color: rgb(255, 255, 0);">"""+self.description+"""</font>""" 
        
        self.env.cr.execute("update sis_spec_prod set buyer_no='"+self.buyer_no+"', buyer_name='"+xbuyer+"' where temp_id='"+self.temp_id+"'")
 
    