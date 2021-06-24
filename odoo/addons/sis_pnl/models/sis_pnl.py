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
    prod_id=fields.One2many('sis.pnl.prod','header_id',string="Detail")
    component_id=fields.One2many('sis.pnl.component','header_id',string="Detail")
    ucused_id=fields.One2many('sis.pnl.ucused','header_id',string="Detail")
    
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
        self.env.cr.execute("DROP TABLE IF EXISTS sis_temp_ve_amount")
        self.env.cr.execute("CREATE TEMP TABLE sis_temp_ve_amount AS SELECT * FROM sis_ve_amount; ")
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

        matcost={}
        matdata={}
        fgcost={}
        fgdata={}
        bomdata={}
        
        self.date=datetime.now()
        wasacc='first'
        for acc in accs:
            if wasacc!=acc.accountname:
                subtotal=0
                actual=0
            if acc.account=='01.sales':
                subtotal=self.get_sales_forecast()
                
            if acc.account=='02.cogs':
                self.get_cogs_calculate(fgcost,fgdata,matcost,matdata,bomdata)
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
                    #ACTUAL
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
        self.save_fgcost_matcost_bomdata(fgcost,fgdata,matcost,matdata,bomdata)

    def save_fgcost_matcost_bomdata(self,fgcost,fgdata,matcost,matdata,bomdata):
        self.env.cr.execute("DELETE FROM sis_pnl_component where header_id="+str(self.id))
        self.env.cr.execute("DELETE FROM sis_pnl_prod where header_id="+str(self.id))
        self.env.cr.execute("DELETE FROM sis_pnl_ucused where header_id="+str(self.id))                
        for itemno in matdata:
            #save matcost
            mrecs=self.env['sis.pnl.component'].search([('header_id','=',self.id),('itemno','=',itemno)])
            if len(mrecs)==0:
                mvals={
                    'itemno':itemno,
                    'description':matdata[itemno]['name'],
                    'variant':'',
                    'uom':matdata[itemno]['uom'],
                    'unitcostest':matcost[itemno]['costunit'],
                    'itc':matdata[itemno]['itc'],
                    'pgc':matdata[itemno]['pgc'],
                    'header_id':self.id
                }
                mrecs=self.env['sis.pnl.component'].create(mvals)
        for item in fgdata:
            (itemno,variant)=item
            for i in range(1,32):
                fgrecs=self.env['sis.pnl.prod'].search([('header_id','=',self.id),('itemno','=',itemno),('variant','=',variant)])
                if len(fgrecs)==0:
                    fgvals={
                        'itemno':itemno,
                        'description':fgdata[item]['name'],
                        'variant':'',
                        'date':str(self.year)+'-'+str(self.month)+'-'+str(i),
                        'uom':fgdata[item]['uom'],
                        'unitcostest':fgcost[item]['c'+str(i)],
                        'qty':fgcost[item]['q'+str(i)],
                        'itc':fgdata[item]['itc'],
                        'pgc':fgdata[item]['pgc'],
                        'header_id':self.id
                    }
                    fgrecs=self.env['sis.pnl.prod'].create(fgvals)

        for item in bomdata:
            (itemno,variant)=item
            f=self.env['sis.pnl.prod'].search([('header_id','=',self.id),('itemno','=',itemno),('variant','=',variant)],limit=1)
            for bom in bomdata[item]:
                (_,lineitem,_,_,_,_,_,_)=bom
                m=self.env['sis.pnl.component'].search([('header_id','=',self.id),('itemno','=',lineitem)])
                use=self.env['sis.pnl.ucused'].search([('header_id','=',self.id),('fgitemno','=',f.itemno),('fgvariant','=',f.variant),('component_id','=',m.id)])
                if len(use)==0:
                    usevals={'header_id':self.id,
                             'fgitemno':f.itemno,
                             'fgdescription':f.description,
                             'fgvariant':f.variant,                                                          
                             'component_id':m.id}
                    self.env['sis.pnl.ucused'].create(usevals)


    def get_cogs_calculate(self,fgcost,fgdata,matcost,matdata,bomdata):
        for s in self.sales_id:
            tgl=int(s.postingdate[8:10])
            s.unitcostest=self.calc_fgcost(tgl,s.itemno,s.variant,s.description,s.uom,'FG','',fgcost,fgdata,matcost,matdata,bomdata)
        pass

    def calc_fgcost(self,tgl,itemno,variant,description,uom,itc,pgc,fgcost,fgdata,matcost,matdata,bomdata):
        try:
            return fgcost[(itemno,variant)]['c'+str(tgl)]
        except:
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
                              'pgc':pgc}})
            try:
                boms=bomdata[(itemno,variant)]
            except:
                self.env.cr.execute(" select variantqtyperuom,lineitem,linevar,linedesc,lineuom,lineqtyper,lineitc,linepgc "+\
                                    " from sis_temp_production_bom where itemno='"+itemno+"' and variant='"+variant+"'")
                boms=self.env.cr.fetchall()
                bomdata.update({(itemno,variant):[]})
                for bom in boms:
                    bomdata[(itemno,variant)].extend([bom])

            prod=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','production')])
            alt=self.env['sis.pps.detail'].search([('item_no','=',itemno),('month','=',self.month),('year','=',self.year),('type','=','alternative')])

            for i in range(1,32):

                fgcost[(itemno,variant)].update({'q'+str(i) : fgcost[(itemno,variant)]['q'+str(i-1)],
                             'c'+str(i) : fgcost[(itemno,variant)]['c'+str(i-1)]
                             })

#                 if len(prod)==0:
#                     if len(alt)==0:
#                         continue
#                      
#                 if prod['t'+str(i)]==0:
#                     if len(alt)==0 or alt['t'+str(i)]==0:
#                         continue 

                qty = prod['t'+str(i)]
                if len(alt)>0 or alt['t'+str(i)]!=0:
                    qty+=alt['t'+str(i)]
                cost=0
                for bom in boms:
                    (variantqtyperuom,lineitem,linevar,linedesc,lineuom,lineqtyper,lineitc,linepgc)=bom
                    try:
                        if lineitc=='FG':
                            unitcost=fgcost[(lineitem,'')]['c'+str(i)]
                        else:                            
                            unitcost=matcost[lineitem]['costunit']
                    except:
                        if lineitc=='FG':
                            unitcost=self.calc_fgcost(tgl,lineitem,linevar,linedesc,lineuom,lineitc,linepgc,fgcost,fgdata,matcost,matdata,bomdata)
                        else:
                            self.env.cr.execute(" select sum(quantity), sum(costactual),sum(costexpected) "+\
                                                " from sis_temp_ve_amount where valuation_date<'"+str(self.year)+"-"+str(self.month)+"-01' "\
                                                " and item_no='"+lineitem+"' and bg='"+self.ati12+"' ")
                            mats=self.env.cr.fetchall()
                            for mat in mats:
                                (matremqty,matcostact,matcostexp)=mat
                                if matcostact==None:
                                    matcostact=0
                                if matcostexp==None:
                                    matcostexp=0
                                if matremqty==None:
                                    matremqty=0

                                if matremqty==0 or matcostact+matcostexp==0:
                                    continue
                                matcost.update({lineitem:{'costunit':(matcostact+matcostexp)/matremqty,
                                                  'qty':matremqty}})
                            if len(mats)==0 or (matremqty)==0:
                                self.env.cr.execute(" select unitcost "+\
                                                    " from sis_temp_items where " +\
                                                    " itemno='"+lineitem+"' ")
                                mats=self.env.cr.fetchall()
                                if len(mats)==0:
                                    raise UserError('Master Item error :'+lineitem)
                                for mat in mats:
                                    (unitcost,)=mat
                                    matcost.update({lineitem:{'costunit':unitcost,
                                                      'qty':0}})           
                            matdata.update({lineitem:{'name':linedesc,
                                              'uom':lineuom,
                                              'itc':lineitc,
                                              'pgc':linepgc}})
                            unitcost=matcost[lineitem]['costunit']
                    cost += variantqtyperuom * lineqtyper * unitcost

                a=fgcost[(itemno,variant)]['q'+str(i)]+qty
                if  a !=0:
                    fgcost[(itemno,variant)]['c'+str(i)] = ( ( fgcost[(itemno,variant)]['q'+str(i)] * fgcost[(itemno,variant)]['c'+str(i)] ) + ( qty * cost ) )/ \
                                       ( fgcost[(itemno,variant)]['q'+str(i)] + qty )                
                    fgcost[(itemno,variant)]['q'+str(i)] += qty
                else:
                    pass
            return fgcost[(itemno,variant)]['c'+str(tgl)]
 
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
    def get_cogs_actual(self,no):
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
                totalact+=s.qtyincanact*s.unitcostact
            else:
                totalfore+=s.qtyincanest*s.unitcostest   
        return totalfore,totalact

    def get_sales_forecast(self):
        
        self.env.cr.execute("update sis_pnl_sales set type='none',sino='',qtyact=0,amountact=0,unitpriceact=0 where header_id="+str(self.id))
        self.env.cr.execute("select 'order',no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice, extdocno, salesperson_code,qtyperuom "+\
                            'from sis_so_header sh inner join sis_so_line sl on  sh.no_=sl.docno and extract(month from postingdate)='+str(self.month)+ \
                            'and extract(year from postingdate)='+str(self.year)+" and bg='"+self.ati12+"'")
        sos=self.env.cr.fetchall()
        self.env.cr.execute("select 'return',no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice, extdocno, salesperson_code,qtyperuom "+\
                            'from sis_sr_header sh inner join sis_sr_line sl on  sh.no_=sl.docno and extract(month from postingdate)='+str(self.month)+ \
                            'and extract(year from postingdate)='+str(self.year)+" and bg='"+self.ati12+"'")
        srs=self.env.cr.fetchall()
        sos.extend(srs)
        total=0
        for so in sos:
            (type_,no_, currency_code,postingdate, selltono, selltoname, shiptoname, lineno, itemno, description, variant, quantity, uom, unitprice,extdocno, salesperson_code,qtyperuom)=so            
            
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
                    'qtyperuomest':qtyperuom,
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
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost,qtyperuom from sis_temp_sales_invoice where docno='"+docno+"' order by sono,solineno")
                                #and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            sis=self.env.cr.fetchall()
            self.env.cr.execute("select 'creditmemo',docno, postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,"+\
                                "variant,quantity,uom,unitprice,extdocno,salespersoncode,returnorderno,returnorderlineno,unitcost,qtyperuom from sis_temp_sales_credit_memo where docno='"+docno+"' order by returnorderno,returnorderlineno ")
            # and extract(month from postingdate)="+str(self.sourcemonth)+" and extract(year from postingdate)="+str(self.sourceyear))
            scs=self.env.cr.fetchall()
            sis.extend(scs)
            
            if len(sis)>0:
                for si in sis:
                    (type_,docno,postingdate,selltocustno, selltocustname,shiptoname,lineno,itemno,description,variant,qty,uom,unitprice,extdocno,salespersoncode,sono,solineno,unitcost,qtyperuom)=si
                    if type_=='creditmemo':
                        unitprice*=-1
                    so=self.env['sis.pnl.sales'].search([('header_id','=',self.id),('no_','=',sono),('lineno','=',solineno)])
                    if sono==None:
                        sono=''
                        solineno=''
                    #qty+=so.qtyact
                    vals = {'qtyact':qty,
                            'qtyperuomact':qtyperuom,                            
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
    qtyperuomest =fields.Float(string="Fore.Qty/UoM")
    uom=fields.Char(size=20,string="Fore.UoM")
    unitpriceest =fields.Float(string="Fore.U.Price")
    unitcostest =fields.Float(string="Fore.U.Cost")
    amountest =fields.Float(compute='_compute_amountest',string="Fore.Amount",store=True)    
    costest =fields.Float(compute='_compute_costest',string="Fore.Cost",store=True)        
    qtyincanest =fields.Float(compute='_compute_qtyincanest',string="Fore.Qty/can",store=True)    
        
    qtyact =fields.Float(string="Act.Qty")
    qtyperuomact =fields.Float(string="Act.Qty/UoM")
    uomact=fields.Char(size=20,string="Act.UoM")
    unitpriceact =fields.Float(string="Act.U.Price")
    unitcostact =fields.Float(string="Act.U.Cost")
    amountact =fields.Float(compute='_compute_amountact',string="Act.U.Cost",store=True)    
    costact =fields.Float(compute='_compute_costact',string="Act.Cost",store=True)    
    qtyincanact =fields.Float(compute='_compute_qtyincanact',string="Act.Qty/can",store=True)
            
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
    @api.depends('qtyact','qtyperuomact')
    def _compute_qtyincanact(self):
        self.qtyincanact=self.qtyact*self.qtyperuomact
    @api.one
    @api.depends('qtyest','qtyperuomest')
    def _compute_qtyincanest(self):
        self.qtyincanest=self.qtyest*self.qtyperuomest
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
        self.costest=self.qtyincanest*self.unitcostest
    @api.one
    @api.depends('qtyact','unitcostact')
    def _compute_costact(self):
        self.costact=self.qtyincanact*self.unitcostact
    
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
        
        
        
class sis_pnl_ucused(models.Model):
    _name='sis.pnl.ucused'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    component_id=fields.Many2one('sis.pnl.component',string="Prod")        

    fgitemno =fields.Char(size=20,string="FG Item No")
    fgdescription =fields.Char(size=200,string="FG Description")
    fgvariant =fields.Char(size=20,string="FG Variant")

    itemno =fields.Char(related='component_id.itemno',size=20,string="Item No")
    description =fields.Char(related='component_id.description',size=200,string="Description")        
    variant =fields.Char(related='component_id.variant',size=20,string="Variant")
    uom=fields.Char(related='component_id.uom',size=20,string="UoM")
    unitcostest =fields.Float(related='component_id.unitcostest',string="Fore.U.Cost")
    itc =fields.Char(related='component_id.itc',size=20,string="Item Cat.Code")
    pgc =fields.Char(related='component_id.pgc',size=20,string="Prod Grp Code")        
    
class sis_pnl_prod(models.Model):
    _name='sis.pnl.prod'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
    date = fields.Date(string='Date')
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qty =fields.Float(string="Qty")
    uom=fields.Char(size=20,string="UoM")
    unitcostest =fields.Float(string="Fore.U.Cost")
    unitcostact =fields.Float(string="Act.U.Cost")
    amount=fields.Float(compute='_compute_amount',string='Amount')
    itc =fields.Char(size=20,string="Item Cat.Code")
    pgc =fields.Char(size=20,string="Prod Grp Code")        
    
    def _compute_amount(self):
        self.amount=self.unitcost*self.qty
        
class sis_pnl_component(models.Model):
    _name='sis.pnl.component'
    header_id=fields.Many2one('sis.pnl.header',string="Header")
        
    itemno =fields.Char(size=20,string="Item No")
    description =fields.Char(size=200,string="Description")        
    variant =fields.Char(size=20,string="Variant")
    qty =fields.Float(string="Qty")
    uom=fields.Char(size=20,string="UoM")
    unitcostest =fields.Float(string="Fore.U.Cost")
    amount=fields.Float(compute='_compute_amount',string='Amount')
    itc =fields.Char(size=20,string="Item Cat.Code")
    pgc =fields.Char(size=20,string="Prod Grp Code")              
    
    
    def _compute_amount(self):
        self.amount=self.unitcost*self.qty