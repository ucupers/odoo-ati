from odoo import models, fields, api
from odoo.exceptions import UserError
import xlsxwriter
import base64

class bc_item(models.TransientModel):
    _name  ='sis.inv.bc.item'
    _description = 'Form item Report Inventory for BC'
    
    temp_id             = fields.Float(string="Temp ID")
    item_no             = fields.Char(string="Item No", size=20)
#    item_category_code  = fields.Char(string="Item Category Code", size=20)
    description         = fields.Char(string="Description", size=100)
#    location_code       = fields.Char(string="Location Code", size=20)
    base_uom            = fields.Char(string="Base UOM", size=10)
    variant_uom         = fields.Char(string="Variant UOM", size=10)

class bc_saldo_awal(models.TransientModel):
    _name  ='sis.inv.bc.first.balance'
    _description = 'Form Begining Balance Report Inventory for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Saldo Awal")

class bc_saldo_awal_bk(models.TransientModel):
    _name  ='sis.inv.bc.first.balance.bk'
    _description = 'Form Begining Balance Report Inventory in Buku Kuning for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Saldo Awal")

class bc_increase(models.TransientModel):
    _name  ='sis.inv.bc.increase'
    _description = 'Form Increase Report Inventory for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Increase")

class bc_increase_bk(models.TransientModel):
    _name  ='sis.inv.bc.increase.bk'
    _description = 'Form Increase Report Inventory in Buku Kuning for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Increase")

class bc_decrease(models.TransientModel):
    _name  ='sis.inv.bc.decrease'
    _description = 'Form Decrease Report Inventory in Buku Kuning for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Decrease")

class bc_decrease_bk(models.TransientModel):
    _name  ='sis.inv.bc.decrease.bk'
    _description = 'Form Decrease Report Inventory in Buku Kuning for BC'
    
    temp_id      = fields.Float(string="Temp ID")
    item_no      = fields.Char(string="Kode Barang", size=20)
    quantity     = fields.Float(string="Decrease")

class report_inventory_bc(models.TransientModel):
    _name       ='sis.report.inv.bc'
    _rec_name   ='rpt_laporan'
    _description= 'Form Report Inventory for BC'
    
    #rel_report_id   = fields.Many2one('sis.report.filter.bc', string="Report ID", required=True)
    rpt_laporan     = fields.Selection(lambda self: self._get_laporan(),string="Laporan", required=True)
    rpt_tanggal1    = fields.Date(string='Tanggal Awal')
    rpt_tanggal2    = fields.Date(string='Tanggal Akhir')
    rpt_kode_barang = fields.Char(string="Kode Barang", size=20)
    rpt_nama_barang = fields.Char(string="Nama Barang", size=100)
    rpt_inv_line    = fields.One2many('sis.report.inv.bc.line', 'rel_inv_line_id', string='Inv. ID')
    rpt_xlsx        = fields.Binary('File data', help='File(xlsx format)')
#    rpt_filename    = fields.Char(string="Filename", size=100)
    
    def _insert_item(self, xItem_Category_Code, xLocation_Code):
        self.env.cr.execute("select ile.item_no, ile.description, ile.base_uom, ile.variant_uom "+\
                            "from sis_ile_odoo_bc ile where ("+xItem_Category_Code+") and ("+xLocation_Code+") "+\
                            "group by ile.item_no, ile.description, ile.base_uom, ile.variant_uom;")
        
        rec_ile=self.env.cr.fetchall()
        if len(rec_ile)>0:
            for dt_ile in rec_ile:
                (xItemNo, xDescription, xBase_UOM, xVariant_UOM)=dt_ile
                
                vals={
                    'temp_id'            : self.id,
                    'item_no'            : xItemNo,
                    #'item_category_code' : xCategoryCode,
                    'description'        : xDescription,
                    #'location_code'      : xLocationCode,
                    'base_uom'           : xBase_UOM,
                    'variant_uom'        : xVariant_UOM
                }
                self.env['sis.inv.bc.item'].create(vals)

    
#    def _insert_begbal(self,xItem_Category_Code, xLocation_Code, xTanggal):
    def _insert_begbal(self,xWhere):
        print(xWhere)
#         self.env.cr.execute("select item_no, round(sum(begbal.quantity)::numeric,2) as total from sis_ile_odoo_bc begbal where "+\
#                             xWhere+" group by begbal.item_no;")
        self.env.cr.execute("select ile.item_no, ile.variant_code, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bc ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+\
                            xWhere+" group by ile.item_no, ile.variant_code")

#         print("select ile.item_no, ile.variant_code, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bc ile "+\
#                             "inner join sis_items_bc it on it.item_no_=ile.item_no where "+\
#                             xWhere+" group by ile.item_no, ile.variant_code;")

        rec_begbal=self.env.cr.fetchall()
        if len(rec_begbal)>0:
            for begbal in rec_begbal:
                (xItemNo, xVarian, xTotal)=begbal
                
                if xVarian.strip()=='': 
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo,
                        'quantity'  : xTotal
                    }
                else:
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo+' '+xVarian,
                        'quantity'  : xTotal
                    }
                    
#                self.env.cr.execute("insert into sis_inv_bc_first_balance (temp_id, item_no, quantity) values('"+str(self.id)+"','"+xItemNo+"','"+str(xTotal)+"')")
                self.env['sis.inv.bc.first.balance'].create(vals)

    def _insert_begbal_bk(self,xWhere):
        self.env.cr.execute("select ile.item_no, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bk ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+\
                            xWhere+" group by ile.item_no;")

#         print("select ile.item_no, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bk ile "+\
#                             "inner join sis_items_bc it on it.item_no_=ile.item_no where "+\
#                             xWhere+" group by ile.item_no;")

        rec_begbal=self.env.cr.fetchall()
        if len(rec_begbal)>0:
            for begbal in rec_begbal:
                (xItemNo, xTotal)=begbal
                 
                vals={
                    'temp_id'   : self.id,
                    'item_no'   : xItemNo,
                    'quantity'  : xTotal
                }
                self.env['sis.inv.bc.first.balance.bk'].create(vals)
                    
#    def _insert_increase(self,xItem_Category_Code, xLocation_Code, xTanggal1, xTanggal2):
    def _insert_increase(self,xWhere):
#         self.env.cr.execute("select item_no, round(sum(inc.quantity)::numeric,2) as total from sis_ile_odoo_bc inc where "+xWhere+" and "+\
#                             "(inc.entry_types=0 or inc.entry_types=2 or inc.entry_types=6 or inc.entry_types=9 or "+\
#                             "(inc.entry_types=4 and inc.quantity>0)) group by inc.item_no;")
        self.env.cr.execute("select ile.item_no, ile.variant_code, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bc ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
                            "(ile.entry_types=0 or ile.entry_types=2 or ile.entry_types=6 or ile.entry_types=9 or "+\
                            "(ile.entry_types=4 and ile.quantity>0)) group by ile.item_no, ile.variant_code")

#         print("select ile.item_no, ile.variant_code, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bc ile "+\
#                             "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
#                             "(ile.entry_types=0 or ile.entry_types=2 or ile.entry_types=6 or ile.entry_types=9 or "+\
#                             "(ile.entry_types=4 and ile.quantity>0)) group by ile.item_no, ile.variant_code;")
        
        rec_inc=self.env.cr.fetchall()
        if len(rec_inc)>0:
            for inc in rec_inc:
                (xItemNo, xVarian, xTotal)=inc
                
                if xVarian.strip()=='': 
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo,
                        'quantity'  : xTotal
                    }
                else:
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo+' '+xVarian,
                        'quantity'  : xTotal
                    }

                self.env['sis.inv.bc.increase'].create(vals)

    def _insert_increase_bk(self,xWhere):
        self.env.cr.execute("select ile.item_no, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bk ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
                            "(ile.entry_types=1 or ile.entry_types=3) and ile.quantity>0 group by ile.item_no;")
#         print("select ile.item_no, round(sum(ile.quantity)::numeric,2) as total from sis_ile_odoo_bk ile "+\
#                             "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
#                             "(ile.entry_types=1 or ile.entry_types=3) and ile.quantity>0 group by ile.item_no;")

        rec_inc=self.env.cr.fetchall()
        if len(rec_inc)>0:
            for inc in rec_inc:
                (xItemNo, xTotal)=inc
                
                vals={
                    'temp_id'   : self.id,
                    'item_no'   : xItemNo,
                    'quantity'  : xTotal
                }
                self.env['sis.inv.bc.increase.bk'].create(vals)

#    def _insert_decrease(self,xItem_Category_Code, xLocation_Code, xTanggal1, xTanggal2):
    def _insert_decrease(self,xWhere):
#         self.env.cr.execute("select item_no, round(abs(sum(dnc.quantity))::numeric,2) as total from sis_ile_odoo_bc dnc where ("+xItem_Category_Code+") and ("+\
#                             xLocation_Code+") and dnc.posting_date between '"+xTanggal1+"' and '"+xTanggal2+"' and "+\
#                             "(dnc.entry_types=1 or dnc.entry_types=3 or dnc.entry_types=5 or dnc.entry_types=8 or "+\
#                             "(dnc.entry_types=4 and dnc.quantity<0)) group by dnc.item_no;")
        self.env.cr.execute("select ile.item_no, ile.variant_code, round(abs(sum(ile.quantity))::numeric,2) as total from sis_ile_odoo_bc ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
                            "(ile.entry_types=1 or ile.entry_types=3 or ile.entry_types=5 or ile.entry_types=8 or "+\
                            "(ile.entry_types=4 and ile.quantity<0)) group by ile.item_no, ile.variant_code")

#         print("select ile.item_no, ile.variant_code, round(abs(sum(ile.quantity))::numeric,2) as total from sis_ile_odoo_bc ile "+\
#                             "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+" and "+\
#                             "(ile.entry_types=1 or ile.entry_types=3 or ile.entry_types=5 or ile.entry_types=8 or "+\
#                             "(ile.entry_types=4 and ile.quantity<0)) group by ile.item_no, ile.variant_code;")

        rec_dnc=self.env.cr.fetchall()
        if len(rec_dnc)>0:
            for dnc in rec_dnc:
                (xItemNo, xVarian, xTotal)=dnc
                
                if xVarian.strip()=='': 
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo,
                        'quantity'  : xTotal
                    }
                else:
                    vals={
                        'temp_id'   : self.id,
                        'item_no'   : xItemNo+' '+xVarian,
                        'quantity'  : xTotal
                    }

                self.env['sis.inv.bc.decrease'].create(vals)

    def _insert_decrease_bk(self,xWhere):
        self.env.cr.execute("select ile.item_no, round(abs(sum(ile.quantity))::numeric,2) as total from sis_ile_odoo_bk ile "+\
                            "inner join sis_items_bc it on it.item_no_=ile.item_no where "+xWhere+\
                            " and ile.entry_types=2 and ile.quantity<0 group by ile.item_no;")

        rec_dnc=self.env.cr.fetchall()
        if len(rec_dnc)>0:
            for dnc in rec_dnc:
                (xItemNo, xTotal)=dnc
                
                vals={
                    'temp_id'   : self.id,
                    'item_no'   : xItemNo,
                    'quantity'  : xTotal
                }
                self.env['sis.inv.bc.decrease.bk'].create(vals)
                
    def _filter_desc2(self, xid):
        xdc=""
        xdc1=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:
                if filter.description_2:
                    if filter.description_2[0:(len(filter.description_2)-2)*-1]=="!=":
                        xdc="description_2!='"+filter.description_2[2:].strip()+"'"
                    else:
                        xdc="description_2='"+filter.description_2.strip()+"'"
                    
#                    xdc1="ile."+xdc
                    xdc1="it."+xdc
#         xdc2="begbal."+xdc
#         xdc3="inc."+xdc
#         xdc4="dnc."+xdc
                        
        return xdc1

    def _filter_item_no(self, xid):
        xitn=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:

                if filter.item_no:            
                    if filter.item_no.find("|")!=-1:
                        koma=0
                        for n in range(len(filter.item_no)):
                            if filter.item_no[n:n+1]=="|":
                                if xitn.strip()=="":
                                    xitn="it.item_no_ in ('"+filter.item_no[koma:n].strip()+"'"
                                else:
                                    xitn += ", '"+filter.item_no[koma:n].strip()+"'"
                                
                                koma=n+1
                            else:
                                if n+1==len(filter.item_no):
                                    xitn += ", '"+filter.item_no[koma:koma+(len(filter.item_no)-koma)].strip()+"')"
                    else:
#                         if xitc.strip()=="":
                        xitn ="it.item_no_='"+filter.item_no.strip()+"'"
                            
        return xitn

    def _filter_item_category(self, xid):
        xitc=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:
                if filter.item_category_code:            
                    if filter.item_category_code.find("|")!=-1:
                        koma=0
                        for n in range(len(filter.item_category_code)):
                            if filter.item_category_code[n:n+1]=="|":
                                if xitc.strip()=="":
                                    xitc="it.item_category_code in ('"+filter.item_category_code[koma:n].strip()+"'"
                                else:
                                    xitc += ", '"+filter.item_category_code[koma:n].strip()+"'"
                                
                                koma=n+1
                            else:
                                if n+1==len(filter.item_category_code):
                                    xitc += ", '"+filter.item_category_code[koma:koma+(len(filter.item_category_code)-koma)].strip()+"')"
                    else:
#                         if xitc.strip()=="":
                        xitc ="it.item_category_code='"+filter.item_category_code.strip()+"'"
                            
        return xitc
                    
    def _filter_location_code(self, xid):
        xlocation=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:
                if filter.location_code:
                    if filter.location_code.find("|")!=-1:
                        koma=0
                        for n in range(len(filter.location_code)):
                            if filter.location_code[n:n+1]=="|":
                                if xlocation.strip()=="":
                                    xlocation="ile.location_code in ('"+filter.location_code[koma:n].strip()+"'"
                                else:
                                    xlocation += ", '"+filter.location_code[koma:n].strip()+"'"
                                
                                koma=n+1
                            else:
                                if n+1==len(filter.location_code):
                                    xlocation += ", '"+filter.location_code[koma:koma+(len(filter.location_code)-koma)].strip()+"')"
                    else:
                        xlocation ="ile.location_code='"+filter.location_code.strip()+"'"
                        
#                     if xWhere.strip()=="":
#                         xWhere="(ile."+xLocation_Code
#                     else:
#                         if xItem_Category_Code.strip()=="":
#                             xWhere=xWhere+" (ile."+xLocation_Code
#                         else: 
#                             xWhere=xWhere+" and ile."+xLocation_Code

        return xlocation
                
    def _filter_product_group(self, xid):
        xpgc=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:
                if filter.product_group_code:            
                    if filter.product_group_code.find("|")!=-1:
                        koma=0
                        for n in range(len(filter.product_group_code)):
                            if filter.product_group_code[n:n+1]=="|":
                                if xpgc.strip()=="":
                                    xpgc="it.product_group_code in ('"+filter.product_group_code[koma:n].strip()+"'"
                                else:
                                    xpgc += ", '"+filter.product_group_code[koma:n].strip()+"'"
                                
                                koma=n+1
                            else:
                                if n+1==len(filter.product_group_code):
                                    xpgc += ", '"+filter.product_group_code[koma:koma+(len(filter.product_group_code)-koma)].strip()+"')"
                    else:
                        xpgc ="it.product_group_code='"+filter.product_group_code.strip()+"'"
                            
        return xpgc
    
    def _filter_wip_bc(self, xid):
        xwip=""
        rbc=self.env['sis.report.filter.bc'].search([('id','=',xid)])
        if len(rbc)>0 :
            for filter in rbc:
                if filter.wip_bc:
                    if filter.wip_bc=='True':
                        xwip="it.status_wip_bc=1"
                    else:
                        xwip="it.status_wip_bc=0"
                            
        return xwip

    def clear_data_bc(self):
        self.rpt_tanggal1=""
        self.rpt_tanggal2=""
        self.rpt_kode_barang=""
        self.rpt_nama_barang=""
        self.get_data_bc()

    def get_data_bc(self):
        if self.rpt_laporan:
            xWhere=""
            zWhere=""
            mainWhere=""
            xFactory, xLokasi=self._get_pabrik_id()
            
            xKode=""
            xNama=""
            if self.rpt_kode_barang:
                xKode="and (LOWER(it.item_no_) like '%"+self.rpt_kode_barang+"%' or it.item_no_ like '%"+self.rpt_kode_barang+"%') "
                zWhere="where (LOWER(it.item_no_) like LOWER('%"+self.rpt_kode_barang+"%') or it.item_no_ like '%"+self.rpt_kode_barang+"%') "
            
            if self.rpt_nama_barang:
                xNama="and (LOWER(it.description_3) like '%"+self.rpt_nama_barang+"%' or it.description_3 like '%"+self.rpt_nama_barang+"%') "
                if zWhere=="":
                    zWhere="where (LOWER(it.description_3) like LOWER('%"+self.rpt_nama_barang+"%') or it.description_3 like '%"+self.rpt_nama_barang+"%') "
                else:
                    zWhere=zWhere+"and (LOWER(it.description_3) like LOWER('%"+self.rpt_nama_barang+"%') or it.description_3 like '%"+self.rpt_nama_barang+"%') "
                
            self.env.cr.execute("delete from sis_inv_bc_first_balance where temp_id="+str(self.id)+";"+\
                                "delete from sis_inv_bc_increase where temp_id="+str(self.id)+";"+\
                                "delete from sis_inv_bc_decrease where temp_id="+str(self.id)+";"+\
                                "delete from sis_inv_bc_first_balance_bk where temp_id="+str(self.id)+";"+\
                                "delete from sis_inv_bc_increase_bk where temp_id="+str(self.id)+";"+\
                                "delete from sis_inv_bc_decrease_bk where temp_id="+str(self.id)+";"+\
                                "delete from sis_report_inv_bc_line where temp_id="+str(self.id)+";")

        rbc=self.env['sis.report.filter.bc'].search([('rpt_name','=',self.rpt_laporan),('factory_code','!=',xFactory)])
        if len(rbc)>0 :
            xbg=""
            xwip=""
            buku_kuning=False
            for filter in rbc:
                xwer=""               
                xwer_ile=""               
                xwer_ibk=""               
                if filter.inc_bk==True:
                    buku_kuning=True
                
                xitc=self._filter_item_category(filter.id)
                xpgc=self._filter_product_group(filter.id)
                xloc=self._filter_location_code(filter.id)
                xitn=self._filter_item_no(filter.id)
                xdc=self._filter_desc2(filter.id)
                xwip=self._filter_wip_bc(filter.id)
                
                if xwip!="":
                    if xwer.strip()=="":
                        xwer = xwip
                    else:
                        xwer += " and "+xwip

                if xitc!="":
                    if xwer.strip()=="":
                        xwer = xitc
                    else:
                        xwer += " and "+xitc
                 
                if xpgc!="":
                    if xwer.strip()=="":
                        xwer = xpgc
                    else:
                        xwer += " and "+xpgc

                if xloc!="":
                    if xwer.strip()=="":
                        xwer = xloc
                    else:
                        xwer += " and "+xloc
                 
                if xitn!="":
                    if xwer.strip()=="":
                        xwer = xitn
                    else:
                        xwer += " and "+xitn
                
                if xdc!="":
                    if xwer.strip()=="":
                        xwer = xdc
                    else:
                        xwer += " and "+xdc

                if xwip!="":
                    if xwer.strip()=="":
                        xwer = xwip
                    else:
                        xwer += " and "+xwip
                
                if filter.bisnis_group==True and filter.factory_code!=3:
                    if xwer.strip()=="":
                        xbg = "ile.bisnis_group='ATI"+filter.factory_code+"' "
                    else:
                        xbg = " and ile.bisnis_group='ATI"+filter.factory_code+"' "

                if filter.inc_bk==True:
                    if xwer.strip()=="":
                        xwer_ile = "(it.buku_kuning=0 and it.exclude_bc=1)"
                        xwer_ibk = "(it.buku_kuning=1 and it.exclude_bc=1)"
                    else:
#                         xwer += " and (it.buku_kuning=1 and it.exclude_bc=1)"
                        xwer_ile = " and (it.buku_kuning=0 and it.exclude_bc=1)"
                        xwer_ibk = " and (it.buku_kuning=1 and it.exclude_bc=1)"

                if xwer.strip()!="":
                    if xWhere.strip()=="":
                        xWhere="("+xwer+")"
                    else:
                        xWhere += " or ("+xwer+")"

            if xWhere.strip()!="":
                xWhere=" and ("+xWhere+")"
#		xWhere=" and "+xWhere

            if self.rpt_tanggal1:
                xTanggal1=self.rpt_tanggal1
            else:
                xTanggal1="2017-05-01"
             
            if self.rpt_tanggal2:
                xTanggal2=self.rpt_tanggal2
            else:
                self.env.cr.execute("select posting_date from sis_ile_odoo_bc order by posting_date desc limit 1")
                rec_data=self.env.cr.fetchall()
                if len(rec_data)>0:
                    for data in rec_data:
                        (xPostingDate,)=data
                         
                xTanggal2=xPostingDate
                
            self._insert_begbal("ile.posting_date<'"+xTanggal1+"'"+xWhere+xbg+xwer_ile)
            self._insert_increase("ile.posting_date between '"+xTanggal1+"' and '"+xTanggal2+"'"+xWhere+xbg+xwer_ile)
            self._insert_decrease("ile.posting_date between '"+xTanggal1+"' and '"+xTanggal2+"'"+xWhere+xbg+xwer_ile)

            self._insert_begbal_bk("ile.posting_date<'"+xTanggal1+"'"+xWhere+xwer_ibk)
            self._insert_increase_bk("ile.posting_date between '"+xTanggal1+"' and '"+xTanggal2+"'"+xWhere+xwer_ibk)
            self._insert_decrease_bk("ile.posting_date between '"+xTanggal1+"' and '"+xTanggal2+"'"+xWhere+xwer_ibk)

            print(str(self.id))
#             print(zWhere)

            if buku_kuning==False:
                self.env.cr.execute("""
                    select distinct ile.item_no, ile.variant_code, it.description_3, ile.base_uom, begbal.quantity as begining_balance, 
                    (case when inc.quantity is null then 0 else inc.quantity end) as increase,
                    (case when dnc.quantity is null then 0 else dnc.quantity end) as decrease, 
                    (case 
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is not null then 0-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is not null then inc.quantity-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is null then inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is null then begbal.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is null then begbal.quantity+inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is not null then begbal.quantity-dnc.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is not null then (begbal.quantity+inc.quantity)-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is null then 0
                    end) as end_balance
                    from sis_ile_odoo_bc ile
                    inner join sis_items_bc it on it.item_no_=ile.item_no
                    left join sis_inv_bc_first_balance begbal on trim(concat(ile.item_no,' ',ile.variant_code))=begbal.item_no and begbal.temp_id="""+str(self.id)+""" and begbal.quantity>=0
                    left join sis_inv_bc_increase inc on inc.item_no=trim(concat(ile.item_no,' ',ile.variant_code)) and inc.temp_id="""+str(self.id)+"""
                    left join sis_inv_bc_decrease dnc on dnc.item_no=trim(concat(ile.item_no,' ',ile.variant_code)) and dnc.temp_id="""+str(self.id)+"""
                      
                    """+zWhere+"""
                      
                    group by ile.item_no, ile.variant_code, it.description_3, ile.base_uom, begbal.quantity, inc.quantity, dnc.quantity
                    having (begbal.quantity!=0 or inc.quantity!=0 or dnc.quantity!=0)
                    order by ile.item_no
                      
                """)
                
            else:
                self.env.cr.execute("""
                    select distinct ile.item_no, ile.variant_code, it.description_3, ile.base_uom, begbal.quantity as begining_balance, 
                    (case when inc.quantity is null then 0 else inc.quantity end) as increase,
                    (case when dnc.quantity is null then 0 else dnc.quantity end) as decrease, 
                    (case 
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is not null then 0-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is not null then inc.quantity-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is null then inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is null then begbal.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is null then begbal.quantity+inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is not null then begbal.quantity-dnc.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is not null then (begbal.quantity+inc.quantity)-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is null then 0
                    end) as end_balance
                    from sis_ile_odoo_bc ile
                    inner join sis_items_bc it on it.item_no_=ile.item_no
                    left join sis_inv_bc_first_balance begbal on trim(concat(ile.item_no,' ',ile.variant_code))=begbal.item_no and begbal.temp_id="""+str(self.id)+""" and begbal.quantity>=0
                    left join sis_inv_bc_increase inc on inc.item_no=trim(concat(ile.item_no,' ',ile.variant_code)) and inc.temp_id="""+str(self.id)+"""
                    left join sis_inv_bc_decrease dnc on dnc.item_no=trim(concat(ile.item_no,' ',ile.variant_code)) and dnc.temp_id="""+str(self.id)+"""
                      
                    """+zWhere+"""
                      
                    group by ile.item_no, ile.variant_code, it.description_3, ile.base_uom, begbal.quantity, inc.quantity, dnc.quantity
                    having (begbal.quantity!=0 or inc.quantity!=0 or dnc.quantity!=0)
                    
                    UNION

                    select distinct ile.item_no, '', it.description_3, ile.base_uom, begbal.quantity as begining_balance, 
                    (case when inc.quantity is null then 0 else inc.quantity end) as increase,
                    (case when dnc.quantity is null then 0 else dnc.quantity end) as decrease, 
                    (case 
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is not null then 0-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is not null then inc.quantity-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is not null and dnc.quantity is null then inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is null then begbal.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is null then begbal.quantity+inc.quantity
                     when begbal.quantity is not null  and inc.quantity is null and dnc.quantity is not null then begbal.quantity-dnc.quantity
                     when begbal.quantity is not null  and inc.quantity is not null and dnc.quantity is not null then (begbal.quantity+inc.quantity)-dnc.quantity
                     when begbal.quantity is null  and inc.quantity is null and dnc.quantity is null then 0
                    end) as end_balance
                    from sis_ile_odoo_bk ile
                    inner join sis_items_bc it on it.item_no_=ile.item_no
                    left join sis_inv_bc_first_balance_bk begbal on ile.item_no=begbal.item_no and begbal.temp_id="""+str(self.id)+""" and begbal.quantity>=0
                    left join sis_inv_bc_increase_bk inc on inc.item_no=ile.item_no and inc.temp_id="""+str(self.id)+"""
                    left join sis_inv_bc_decrease_bk dnc on dnc.item_no=ile.item_no and dnc.temp_id="""+str(self.id)+"""
                      
                    """+zWhere+"""
                      
                    group by ile.item_no, it.description_3, ile.base_uom, begbal.quantity, inc.quantity, dnc.quantity
                    having (begbal.quantity!=0 or inc.quantity!=0 or dnc.quantity!=0)
                      
                """)


            rec_bc=self.env.cr.fetchall()
            xNomer=0
            if len(rec_bc)>0:
                new_lines = self.env['sis.report.inv.bc.line']
                for ibc in rec_bc:
                    (xItemNo, xVarCode, xDescription, xBUOM, xBegBal, xIncrease, xDecrease, xEndBal)=ibc
#                     (xItemNo, xDescription, xBUOM, xBegBal, xIncrease, xDecrease, xEndBal)=ibc
                    xNomer=xNomer+1
#                     vals={
#                         'line_no'       :xNomer,
#                         'item_no'       :xItemNo,
#                         'description'   :xDescription,
#                         'base_uom'      :xBUOM,
#                         'begbal'        :xBegBal,
#                         'increase'      :xIncrease,
#                         'decrease'      :xDecrease,
#                         'adjustment'    :0,
#                         'endbal'        :xEndBal,
#                         'remark'        :'Sesuai',
#                         'temp_id'       :self.id
#                     }

                    if xVarCode.strip()=='':
                        vals={
                            'line_no'       :xNomer,
                            'item_no'       :xItemNo,
                            'description'   :xDescription,
                            'base_uom'      :xBUOM,
                            'begbal'        :xBegBal,
                            'increase'      :xIncrease,
                            'decrease'      :xDecrease,
                            'adjustment'    :0,
                            'endbal'        :xEndBal,
                            'remark'        :'Sesuai',
                            'temp_id'       :self.id
                        }
                    else:                          
                        vals={
                            'line_no'       :xNomer,
                            'item_no'       :xItemNo+' '+xVarCode,
                            'description'   :xDescription,
                            'base_uom'      :xBUOM,
                            'begbal'        :xBegBal,
                            'increase'      :xIncrease,
                            'decrease'      :xDecrease,
                            'adjustment'    :0,
                            'endbal'        :xEndBal,
                            'remark'        :'Sesuai',
                            'temp_id'       :self.id
                        }
                    
                    new_lines += new_lines.new(vals)
  
                self.rpt_inv_line=new_lines

#     def plus(a):
#         if a==-1:
#             return ''    
#         c=chr(65+(a%26))
#         b=''
#         if a//26>0:
#             b=plus(a//26-1)
#         return b+c
    
    @api.multi    
    def write_xlsx(self):
        xFactory, xLokasi=self._get_pabrik_id()
        xtgl=""
#         xLaporan=self.rpt_laporan
        if self.rpt_tanggal1:
            xtgl=self.rpt_tanggal1.replace('-','')

        if self.rpt_tanggal2:
            if xtgl=="":
                xtgl=self.rpt_tanggal2.replace('-','')
            else:
                xtgl += "-"+self.rpt_tanggal2.replace('-','')

        if xtgl=="":
            xLaporan="ATI"+xLokasi+"-"+self.rpt_laporan.replace(' ','_')+"_"+str(self.id)+".xlsx"
        else:
            xLaporan="ATI"+xLokasi+"-"+self.rpt_laporan.replace(' ','_')+"_"+xtgl+"_"+str(self.id)+".xlsx"
            
#         print(self.rpt_laporan.replace(' ','_')+"_"+str(self.id)+".xlsx")
#         print(xLokasi)
        workbook = xlsxwriter.Workbook('/tmp/'+xLaporan)        
#         workbook = xlsxwriter.Workbook('/home/rusdi/Documents/shared/ati_laporan_mutasi.xlsx')        
        worksheet = workbook.add_worksheet()
        
        bold = workbook.add_format({'bold': True})
        header_format = workbook.add_format({'bold': 1, 'border': 1, 'align': 'center', 'valign': 'vcenter', 'fg_color': '#BDBDDF'}) #AFAFD8
        title_format = workbook.add_format()
        title_format.set_font_size(16)
        title_format.set_bold()
        title_format2 = workbook.add_format()
        title_format2.set_font_size(16)
        title_format2.set_bold()
        title_format2.set_align('right')
        title_format3 = workbook.add_format()
        title_format3.set_font_size(16)
        title_format3.set_bold()
        date_format2 = workbook.add_format()
        date_format2.set_bold() 
        date_format2.set_align('right')
        date_format3 = workbook.add_format()
        date_format3.set_bold() 
        pabrik_format = workbook.add_format()
        pabrik_format.set_bold()
        pabrik_format.set_align('right')
        row_format = workbook.add_format({'border': 1, 'valign': 'vcenter'})
        row_center_format = workbook.add_format({'border': 1, 'align': 'center', 'valign': 'vcenter'})
        row_right_format = workbook.add_format({'border': 1, 'align': 'right', 'valign': 'vcenter'})
        cell_format = workbook.add_format()
        cell_format.set_border(2)
        cell_format.set_border_color('red')
        
#        versi 1 dan 2
        worksheet.insert_image('A1', '/tmp/logo-aja.png')
        if xLokasi=="1":
            worksheet.write(0,2,"PT Aneka Tuna Indonesia - Gempol Factory", bold)
            worksheet.write(1,2,"Jl. Raya Surabaya-Malang Km. 38 Gempol Pasuruan", bold)
        else:
            worksheet.write(0,2,"PT Aneka Tuna Indonesia - Pandaan Factory", bold)
            worksheet.write(1,2,"Jl. Gunung Gangsir RT 07/09, Nogosari, Pandaan Pasuruan", bold)

#        versi 3
#         worksheet.insert_image('L1', '/home/rusdi/Documents/shared/logo-aja.png')
#         if xLokasi=="1":
#             worksheet.write(0,10,"PT Aneka Tuna Indonesia - Gempol Factory", pabrik_format)
#             worksheet.write(1,10,"Jl. Raya Surabaya-Malang Km. 38 Gempol Pasuruan", pabrik_format)
#         else:
#             worksheet.write(0,10,"PT Aneka Tuna Indonesia - Pandaan Factory", pabrik_format)
#             worksheet.write(1,10,"Jl. Gunung Gangsir RT 07/09, Nogosari, Pandaan Pasuruan", pabrik_format)

#        versi 1
#         worksheet.write(3,0,self.rpt_laporan, title_format)
#         if self.rpt_tanggal1 and self.rpt_tanggal2:
#             worksheet.write(4,0,"Tanggal : "+self.rpt_tanggal1+" s/d "+self.rpt_tanggal2, bold)
#         elif self.rpt_tanggal1:
#             worksheet.write(4,0,"Tanggal : "+self.rpt_tanggal1, bold)
#         else:
#             worksheet.write(4,0,"Tanggal : -", bold)

#        versi 2
        worksheet.write(0,11,self.rpt_laporan, title_format2)
        if self.rpt_tanggal1 and self.rpt_tanggal2:
            worksheet.write(1,11,"Tanggal : "+self.rpt_tanggal1+" s/d "+self.rpt_tanggal2, date_format2)
        elif self.rpt_tanggal1:
            worksheet.write(1,11,"Tanggal : "+self.rpt_tanggal1, date_format2)
        else:
            worksheet.write(1,11,"Tanggal : -", date_format2)

#        versi 3
#         worksheet.write(0,0,self.rpt_laporan, title_format3)
#         if self.rpt_tanggal1 and self.rpt_tanggal2:
#             worksheet.write(1,0,"Tanggal : "+self.rpt_tanggal1+" s/d "+self.rpt_tanggal2, date_format3)
#         elif self.rpt_tanggal1:
#             worksheet.write(1,0,"Tanggal : "+self.rpt_tanggal1, date_format3)
#         else:
#             worksheet.write(1,0,"Tanggal : -", date_format3)
        
#        versi 1
#         worksheet.write(6,0,"No.", header_format)
#         worksheet.write(6,1,"Kode Barang", header_format)
#         worksheet.write(6,2,"Nama Barang", header_format)
#         worksheet.write(6,3,"Satuan", header_format)
#         worksheet.write(6,4,"Saldo Awal", header_format)
#         worksheet.write(6,5,"Pemasukan", header_format)
#         worksheet.write(6,6,"Pengeluaran", header_format)
#         worksheet.write(6,7,"Penyesuaian", header_format)
#         worksheet.write(6,8,"Saldo Akhir", header_format)
#         worksheet.write(6,9,"Stock Opname", header_format)
#         worksheet.write(6,10,"Selisih", header_format)
#         worksheet.write(6,11,"Keterangan", header_format)

#        versi 2 dan 3
        worksheet.write(4,0,"No.", header_format)
        worksheet.write(4,1,"Kode Barang", header_format)
        worksheet.write(4,2,"Nama Barang", header_format)
        worksheet.write(4,3,"Satuan", header_format)
        worksheet.write(4,4,"Saldo Awal", header_format)
        worksheet.write(4,5,"Pemasukan", header_format)
        worksheet.write(4,6,"Pengeluaran", header_format)
        worksheet.write(4,7,"Penyesuaian", header_format)
        worksheet.write(4,8,"Saldo Akhir", header_format)
        worksheet.write(4,9,"Stock Opname", header_format)
        worksheet.write(4,10,"Selisih", header_format)
        worksheet.write(4,11,"Keterangan", header_format)


        worksheet.set_column(0, 0, 6)
        worksheet.set_column(1, 1, 20)
        worksheet.set_column(2, 2, 60)
        worksheet.set_column(3, 3, 10)
        worksheet.set_column(4, 10, 15)
        worksheet.set_column(11, 11, 20)
        
#         for osheet in (workbook.worksheets()):
#             osheet.set_column('A', 12)
#             osheet.set_column('B', 12)
#             osheet.set_column('C', 12)
#             osheet.set_column('D', 12)
#             osheet.set_column('E', 12)
#             osheet.set_column('F', 12)
#             osheet.set_column('G', 12)
#             osheet.set_column('H', 12)
#             osheet.set_column('I', 12)
#             osheet.set_column('J', 12)
#             osheet.set_column('K', 12)
#             osheet.set_column('L', 12)
            

        
        self.env.cr.execute("SELECT line_no, item_no, description, base_uom, begbal, increase, decrease, adjustment, endbal, remark "+\
                            "from sis_report_inv_bc_line where temp_id="+str(self.id)+" order by line_no")
        rpt=self.env.cr.fetchall()
#        versi 1
#         xNomer=6

#        versi 2
        xNomer=4
        if len(rpt)>0:
            for irpt in rpt:
                (xline_no, xitem_no, xdescription, xbase_uom, xbegbal, xincrease, xdecrease, xadjust, xendbal, xremark )=irpt
                xNomer=xNomer+1
  #              for kolom in range(11):
                worksheet.write(xNomer,0,str(xline_no)+". ", row_right_format)
                worksheet.write(xNomer,1,xitem_no, row_format)
                worksheet.write(xNomer,2,xdescription, row_format)
                worksheet.write(xNomer,3,xbase_uom, row_center_format)
                worksheet.write(xNomer,4,xbegbal, row_format)
                worksheet.write(xNomer,5,xincrease, row_format)
                worksheet.write(xNomer,6,xdecrease, row_format)
                worksheet.write(xNomer,7,xadjust, row_format)
                worksheet.write(xNomer,8,xendbal, row_format)
                worksheet.write(xNomer,9,xendbal, row_format)
                worksheet.write(xNomer,10,xadjust, row_format)
                worksheet.write(xNomer,11,xremark, row_center_format)
#                    print(str(xNomer)+" - "+str(kolom))
    
#            versi 1
#             worksheet.autofilter('A7:L7')

#            versi 2
            worksheet.autofilter('A5:L5')
            
        workbook.close()

        rec=self.env['sis.report.inv.bc'].search([('id','=',self.id)])
        for r in rec:
            vals={ 
                    'rpt_xlsx':base64.b64encode(open("/tmp/"+xLaporan, "rb").read())
#                   'rpt_xlsx':base64.b64encode(open("/home/rusdi/Documents/shared/ati_laporan_mutasi.xlsx", "rb").read())
                }
            r.write(vals)

#         print('/web/content/sis.report.inv.bc/%s/rpt_xlsx/'+xLaporan+'?download=true')
        return {
            'type': 'ir.actions.act_url',
            'name': 'Report',
            'url': '/web/content/sis.report.inv.bc/%s/rpt_xlsx/%s?download=true' % (str(self.id), xLaporan)
#             'url': '/web/content/sis.report.inv.bc/%s/rpt_xlsx/ati_laporan_mutasi.xlsx?download=true' %(self.id),
        }

            
    def _get_pabrik_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
             
        for def_lokasi in rc_lokasi:
            (xpabrik_id,)=def_lokasi

        if xpabrik_id=="ATI1":
            xLokasi='1'
            xFactory='2'
        elif xpabrik_id=="ATI2":
            xLokasi='2'
            xFactory='1'

        return xFactory,xLokasi
    
    @api.model
    def _get_laporan(self):
        lst_report=list()
        
        xFactory, xLokasi=self._get_pabrik_id()
        
#        self.env.cr.execute("select distinct tgl_produksi from sis_fish_status_header")
        cSQL="select distinct rpt_name from sis_report_filter_bc where factory_code<>'"+xFactory+"' and set_active=True order by rpt_name"
        self.env.cr.execute(cSQL)
        rc_report=self.env.cr.fetchall()
        
        if len(rc_report)>0:
#            raise UserError("No report available!")
#        else:
            for def_report in rc_report:
                (xreport,)=def_report
                lst_report.append((xreport, xreport))
            return lst_report

        
    
class report_inventory_bc_line(models.TransientModel):
    _name  ='sis.report.inv.bc.line'
    _description = 'Form Detail Report Inventory for BC'
    
    rel_inv_line_id = fields.Many2one('sis.report.inv.bc', string="Inv. ID")
    line_no         = fields.Integer(string="No.")
    item_no         = fields.Char(string="Kode Barang", size=20)
    description     = fields.Char(string="Nama Barang", size=100)
    base_uom        = fields.Char(string="Satuan", size=10)
    begbal          = fields.Float(string="Saldo Awal")
    increase        = fields.Float(string="Pemasukan")
    decrease        = fields.Float(string="Pengeluaran")
    adjustment      = fields.Float(string="Penyesuaian")
    endbal          = fields.Float(string="Saldo Akhir")
    remark          = fields.Char(string="Keterangan", size=50)
    temp_id         = fields.Float(string="Temp ID")
    
    
