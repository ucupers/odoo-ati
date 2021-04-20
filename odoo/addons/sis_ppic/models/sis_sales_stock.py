from odoo import models, fields, api, _
from odoo.exceptions import UserError
from _datetime import datetime, timedelta
    
class sis_pps_sales_stock(models.Model):
    _name='sis.pps.sales.stock'

    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    
    detailnum = fields.Integer(string='#')
    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    uom = fields.Char(size=20,string="___UoM___")
    qtyperuom = fields.Float(string='Qty/UoM')
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('sales','Sales'),('unlabeled','Unlabeled'),('labeled','Labeled')],default='sales',string="Type")

    t0 = fields.Integer(string="Beg.Bal") #saldo awal
    t1 = fields.Integer(string="1____")
    t2 = fields.Integer(string="2____")
    t3 = fields.Integer(string="3____")
    t4 = fields.Integer(string="4____")
    t5 = fields.Integer(string="5____")
    t6 = fields.Integer(string="6____")
    t7 = fields.Integer(string="7____")
    t8 = fields.Integer(string="8____")
    t9 = fields.Integer(string="9____")
    t10 = fields.Integer(string="10__")
    t11 = fields.Integer(string="11____")
    t12 = fields.Integer(string="12____")
    t13 = fields.Integer(string="13____")
    t14 = fields.Integer(string="14____")
    t15 = fields.Integer(string="15____")
    t16 = fields.Integer(string="16____")
    t17 = fields.Integer(string="17____")
    t18 = fields.Integer(string="18____")
    t19 = fields.Integer(string="19____")
    t20 = fields.Integer(string="20____")
    t21 = fields.Integer(string="21____")
    t22 = fields.Integer(string="22____")
    t23 = fields.Integer(string="23____")
    t24 = fields.Integer(string="24____")
    t25 = fields.Integer(string="25____")
    t26 = fields.Integer(string="26____")
    t27 = fields.Integer(string="27____")
    t28 = fields.Integer(string="28____")
    t29 = fields.Integer(string="29____")
    t30 = fields.Integer(string="30____")
    t31 = fields.Integer(string="31____")

    a1 = fields.Boolean(string="__A1", default=False)
    a2 = fields.Boolean(string="__A2", default=False)
    a3 = fields.Boolean(string="__A3", default=False)        
    a4 = fields.Boolean(string="__A4", default=False)
    a5 = fields.Boolean(string="__A5", default=False)
    a6 = fields.Boolean(string="__A6", default=False)        
    a7 = fields.Boolean(string="__A7", default=False)
    a8 = fields.Boolean(string="__A8", default=False)
    a9 = fields.Boolean(string="__A9", default=False)        
    a10 = fields.Boolean(string="__A10", default=False)
    a11 = fields.Boolean(string="__A11", default=False)
    a12 = fields.Boolean(string="__A12", default=False)        
    a13 = fields.Boolean(string="__A13", default=False)
    a14 = fields.Boolean(string="__A14", default=False)
    a15 = fields.Boolean(string="__A15", default=False)        
    a16 = fields.Boolean(string="__A16", default=False)
    a17 = fields.Boolean(string="__A17", default=False)
    a18 = fields.Boolean(string="__A18", default=False)        
    a19 = fields.Boolean(string="__A19", default=False)
    a20 = fields.Boolean(string="__A20", default=False)
    a21 = fields.Boolean(string="__A21", default=False)        
    a22 = fields.Boolean(string="__A22", default=False)
    a23 = fields.Boolean(string="__A23", default=False)
    a24 = fields.Boolean(string="__A24", default=False)        
    a25 = fields.Boolean(string="__A25", default=False)
    a26 = fields.Boolean(string="__A26", default=False)
    a27 = fields.Boolean(string="__A27", default=False)        
    a28 = fields.Boolean(string="__A28", default=False)
    a29 = fields.Boolean(string="__A29", default=False)
    a30 = fields.Boolean(string="__A30", default=False)        
    a31 = fields.Boolean(string="__A31", default=False)
    
    invist29 = fields.Boolean(compute='_compute_invist29',string='__Invis')
    invist30 = fields.Boolean(compute='_compute_invist30',string='__Invis')
    invist31 = fields.Boolean(compute='_compute_invist31',string='__Invis')

    hideline = fields.Boolean(string='Hide Line') 
    
    so_current_id=fields.One2many('sis.pps.sales.current','header_id')
    
    def open_soview(self): 
        if self.variant_code:
            variant=self.variant_code
        else:
            variant=''
        if self.type=='sales':
            return {
                'name': self.description + ' - '+variant,
                'res_model': 'sis.pps.so.current',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_so_current_tree').id,
                'target': 'new',
                'nodestroy':True,
                'domain':"[('header_id','=',"+str(self.id)+")]"
            }

    @api.one
    @api.depends('month','year')
    def _compute_invist29(self): 
        if self.month ==2 and self.year%4!=0:
            self.invist29=True
        else:
            self.invist29=False

    @api.one
    @api.depends('month')
    def _compute_invist30(self): 
        if self.month != 2:
            self.invist30=False
        else:
            self.invist30=True
 
    @api.one
    @api.depends('month')       
    def _compute_invist31(self): 
        if self.month in (1,3,5,7,8,10,12):
            self.invist31=False
        else:
            self.invist31=True

    def countfgstock(self):
        self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_temp_sales")
        self.env.cr.execute("CREATE TEMP TABLE sis_ile_temp_sales AS SELECT * FROM sis_ile; ")


        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','production')])
        for prod in prods:
            if  prod.variant_code==False:
                variant=''
            else:
                variant=prod.variant_code
            ## UPDATE ACTUAL PRODUCTION FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_temp_sales"+ \
                            " where item_no='"+prod.item_no+"' and variant='"+variant+"'" \
                            " and entrytype = 'Output'" + \
                            " and bg='"+prod.ati12.upper()+"'")
            proddates=self.env.cr.fetchall()
            for proddate in proddates:
                (tgl,)=proddate
            tglnow=(datetime.now()-timedelta(days=3)).strftime("%Y-%m-%d")
            if tgl==None:
                tgl=tglnow
            if tglnow>tgl :
                tgl=tglnow
             
            valsprod={}
#             for counter in range (1,32):
#                 valsprod.update({'a'+str(counter):False})

            if tgl!=None:
                year=int(tgl[:4])
                month=int(tgl[5:7])
                day=int(tgl[8:10])
                
                runyear=self.year
                runmonth=self.month

                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    for runday in range(1,32):
                        if year*10000+month*100+day<runyear*10000+runmonth*100+runday:
                            valsprod.update({'a'+str(runday):False})
                        else:
                            valsprod.update({'a'+str(runday):True})
                
                    ##UPDATE PRODUCTION
                    self.env.cr.execute("select extract(day from posting_date),sum(quantity) from sis_ile_temp_sales "+ \
                                    " where extract(month from posting_date)="+str(self.month)+ \
                                    " and extract(year from posting_date)="+str(self.year)+ \
                                    " and item_no='"+prod.item_no+"' and variant='"+variant+"'" \
                                    " and entrytype ='Output'" + " and bg='"+prod.ati12.upper()+"'"+ \
                                    " group by extract(day from posting_date)")
                    actprods=self.env.cr.fetchall()
                    for counter in range (1,32):
                        if valsprod['a'+str(int(counter))]==True:
                            valsprod.update({'t'+str(counter):0})
                    for actprod in actprods:
                        (tgl,qty)=actprod
                        try:
                            if valsprod['a'+str(int(tgl))]==True:
                                valsprod['t'+str(int(tgl))] = qty / prod.qtyperuom
                        except:
                            pass
                    prod.write(valsprod)
        self.update_inventory(True)

    def update_inventory(self,calclabeled):
        invs=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','inventory')])
        for inv in invs:
            if calclabeled:
                self.calc_include_labeled(inv)
            valsrun={}
            sales=self.env['sis.pps.detail'].search([('header_id','=',inv.header_id.id),('detailnum','=',inv.detailnum),('type','=','sales')])
            prod=self.env['sis.pps.detail'].search([('header_id','=',inv.header_id.id),('detailnum','=',inv.detailnum),('type','=','production')])
            valsrun={'t0':inv['t0']}
            for it in range(1,32):
                if inv['a'+str(it)]==False:
                    valsrun.update({'t'+str(it):valsrun['t'+str(it-1)]+prod['t'+str(it)]-sales['t'+str(it)]})
                else:
                    valsrun.update({'t'+str(it):inv['t'+str(it)]})                
            inv.write(valsrun)
            

    def calc_include_labeled(self,invori):
        if  invori.variant_code==False:
            variant=''
        else:
            variant=invori.variant_code
        invs=[(invori.item_no,invori.description,variant,invori.variant_code)]
        labeled=self.env['sis.items'].search([('refitem','=',invori.item_no)])
        for label in labeled:
            variants=self.env['sis.item.variants'].search([('itemno','=',label.itemno)])
            if len(variants)>1:
                for var in variants:            
                    if  var.variant==False:
                        variant=''
                    else:
                        variant=var.variant
                    invs+=[(var.itemno,label.description,variant,var.variant)]
            else:
                invs+=[(label.itemno,label.description,'',False)]

        valsinv={}

        ##inisialisasi
        t0=0
        for counter in range (0,32):
            valsinv.update({'t'+str(counter):0})
        for counter in range (1,32):
            valsinv.update({'a'+str(counter):False})
        self.env.cr.execute("delete from sis_pps_inv_detail "+ \
                    " where header_id="+str(invori.id))
            
        #perhitungan per item no per variant
        for (itemno,description,variant,variant_code) in invs:
            ## UPDATE ACTUAL INVENTORY FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_temp_sales"+ \
                            " where item_no='"+itemno+"' and variant='"+variant+"'" \
                            " and bg='"+invori.ati12.upper()+"'")
            invdates=self.env.cr.fetchall()
            for invdate in invdates:
                (tgl,)=invdate
          
            if tgl!=None:
                year=int(tgl[:4])
                month=int(tgl[5:7])
                day=int(tgl[8:10])
                
                runyear=self.year
                runmonth=self.month
    
                #CALCULATE T0
                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp_sales"+ \
                                    " where item_no='"+itemno+"' and variant='"+variant+"'" \
                                    " and bg='"+invori.ati12.upper()+"'" +\
                                    " and posting_date<'"+str(runyear)+"-"+str(runmonth)+"-1'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0run,)=stock
                    
                else:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp_sales"+ \
                                    " where item_no='"+itemno+"' and variant='"+variant+"'" \
                                    " and bg='"+invori.ati12.upper()+"'" +\
                                    " and posting_date<='"+str(year)+"-"+str(month)+"-"+str(day)+"'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0run,)=stock

                    t0year=year
                    t0month=month

                    while t0year*100+t0month<runyear*100+runmonth:
                        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',itemno),('variant_code','=',variant_code),('type','=','production'),('year','=',t0year),('month','=',t0month)])
                        t0inc=0
                        for t0day in range(1,32):
                            if (t0year==year and t0month==month and t0day>day) or\
                               (t0year==year and t0month<month) or\
                               (t0year<year):
                                for prod in prods:
                                    t0inc+=prod['t'+str(t0day)]
                        t0month+=1
                        if t0month>12:
                            t0month=1
                            t0year+=1
                        t0run+=t0inc
                if t0run:
                    t0run/=invori.qtyperuom
                else:
                    t0run=0;
                t0+=t0run
                
                # CALCULATE ACTUAL INVENTORY
                
                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    for runday in range(1,32):
                        if year*10000+month*100+day<runyear*10000+runmonth*100+runday:
                            break
                        valsinv.update({'a'+str(runday):True})

                ##UPDATE INVENTORY
                self.env.cr.execute("select extract(day from posting_date), sum(quantity) from sis_ile_temp_sales "+ \
                                " where extract(month from posting_date)="+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ \
                                " and item_no='"+itemno+"' and variant='"+variant+"'" \
                                " and bg='"+invori.ati12.upper()+"'"+ \
                                " group by extract(day from posting_date)")
                actinvs=self.env.cr.fetchall()

                valsrun={}
                for counter in range (0,32):
                    valsrun.update({'t'+str(counter):0})
                valsrun.update({'t0':t0run})
                
                for actinv in actinvs:
                    (tgl,qty)=actinv
                    try:
                        if valsinv['a'+str(int(tgl))]==True:
                            valsrun['t'+str(int(tgl))] = qty / invori.qtyperuom
                    except:
                        pass
                    
                s=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',invori.detailnum),('type','=','sales')])
                p=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',invori.detailnum),('type','=','production')])
                for counter in range (1,32):
                    if valsinv['a'+str(int(counter))]==True:
                        if counter==1:
                            valsinv['t0']+=valsrun['t0']  
                        valsrun['t'+str(counter)]+=valsrun['t'+str(counter-1)]                   
                        valsinv['t'+str(counter)]+=valsrun['t'+str(counter)]
                    else:
                        valsinv['t'+str(counter)]+=p['t'+str(counter)]-s['t'+str(counter)]                        


                    
            #--------------------------------------------------------------------------------------------------------------------------------
                ##UPDATE INVENTORY DETAIL
               
                self.env.cr.execute("select extract(day from posting_date), entrytype, sum(quantity) from sis_ile_temp_sales "+ \
                                " where extract(month from posting_date)="+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ \
                                " and item_no='"+itemno+"' and variant='"+variant+"'" \
                                " and bg='"+invori.ati12.upper()+"'"+ \
                                " group by extract(day from posting_date), entrytype"+\
                                " order by entrytype, extract(day from posting_date)")
                actinvs=self.env.cr.fetchall()
                
                valsinvdetail={}
#                 for counter in range (1,32):
#                     valsinv.update({'t'+str(counter):0})
                currentrytype=''
                for actinv in actinvs:
                    (tgl,entrytype,qty)=actinv
                    if valsinv['a'+str(int(tgl))]==True:
                        if currentrytype!=entrytype:
                            if currentrytype!='':
                                valsinvdetail.update({'entrytype':currentrytype})
                                
                                
                                
                                self.env['sis.pps.inv.detail'].create(valsinvdetail)
                            valsinvdetail={'item_no':itemno,
                                     'description':description,
                                     'variant':variant,
                                     'header_id':invori.id
                                     }
                            currentrytype=entrytype                    
                        valsinvdetail.update({'t'+str(int(tgl)): qty / invori.qtyperuom})

                valsinvdetail.update({'entrytype':currentrytype})
                self.env['sis.pps.inv.detail'].create(valsinvdetail)

        invori.write(valsinv)
        