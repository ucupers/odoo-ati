from odoo import models, fields, api, _
from odoo.exceptions import UserError
from _datetime import datetime, timedelta

class sis_pps_detail_add(models.TransientModel):
    _name='sis.pps.detail.add'

    itm = fields.Many2one('sis.items',string='Item',domain=[('itc','=','FG')],required=True)
    variant = fields.Many2one('sis.item.variants',string='Variant', domain=lambda self: [('itemno','=',self.itm.itemno)])
    item_no = fields.Char(related='itm.itemno',string="Item No.")
    variant_code = fields.Char(related='variant.variant',string='Variant Code')
    line_id = fields.Char(size=20,string='Line')

#     def _get_default_line(self):
#         if self.item_no:
#             rs=self.env['sis.pps.item'].search([('item_no','=',self.item_no)])
#             if len(rs)==1:
#                 return rs.line

    def additem(self):
        idd=self._context['insert_id']
        self.env.cr.execute("select max(detailnum) from sis_pps_detail where header_id="+str(idd))
        ds=self.env.cr.fetchall()
        if ds!=[(None,)]:
            [(detailnum,)]=ds
        else:
            detailnum=0
        detailnum+=1
        if len(self.variant)>0:
            uom=self.variant.uom
        else:
            uom=self.itm.salesuom
        head=self.env['sis.pps.header'].search([('id','=',idd)])
        rs=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=', head.ati12)])
        if len(rs)>1:
            raise UserError('Double in Item Settings !')
        if len(rs)==1:
            line= rs.line
        else:
            raise UserError('No Line in Item Settings !')
        for i in ('sales','production','inventory'):
            #if self.env['sis.pps.detail'].search_count([('header_id','=',idd),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('type','=',i)])==0:
                vals = {
                    'header_id':idd,
                    'header':idd,
                    'item_no':self.itm.itemno,
                    'variant_code':self.variant.variant,
                    'description':self.itm.description,     
                    'type':i,
                    'uom':uom,
                    'qtyperuom':self.itm.qtyperuom,
                    'detailnum':detailnum
                    }    
                if i=='production':
                    if line and len(line)>0:
                        vals.update({'line_id':line})
                else:
                    vals.pop('line_id',None)
                if i=='sales':
                    vals.update({'hideline':False})
                else:
                    vals.update({'hideline':True})                    
                self.env['sis.pps.detail'].create(vals)
            #else:
            #    raise UserError('Data already exist !')
    
class sis_pps_header(models.Model):
    _name='sis.pps.header'

    pp_no = fields.Char(size=20,string="PP No.")
    ul = fields.Selection([('unlabeled','Unlabeled'),('labeled','Labeled')],string="Un/Labeled",required=True)
    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    
    lastupdate = fields.Datetime(string='Last Update')
    
    check = fields.Boolean(compute='_compute_invis',string='check',store=True)
    invist29 = fields.Boolean(compute='_compute_invist29',string='__Invis')
    invist30 = fields.Boolean(compute='_compute_invist30',string='__Invis')
    invist31 = fields.Boolean(compute='_compute_invist31',string='__Invis')
   

    detail_id=fields.One2many('sis.pps.detail','header_id')
    detail2_id=fields.One2many('sis.pps.detail','header_id',domain=['|','|',('type','=','production'),('type','=','sales'),('type','=','inventory')])
    actual_id=fields.One2many('sis.pps.detail','header_id',domain=['|',('type','=','production'),('type','=','plan')])
    material_id=fields.One2many('sis.pps.material','header_id')
    fishmaterial_id=fields.One2many('sis.pps.fishmaterial','header_id')

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

    def open_treeview(self): 
        return {
            'name': 'Production Plan  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.detail',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_detail_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id),('type','in',['sales','inventory','production'])]
        }

    def open_materialtreeview(self): 
        return {
            'name': 'Material  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.material',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_material_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }

    def open_fishmaterialtreeview(self): 
        return {
            'name': 'Fish Material  '+self.ati12.upper()+'-'+self.ul.upper()+'-'+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.fishmaterial',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_fishmaterial_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }

    def open_actual(self): 
        return {
            'name': 'Plan-Production'+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.detail',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_actual_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id),('type','in',['production','plan'])]
        }


    def additem(self): 
        return {
            'name': self.id,
            'res_model': 'sis.pps.detail.add',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_detail_add_form').id,
            'target': 'new',
            'nodestroy':True,
            'context':"{'insert_id':"+str(self.id)+"}"
        }

    def countfgstock(self):
        self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_temp")
        self.env.cr.execute("CREATE TEMP TABLE sis_ile_temp AS SELECT * FROM sis_ile; ")


        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','production')])
        for prod in prods:
            if  prod.variant_code==False:
                variant=''
            else:
                variant=prod.variant_code

            ## UPDATE ACTUAL PRODUCTION FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_temp"+ \
                            " where item_no='"+prod.item_no+"' and variant='"+variant+"'" \
                            " and entrytype = 'Output'" + \
                            " and bg='"+prod.ati12.upper()+"'")
            proddates=self.env.cr.fetchall()
            for proddate in proddates:
                (tgl,)=proddate
 
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
                    self.env.cr.execute("select extract(day from posting_date),sum(quantity) from sis_ile_temp "+ \
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

        invs=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','inventory')])
        for inv in invs:
            if  inv.variant_code==False:
                variant=''
            else:
                variant=inv.variant_code
            ## UPDATE ACTUAL INVENTORY FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_temp"+ \
                            " where item_no='"+inv.item_no+"' and variant='"+variant+"'" \
                            " and bg='"+inv.ati12.upper()+"'")
            invdates=self.env.cr.fetchall()
            for invdate in invdates:
                (tgl,)=invdate
            
            valsinv={}
          
            if tgl!=None:
                year=int(tgl[:4])
                month=int(tgl[5:7])
                day=int(tgl[8:10])
                
                runyear=self.year
                runmonth=self.month
    
                #CALCULATE T0
                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp"+ \
                                    " where item_no='"+inv.item_no+"' and variant='"+variant+"'" \
                                    " and bg='"+inv.ati12.upper()+"'" +\
                                    " and posting_date<'"+str(runyear)+"-"+str(runmonth)+"-1'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0,)=stock
                    
                else:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp"+ \
                                    " where item_no='"+inv.item_no+"' and variant='"+variant+"'" \
                                    " and bg='"+inv.ati12.upper()+"'" +\
                                    " and posting_date<='"+str(year)+"-"+str(month)+"-"+str(day)+"'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0,)=stock

                    t0year=year
                    t0month=month

                    while t0year*100+t0month<runyear*100+runmonth:
                        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',inv.item_no),('variant_code','=',inv.variant_code),('type','=','production'),('year','=',t0year),('month','=',t0month)])
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
                        t0+=t0inc
                if t0:
                    t0/=inv.qtyperuom
                else:
                    t0=0;
                valsinv.update({'t0':t0})
                
                # CALCULATE ACTUAL INVENTORY
                for counter in range (1,32):
                    valsinv.update({'a'+str(counter):False})                
                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    for runday in range(1,32):
                        if year*10000+month*100+day<runyear*10000+runmonth*100+runday:
                            break
                        valsinv.update({'a'+str(runday):True})

                ##UPDATE INVENTORY
                self.env.cr.execute("select extract(day from posting_date), sum(quantity) from sis_ile_temp "+ \
                                " where extract(month from posting_date)="+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ \
                                " and item_no='"+inv.item_no+"' and variant='"+variant+"'" \
                                " and bg='"+inv.ati12.upper()+"'"+ \
                                " group by extract(day from posting_date)")
                actinvs=self.env.cr.fetchall()
                for counter in range (1,32):
                    valsinv.update({'t'+str(counter):0})
                
                for actinv in actinvs:
                    (tgl,qty)=actinv
                    try:
                        if valsinv['a'+str(int(tgl))]==True:
                            valsinv['t'+str(int(tgl))] = qty / inv.qtyperuom
                    except:
                        pass
                    
                s=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',inv.detailnum),('type','=','sales')])
                p=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',inv.detailnum),('type','=','production')])
                for counter in range (1,32):
                    if valsinv['a'+str(int(counter))]==True:                    
                        valsinv['t'+str(counter)]+=valsinv['t'+str(counter-1)]
                    else:
                        valsinv['t'+str(counter)]=valsinv['t'+str(counter-1)]+p['t'+str(counter)]-s['t'+str(counter)]                        


                    
                inv.write(valsinv)
            #--------------------------------------------------------------------------------------------------------------------------------
                ##UPDATE INVENTORY DETAIL
                self.env.cr.execute("delete from sis_pps_inv_detail "+ \
                            " where header_id="+str(inv.id))
                
                self.env.cr.execute("select extract(day from posting_date), entrytype, sum(quantity) from sis_ile_temp "+ \
                                " where extract(month from posting_date)="+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ \
                                " and item_no='"+inv.item_no+"' and variant='"+variant+"'" \
                                " and bg='"+inv.ati12.upper()+"'"+ \
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
                            valsinvdetail={'item_no':inv.item_no,
                                     'description':inv.description,
                                     'variant':variant,
                                     'header_id':inv.id
                                     }
                            currentrytype=entrytype                    
                        valsinvdetail.update({'t'+str(int(tgl)): qty / inv.qtyperuom})

                valsinvdetail.update({'entrytype':currentrytype})
                self.env['sis.pps.inv.detail'].create(valsinvdetail)

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
        


    def countmaterial(self):

        self.env['sis.pps.material'].search([('header_id','=',self.id)]).unlink()
        self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id)]).unlink()        
#        shs=self.env['sis.so.header'].search([('shipmentdate','&lt;',datetime.strftime(str(self.year)+'-'+str(self.month+1)+'-01')), ('shipmentdate','&gt;=',datetime.strftime(str(self.year)+'-'+str(self.month)+'-01'))])
#        for sh in shs:
        vals={}
        uoms={}
        for d in self.detail_id:
            if d.type!='production':
                continue
            if d.variant_code==False:
                variant1=''
            else:
                variant1=d.variant_code
            pb=self.env['sis.production.bom'].search([('itemno','=',d.item_no),('variant','=',variant1)])
            if len(pb)==0:
                continue
                raise UserError('There is Item in Plan without BoM')
            else:
                for pl in pb:
                    for i in range(1,32):
                        if d['t'+str(i)]!=0:
                            fprd=self.env['sis.items'].search([('itemno','=',d.item_no)])
                            if len(fprd)==1 and pl.lineitc=='WIP' and pl.linepgc!='':
                                fish=fprd.fishmaterial
                            else:
                                fish=''
                            if not (pl.lineitem,fish) in vals:
                                vals.update({(pl.lineitem,fish) : {}})
                                for j in range(1,32):
                                    vals[(pl.lineitem,fish)].update({'t'+str(j):0})
                                uoms.update({pl.lineitem : (pl.lineuom,pl.linedesc)})
                                
                            if pl.variantuom==d.uom:
                                vals[(pl.lineitem,fish)]['t'+str(i)]+=pl.lineqtyper*d['t'+str(i)]
                            else:                                
                                vals[(pl.lineitem,fish)]['t'+str(i)]+=d['t'+str(i)]*d.qtyperuom/pl.variantqtyperuom*pl.lineqtyper
        for (item,fish),v in vals.items():
            #insert to material
            s=self.env['sis.pps.material'].search([('item_no','=',item),('fish','=',fish),('header_id','=',self.id)])
            
            (uom,desc)=uoms[item]
            v.update({'item_no':item,
                      'fish':fish,
                  'type':'material',
                  'description':desc,
                  'uom':uom
                })
            
            if len(s)==1:
                s.write(v)
            else:
                v.update({
                  'header':self.id,
                  'header_id':self.id
                })
                if len(s)==0:
                    self.env['sis.pps.material'].create(v)
                else:
                    raise UserError('Double material record !!')
             
            #insert to fish material
            if fish!='':
                v1={}
                fish1=fish
                if len(fish1)>2:
                    fish1=fish1[:2]
                budomari=self.env['sis.budomari'].search([('month','=',self.month),('year','=',self.year),('ati12','=',self.ati12),('fish','=',fish1)]).budomari
                if budomari==0:
                    raise UserError('Budomari = 0 or does not exist')
                for i in range(1,32):
                    v1.update({'t'+str(i) : v['t'+str(i)]*100/budomari})
                    if v1['t'+str(i)]!=0 and uom=='GR':
                        v1['t'+str(i)]/=1000
                uom='KG'
                
                s=self.env['sis.pps.fishmaterial'].search([('fish','=',fish),('header_id','=',self.id)])
                
                v1.update({'fish':fish,
                           'type':'FISH',
                           'uom':uom
                    })
                
                if len(s)==1:
                    s.write(v1)
                else:
                    v1.update({
                      'header':self.id,
                      'header_id':self.id
                    })
                    if len(s)==0:
                        self.env['sis.pps.fishmaterial'].create(v1)
                    else:
                        raise UserError('Double material record !!')
        
        self.calculate_loin_need()
        
    def calculate_loin_need(self):

        #CALCULATE LOIN NEEDED AND FISH REDUCE
        vf={}
        vl={}
       
        if self.ul!='unlabeled':
            return
        for j in range(1,32):
            i=str(j)
            rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('t'+i,'!=',0)])
            total=0
            for r in rs:
                total+=r['t'+i]
            l=self.env['sis.clean.capacity'].search([('ati12','=',self.ati12),('month','=',self.month),('year','=',self.year)])
            if len(l)>0 and len(rs)>0:
                if l.capacity<total:
                    overfish=total-l.capacity
                    ppsitems=self.env['sis.pps.item'].search([('ati12','=',self.ati12),('priority','!=',0)],order="priority, item_no")
                    for ppsitem in ppsitems:

                        orders=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',ppsitem.item_no),('t'+i,'!=',0),('type','=','production')])
                        for order in orders:

                            #look to NAV item master
                            fprd=self.env['sis.items'].search([('itemno','=',order.item_no)])
                            if fprd and len(fprd)==1:
                                pass
                            else:
                                raise UserError('Error In Item Master NAV !')

                            if fprd.fishmaterial=='':
                                raise UserError('There is product that does not have fish material in NAV !')
    
                            if order.variant_code==False:
                                variant1=''
                            else:
                                variant1=order.variant_code
                                
                            #look for type of fish
                            fish=fprd.fishmaterial
                            fish1=fish
                            if len(fish1)>2:
                                fish1=fish1[:2]
                        
                            budomari=self.env['sis.budomari'].search([('month','=',self.month),('year','=',self.year),('ati12','=',self.ati12),('fish','=',fish1)]).budomari        
                            pb=self.env['sis.production.bom'].search([('itemno','=',order.item_no),('variant','=',variant1),('lineitc','=','WIP'),('linepgc','!=','')])

                            loin4order=order['t'+i]*order.qtyperuom*pb.lineqtyper*ppsitem.fzpercent/100
                            fish2reduce=loin4order/(budomari/100)
                            if pb.lineuom=='GR':
                                loin4order /=1000
                                fish2reduce/=1000
                            if overfish>fish2reduce:
                                overfish -= fish2reduce
                            else:
                                fish2reduce=overfish
                                loin4order=fish2reduce*budomari/100
                                overfish=0
                            
                            try:
                                vf[fish]['t'+i] += fish2reduce
                                vl[(ppsitem.fz,fprd.pgc)]['t'+i] += loin4order                                
                            except:
                                for counter in (1,32):
                                    vf.update({fish: {'t'+i:0}})                                
                                    vl.update({(ppsitem.fz,fprd.pgc): {'t'+i:0}})
                                    
                                vf.update({fish: {'t'+i:fish2reduce}})                                
                                vl.update({(ppsitem.fz,fprd.pgc): {'t'+i:loin4order}})
                                                                                            
                            if overfish==0:
                                break
                        if overfish==0:
                            break

        #REDUCING FISH QTY IN DB
        for fish,txs in vf.items():
            valfish={}
            rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('fish','=',fish)])
            if rs and len(rs)==1:
                pass
            else:
                raise UserError('Error in reducing fish !')
            for t in txs.items():
                tx,value = t
                if value!=0:
                    valfish.update({tx:rs[tx]-value})
            rs.update(valfish)
        
        #CALCULATE TOTAL FISH
        total={'header_id':self.id,
               'header':self.id,
               'type':'TOTAL',
               'fish':'FISH',
               'uom':'KG'}
        for counter in range(1,32):
            total.update({'t'+str(counter):0})
        rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('type','=','FISH')])       
        for r in rs:      
            for counter in range(1,32):
                if r['t'+str(counter)]!=0:
                    total['t'+str(counter)]+=r['t'+str(counter)]
        self.env['sis.pps.fishmaterial'].create(total)
              
        #WRITING LOIN QTY IN DB
        for (loin,pgc),tx in vl.items():
            valfish={'type':'LOIN',
                     'fish':loin,
                     'pgc':pgc,
                     'header_id':self.id,
                     'header':self.id,
                     'uom':'KG'}
            valfish.update(tx)
            self.env['sis.pps.fishmaterial'].create(valfish)

        #CALCULATE TOTAL LOIN
        total={'header_id':self.id,
               'header':self.id,
               'type':'TOTAL',
               'fish':'LOIN',
               'uom':'KG'}
        for counter in (1,32):
            total.update({'t'+str(counter):0})
        rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('type','=','LOIN')])       
        for r in rs:      
            for counter in range(1,32):
                if r['t'+str(counter)]!=0:
                    total['t'+str(counter)]+=r['t'+str(counter)]
        self.env['sis.pps.fishmaterial'].create(total)


        
    def getso(self):
#        shs=self.env['sis.so.header'].search([('shipmentdate','&lt;',datetime.strftime(str(self.year)+'-'+str(self.month+1)+'-01')), ('shipmentdate','&gt;=',datetime.strftime(str(self.year)+'-'+str(self.month)+'-01'))])
#        for sh in shs:

        self.env.cr.execute("select max(detailnum) from sis_pps_detail where header_id="+str(self.id))
        ds=self.env.cr.fetchall()
        if ds!=[(None,)]:
            [(detailnum,)]=ds
        else:
            detailnum=0

        if self.ati12=='ati2':
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from postingdate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                                " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                                " and extract(year from postingdate)="+str(self.year)+ \
                                " and bg='ATI2'" \
                                " group by extract(day from postingdate), itemno, variant, uom, qtyperuom, pgc "+ \
                                " order by itemno, variant, extract(day from postingdate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), itemnoun, '', sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                                " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                                " and extract(year from itemrequireddate)="+str(self.year)+ \
                                " and bg='ATI2'" \
                                " group by extract(day from itemrequireddate), itemnoun, uom, qtyperuom, pgc "+ \
                                " order by itemnoun, extract(day from itemrequireddate)")
        else:
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from postingdate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                                " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                                " and extract(year from postingdate)="+str(self.year)+ \
                                " and bg<>'ATI2'" \
                                " group by extract(day from postingdate), itemno, variant, uom, qtyperuom, pgc "+ \
                                " order by itemno, variant, extract(day from postingdate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), itemnoun, '', sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                                " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                                " and extract(year from itemrequireddate)="+str(self.year)+ \
                                " and bg<>'ATI2'" \
                                " group by extract(day from itemrequireddate), itemnoun, uom, qtyperuom, pgc "+ \
                                " order by itemnoun, extract(day from itemrequireddate)")
        rs=self.env.cr.fetchall()
        
        curritem="first"
        vals={}
        wvart=None
        vart=None
        wit=None
        wuom=None
        for r in rs:
            (d,item,variant,qty,uom, qtyperuom, pgc)=r
            
            pgcm=self.env['sis.pgc.case48'].search([('pgc','=',pgc)])
            if len(pgcm)>1:
                raise UserError('PGC double on PGC Case48 master')                
            else:
                if len(pgcm)==1:
                    qty=qty*qtyperuom/48
                    qtyperuom=48
                    uom='CASE'

            if len(item)>0:
                it=self.env['sis.items'].search([('itemno','=',item)])
                if len(it)==0:
                    raise UserError('Item on SO does not exist on NAV Item Master')
                    continue
                if len(it)>1:
                    raise UserError('Double item !')
                    continue
                
            else:
                continue
            
            if variant!='' and self.ul=='labeled':
                vart=self.env['sis.item.variants'].search([('itemno','=',item),('variant','=',variant)])
                if len(vart)==0:
                    raise UserError('Variant on SO does not exist on NAV Variant Master')
                    continue                        
            
            if item+variant!=curritem or curritem=='first':
                if curritem!='first':
                    detailnum=self.insert_data(vals,variant, item,wit,wvart, wuom, detailnum)  
                vals={}
                for i in range(1,32):
                    vals.update({'t'+str(i):0})
                curritem=item+variant
            vals['t'+str(int(d))]=qty
            wvart=vart
            wit=it
            wuom=uom
            
        #insert last item
        if curritem!='first':
            detailnum=self.insert_data(vals,variant, item,wit,wvart, wuom,detailnum)      
            
        self.lastupdate=datetime.now()+timedelta(hours=7)     

    def insert_data(self, vals, variant, item,wit,wvart, uom,detailnum):            
        if wvart==None:
            variant1=None
        else:
            variant1=wvart.variant
        item=wit.itemno
            
#         vals1={}
#         running=0
        first=True
#         for i in range(1,32):
#             running=running-vals['t'+str(i)]
#             vals1.update({'t'+str(i):running})
                
        for i in ['sales','production','inventory']:
            sl=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',item),('variant_code','=',variant1),('type','=',i)])

            if i=='inventory' or i=='production' or i=='plan':
                vals.update({'hideline':True})
            else:
                vals.update({'hideline':False})


            if len(sl)==0:
                if i=='production' or i=='plan' or i=='inventory':
                    for x in range(1,32):                     
                        vals.update({'t'+str(x):0})

                if wvart!=None:
                    vals.update({'variant_code':wvart.variant})
                if first:
                    detailnum=detailnum+1
                    first=False
                vals.update({'header_id':self.id,
                             'header':self.id,
                            'item_no':wit.itemno,
                            'description':wit.description,
                          'uom':uom,
                          'type':i,
                          'qtyperuom':wit.qtyperuom,
                          'detailnum':detailnum
                          })
                rs=self.env['sis.pps.item'].search([('item_no','=',wit.itemno)])
                line=False
                if len(rs)==1:
                    line= rs.line
 
                if i=='production':
                    if line and len(line)>0:
                        vals.update({'line_id':line})
                else:
                    vals.pop('line_id',None)

                sl=self.env['sis.pps.detail'].create(vals)                
                if i=='sales':
                    sid=sl.id
                
            else:    
                if i=='sales':
                    sl.write(vals)
                    sid=sl.id

        #update flag NAV
        sql="update sis_pps_so_current set existnav=False where header_id="+str(sid)
        self.env.cr.execute(sql)
        
        #update history SO
        if self.ul=='labeled':
            sql= "select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom from sis_so_header sh "+ \
                        " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                        " and extract(year from postingdate)="+str(self.year)+" and itemno='"+wit.itemno+"'" 
            if wvart!=None:
                sql+=" and variant='"+variant+"'"
        else:
            sql="select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom from sis_so_header sh "+ \
                        " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                        " and extract(year from itemrequireddate)="+str(self.year) +" and itemnoun='"+wit.itemno+"'" 
            if wvart!=None:
                sql+=" and variant='"+variant+"'"
        self.env.cr.execute(sql)
        ss=self.env.cr.fetchall()

        for s in ss:
            (no, pd, ird, custcode, custname, shiptoname, extdocno, bg, lineno, itemno, description, variant, qty, qtyperuom, uom)=s

            scs=self.env['sis.pps.so.current'].search([('header_id','=',sid),('no','=',no),('lineno','=',lineno),('itemno','=',itemno),('variant','=',variant)],order='id desc',limit=1)
            if len(scs)==1:
                if scs.postingdate==pd and scs.itemrequireddate==ird and scs.bg==bg and scs.quantity==qty and scs.uom==uom:
                    scs.existnav=True
                else:            
                    valso={'header_id':scs.header_id.id,
                                'no':scs.no,
                                'selltono': scs.selltono,
                                'selltoname': scs.selltoname,
                                'shiptoname':scs.shiptoname,
                                'itemrequireddate': scs.itemrequireddate,
                                'postingdate':scs.postingdate,
                                'extdocno':scs.extdocno,
                                'bg':scs.bg,
                                'lineno':scs.lineno,
                                'itemno':scs.itemno,
                                'description':scs.description,
                                'variant':scs.variant,
                                'quantity':scs.quantity,
                                'qtyperuom': scs.qtyperuom,
                                'uom':scs.uom,
                                'ati1qty':scs.ati1qty,
                                'ati1date':scs.ati1date,
                                'ati2qty':scs.ati2qty,
                                'ati2date':scs.ati2date,                                                                                                
                                'existnav':False,
                                'changetime':scs.write_date,
                                'curr_id':scs.id
                              }
                    self.env['sis.pps.so.history'].create(valso)              
                 
                    valso={'selltono': custcode,
                        'selltoname': custname,
                        'shiptoname':shiptoname,
                        'itemrequireddate': ird,
                        'postingdate':pd,
                        'extdocno':extdocno,
                        'bg':bg,
                        'quantity':qty,
                        'qtyperuom':qtyperuom,
                        'uom':uom,
                        'existnav':True
                      }
                    scs.write(valso)              
            else:
                valso={'header_id':sid,
                    'no':no,
                    'selltono': custcode,
                    'selltoname': custname,
                    'shiptoname':shiptoname,
                    'itemrequireddate': ird,
                    'postingdate':pd,
                    'extdocno':extdocno,
                    'bg':bg,
                    'lineno':lineno,
                    'itemno':itemno,
                    'description':description,
                    'variant':variant,
                    'quantity':qty,
                    'qtyperuom':qtyperuom,
                    'uom':uom,
                    'existnav':True
                  }
                curr_id=self.env['sis.pps.so.current'].create(valso)  
                
#                valso.update({'curr_id':curr_id.id,
#                              'changetime':curr_id.write_date})
#                self.env['sis.pps.so.history'].create(valso)              
        return detailnum
#     @api.depends('month')
#     def _compute_invis(self):
#         for d in self.detail_id:
#             if d.header_id.year%4!=0 and self.month ==2:
#                 d.invist29=True
#             else:
#                 d.invist29=False
#             if self.month != 2:
#                 self.invist30=False
#             else:
#                 self.invist30=True
#             if self.month in (1,3,5,7,8,10,12):
#                 self.invist31=False
#             else:
#                 self.invist31=True
#         self.check=True

    @api.constrains('pp_no')
    def pp_no_unique(self):
        if self.search_count([('pp_no','=',self.pp_no),('id','!=',self.id)])>0:
            raise UserError ('Error in Production Planning Number')
        
    @api.constrains('ul','month','year','ati12')
    def all_unique(self):
        if self.search_count([('ul','=',self.ul),('month','=',self.month),('year','=',self.year),('ati12','=',self.ati12),('id','!=',self.id)])>0:
            raise UserError ('Production Planning already EXISTS')
        
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        if vals['ati12']=='ati1':
            no=self.env['ir.sequence'].next_by_code('sis.pps.header.ati1.seq')
        if vals['ati12']=='ati2':
            no=self.env['ir.sequence'].next_by_code('sis.pps.header.ati2.seq')
        vals.update({'pp_no':no}) 
        return models.Model.create(self, vals)
    
class sis_pps_detail(models.Model):
    _name='sis.pps.detail'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    year=fields.Integer(related='header_id.year', string='year')
    ati12=fields.Selection(related='header_id.ati12', string='ati')

    detailnum = fields.Integer(string='#')
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    uom = fields.Char(size=20,string="___UoM___")
    qtyperuom = fields.Float(string='Qty/UoM')
    #line_id = fields.Many2one('sis.pps.line',string='___Line___')#fields.Char(size=10,string='Line')    
    line_id = fields.Char(size=20,string='Line')    
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('sales','Sales'),('production','Production'),('plan','Plan'),('inventory','Inventory')],default='sales',string="Type")

    actualdate = fields.Date('Actual Date')
    qtyactual = fields.Float(string='Actual Qty')
    t0 = fields.Integer(string="__O") #saldo awal
    capacity = fields.Float(compute='_compute_capacity',string='Capacity/Line/Hour')
    linenum = fields.Integer(compute='_compute_linenum',string='Line num')

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
    
    f1 = fields.Integer(compute='_compute_overcapacity1',string="__O1")
    f2 = fields.Integer(compute='_compute_overcapacity2',string="__O")
    f3 = fields.Integer(compute='_compute_overcapacity3',string="__O")
    f4 = fields.Integer(compute='_compute_overcapacity4',string="__O")
    f5 = fields.Integer(compute='_compute_overcapacity5',string="__O")
    f6 = fields.Integer(compute='_compute_overcapacity6',string="__O")
    f7 = fields.Integer(compute='_compute_overcapacity7',string="__O")
    f8 = fields.Integer(compute='_compute_overcapacity8',string="__O")
    f9 = fields.Integer(compute='_compute_overcapacity9',string="__O")
    f10 = fields.Integer(compute='_compute_overcapacity10',string="__O")
    f11 = fields.Integer(compute='_compute_overcapacity11',string="__O")
    f12 = fields.Integer(compute='_compute_overcapacity12',string="__O")
    f13 = fields.Integer(compute='_compute_overcapacity13',string="__O")
    f14 = fields.Integer(compute='_compute_overcapacity14',string="__O")
    f15 = fields.Integer(compute='_compute_overcapacity15',string="__O")
    f16 = fields.Integer(compute='_compute_overcapacity16',string="__O")
    f17 = fields.Integer(compute='_compute_overcapacity17',string="__O")
    f18 = fields.Integer(compute='_compute_overcapacity18',string="__O")
    f19 = fields.Integer(compute='_compute_overcapacity19',string="__O")
    f20 = fields.Integer(compute='_compute_overcapacity20',string="__O")
    f21 = fields.Integer(compute='_compute_overcapacity21',string="__O")
    f22 = fields.Integer(compute='_compute_overcapacity22',string="__O")
    f23 = fields.Integer(compute='_compute_overcapacity23',string="__O")
    f24 = fields.Integer(compute='_compute_overcapacity24',string="__O")
    f25 = fields.Integer(compute='_compute_overcapacity25',string="__O")
    f26 = fields.Integer(compute='_compute_overcapacity26',string="__O")
    f27 = fields.Integer(compute='_compute_overcapacity27',string="__O")
    f28 = fields.Integer(compute='_compute_overcapacity28',string="__O")
    f29 = fields.Integer(compute='_compute_overcapacity29',string="__O")
    f30 = fields.Integer(compute='_compute_overcapacity30',string="__O")
    f31 = fields.Integer(compute='_compute_overcapacity31',string="__O")

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

    
    invist29 = fields.Boolean(related='header_id.invist29',string='Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='Invis')

    hideline = fields.Boolean(string='Hide Line') 
    
    readonlyall=fields.Boolean(compute='',string='Readonly')   
    so_current_id=fields.One2many('sis.pps.so.current','header_id')
    so_history_id=fields.One2many('sis.pps.so.history','header_id')
#     updateinvent1=fields.Boolean(string='Readonly',store=True)   
#     updateinvent=fields.Boolean(compute='_compute_inventory1',string='Readonly') 


    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        idd=models.Model.create(self, vals)
        if idd.type=='production':
            vals.pop('line_id',None)
            vals.update({'type':'plan'})
            self.env['sis.pps.detail'].create(vals)
        return idd

    @api.multi
    def write(self, vals):
        idd=models.Model.write(self, vals)
        if self.type=='production':
            vals.pop('line_id',None)
            #vals.update({'type':'plan'})
            for i in range(1,32):
                if self['a'+str(i)]==True:
                    vals.pop('t'+str(i),None)
            rs=self.env['sis.pps.detail'].search([('header_id','=',self.header),('detailnum','=',self.detailnum),('type','=','plan')])
            rs.write(vals)
        return idd

    @api.one
    @api.constrains('line_id')
    def _constrain_line_id(self):
        if self.item_no and self.header_id.ati12 and self.line_id:
            s=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=',self.header_id.ati12)])
            if s and len(s)==1:
                lines=s.line.split(',')
                if lines:
                    for line in self.line_id.split(','):
                        if  line in lines:    
                            pass
                        else: 
                            raise UserError('Item does not match line!')                    
                else:
                    raise UserError('Line config is error')
            else:
                raise UserError('Item does not exist in Lines!')
   
            if self.type=='production':
                looks=self.env['sis.pps.detail'].search([('header_id','=',self.header),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('type','=','production'),('id','!=',self.id)])
                if looks and len(looks)>0:
                    raise UserError('Data Already exist !')
#                 for look in looks:
#                     curr=self.line_id.split(',')
#                     lines=look.line_id.split(',')
#                     a=set(curr).intersection(lines)
#                     if a and len(a)==len(curr) and len(a)==len(lines):
#                         raise UserError('Data Already exist !')
   

    @api.one
    @api.depends('item_no','line_id','header_id.ati12')
    def _compute_capacity(self):
        if self.item_no and self.header_id.ati12 and self.line_id:
            ss=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=',self.header_id.ati12)])
            if ss and len(ss)==1:
                found=False
                for s in ss:
                    for lin in self.line_id.split(','):
                        if lin in s.line.split(','):
                            found=True 
                            self.capacity=s.capacity
                            break
                    if found:
                        break
                if not found:
                    raise UserError('Cannot find capacity for '+ self.item_no)
            else:
                raise UserError('Capacity Error!')
            
    @api.one
    @api.depends('line_id')
    def _compute_linenum(self):
        if self.line_id and self.type=='production':        
            self.linenum=len(self.line_id.split(','))
#             rs=self.env['sis.pps.detail'].search([('header_id','=',self.header),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('detailnum','=',self.detailnum),('type','!=','production')])
#             for r in rs:
#                 if r.line_id!=self.line_id.id:
#                     r.line_id=self.line_id.id

    
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
        if self.type=='production':
            return {
                'name': self.description + ' - '+variant,
                'res_model': 'sis.production.bom',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_master.sis_production_bom_tree').id,
                'target': 'new',
                'nodestroy':True,
                'domain':"[('itemno','=','"+self.item_no+"'),('variant','=','"+variant+"')]"
            }
        if self.type=='inventory':
            return {
                'name': self.description + ' - '+variant,
                'res_model': 'sis.pps.inv.detail',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_inv_detail_tree').id,
                'target': 'new',
                'nodestroy':True,
                'domain':"[('item_no','=','"+self.item_no+"'),('variant','=','"+variant+"'),('header_id','=',"+str(self.id)+")]"
            }


    @api.multi
    @api.onchange('t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13','t14','t15','t16','t17','t18','t19','t20','t21','t22','t23','t24','t25','t26','t27','t28','t29','t30','t31')
    def _onchange_inventory1(self):
        for r in self:
            header_id=self._origin.header
            s=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',self._origin.detailnum),('type','=','sales')])
            inv=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',self._origin.detailnum),('type','=','inventory')])
            vals={'t0':inv['t0']}
            run=inv['t0']
            for i in range(1,32):
                if inv['a'+str(i)]==False:
                    vals.update({'t'+str(i):run+r['t'+str(i)]-s['t'+str(i)]})
                    run+=(r['t'+str(i)]-s['t'+str(i)])
                else:
                    run=inv['t'+str(i)]
            inv.write(vals)

    @api.one
    @api.depends('line_id', 't1')
    def _compute_overcapacity1(self):
        return self.overcapacity('1')
    @api.one
    @api.depends('line_id', 't2')
    def _compute_overcapacity2(self):
        return self.overcapacity('2')
    @api.one
    @api.depends('line_id', 't3')
    def _compute_overcapacity3(self):
        return self.overcapacity('3')
    @api.one
    @api.depends('line_id', 't4')
    def _compute_overcapacity4(self):
        return self.overcapacity('4')
    @api.one
    @api.depends('line_id', 't5')
    def _compute_overcapacity5(self):
        return self.overcapacity('5')
    @api.one
    @api.depends('line_id', 't6')
    def _compute_overcapacity6(self):
        return self.overcapacity('6')
    @api.one
    @api.depends('line_id', 't7')
    def _compute_overcapacity7(self):
        return self.overcapacity('7')
    @api.one
    @api.depends('line_id', 't8')
    def _compute_overcapacity8(self):
        return self.overcapacity('8')
    @api.one
    @api.depends('line_id', 't9')
    def _compute_overcapacity9(self):
        return self.overcapacity('9')
    @api.one
    @api.depends('line_id', 't10')
    def _compute_overcapacity10(self):
        return self.overcapacity('10')
    @api.one
    @api.depends('line_id', 't11')
    def _compute_overcapacity11(self):
        return self.overcapacity('11')
    @api.one
    @api.depends('line_id', 't12')
    def _compute_overcapacity12(self):
        return self.overcapacity('12')
    @api.one
    @api.depends('line_id', 't13')
    def _compute_overcapacity13(self):
        return self.overcapacity('13')
    @api.one
    @api.depends('line_id', 't14')
    def _compute_overcapacity14(self):
        return self.overcapacity('14')
    @api.one
    @api.depends('line_id', 't15')
    def _compute_overcapacity15(self):
        return self.overcapacity('15')
    @api.one
    @api.depends('line_id', 't16')
    def _compute_overcapacity16(self):
        return self.overcapacity('16')
    @api.one
    @api.depends('line_id', 't17')
    def _compute_overcapacity17(self):
        return self.overcapacity('17')
    @api.one
    @api.depends('line_id', 't18')
    def _compute_overcapacity18(self):
        return self.overcapacity('18')
    @api.one
    @api.depends('line_id', 't19')
    def _compute_overcapacity19(self):
        return self.overcapacity('19')
    @api.one
    @api.depends('line_id', 't20')
    def _compute_overcapacity20(self):
        return self.overcapacity('20')
    @api.one
    @api.depends('line_id', 't21')
    def _compute_overcapacity21(self):
        return self.overcapacity('21')
    @api.one
    @api.depends('line_id', 't22')
    def _compute_overcapacity22(self):
        return self.overcapacity('22')
    @api.one
    @api.depends('line_id', 't23')
    def _compute_overcapacity23(self):
        return self.overcapacity('23')
    @api.one
    @api.depends('line_id', 't24')
    def _compute_overcapacity24(self):
        return self.overcapacity('24')
    @api.one
    @api.depends('line_id', 't25')
    def _compute_overcapacity25(self):
        return self.overcapacity('25')
    @api.one
    @api.depends('line_id', 't26')
    def _compute_overcapacity26(self):
        return self.overcapacity('26')
    @api.one
    @api.depends('line_id', 't27')
    def _compute_overcapacity27(self):
        return self.overcapacity('27')
    @api.one
    @api.depends('line_id', 't28')
    def _compute_overcapacity28(self):
        return self.overcapacity('28')
    @api.one
    @api.depends('line_id', 't29')
    def _compute_overcapacity29(self):
        return self.overcapacity('29')
    @api.one
    @api.depends('line_id', 't30')
    def _compute_overcapacity30(self):
        return self.overcapacity('30')
    @api.one
    @api.depends('line_id', 't31')
    def _compute_overcapacity31(self):
        return self.overcapacity('31')

    def overcapacity(self,i):            
        try:
            test=self.env['sis.pps.header'].search([('id','=',self.header)])
        except:
            test=False
            
        if test and len(test)==1 and self.type=='production' :#and self.ul=='unlabeled':
            if self.line_id:
                #update group
#                 rs=self.env['sis.pps.detail'].search([('header_id','=',self.header),('detailnum','=',self.detailnum),('type','=','plan')])
#                 if rs['a'+i]==False and rs.type=='plan' and rs['t'+i]!=self['t'+i]:
#                     a={'t'+i:self['t'+i]}
#                     rs.write(a)
                      
                #look for workhours
                try:
                    dt=datetime.strptime(str(self.year)+'-'+str(self.month)+'-'+i,'%Y-%m-%d')
                except:
                    return
                days=self.env['sis.pps.exhour'].search([('workdate','=',dt)])
                if len(days)==0:
                    ordi=self.env['sis.pps.option'].search([('ati12','=',test.ati12)])
                    if ordi and len(ordi)==1:
                        if dt.weekday()==5:
                            hourlimit=ordi.fri
                        else:
                            if dt.weekday()==6:
                                hourlimit=ordi.sat
                            else:
                                hourlimit=ordi.montothu
                    else:
                        raise UserError('Option Error !')
                else:
                    if days and len(days)==1:
                        hourlimit=days.hours
                    else:
                        raise UserError('Hours option error !')
                                             
                 
                #update over capacity
                #lines=self.env['sis.pps.line'].search([('id','=',self.line_id.id)])
                ls=self.line_id.split(',')
 
                total=0#self['t'+i]/self['linenum']/self['capacity']
                if ls :
                    rs=self.env['sis.pps.detail'].search([('header_id','=',self.header),('line_id','!=',''),('t'+i,'!=',0),('type','=','production')])
                    for r in rs:
                        for lin in r.line_id.split(','):
                            if lin in ls: 
                                total+=r['t'+i]/r['linenum']/r['capacity']
                                break
 
                if hourlimit<total:
                    self['f'+i]=1
                else:
                    self['f'+i]=0                
            else:
                self['f'+i]=1            
        else:
            if self.type=='inventory':
                try:
                    dd=datetime.strptime(str(self.header_id.year)+'-'+str(self.header_id.month)+'-'+i,"%Y-%m-%d").weekday()
                except:
                    pass
                else:
                    if dd==6: 
                        self['f'+i]=2
                        

    @api.multi
    def unlink(self):
        for r in self:
            if r.type=='sales':               
                ds=self.env['sis.pps.detail'].search([('header_id','=',r.header_id.id),('detailnum','=',r.detailnum)])
                for d in ds:
                    d.unlink()
            return models.Model.unlink(self)   
        
class sis_pps_material(models.Model):
    _name='sis.pps.material'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No.___")
    uom = fields.Char(size=20,string="UoM______")
    description = fields.Char(size=200,string="Description________________________")
    type = fields.Selection([('material','Material')],default='material',string="Type")

    fish = fields.Char(size=20,string="Fish Type")
    t1 = fields.Float(string="1____")
    t2 = fields.Float(string="2____")
    t3 = fields.Float(string="3____")
    t4 = fields.Float(string="4____")
    t5 = fields.Float(string="5____")
    t6 = fields.Float(string="6____")
    t7 = fields.Float(string="7____")
    t8 = fields.Float(string="8____")
    t9 = fields.Float(string="9____")
    t10 = fields.Float(string="10____")
    t11 = fields.Float(string="11____")
    t12 = fields.Float(string="12____")
    t13 = fields.Float(string="13____")
    t14 = fields.Float(string="14____")
    t15 = fields.Float(string="15____")
    t16 = fields.Float(string="16____")
    t17 = fields.Float(string="17____")
    t18 = fields.Float(string="18____")
    t19 = fields.Float(string="19____")
    t20 = fields.Float(string="20____")
    t21 = fields.Float(string="21____")
    t22 = fields.Float(string="22____")
    t23 = fields.Float(string="23____")
    t24 = fields.Float(string="24____")
    t25 = fields.Float(string="25____")
    t26 = fields.Float(string="26____")
    t27 = fields.Float(string="27____")
    t28 = fields.Float(string="28____")
    t29 = fields.Float(string="29____")
    t30 = fields.Float(string="30____")
    t31 = fields.Float(string="31____")        
    
    invist29 = fields.Boolean(related='header_id.invist29',string='__Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='__Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='__Invis')


class sis_pps_fishmaterial(models.Model):
    _name='sis.pps.fishmaterial'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    
    header = fields.Integer(string="header")
    type = fields.Char(size=20,string="Type")
    fish = fields.Char(size=20,string="Fish/Loin")
    pgc = fields.Char(size=10,string="PGC")
    uom = fields.Char(size=20,string="UoM")
    t1 = fields.Integer(string="1____")
    t2 = fields.Integer(string="2____")
    t3 = fields.Integer(string="3____")
    t4 = fields.Integer(string="4____")
    t5 = fields.Integer(string="5____")
    t6 = fields.Integer(string="6____")
    t7 = fields.Integer(string="7____")
    t8 = fields.Integer(string="8____")
    t9 = fields.Integer(string="9____")
    t10 = fields.Integer(string="10____")
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
    
    invist29 = fields.Boolean(related='header_id.invist29',string='__Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='__Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='__Invis')
    
    f1 = fields.Integer(compute='_compute_overcapacity1',string="__Over1")
    f2 = fields.Integer(compute='_compute_overcapacity2',string="__Over2")
    f3 = fields.Integer(compute='_compute_overcapacity3',string="__Over3")
    f4 = fields.Integer(compute='_compute_overcapacity4',string="__Over4")
    f5 = fields.Integer(compute='_compute_overcapacity5',string="__Over5")
    f6 = fields.Integer(compute='_compute_overcapacity6',string="__Over6")
    f7 = fields.Integer(compute='_compute_overcapacity7',string="__Over7")
    f8 = fields.Integer(compute='_compute_overcapacity8',string="__Over8")
    f9 = fields.Integer(compute='_compute_overcapacity9',string="__Over9")
    f10 = fields.Integer(compute='_compute_overcapacity10',string="__Over10")
    f11 = fields.Integer(compute='_compute_overcapacity11',string="__Over11")
    f12 = fields.Integer(compute='_compute_overcapacity12',string="__Over12")
    f13 = fields.Integer(compute='_compute_overcapacity13',string="__Over13")
    f14 = fields.Integer(compute='_compute_overcapacity14',string="__Over14")
    f15 = fields.Integer(compute='_compute_overcapacity15',string="__Over15")
    f16 = fields.Integer(compute='_compute_overcapacity16',string="__Over16")
    f17 = fields.Integer(compute='_compute_overcapacity17',string="__Over17")
    f18 = fields.Integer(compute='_compute_overcapacity18',string="__Over18")
    f19 = fields.Integer(compute='_compute_overcapacity19',string="__Over19")
    f20 = fields.Integer(compute='_compute_overcapacity20',string="__Over20")
    f21 = fields.Integer(compute='_compute_overcapacity21',string="__Over21")
    f22 = fields.Integer(compute='_compute_overcapacity22',string="__Over22")
    f23 = fields.Integer(compute='_compute_overcapacity23',string="__Over23")
    f24 = fields.Integer(compute='_compute_overcapacity24',string="__Over24")
    f25 = fields.Integer(compute='_compute_overcapacity25',string="__Over25")
    f26 = fields.Integer(compute='_compute_overcapacity26',string="__Over26")
    f27 = fields.Integer(compute='_compute_overcapacity27',string="__Over27")
    f28 = fields.Integer(compute='_compute_overcapacity28',string="__Over28")
    f29 = fields.Integer(compute='_compute_overcapacity29',string="__Over29")
    f30 = fields.Integer(compute='_compute_overcapacity30',string="__Over30")
    f31 = fields.Integer(compute='_compute_overcapacity31',string="__Over31")
    
    @api.one
    @api.depends('t1')
    def _compute_overcapacity1(self):
        return self.overcapacity('1')
    @api.one
    @api.depends('t2')
    def _compute_overcapacity2(self):
        return self.overcapacity('2')
    @api.one
    @api.depends('t3')
    def _compute_overcapacity3(self):
        return self.overcapacity('3')
    @api.one
    @api.depends('t4')
    def _compute_overcapacity4(self):
        return self.overcapacity('4')
    @api.one
    @api.depends('t5')
    def _compute_overcapacity5(self):
        return self.overcapacity('5')
    @api.one
    @api.depends('t6')
    def _compute_overcapacity6(self):
        return self.overcapacity('6')
    @api.one
    @api.depends('t7')
    def _compute_overcapacity7(self):
        return self.overcapacity('7')
    @api.one
    @api.depends('t8')
    def _compute_overcapacity8(self):
        return self.overcapacity('8')
    @api.one
    @api.depends('t9')
    def _compute_overcapacity9(self):
        return self.overcapacity('9')
    @api.one
    @api.depends('t10')
    def _compute_overcapacity10(self):
        return self.overcapacity('10')
    @api.one
    @api.depends('t11')
    def _compute_overcapacity11(self):
        return self.overcapacity('11')
    @api.one
    @api.depends('t12')
    def _compute_overcapacity12(self):
        return self.overcapacity('12')
    @api.one
    @api.depends('t13')
    def _compute_overcapacity13(self):
        return self.overcapacity('13')
    @api.one
    @api.depends('t14')
    def _compute_overcapacity14(self):
        return self.overcapacity('14')
    @api.one
    @api.depends('t15')
    def _compute_overcapacity15(self):
        return self.overcapacity('15')
    @api.one
    @api.depends('t16')
    def _compute_overcapacity16(self):
        return self.overcapacity('16')
    @api.one
    @api.depends('t17')
    def _compute_overcapacity17(self):
        return self.overcapacity('17')
    @api.one
    @api.depends('t18')
    def _compute_overcapacity18(self):
        return self.overcapacity('18')
    @api.one
    @api.depends('t19')
    def _compute_overcapacity19(self):
        return self.overcapacity('19')
    @api.one
    @api.depends('t20')
    def _compute_overcapacity20(self):
        return self.overcapacity('20')
    @api.one
    @api.depends('t21')
    def _compute_overcapacity21(self):
        return self.overcapacity('21')
    @api.one
    @api.depends('t22')
    def _compute_overcapacity22(self):
        return self.overcapacity('22')
    @api.one
    @api.depends('t23')
    def _compute_overcapacity23(self):
        return self.overcapacity('23')
    @api.one
    @api.depends('t24')
    def _compute_overcapacity24(self):
        return self.overcapacity('24')
    @api.one
    @api.depends('t25')
    def _compute_overcapacity25(self):
        return self.overcapacity('25')
    @api.one
    @api.depends('t26')
    def _compute_overcapacity26(self):
        return self.overcapacity('26')
    @api.one
    @api.depends('t27')
    def _compute_overcapacity27(self):
        return self.overcapacity('27')
    @api.one
    @api.depends('t28')
    def _compute_overcapacity28(self):
        return self.overcapacity('28')
    @api.one
    @api.depends('t29')
    def _compute_overcapacity29(self):
        return self.overcapacity('29')
    @api.one
    @api.depends('t30')
    def _compute_overcapacity30(self):
        return self.overcapacity('30')
    @api.one
    @api.depends('t31')
    def _compute_overcapacity31(self):
        return self.overcapacity('31')
    
    
    def overcapacity(self,i):            
        if self.type=='FISH' or self.fish=='FISH':
            rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.header_id.id),('t'+i,'!=',0),('type','=','FISH')])
            total=0
            for r in rs:
                total+=r['t'+i]
            l=self.env['sis.clean.capacity'].search([('ati12','=',self.header_id.ati12),('month','=',self.header_id.month),('year','=',self.header_id.year)])
            if len(l)>0 and len(rs)>0:
                if l.capacity<total:
                    self['f'+i]=1
                else:
                    self['f'+i]=0                
            else:
                self['f'+i]=0     

class sis_pps_inv_detail(models.Model):
    _name='sis.pps.inv.detail'

    header_id=fields.Many2one('sis.pps.detail',string='Header')
    item_no = fields.Char(size=20,string="Item No")
    description= fields.Char(size=200,string="Description")
    variant = fields.Char(size=20,string="Variant")
    entrytype = fields.Char(size=50,string="Variant")
    t1 = fields.Float(string="1____")
    t2 = fields.Float(string="2____")
    t3 = fields.Float(string="3____")
    t4 = fields.Float(string="4____")
    t5 = fields.Float(string="5____")
    t6 = fields.Float(string="6____")
    t7 = fields.Float(string="7____")
    t8 = fields.Float(string="8____")
    t9 = fields.Float(string="9____")
    t10 = fields.Float(string="10____")
    t11 = fields.Float(string="11____")
    t12 = fields.Float(string="12____")
    t13 = fields.Float(string="13____")
    t14 = fields.Float(string="14____")
    t15 = fields.Float(string="15____")
    t16 = fields.Float(string="16____")
    t17 = fields.Float(string="17____")
    t18 = fields.Float(string="18____")
    t19 = fields.Float(string="19____")
    t20 = fields.Float(string="20____")
    t21 = fields.Float(string="21____")
    t22 = fields.Float(string="22____")
    t23 = fields.Float(string="23____")
    t24 = fields.Float(string="24____")
    t25 = fields.Float(string="25____")
    t26 = fields.Float(string="26____")
    t27 = fields.Float(string="27____")
    t28 = fields.Float(string="28____")
    t29 = fields.Float(string="29____")
    t30 = fields.Float(string="30____")
    t31 = fields.Float(string="31____")        
        