from odoo import models, fields, api

class master_bom(models.TransientModel):
    _name  ='sis.bom'
    _description = 'Master BOM NAV for Spec'
    _rec_name='filter'
    
    temp_id     = fields.Char(string="ID")     
    filter      = fields.Char(string="BOM", size=100)
    selected_bom= fields.Char(size=200,string='Selected BOM',compute="_get_filter")
    bom_line    = fields.One2many('sis.bom.line', 'rel_bom', string='rel_bom')
#compute='_get_init_data'    

#     @api.onchange('temp_id')
#     def _get_init_data(self):
#         self.env.cr.execute("delete from sis_bom_line where temp_id='"+self.temp_id+"'")
#         self.env.cr.execute("select itemno, description from sis_production_bom where lineitc='FG' order by itemno")
#         rec_bom=self.env.cr.fetchall()
#         new_lines = self.env['sis.bom.line']
#         if len(rec_bom)>0:
#             for bom_line in rec_bom:
#                 (xbom_no, xbom_desc)=bom_line
#                 bom_vals = {
#                     'temp_id'       : self.temp_id,
#                     'item_no'       : xbom_no,
#                     'description'   : xbom_desc
#                     }
#                 new_lines += new_lines.new(bom_vals)
#                 
#             self.bom_line=new_lines
#         self.find_bom()
                  
    @api.one
    def _get_filter(self):
        xitem_desc=""
        if self.filter:
            self.env.cr.execute("select description from sis_bom_line where rel_bom="+str(self.id)+" and status_bom=true")
            rec_bom=self.env.cr.fetchall()
            for bom_line in rec_bom:
                (xitem_desc,)=bom_line
            
        self.selected_bom=xitem_desc    

    def find_bom(self):
        
        if self.filter: 
            self.env.cr.execute("delete from sis_bom_line where temp_id='"+self.temp_id+"'")
            self.env.cr.execute("select distinct itemno, description from sis_production_bom where linerouting='UNLABEL' and (LOWER(description) like '%"+self.filter+"%' or UPPER(description) like '%"+self.filter+"%' or description like '%"+self.filter+"%') order by itemno")
        else:
            self.env.cr.execute("delete from sis_bom_line where temp_id='"+self.temp_id+"'")
            self.env.cr.execute("select distinct itemno, description from sis_production_bom where linerouting='UNLABEL' order by itemno")
#         print("select itemno, description from sis_production_bom where lineitc='FG' and description like '%"+self.filter+"%' order by itemno")

        rec_bom=self.env.cr.fetchall()
        if len(rec_bom)>0:
            new_lines = self.env['sis.bom.line']
            for bom_line in rec_bom:
                (xbom_no, xbom_desc)=bom_line
                
                bom_vals = {
                    'temp_id'       : self.temp_id,
                    'item_no'       : xbom_no,
                    'description'   : xbom_desc
                    }
                 
                new_lines += new_lines.new(bom_vals)
            
            self.bom_line=new_lines

    def kembali(self):
        return {'type': 'ir.actions.client', 
                'tag': 'history_back'
#                 'context'   : {'default_item_desc':self.temp_id} 
                }
              
class master_bom_line(models.TransientModel):
    _name  ='sis.bom.line'
    _description = 'Master BOM NAV for Spec (line)'
    _order = 'item_no'
    
    rel_bom       = fields.Many2one('sis.bom', string="BOM Lines", ondelete='cascade')
    temp_id       = fields.Char(string="ID")     
#     status_itc    = fields.Boolean(string="Set as Filter")
    item_no       = fields.Char(string="Item No", size=20)
    description   = fields.Char(string="Description")
    status_bom    = fields.Boolean(string="Set as Filter") 

    def _get_ukuran_kaleng(self, xitem_no):
        xcan=""
        self.env.cr.execute("select lineitem, linedesc, linevar from sis_production_bom where itemno='"+xitem_no+"' and lineitc='PKG' and (linepgc='CAN' or linepgc='POUCH')")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlineitem, xlinedesc, xlinevar)=spec_line
                
                if xlineitem[2:3]=='B':
                    if xcan.strip()=="":
                        if xlinevar!="":
                            xcan=xlinedesc+" ("+xlineitem+" "+xlinevar+")"
                        else:
                            xcan=xlinedesc+" ("+xlineitem+")"
                    else:
                        if xlinevar!="":
                            xcan=xcan+", "+xlinedesc+" ("+xlineitem+" "+xlinevar+")"
                        else:
                            xcan=xcan+", "+xlinedesc+" ("+xlineitem+")"
        else:
            xcan="-"
                        
        return xcan
    
    def _get_lid(self, xitem_no):
        xlid=""
        self.env.cr.execute("select lineitem, linedesc, linevar from sis_production_bom where itemno='"+xitem_no+"' and lineitc='PKG' and linepgc='CAN'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlineitem, xlinedesc, xlinevar)=spec_line
                
                if xlineitem[2:3]=='E':
                    if xlid.strip()=="":
                        if xlinevar!="":
                            xlid=xlinedesc+" ("+xlineitem+" "+xlinevar+")"
                        else:
                            xlid=xlinedesc+" ("+xlineitem+")"
                    else:
                        if xlinevar!="":
                            xlid=xlid+", "+xlinedesc+" ("+xlineitem+" "+xlinevar+")"
                        else:
                            xlid=xlid+", "+xlinedesc+" ("+xlineitem+")"
        else:
            xlid="-"
                        
        return xlid
    
    def _get_fish(self, xitem_no):
        xfish=""
        self.env.cr.execute("select linedesc from sis_production_bom where itemno='"+xitem_no+"' and lineitc='WIP'")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlinedesc,)=spec_line
                
                if xfish.strip()=="":
                    xfish=xlinedesc
                else:
                    xfish=xfish+", "+xlinedesc
        else:
            xfish="-"
                        
        return xfish
    
    def _get_komposisi(self, xitem_no):
        xkomposisi=""
        self.env.cr.execute("select linedesc from sis_production_bom where itemno='"+xitem_no+"' and lineitc!='PKG' order by lineitc desc, lineqty")
        rec_spec=self.env.cr.fetchall()
        if len(rec_spec)>0:
            for spec_line in rec_spec:
                (xlinedesc,)=spec_line
                
                if xkomposisi.strip()=="":
                    xkomposisi=xlinedesc
                else:
                    xkomposisi=xkomposisi+", "+xlinedesc
                        
        return xkomposisi
    
    def _get_formulasi(self,xitem_no):
        xtotal_desc=""
        xtotal_qty=0
        xformulasi="-"
        self.env.cr.execute("""
        select sum(bom.lineqty) as Meat, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+xitem_no+"""' and bom.lineitc='WIP' group by bom.lineuom""")
        
        rc_meat=self.env.cr.fetchall()
        if len(rc_meat)>0:
            for meat_data in rc_meat:
                (meat_qty, meat_uom)=meat_data
                xformulasi="""<tr><td style="font-size:13px;border:0">Meat</td><td align="right" style="font-size:13px;border:0">"""+str(meat_qty)+" "+meat_uom+"""&nbsp;&nbsp;</td></tr>"""
                xtotal_desc="Meat"
                xtotal_qty=meat_qty
                    
        self.env.cr.execute("""
        select bom.linedesc, bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+xitem_no+"""' and bom.lineitc='SS' and bom.linepgc='VEGNFRT' order by bom.lineqty desc        
        """)
                
        rc_ss=self.env.cr.fetchall()
        if len(rc_ss)>0:
            xnomer=0
            for ss_data in rc_ss:
                (xssdesc, xssqty, xssuom)=ss_data
                xnomer=xnomer+1
                
                if xtotal_desc.strip()=="":
                    xtotal_desc=xssdesc
                else:
                    xtotal_desc +=", "+xssdesc
                
                xtotal_qty +=xssqty
                
                if xnomer==len(rc_ss):
                    xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xssdesc+"""</td><td align="right" style="font-size:13px;border:0"><u>"""+str(xssqty)+" "+xssuom+"""</u>&nbsp;&nbsp;</td></tr>"""
                else:
                    xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xssdesc+"""</td><td align="right" style="font-size:13px;border:0">"""+str(xssqty)+" "+xssuom+"""&nbsp;&nbsp;</td></tr>"""
            
            xformulasi +="""<tr><td style="font-size:13px;border:0">"""+xtotal_desc+"""</td><td align="right" style="font-size:13px;border:0">"""+str(xtotal_qty)+" "+xssuom+"""&nbsp;&nbsp;</td></tr>"""

            xformulasi="""<p><br></p><p align="center"><table border="0" width="60%"><tbody>"""+xformulasi+"""</tbody></table></p><p><br></p>"""
            
        xformulasi +="""<p><br></p><p align="center"><table border="0" width="60%">"""
        
        self.env.cr.execute("""
        select bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+xitem_no+"""' and bom.lineitc='SS' and bom.linepgc='OIL' order by bom.lineqty desc        
        """)
 
        xoil=0                
        rc_oil=self.env.cr.fetchall()
        if len(rc_oil)>0:
            for oil_data in rc_oil:
                (xoilqty, xoiluom)=oil_data
                xoil+=xoilqty
            
            if xoil!=0:
                xformulasi +="""
                <tr><td style="font-size:13px;border:0">Minyak/Oil</td><td width="20%" align="right" style="font-size:13px;border:0">"""+str(xoil)+""" """+xoiluom+"""&nbsp;&nbsp;</td></tr>
                """

        self.env.cr.execute("""
        select bom.lineqty, bom.lineuom
        from sis_production_bom bom
        inner join sis_nav_items_bc it on it.item_no=bom.itemno
        where bom.linerouting='UNLABEL' and bom.itemno='"""+xitem_no+"""' and 
        (bom.linedesc like '%Garam%' or bom.linedesc like '%garam%' or bom.linedesc like '%GARAM%' or bom.linedesc like '%Salt%' or bom.linedesc like '%salt%' or bom.linedesc like '%SALT%')
        """)
        xsalt=0                
        rc_salt=self.env.cr.fetchall()
        if len(rc_salt)>0:
            for salt_data in rc_salt:
                (xsaltqty, xsaltuom)=salt_data
                xsalt +=xsaltqty
            
            if xsalt!=0:
                xformulasi +="""
                <tr><td style="font-size:13px;border:0">Air Garam/Brine</td><td width="20%" align="right" style="font-size:13px;border:0">"""+str(xsalt)+""" """+xsaltuom+"""&nbsp;&nbsp;</td></tr>
                """
        xformulasi +="</table></p>"
        
        return xformulasi
                
    def _get_oil(self,xitem_no):
        xoil=""
        self.env.cr.execute("select linedesc from sis_production_bom where itemno='"+xitem_no+"' and lineitc='SS' and linepgc='OIL' order by linedesc")
        rc_oil=self.env.cr.fetchall()
        if len(rc_oil)>0:
            for oil_line in rc_oil:
                (xlinedesc,)=oil_line
                
                if xoil.strip()=="":
                    xoil=xlinedesc
                else:
                    xoil=xoil+", "+xlinedesc
        else:
            xoil="-"
                        
        return xoil
    
    def _get_seasoning(self,xitem_no):
        xseas=""
        self.env.cr.execute("select linedesc, lineqty, lineuom from sis_production_bom where itemno='"+xitem_no+"' and lineitc='SS' and (linepgc!='OIL' and linepgc!='VEGNFRT') order by lineqty desc")
        rc_ss=self.env.cr.fetchall()
        if len(rc_ss)>0:
            for ss_line in rc_ss:
                (xlinedesc, xlineqty, xlineuom)=ss_line
                
                if xseas.strip()=="":
                    xseas="""<tr><td style="font-size:13px">"""+xlinedesc+"""</td><td align="center" style="font-size:13px" width="20%">"""+str(xlineqty)+"""</td></tr>"""
                else:
                    xseas +="""<tr><td style="font-size:13px">"""+xlinedesc+"""</td><td align="center" style="font-size:13px" width="20%">"""+str(xlineqty)+"""</td></tr>"""
    
            xseas="""
            <table border="1" width="60%">
            <tr><td colspan="2" align="center"><b>Brine (g)/tin</b></td></tr>
            """+xseas+"""</table><p><br></p>
            """
        else:
            xseas="-"
            
        return xseas
    
    def create_spec(self):
        self.env.cr.execute("update sis_bom_line set status_bom=false")
        self.env.cr.execute("update sis_bom_line set status_bom=true where item_no='"+self.item_no+"'")

        self.env.cr.execute("""
        select distinct bom.description, it.description2 
        from sis_production_bom bom 
        inner join sis_nav_items_bc it on it.item_no=bom.itemno 
        where bom.linerouting='UNLABEL' and bom.itemno='"""+self.item_no+"""'
        """)
                
        rc_bom=self.env.cr.fetchall()
#         print(str(len(rc_bom)))
        if len(rc_bom)>0:
            for bom_data in rc_bom:
                (xdesc, xdesc2)=bom_data
        
        xcan=self._get_ukuran_kaleng(self.item_no)
        xlid=self._get_lid(self.item_no)
        xfish=self._get_fish(self.item_no)
        xkomposisi=self._get_komposisi(self.item_no)
        xformulasi=self._get_formulasi(self.item_no)
        xoil=self._get_oil(self.item_no)
        xseas=self._get_seasoning(self.item_no)

        self.env.cr.execute("update sis_spec_prod set item_no='"+self.item_no+"', item_desc='"+xdesc+"', nama_produk='"+xdesc2+"', can_size='"+xcan+"', lid='"+xlid+"', jenis_ikan='"+xfish+"', komposisi='"+xkomposisi+"', formulasi='"+xformulasi+"', jenis_minyak='"+xoil+"', bumbu='"+xseas+"' where temp_id='"+self.temp_id+"'")
    