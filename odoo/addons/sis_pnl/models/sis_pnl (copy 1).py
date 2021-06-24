from odoo import models, fields,api
from datetime import datetime,timedelta
from odoo.exceptions import UserError
class sis_pnl_header(models.Model):
    _name='sis.pnl.header'
    _rec_name='no'
    date =fields.Datetime(string="Estimation Date", default=datetime.today(),required=True)
    no =fields.Char(size=20,string="No")
    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    exchangerate = fields.Integer(string="Exchange rate",required=True)
    ati12 = fields.Selection([('ATI1','ATI1'),('ATI2','ATI2')],string="ATI1/ATI2",required=True)   
    rpo3pct= fields.Integer(string="Labelling add %",required=True, default=0)
    
    sourcemonth = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Source Month",required=True)
    sourceyear = fields.Integer(string="Source Year",required=True)    
    detail_id=fields.One2many('sis.pnl.detail','header_id',string="Detail")
    sales_id=fields.One2many('sis.pnl.sales','header_id',string="Detail")
    cogs_id=fields.One2many('sis.pnl.cogs','header_id',string="Detail")
    selling_id=fields.One2many('sis.pnl.selling','header_id',string="Detail")        
    expense_id=fields.One2many('sis.pnl.expense','header_id',string="Detail")
    forex_id=fields.One2many('sis.pnl.forex','header_id',string="Detail")
    otherinex_id=fields.One2many('sis.pnl.otherinex','header_id',string="Detail")
    financialinex_id=fields.One2many('sis.pnl.financialinex','header_id',string="Detail")
    provision_id=fields.One2many('sis.pnl.provision','header_id',string="Detail")
    locked=fields.Boolean(string='Locked',default=False)
    @api.model
    def create(self, values):
        no=self.env['ir.sequence'].next_by_code('sis.pnl.sequence')
        values.update({'no':no}) 
        res_id = super(sis_pnl_header, self).create(values)
        return res_id
    @api.multi
    def write(self, vals):
        if self.locked:
            raise UserError('This PnL Estimation is already locked')
        vals.update({'date':datetime.now()+timedelta(hours=7)})
        return models.Model.write(self, vals)
    def getnav(self):
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_items")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_items AS SELECT * FROM sis_items; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_item_variants")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_item_variants AS SELECT * FROM sis_item_variants; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_ile")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_ile AS SELECT * FROM sis_ile; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_ve_amount")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_ve_amount AS SELECT * FROM sis_ve_amount; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_ile_remqtyamt")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_ile_remqtyamt AS SELECT * FROM sis_ile_remaining_quantity_amount; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_production_bom")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_production_bom AS SELECT * FROM sis_production_bom; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_sales_invoice")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_sales_invoice AS SELECT * FROM sis_sales_invoice; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_sales_credit_memo")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_sales_credit_memo AS SELECT * FROM sis_sales_credit_memo; ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_gl_entry")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_gl_entry AS SELECT * FROM sis_gl_entry; ")
        self.compute()

    def compute(self):
        accs=self.env['sis.account.setting'].search([],order="account")
        accvals={}
        actualvals={}
        self.date=datetime.now()
        wasacc='first'
        for acc in accs:
            if wasacc!=acc.accountname:
                subtotal=0
                actual=0
            if acc.account=='01.sales':
                subtotal=self.get_sales_forecast()
                
            if acc.account=='02.cogs':
                self.get_cogs_calculate()
                subtotal=self.get_cogs_forecast()
            if acc.account=='04.selling':   
                classname='sis.pnl.selling'
            if acc.account=='05.expense':
                classname='sis.pnl.expense'
            if acc.account=='06.forex':
                classname='sis.pnl.forex'
            if acc.account=='07.otherinex':
                classname='sis.pnl.otherinex'
            if acc.account=='10.financialin':
                classname='sis.pnl.financialinex'
            if acc.account=='11.financialex':
                classname='sis.pnl.financialinex'
            if acc.account=='13.provision':
                classname='sis.pnl.provision'
            if acc.account=='14.deffered':
                classname='sis.pnl.provision'
            
            if acc.account=='01.sales' or acc.account=='04.selling' or acc.account=='05.expense' or acc.account=='06.forex' or acc.account=='07.otherinex' \
               or acc.account=='10.financialin' or acc.account=='11.financialex' or acc.account=='13.provision' or acc.account=='14.deffered':
                if acc.end:
                    self.env.cr.execute("select no,name from sis_gl_account where no>='"+acc.start+"' and no<='"+acc.end+"' and account_type='Posting'")
                else:
                    self.env.cr.execute("select no,name from sis_gl_account where no='"+acc.start+"' and account_type='Posting'")
                glaccs=self.env.cr.fetchall()
                for glacc in glaccs:
                    (no,name)=glacc
                    
                    if acc.account=='01.sales':
                        self.get_sales_actual(no)
                        continue
                    if acc.account=='02.cogs':
                        self.get_cogs_actual(no)
                        continue
                    #FORECAST
                    self.env.cr.execute("select sum(amount) from sis_temp_gl_entry where accno='"+no+"' and extract(month from postingdate)="+str(self.sourcemonth)+ \
                                        " and extract(year from postingdate)="+str(self.sourceyear)+" and bg='"+self.ati12+"'")
                    amounttemp=self.env.cr.fetchall()
                    if amounttemp!=[(None,)]:
                        [(amount,)]=amounttemp
                    else:
                        amount=0
                    if acc.opposite==True:
                        amount=-amount
                    subtotal+=amount
                    vals={
                        'header_id':self.id,
                        'no':no,
                        'name':name,
                        'amount':amount
                        }                    
                    rs=self.env[classname].search([('header_id','=',self.id),('no','=',no)])
                    if rs and len(rs)>0 :
                        rs.write(vals)
                    else:
                        self.env[classname].create(vals)
                    #FORECAST
                    self.env.cr.execute("select sum(amount) from sis_temp_gl_entry where accno='"+no+"' and extract(month from postingdate)="+str(self.month)+ \
                                        " and extract(year from postingdate)="+str(self.year)+"  and bg='"+self.ati12+"'")
                    amounttemp=self.env.cr.fetchall()
                    if amounttemp!=[(None,)]:
                        [(amount,)]=amounttemp
                    else:
                        amount=0
                    if acc.opposite==True:
                        amount=-amount
                    actual+=amount
            if acc.account=='03.gross' or acc.account=='08.totalexpense' or acc.account=='09.totaloperating' or acc.account=='12.profit' or acc.account=='15.total':                                                                
                nums=acc.sum.split(',')
                for num in nums:
                    for av in accvals:
                        if av[:2]==num:
                            subtotal+=accvals[av]
                            actual+=actualvals[av]
                            break
            if acc.account=='01.sales':
                fore,act=self.get_sales_amount()
                subtotal=fore+act
                actual=act
                if acc.opposite==True:
                    subtotal=-subtotal
                    actual=-actual
            if acc.account=='02.cogs':
                fore,act=self.get_cogs_amount()
                subtotal=fore+act
                actual=act
                if acc.opposite==True:
                    subtotal=-subtotal
                    actual=-actual
            if subtotal==None:
                subtotal=0
            try:
                accvals[acc.accountname]=subtotal
                actualvals[acc.accountname]=actual                
            except:
                accvals.update({acc.accountname :subtotal})
                actualvals.update({acc.accountname :actual})
            
            vals={
                'header_id':self.id,
                'description':acc.accountname,
                'amount':subtotal,
                'bold':acc.bold,
                'actual':actual
                }                    
            rs=self.env['sis.pnl.detail'].search([('header_id','=',self.id),('description','=',acc.accountname)])
            if rs and len(rs)>0 :
                rs.write(vals)
            else:
                self.env['sis.pnl.detail'].create(vals)#                 
            wasacc=acc.accountname

    def get_cogs_calculate(self):
        
        #MATERIALS
        self.env.cr.execute(" select item_no,description,uom, sum(quantity), sum(costactual),sum(costexpected),itc,pgc "+\
                            " from sis_temp_ve_amount where valuation_date<'"+str(self.year)+"-"+str(self.month)+"-01' "\
                            " and itc in ('PKG','SS') and bg='"+self.ati12+"' "+\
                            " group by item_no,description,uom, itc,pgc")
        mats=self.env.cr.fetchall()
        matcost={}
        matdata={}
        for mat in mats:
            (itemno,description,uom,remqty,costact,costexp,itc,pgc)=mat
            if remqty==0:
                continue
            matcost.update({itemno:{'costunit':(costact+costexp)/remqty,
                              'qty':remqty}})
            matdata.update({itemno:{'name':description,
                              'uom':uom,
                              'itc':itc,
                              'pgc':pgc,
                              'used':0}})

        #WIP 
        self.env.cr.execute(" select item_no,description,uom, sum(quantity), sum(costactual),sum(costexpected),itc,pgc "+\
                    " from sis_temp_ve_amount where extract(month from valuation_date)="+str(self.sourcemonth)+ \
                    " and extract(year from valuation_date)="+str(self.sourceyear) + \
                    " and item_no like 'WIP-%' and bg='"+self.ati12+"' and entrytype='Output' "+\
                    " group by item_no,description,uom, itc,pgc ")
        wips=self.env.cr.fetchall()
        for wip in wips:
            (itemno,description,uom,qty,costact,costexp,itc,pgc)=wip
            if qty==0:
                continue
            matcost.update({itemno:{'costunit':(costact+costexp)/qty,
                              'qty':0}})
            matdata.update({itemno:{'name':description,
                              'uom':uom,
                              'itc':itc,
                              'pgc':pgc,
                              'used':0}})

        #UNLABELED
        fgcost={}
        fgdata={}
        self.env.cr.execute(" select itemno,description,salesuom,itc,pgc,prodbomno "+\
                    " from sis_temp_items where refitem='' and itc='FG' order by itemno")
        itms=self.env.cr.fetchall()
        for itm in itms:
            (itemno,description,uom,itc,pgc,prodbomno)=itm
            c0,q0=self.calc_fg0(itemno,'')
            if q0==0 or q0==None:
                c0=0
                q0=0
            else:
                c0=c0/q0
            fgcost.update({(itemno,''):{'c0':c0,
                                   'q0':q0}})
            fgdata.update({(itemno,''):{'name':description,
                              'uom':uom,
                              'itc':itc,
                              'pgc':pgc,
                              'used':0}})

            self.env.cr.execute(" select variantqtyperuom,lineitem,lineqtyper "+\
                        " from sis_temp_production_bom where itemno='"+prodbomno+"'")
            boms=self.env.cr.fetchall()

            prod=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','production')])
            alt=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','alternative')])

            for i in range(1,32):

                fgcost[(itemno,'')].update({'q'+str(i) : fgcost[(itemno,'')]['q'+str(i-1)],
                             'c'+str(i) : fgcost[(itemno,'')]['c'+str(i-1)]
                             })

                if len(prod)==0:
                    if len(alt)==0:
                        continue
                
                if prod['t'+str(i)]==0:
                    if len(alt)==0 or alt['t'+str(i)]==0:
                        continue

                qty = prod['t'+str(i)]+alt['t'+str(i)]
                cost=0
                for bom in boms:
                    (variantqtyperuom,lineitem,lineqtyper)=bom
                    try:
                        unitcost=matcost[lineitem]['costunit']
                    except:
                        self.env.cr.execute(" select description,baseuom,itc,pgc,unitcost "+\
                                            " from sis_temp_items where " +\
                                            " itemno='"+lineitem+"' ")
                        mats=self.env.cr.fetchall()
                        for mat in mats:
                            (description,uom,itc,pgc,unitcost)=mat
                            matcost.update({lineitem:{'costunit':unitcost,
                                              'qty':0}})
                            matdata.update({lineitem:{'name':description,
                                              'uom':uom,
                                              'itc':itc,
                                              'pgc':pgc,
                                              'used':0}})                        
                    cost += variantqtyperuom * lineqtyper * unitcost
                fgcost[(itemno,'')]['c'+str(i)] = ( ( fgcost[(itemno,'')]['q'+str(i)] * fgcost[(itemno,'')]['c'+str(i)] ) + ( qty * cost ) )/ \
                                   ( fgcost[(itemno,'')]['q'+str(i)] + qty )                
                fgcost[(itemno,'')]['q'+str(i)] += qty                 

        #LABELED
        self.env.cr.execute(" select itemno,'',description,salesuom,itc,pgc,prodbomno "+\
                    " from sis_temp_items where refitem!='' and itc='FG' order by itemno")
        itms=self.env.cr.fetchall()
        for itm in itms:
            (itemno,variant,description,uom,itc,pgc,prodbomno)=itm
            
            if variant=='':
                self.env.cr.execute(" select variant,description,uom "+\
                            " from sis_temp_item_variants where itemno='"+itemno+"'")
                vs=self.env.cr.fetchall()
                if len(vs)>0:
                    for v in vs:
                        (varno,vardesc,varuom) = v
                        itms.extend({(itemno,varno,vardesc,varuom,itc,pgc,prodbomno)})
            
            c0,q0=self.calc_fg0(itemno,variant)
            if q0==0 or q0==None:
                c0=0
                q0=0
            else:
                c0=c0/q0
            fgcost.update({(itemno,variant):{'c0':c0,
                                   'q0':q0}})
            fgdata.update({(itemno,variant):{'name':description,
                              'uom':uom,
                              'itc':itc,
                              'pgc':pgc,
                              'used':0}})

            self.env.cr.execute(" select variantqtyperuom,lineitem,lineqtyper,lineitc "+\
                        " from sis_temp_production_bom where itemno='"+prodbomno+"' and variant='"+variant+"'")
            boms=self.env.cr.fetchall()

            prod=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','production')])
            alt=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','alternative')])

            for i in range(1,32):

                fgcost[(itemno,variant)].update({'q'+str(i) : fgcost[(itemno,'')]['q'+str(i-1)],
                             'c'+str(i) : fgcost[(itemno,'')]['c'+str(i-1)]
                             })

                if len(prod)==0:
                    if len(alt)==0:
                        continue
                
                if prod['t'+str(i)]==0:
                    if len(alt)==0 or alt['t'+str(i)]==0:
                        continue

                qty = prod['t'+str(i)]+alt['t'+str(i)]
                cost=0
                for bom in boms:
                    (variantqtyperuom,lineitem,lineqtyper,lineitc)=bom
                    try:
                        if lineitc=='FG':
                            unitcost=fgcost[(lineitem,'')]['c'+str(i)]
                            fgdata[(lineitem,'')]['used']=1
                        else:                            
                            unitcost=matcost[lineitem]['costunit']
                            matdata[(lineitem,'')]['used']=1
                    except:
                        if lineitc=='FG':
                            raise UserError('UNLABELED not found!')
                        self.env.cr.execute(" select description,baseuom,itc,pgc,unitcost "+\
                                            " from sis_temp_items where " +\
                                            " itemno='"+lineitem+"' ")
                        mats=self.env.cr.fetchall()
                        for mat in mats:
                            (description,uom,itc,pgc,unitcost)=mat
                            matcost.update({lineitem:{'costunit':unitcost,
                                              'qty':0}})
                            matdata.update({lineitem:{'name':description,
                                              'uom':uom,
                                              'itc':itc,
                                              'pgc':pgc,
                                              'used':1}})                        
                    cost += variantqtyperuom * lineqtyper * unitcost
                fgcost[(itemno,variant)]['c'+str(i)] = ( ( fgcost[(itemno,'')]['q'+str(i)] * fgcost[(itemno,'')]['c'+str(i)] ) + ( qty * cost ) )/ \
                                   ( fgcost[(itemno,'')]['q'+str(i)] + qty )                
                fgcost[(itemno,variant)]['q'+str(i)] += qty                 

        for s in self.sales_id:
            tgl=int(s.postingdate[8:10])
            s.unicostest=fgcost[(s.itemno,s.variant)]['c'+str(tgl)]
            fgdata[(s.itemno,s.variant)]['used']=1
        pass
#     header_id=fields.Many2one('sis.pnl.header',string="Header")
#     date = fields.Date(string='Date')
#     itemno =fields.Char(size=20,string="Item No")
#     description =fields.Char(size=200,string="Description")        
#     variant =fields.Char(size=20,string="Variant")
#     qty =fields.Float(string="Qty")
#     uom=fields.Char(size=20,string="UoM")
#     unitcost =fields.Float(string="Unit Cost Est")
#     amount=fields.Float(compute='_compute_amount',string='Amount')
#     itc =fields.Char(size=20,string="Item Cat.Code")
#     pgc =fields.Char(size=20,string="Prod Grp Code")        
#     
#     type = fields.Selection([('forecast','Forecast'),('actual','Actual')],string="Type", required=True)        

    def calc_fg0(self,itemno,variant):
        sql=" select sum(quantity),  sum(costactual+costexpected) "+\
                    " from sis_temp_ve_amount where valuation_date<'"+str(self.year)+"-"+str(self.month)+"-01' "\
                    " and item_no='"+itemno+"' and bg='"+self.ati12+"' "
        if variant!='':
            sql += " and variant='"+variant+"' "
        self.env.cr.execute(sql)            
        ds=self.env.cr.fetchall()
        for d in ds:
            (q0,c0)=d
        if len(ds)==0:
            q0=c0=0
            
        return c0,q0 
    
    def get_cogs_forecast(self):
        return
    
    def get_cogs_actual(self,no):
        return
        self.env.cr.execute("select distinct docno from sis_temp_gl_entry where accno='"+no+"' and extract(month from postingdate)="+str(self.month)+\
                            " and extract(year from postingdate)="+str(self.year)+"  and bg='"+self.ati12+"'")
        gls=self.env.cr.fetchall()
        
        for gl in gls:
            (docno,)=gl
            self.env.cr.execute("select 'invoice',docno, postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,"+\
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost from sis_temp_sales_invoice where docno='"+docno+"' order by sono,solineno")
                                #and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            sis=self.env.cr.fetchall()
            self.env.cr.execute("select 'creditmemo',docno, postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,"+\
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,returnorderno,returnorderlineno,unitcost from sis_temp_sales_credit_memo where docno='"+docno+"' order by returnorderno,returnorderlineno ")
            # and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            scs=self.env.cr.fetchall()
            sis.extend(scs)
            
            if len(sis)>0:
                for si in sis:
                    (type_,docno,postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,variant,qty,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost)=si
                    so=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('no_','=',sono),('lineno','=',solineno)])
                    if sono==None:
                        sono=''
                        solineno=''
                    vals = {'qtyact':qty,
                            'uomact':uom,
                            'unitpriceact':unitprice,
                            'unitcostact':unitcost,
                            'sino':docno,
                            'type':type_,
                            'accno':no
                        }                    
                    if len(so)==0:
                        si=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('sino','=',docno),('lineno','=',lineno)])
                        if len(si)>0:
                            si.write(vals)
                        else:
                            vals.update({'header_id':self.id,
                                    'postingdate':postingdate,
                                    'selltono':selltocustno,
                                    'selltoname':selltocustname,
                                    'shiptoname':shiptoname,
                                    'lineno':lineno,
                                    'itemno':itemno,
                                    'description':description,
                                    'variant':variant,
                                    'extdocno':extdocno,
                                    'salespersoncode':salespersoncode
                                })
                            self.env['sis.pnl.sales'].create(vals)
                continue
    def get_cogs_amount(self):
        totalact=0
        totalfore=0
        for s in self.sales_id:
            if s.sino and len(s.sino)>0:
                totalact+=s.qtyact*s.unitcostact
            else:
                totalfore+=s.qtyest*s.unitcostest   
        return totalfore,totalact
    def get_sales_forecast(self):
        
        self.env.cr.execute("update sis_pnl_sales set type='none',sino='',qtyact=0,amountact=0,unitpriceact=0 where header_id="+str(self.id))
        self.env.cr.execute("select 'order',no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice, extdocno, salesperson_code "+\
                            'from sis_so_header sh inner join sis_so_line sl on  sh.no_=sl.docno and extract(month from postingdate)='+str(self.month)+ \
                            'and extract(year from postingdate)='+str(self.year)+" and bg='"+self.ati12+"'")
        sos=self.env.cr.fetchall()
        self.env.cr.execute("select 'return',no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice, extdocno, salesperson_code "+\
                            'from sis_sr_header sh inner join sis_sr_line sl on  sh.no_=sl.docno and extract(month from postingdate)='+str(self.month)+ \
                            'and extract(year from postingdate)='+str(self.year)+" and bg='"+self.ati12+"'")
        srs=self.env.cr.fetchall()
        sos.extend(srs)
        total=0
        for so in sos:
            (type_,no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice,extdocno, salesperson_code)=so            
            
            if currency_code=='IDR':
                unitprice/=self.exchangerate
            if type_=='return':
                unitprice*=-1
            so=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('no_','=',no_),('lineno','=',lineno)])
            vals = {'postingdate':postingdate,
                    'selltono':selltono,
                    'selltoname':selltoname,
                    'shiptoname':shiptoname,
                    'itemno':itemno,
                    'description':description,
                    'variant':variant,
                    'qtyest':quantity,
                    'uomact':uom,
                    'unitpriceest':unitprice,
                    'extdocno':extdocno,
                    'salespersoncode':salesperson_code,
                    'type':type_
                }
            if len(so)>0:
                so.write(vals)
            else:
                vals.update({'header_id':self.id,
                        'no_':no_, 
                        'lineno':lineno
                    })
                self.env['sis.pnl.sales'].create(vals)
        self.env.cr.execute("delete from sis_pnl_sales where type='none' and header_id="+str(self.id))
        return total
    def get_sales_actual(self,no):
        self.env.cr.execute("select distinct docno from sis_temp_gl_entry where accno='"+no+"' and extract(month from postingdate)="+str(self.month)+ \
                            " and extract(year from postingdate)="+str(self.year)+" and bg='"+self.ati12+"'")
        gls=self.env.cr.fetchall()
        
        for gl in gls:
            (docno,)=gl
            self.env.cr.execute("select 'invoice',docno, postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,"+\
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost from sis_temp_sales_invoice where docno='"+docno+"' order by sono,solineno")
                                #and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            sis=self.env.cr.fetchall()
            self.env.cr.execute("select 'creditmemo',docno, postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,"+\
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,returnorderno,returnorderlineno,unitcost from sis_temp_sales_credit_memo where docno='"+docno+"' order by returnorderno,returnorderlineno ")
            # and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            scs=self.env.cr.fetchall()
            sis.extend(scs)
            
            if len(sis)>0:
                for si in sis:
                    (type_,docno,postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,variant,qty,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost)=si
                    if type_=='creditmemo':
                        unitprice*=-1
                    so=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('no_','=',sono),('lineno','=',solineno)])
                    if sono==None:
                        sono=''
                        solineno=''
                    #qty+=so.qtyact
                    vals = {'qtyact':qty,
                            'uomact':uom,
                            'unitpriceact':unitprice,
                            'unitcostact':unitcost,
                            'sino':docno,
                            'type':type_,
                            'accno':no
                        }                    
                    if len(so)>0:
                        if so.sino=='':
                            so.write(vals)
                        else:
                            solineno1=int(solineno)+1
                            while self.env['sis.pnl.sales'].search_count([('header_id','=',self.id),('no_','=',sono),('lineno','=',solineno1)])>0:
                                solineno1+=1
                            vals.update({'header_id':self.id,
                                        'qtyest':0,
                                        'unitpriceest':0,
                                        'no_':so.no_,
                                        'postingdate':postingdate,
                                        'selltono':selltocustno,
                                        'selltoname':selltocustname,
                                        'shiptoname':shiptoname,
                                        'lineno':str(solineno1),
                                        'itemno':itemno,
                                        'description':description,
                                        'variant':variant,
                                        'extdocno':extdocno,
                                        'salespersoncode':salespersoncode
                                    })
                            self.env['sis.pnl.sales'].create(vals)
                    else:
                        si=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('sino','=',docno),('lineno','=',lineno)])
                        if len(si)>0:
                            si.write(vals)
                        else:
                            vals.update({'header_id':self.id,
                                    'postingdate':postingdate,
                                    'selltono':selltocustno,
                                    'selltoname':selltocustname,
                                    'shiptoname':shiptoname,
                                    'lineno':lineno,
                                    'itemno':itemno,
                                    'description':description,
                                    'variant':variant,
                                    'extdocno':extdocno,
                                    'salespersoncode':salespersoncode
                                })
                            self.env['sis.pnl.sales'].create(vals)
                continue
    def get_sales_amount(self):
        totalact=0
        totalfore=0
        for s in self.sales_id:
            if s.sino and len(s.sino)>0:
                totalact+=s.qtyact*s.unitpriceact
            else:
                totalfore+=s.qtyest*s.unitpriceest   
        return totalfore,totalact
class sis_pnl_detail(models.Model):
    _name='sis.pnl.detail'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    description =fields.Char(size=100,string="Description")
    amount =fields.Float(string="Amount")
    changepercent = fields.Float(string="Change %(+/-)")
    changeamount = fields.Float(string="Change amount")
    finalamount = fields.Float(compute='compute_finalamount',string="Final Amount")
    bold = fields.Boolean(string='Bold?')
    estimation = fields.Float(compute='compute_estimation',string="Estimation")
    actual = fields.Float(string="Actual")
    @api.one
    @api.depends('finalamount','actual')
    def compute_estimation(self):
        self.estimation=self.finalamount-self.actual
    @api.one
    @api.depends('amount','changepercent','changeamount')
    def compute_finalamount(self):
        self.finalamount=self.amount*(1+self.changepercent/100)+self.changeamount
class sis_pnl_sales(models.Model):
    _name='sis.pnl.sales'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no_ =fields.Char(size=20,string="So No.")
    postingdate =fields.Date(string="Date")    
    selltono =fields.Char(size=20,string="Sell to No")
    selltoname =fields.Char(size=200,string="Sell to Name")
    shiptoname =fields.Char(size=200,string="Ship to Name")       
    lineno =fields.Integer(string="Line No")
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qtyest =fields.Float(string="Fore.Qty")
    uom=fields.Char(size=20,string="Fore.UoM")
    unitpriceest =fields.Float(string="Fore.U.Price")
    unitcostest =fields.Float(string="Fore.U.Cost")
    amountest =fields.Float(compute='_compute_amountest',string="Fore.Amount",store=True)    
    costest =fields.Float(compute='_compute_costest',string="Fore.Cost",store=True)        
    
    qtyact =fields.Float(string="Act.Qty")
    uomact=fields.Char(size=20,string="Act.UoM")
    unitpriceact =fields.Float(string="Act.U.Price")
    unitcostact =fields.Float(string="Act.U.Cost")
    amountact =fields.Float(compute='_compute_amountact',string="Act.U.Cost",store=True)    
    costact =fields.Float(compute='_compute_costact',string="Act.Cost",store=True)    
    costdiff =fields.Float(compute='_compute_costdiff',string="Diff.Cost",store=True)        
    qtydiff =fields.Float(compute='_compute_qtydiff',string="Diff.Qty",store=True)        
    amounttdiff =fields.Float(compute='_compute_amountdiff',string="Diff.Amt",store=True)            
    
    extdocno =fields.Char(size=50,string="Ext.Doc.No")
    salespersoncode=fields.Char(size=50,string="Salesperson")
    sino =fields.Char(size=20,string="SI No.")
    accno =fields.Char(size=20,string="Acc.No.")
    
    type = fields.Selection([('order','S.Order'),('return','R.Order'),('invoice','S.Invc'),('creditmemo','Cred.Memo')],string="Type", required=True)       
    @api.multi
    def write(self, vals):
        return models.Model.write(self, vals)
    
    @api.one
    @api.depends('qtyact','unitpriceact','qtyest','unitpriceest')
    def _compute_amountdiff(self):
        self.amountdiff=(self.qtyact*self.unitpriceact)-(self.qtyest*self.unitpriceest)
    @api.one
    @api.depends('qtyact','qtyest')
    def _compute_qtydiff(self):
        self.qtydiff=self.qtyact-self.qtyest
    @api.one
    @api.depends('qtyact','unitpriceact','qtyest','unitpriceest','unitcostact','unitcostest')
    def _compute_costdiff(self):
        self.costdiff=(self.qtyact*self.unitcostact)-(self.qtyest*self.unitcostest)
    @api.one
    @api.depends('qtyest','unitpriceest')
    def _compute_amountest(self):
        self.amountest=self.qtyest*self.unitpriceest
    @api.one
    @api.depends('qtyact','unitpriceact')
    def _compute_amountact(self):
        self.amountact=self.qtyact*self.unitpriceact
    @api.one
    @api.depends('qtyest','unitcostest')
    def _compute_costest(self):
        self.costest=self.qtyest*self.unitcostest
    @api.one
    @api.depends('qtyact','unitcostact')
    def _compute_costact(self):
        self.costact=self.qtyact*self.unitcostact
    
class sis_pnl_cogs(models.Model):
    _name='sis.pnl.cogs'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    name=fields.Char(size=20,string="Name")        
    amount=fields.Float(string="amount")
class sis_pnl_selling(models.Model):
    _name='sis.pnl.selling'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_pnl_expense(models.Model):
    _name='sis.pnl.expense'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_pnl_forex(models.Model):
    _name='sis.pnl.forex'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_pnl_otherinex(models.Model):
    _name='sis.pnl.otherinex'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_pnl_financialinex(models.Model):
    _name='sis.pnl.financialinex'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_pnl_provision(models.Model):
    _name='sis.pnl.provision'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    no =fields.Char(size=20,string="Account No.")
    name =fields.Char(size=200,string="Account Name")        
    amount =fields.Float(string="Amount")
class sis_cogs(models.Model):
    _name='sis.cogs'
    name =fields.Char(size=20,string="COGS Name")        
    startwith =fields.Char(size=20,string="Doc No start with")        
    
class sis_account_setting(models.Model):
    _name='sis.account.setting'
    account =fields.Selection([('01.sales','01.SALES'),('02.cogs','02.COGS'),('03.gross','03.GROSS PROFIT / LOSS'),('04.selling','04.Selling Expense'),\
                                ('05.expense','05.General and Administration Expense'),('06.forex','06.Foreign Exchange Profit/Loss'),\
                                ('07.otherinex','07.Other Operating Income/Expense'),('08.totalexpense','08.Total Operating Expenses'),\
                                ('09.totaloperating','09.OPERATING PROFIT/LOSS'),('10.financialin','10.Financial Income'),\
                                ('11.financialex','11.Financial Expense'),('12.profit','12.PROFIT BEFORE TAX'),\
                                ('13.provision','13.Provision for Income Tax'),('14.deffered','14.Deffered Provision for Income Tax'),\
                                ('15.total','15.*** TOTAL COMPREHENSIVE INCOME ***')],string="Account in P/L",required=True)
    accountname=fields.Char(compute='_compute_accountname',size=50,string='Account Name',store=True)
    sum = fields.Char(size=50,string='Sum of account sequences')
    start_id=fields.Many2one('sis.gl.account',string="Start account in NAV",domain=[('income_balance','=',0)])
    start =fields.Char(compute='_compute_start',size=20,string="Start account in NAV",store=True)        
    end_id=fields.Many2one('sis.gl.account',string="End account in NAV",domain=[('income_balance','=',0)])
    end =fields.Char(compute='_compute_end',size=20,string="End account in NAV",store=True)
    opposite= fields.Boolean(string='Opposite Sign?')
    bold = fields.Boolean(string='Bold?')
        
    @api.one
    @api.depends('account')
    def _compute_accountname(self):
        self.accountname=dict(self._fields['account'].selection).get(self.account)
            
    @api.depends('start_id')
    def _compute_start(self):
        self.start=self.start_id.no
    @api.depends('end_id')               
    def _compute_end(self):        
        self.end=self.end_id.no  
        
        
        
class sis_pnl_lastmonth(models.Model):
    _name='sis.pnl.lastmonth'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    date = fields.Date(string='Date')
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qty =fields.Float(string="Qty")
    uom=fields.Char(size=20,string="UoM")
    unitcost =fields.Float(string="Unit Cost Est")
    amount=fields.Float(compute='_compute_amount',string='Amount')
    itc =fields.Char(size=20,string="Item Cat.Code")
    pgc =fields.Char(size=20,string="Prod Grp Code")        
    
    type = fields.Selection([('forecast','Forecast'),('actual','Actual')],string="Type", required=True)        
    
    
    def _compute_amount(self):
        self.amount=self.unitcost*self.qty
        
        
class sis_pnl_prod(models.Model):
    _name='sis.pnl.prod'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    date = fields.Date(string='Date')
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qty =fields.Float(string="Qty")
    uom=fields.Char(size=20,string="UoM")
    unitcost =fields.Float(string="Unit Cost Est")
    amount=fields.Float(compute='_compute_amount',string='Amount')
    itc =fields.Char(size=20,string="Item Cat.Code")
    pgc =fields.Char(size=20,string="Prod Grp Code")        
    
    type = fields.Selection([('plan','Plan'),('actual','Actual')],string="Type", required=True)        
    
    
    def _compute_amount(self):
        self.amount=self.unitcost*self.qty
        
class sis_pnl_component(models.Model):
    _name='sis.pnl.component'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    prod_id=fields.Many2one('sis.pnl.prod',string="Prod")
        
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qty =fields.Float(string="Qty")
    uom=fields.Char(size=20,string="UoM")
    unitcost =fields.Float(string="Unit Cost")
    amount=fields.Float(compute='_compute_amount',string='Amount')
    itc =fields.Char(size=20,string="Item Cat.Code")
    pgc =fields.Char(size=20,string="Prod Grp Code")        
    
    type = fields.Selection([('plan','Plan'),('actual','Actual')],string="Type", required=True)        
    
    
    def _compute_amount(self):
        self.amount=self.unitcost*self.qty