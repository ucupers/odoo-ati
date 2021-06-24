from odoo import models, fields, api, _
from odoo.exceptions import UserError
from _datetime import datetime, timedelta

class sis_pps_detail_add(models.TransientModel):
    _name='sis.pps.detail.add'

    itm = fields.Many2one('sis.items',string='Item',domain=[('itc','=','FG')],required=True)
    variant = fields.Many2one('sis.item.variants',string='Variant', domain=lambda self: [('itemno','=',self.itm.itemno)])
    item_no = fields.Char(related='itm.itemno',string="Item No.")
    variant_code = fields.Char(related='variant.variant',string='Variant Code')
    line = fields.Char(size=10,string='Line') 
    
    def additem(self):
        idd=self._context['insert_id']
        for i in ('sales','production','inventory','plan'):
            if self.env['sis.pps.detail'].search_count([('header_id','=',idd),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('line','=',self.line),('type','=',i)])==0:
                if len(self.variant)>0:
                    uom=self.variant.uom
                else:
                    uom=self.itm.salesuom
                vals = {
                    'header_id':idd,
                    'header':idd,
                    'item_no':self.itm.itemno,
                    'variant_code':self.variant.variant,
                    'description':self.itm.description,                    
                    'type':i,
                    'uom':uom,
                    'qtyperuom':self.itm.qtyperuom
                    }    
                if i=='sales':
                    vals.update({'hideline':False})
                else:
                    vals.update({'hideline':True})                    
                self.env['sis.pps.detail'].create(vals)
            else:
                raise UserError('Data already exist !')
    
class sis_pps_header(models.Model):
    _name='sis.pps.header'

    pp_no = fields.Char(size=20,string="PP No.")
    ul = fields.Selection([('unlabeled','Unlabeled'),('labeled','Labeled')],string="Un/Labeled",required=True)
    month = fields.Selection([(1,'January'),(2,'February'),(3,'March'),(4,'April'),(5,'May'),(6,'June'),(7,'July'),(8,'August'),(9,'September'),(10,'October'),(11,'November'),(12,'December')],string="Month",required=True)
    year = fields.Integer(string="Year",required=True)
    ati12 = fields.Selection([('ati1','ATI1'),('ati2','ATI2')],string="ATI1/ATI2",required=True)
    
    lastupdate = fields.Datetime(string='Last Update')
    
    check = fields.Boolean(compute='_compute_invis',string='check',store=True)
    invist29 = fields.Boolean(compute='_compute_invist29',string='Invis')
    invist30 = fields.Boolean(compute='_compute_invist30',string='Invis')
    invist31 = fields.Boolean(compute='_compute_invist31',string='Invis')
   

    detail_id=fields.One2many('sis.pps.detail','header_id')
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
        ds=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','inventory')])
        for d in ds:
            #------------- hitung t0, actual date, actual stock
            if  d.variant_code==False:
                variant=''
                variantpps=None
            else:
                variant=variantpps=d.variant_code
            self.env.cr.execute("select max(posting_date), sum(quantity)"+ \
                            " from sis_ile" + \
                            " where posting_date<'"+str(self.year)+"-"+str(self.month)+"-1'"\
                            " and item_no='"+d.item_no+"' and variant='"+variant+"'"+ " and bg='"+d.ati12.upper()+"'")
            rs=self.env.cr.fetchall()
            for r in rs:
                (postingdate,quantity)=r
            
            valsd={'actualqty':quantity/d.qtyperuom,
                   'actualdate':datetime.strptime(postingdate,"%Y-%m-%d")}            
            yr=int(postingdate[:4])
            mt=int(postingdate[5:7])
            dy=int(postingdate[8:10])
            runm=mt
            runy=yr
            while runy*100+runm<d.year*100+d.month:
                if runm==mt:
                    start=dy+1
                if runm!=mt:
                    start=1                
                prod=self.env['sis.pps.detail'].search([('ati12','=',d.ati12),('ul','=',d.ul),('month','=',runm),('year','=',runy),('item_no','=',d.item_no),('variant_code','=',variantpps),('type','=','production')])
                if len(prod)>1:
                    raise UserError('Error in Production line')
                sls=self.env['sis.pps.detail'].search([('ati12','=',d.ati12),('ul','=',d.ul),('month','=',runm),('year','=',runy),('item_no','=',d.item_no),('variant_code','=',variantpps),('type','=','sales')])                        
                if len(sls)>1:
                    raise UserError('Error in Sales line')
                if len(prod)==1 and len(sls)==1:
                    for rund in range(start,32):
                        quantity=quantity+prod['t'+str(rund)]-sls['t'+str(rund)]
                
                runm+=1
                if runm>12:
                    runy+=1
                    runm=1

            valsd.update({'t0':quantity/d.qtyperuom})            
            #d.write(valsd)
            #------------- update actual production cuurent month            
            self.env.cr.execute("select max(extract(day from posting_date)) from sis_ile "+ \
                            " where extract(month from posting_date)="+str(self.month)+ \
                            " and extract(year from posting_date)="+str(self.year)+ \
                            " and item_no='"+d.item_no+"' and variant='"+variant+"'" \
                            " and item_no = 'Output'" + " and bg='"+d.ati12.upper()+"'")
            maxs=self.env.cr.fetchall()
            for maxx in maxs:
                (maxtgl)=maxx

            self.env.cr.execute("select extract(day from posting_date), sum(quantity) from sis_ile "+ \
                            " where extract(month from posting_date)="+str(self.month)+ \
                            " and extract(year from posting_date)="+str(self.year)+ \
                            " and item_no='"+d.item_no+"' and variant='"+variant+"'" \
                            " and item_no = 'Output'" + " and bg='"+d.ati12.upper()+"'"\
                            " group by extract(day from posting_date) "+ \
                            " order by extract(day from posting_date)")
            rs=self.env.cr.fetchall()
            tanggal=0
            actual={}
            for r in rs:
                (tanggal,qty)=r
                actual.update({tanggal:qty})

            if variant=='':
                variant=None
            prod=self.env['sis.pps.detail'].search([('ati12','=',d.ati12),('ul','=',d.ul),('month','=',d.month),('year','=',d.year),('item_no','=',d.item_no),('variant_code','=',variant),('line','=',d.line),('line','!=',None),('type','=','production')])
            if len(prod)>1:
                raise UserError('Error in Production line (update)')
            sls=self.env['sis.pps.detail'].search([('ati12','=',d.ati12),('ul','=',d.ul),('month','=',d.month),('year','=',d.year),('item_no','=',d.item_no),('variant_code','=',variant),('line','=',d.line),('line','!=',None),('type','=','sales')])                        
            if len(sls)>1:
                raise UserError('Error in Sales line (update)')

            valprod={}
            valinv={}
            for day in range(1,32):
                prodqty=prod['t'+str(day)]
                try:
                    prodqty=actual[day]
                except:
                    if maxtgl>=day:
                        prodqty=0
                    else:
                        prodqty=prod['t'+str(day)]
                valprod.update({'t'+str(day):prodqty})

                quantity=quantity+prodqty-sls['t'+str(day)]
                valinv.update({'t'+str(day):quantity})
            prod.write(valprod)
            d.write(valinv)
            
 #           for r in rs:


    def countmaterial(self):
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
                               
                
                        
        
    def getso(self):
#        shs=self.env['sis.so.header'].search([('shipmentdate','&lt;',datetime.strftime(str(self.year)+'-'+str(self.month+1)+'-01')), ('shipmentdate','&gt;=',datetime.strftime(str(self.year)+'-'+str(self.month)+'-01'))])
#        for sh in shs:

        if self.ul=='labeled':
            self.env.cr.execute("select extract(day from postingdate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                            " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                            " and extract(year from postingdate)="+str(self.year)+ \
                            " group by extract(day from postingdate), itemno, variant, uom, qtyperuom, pgc "+ \
                            " order by itemno, variant, extract(day from postingdate)")
        else:
            self.env.cr.execute("select extract(day from itemrequireddate), itemnoun, '', sum(quantity), uom, qtyperuom, pgc from sis_so_header sh "+ \
                            " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                            " and extract(year from itemrequireddate)="+str(self.year)+ \
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
                    self.insert_data(vals,variant, item,wit,wvart, wuom)  
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
            self.insert_data(vals,variant, item,wit,wvart, wuom)      
            
        self.lastupdate=datetime.now()+timedelta(hours=7)     

    def insert_data(self, vals, variant, item1,wit,wvart, uom):            
        if wvart==None:
            variant1=None
        else:
            variant1=wvart.variant
        item=wit.itemno
            
        vals1={}
        running=0
        for i in range(1,32):
            running=running-vals['t'+str(i)]
            vals1.update({'t'+str(i):running})
                
        for i in ['sales','production','inventory','plan']:
            sl=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',item),('variant_code','=',variant1),('type','=',i)])

            if i=='inventory' or i=='production' or i=='plan':
                vals.update({'hideline':True})
            else:
                vals.update({'hideline':False})

            if i=='production' or i=='plan':
                for x in range(1,32):
                    vals.update({'t'+str(x):0})
            if i=='inventory':
                for x in range(1,32):
                    vals.update({'t'+str(x):vals1['t'+str(x)]})

            if len(sl)==0:
                if wvart!=None:
                    vals.update({'variant_code':wvart.variant})
                vals.update({'header_id':self.id,
                             'header':self.id,
                            'item_no':wit.itemno,
                            'description':wit.description,
                          'uom':uom,
                          'type':i,
                          'qtyperuom':wit.qtyperuom
                          })

                sl=self.env['sis.pps.detail'].create(vals)                
                if i=='sales':
                    sid=sl.id
                
            else:    
                sl.write(vals)
                if i=='sales':
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
                sql+=" and variant='"+wvart.variant+"'"
        else:
            sql="select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom from sis_so_header sh "+ \
                        " inner join sis_so_line sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                        " and extract(year from itemrequireddate)="+str(self.year) +" and itemnoun='"+wit.itemno+"'" 
            if wvart!=None:
                sql+=" and variant='"+wvart.variant+"'"
        self.env.cr.execute(sql)
        ss=self.env.cr.fetchall()

        for s in ss:
            (no, pd, ird, custcode, custname, shiptoname, extdocno, bg, lineno, itemno, description, variant, qty, qtyperuom, uom)=s

            scs=self.env['sis.pps.so.current'].search([('header_id','=',sid),('no','=',no),('lineno','=',lineno),('itemno','=',itemno),('variant','=',variant1)],order='id desc',limit=1)
            if len(scs)==1:
                if scs.postingdate==pd and scs.itemrequireddate==ird and scs.bg==bg and scs.qty==qty:
                    scs.existnav=True
                else:            
                    valso={'header_id':scs.header_id,
                                'no':scs.no,
                                'selltono': scs.custcode,
                                'selltoname': scs.custname,
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
                                'curr_id':scs.curr_id
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
                
                valso.update({'curr_id':curr_id.id,
                              'changetime':curr_id.write_date})
                self.env['sis.pps.so.history'].create(valso)              

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
    
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    uom = fields.Char(size=20,string="___UoM___")
    qtyperuom = fields.Float(string='Qty/UoM')
    line = fields.Many2one('sis.pps.line',string='Line',required=True)#fields.Char(size=10,string='Line')    
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('sales','Sales'),('production','Production'),('plan','Plan'),('inventory','Inventory')],default='sales',string="Type")

    actualdate = fields.Date('Actual Date')
    qtyactual = fields.Float(string='Actual Qty')
    t0 = fields.Integer(string="__1__") #saldo awal
    capacity = fields.Float(compute='_compute_capacity',string='Capacity/Line/Hour')
    linenum = fields.Integer(compute='_compute_capacity',string='Capacity/Line/Hour')

    t1 = fields.Integer(string="__1__")
    t2 = fields.Integer(string="__2__")
    t3 = fields.Integer(string="__3__")
    t4 = fields.Integer(string="__4__")
    t5 = fields.Integer(string="__5__")
    t6 = fields.Integer(string="__6__")
    t7 = fields.Integer(string="__7__")
    t8 = fields.Integer(string="__8__")
    t9 = fields.Integer(string="__9__")
    t10 = fields.Integer(string="__10__")
    t11 = fields.Integer(string="__11__")
    t12 = fields.Integer(string="__12__")
    t13 = fields.Integer(string="__13__")
    t14 = fields.Integer(string="__14__")
    t15 = fields.Integer(string="__15__")
    t16 = fields.Integer(string="__16__")
    t17 = fields.Integer(string="__17__")
    t18 = fields.Integer(string="__18__")
    t19 = fields.Integer(string="__19__")
    t20 = fields.Integer(string="__20__")
    t21 = fields.Integer(string="__21__")
    t22 = fields.Integer(string="__22__")
    t23 = fields.Integer(string="__23__")
    t24 = fields.Integer(string="__24__")
    t25 = fields.Integer(string="__25__")
    t26 = fields.Integer(string="__26__")
    t27 = fields.Integer(string="__27__")
    t28 = fields.Integer(string="__28__")
    t29 = fields.Integer(string="__29__")
    t30 = fields.Integer(string="__30__")
    t31 = fields.Integer(string="__31__")
    
    f1 = fields.Integer(compute='_compute_overcapacity1',string="__1__")
    f2 = fields.Integer(compute='_compute_overcapacity2',string="__1__")
    f3 = fields.Integer(compute='_compute_overcapacity3',string="__1__")
    f4 = fields.Integer(compute='_compute_overcapacity4',string="__1__")
    f5 = fields.Integer(compute='_compute_overcapacity5',string="__1__")
    f6 = fields.Integer(compute='_compute_overcapacity6',string="__1__")
    f7 = fields.Integer(compute='_compute_overcapacity7',string="__1__")
    f8 = fields.Integer(compute='_compute_overcapacity8',string="__1__")
    f9 = fields.Integer(compute='_compute_overcapacity9',string="__1__")
    f10 = fields.Integer(compute='_compute_overcapacity10',string="__1__")
    f11 = fields.Integer(compute='_compute_overcapacity11',string="__1__")
    f12 = fields.Integer(compute='_compute_overcapacity12',string="__1__")
    f13 = fields.Integer(compute='_compute_overcapacity13',string="__1__")
    f14 = fields.Integer(compute='_compute_overcapacity14',string="__1__")
    f15 = fields.Integer(compute='_compute_overcapacity15',string="__1__")
    f16 = fields.Integer(compute='_compute_overcapacity16',string="__1__")
    f17 = fields.Integer(compute='_compute_overcapacity17',string="__1__")
    f18 = fields.Integer(compute='_compute_overcapacity18',string="__1__")
    f19 = fields.Integer(compute='_compute_overcapacity19',string="__1__")
    f20 = fields.Integer(compute='_compute_overcapacity20',string="__1__")
    f21 = fields.Integer(compute='_compute_overcapacity21',string="__1__")
    f22 = fields.Integer(compute='_compute_overcapacity22',string="__1__")
    f23 = fields.Integer(compute='_compute_overcapacity23',string="__1__")
    f24 = fields.Integer(compute='_compute_overcapacity24',string="__1__")
    f25 = fields.Integer(compute='_compute_overcapacity25',string="__1__")
    f26 = fields.Integer(compute='_compute_overcapacity26',string="__1__")
    f27 = fields.Integer(compute='_compute_overcapacity27',string="__1__")
    f28 = fields.Integer(compute='_compute_overcapacity28',string="__1__")
    f29 = fields.Integer(compute='_compute_overcapacity29',string="__1__")
    f30 = fields.Integer(compute='_compute_overcapacity30',string="__1__")
    f31 = fields.Integer(compute='_compute_overcapacity31',string="__1__")
    
    
    invist29 = fields.Boolean(related='header_id.invist29',string='Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='Invis')

    hideline = fields.Boolean(string='Hide Line') 
    
    readonlyall=fields.Boolean(compute='',string='Readonly')   
    so_current_id=fields.One2many('sis.pps.so.current','header_id')
    so_history_id=fields.One2many('sis.pps.so.history','header_id')
#     updateinvent1=fields.Boolean(string='Readonly',store=True)   
#     updateinvent=fields.Boolean(compute='_compute_inventory1',string='Readonly') 


    @api.depends('item_no','header_id.ati12')
    def _compute_capacity(self):
        if self.item_no and self.header_id.ati12:
            s=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=',self.header_id.ati12)])
            if s and len(s)==1:
                self.capacity=s.capacity
            
    @api.depends('line')
    def _compute_linenum(self):
        if self.line:
            s=self.linenum=self.env['sis.pps.line'].search([('line','=',self.line)])
            self.linenum=s.linenum
    
    
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
            v= {
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
            return v


    @api.multi
    @api.onchange('t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13','t14','t15','t16','t17','t18','t19','t20','t21','t22','t23','t24','t25','t26','t27','t28','t29','t30','t31')
    def _onchange_inventory1(self):
        for r in self:
            header_id=self._origin.header
            s=self.env['sis.pps.detail'].search([('header_id','=',header_id),('item_no','=',self._origin.item_no),('variant_code','=',self._origin.variant_code),('type','=','sales')])
            inv=self.env['sis.pps.detail'].search([('header_id','=',header_id),('item_no','=',self._origin.item_no),('variant_code','=',self._origin.variant_code),('type','=','inventory')])
            running=0
            vals={}
            for i in range(1,32):
                running=running+r['t'+str(i)]-s['t'+str(i)]
                vals.update({'t'+str(i):running})
            inv.write(vals)
            
            

    @api.one
    @api.depends('line', 't1')
    def _compute_overcapacity1(self):
        return self.overcapacity('1')
    @api.one
    @api.depends('line', 't2')
    def _compute_overcapacity2(self):
        return self.overcapacity('2')
    @api.one
    @api.depends('line', 't3')
    def _compute_overcapacity3(self):
        return self.overcapacity('3')
    @api.one
    @api.depends('line', 't4')
    def _compute_overcapacity4(self):
        return self.overcapacity('4')
    @api.one
    @api.depends('line', 't5')
    def _compute_overcapacity5(self):
        return self.overcapacity('5')
    @api.one
    @api.depends('line', 't6')
    def _compute_overcapacity6(self):
        return self.overcapacity('6')
    @api.one
    @api.depends('line', 't7')
    def _compute_overcapacity7(self):
        return self.overcapacity('7')
    @api.one
    @api.depends('line', 't8')
    def _compute_overcapacity8(self):
        return self.overcapacity('8')
    @api.one
    @api.depends('line', 't9')
    def _compute_overcapacity9(self):
        return self.overcapacity('9')
    @api.one
    @api.depends('line', 't10')
    def _compute_overcapacity10(self):
        return self.overcapacity('10')
    @api.one
    @api.depends('line', 't11')
    def _compute_overcapacity11(self):
        return self.overcapacity('11')
    @api.one
    @api.depends('line', 't12')
    def _compute_overcapacity12(self):
        return self.overcapacity('12')
    @api.one
    @api.depends('line', 't13')
    def _compute_overcapacity13(self):
        return self.overcapacity('13')
    @api.one
    @api.depends('line', 't14')
    def _compute_overcapacity14(self):
        return self.overcapacity('14')
    @api.one
    @api.depends('line', 't15')
    def _compute_overcapacity15(self):
        return self.overcapacity('15')
    @api.one
    @api.depends('line', 't16')
    def _compute_overcapacity16(self):
        return self.overcapacity('16')
    @api.one
    @api.depends('line', 't17')
    def _compute_overcapacity17(self):
        return self.overcapacity('17')
    @api.one
    @api.depends('line', 't18')
    def _compute_overcapacity18(self):
        return self.overcapacity('18')
    @api.one
    @api.depends('line', 't19')
    def _compute_overcapacity19(self):
        return self.overcapacity('19')
    @api.one
    @api.depends('line', 't20')
    def _compute_overcapacity20(self):
        return self.overcapacity('20')
    @api.one
    @api.depends('line', 't21')
    def _compute_overcapacity21(self):
        return self.overcapacity('21')
    @api.one
    @api.depends('line', 't22')
    def _compute_overcapacity22(self):
        return self.overcapacity('22')
    @api.one
    @api.depends('line', 't23')
    def _compute_overcapacity23(self):
        return self.overcapacity('23')
    @api.one
    @api.depends('line', 't24')
    def _compute_overcapacity24(self):
        return self.overcapacity('24')
    @api.one
    @api.depends('line', 't25')
    def _compute_overcapacity25(self):
        return self.overcapacity('25')
    @api.one
    @api.depends('line', 't26')
    def _compute_overcapacity26(self):
        return self.overcapacity('26')
    @api.one
    @api.depends('line', 't27')
    def _compute_overcapacity27(self):
        return self.overcapacity('27')
    @api.one
    @api.depends('line', 't28')
    def _compute_overcapacity28(self):
        return self.overcapacity('28')
    @api.one
    @api.depends('line', 't29')
    def _compute_overcapacity29(self):
        return self.overcapacity('29')
    @api.one
    @api.depends('line', 't30')
    def _compute_overcapacity30(self):
        return self.overcapacity('30')
    @api.one
    @api.depends('line', 't31')
    def _compute_overcapacity31(self):
        return self.overcapacity('31')

    def overcapacity(self,i):            
        if self.type=='production' :#and self.ul=='unlabeled':
            if self.line!=False:
                #update group
                rs=self.env['sis.pps.detail'].search([('header_id','=',self.header_id.id),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('line','=',self.line.id),('line','!=',None),('type','!=','production')])
                for r in rs:
                    r.line=self.line
                    if r.type=='plan':
                        valplan={'t'+i:self['t'+i]}
                        r.write(valplan)
                     
                
#                 rs=self.env['sis.pps.detail'].search([('header_id','=',self.header_id.id),('line','=',self.line),('line','!=',None),('t'+i,'!=',0),('type','=','production')])
#                 total=0
#                 for r in rs:
#                     total+=r['t'+i]
#                 l=self.env['sis.line.capacity'].search([('ati12','=',self.header_id.ati12),('line','=',self.line),('month','=',self.header_id.month),('year','=',self.header_id.year)])
#                 if len(l)>0 :
#                     if len(rs)>0:
#                         if l.capacity<total:
#                             self['f'+i]=1
#                         else:
#                             self['f'+i]=0                
#                 else:
#                     self['f'+i]=1            
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
                ds=self.env['sis.pps.detail'].search([('header_id','=',r.header_id.id),('item_no','=',r.item_no),('variant_code','=',r.variant_code),('type','!=','sales')])
                for d in ds:
                    d.unlink()
            return models.Model.unlink(self)
    
        
class sis_pps_material(models.Model):
    _name='sis.pps.material'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="_______________Item________________")
    uom = fields.Char(size=20,string="___UoM___")
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('material','Material')],default='material',string="Type")

    fish = fields.Char(size=20,string="Fish Type")
    t1 = fields.Float(string="__1__")
    t2 = fields.Float(string="__2__")
    t3 = fields.Float(string="__3__")
    t4 = fields.Float(string="__4__")
    t5 = fields.Float(string="__5__")
    t6 = fields.Float(string="__6__")
    t7 = fields.Float(string="__7__")
    t8 = fields.Float(string="__8__")
    t9 = fields.Float(string="__9__")
    t10 = fields.Float(string="__10__")
    t11 = fields.Float(string="__11__")
    t12 = fields.Float(string="__12__")
    t13 = fields.Float(string="__13__")
    t14 = fields.Float(string="__14__")
    t15 = fields.Float(string="__15__")
    t16 = fields.Float(string="__16__")
    t17 = fields.Float(string="__17__")
    t18 = fields.Float(string="__18__")
    t19 = fields.Float(string="__19__")
    t20 = fields.Float(string="__20__")
    t21 = fields.Float(string="__21__")
    t22 = fields.Float(string="__22__")
    t23 = fields.Float(string="__23__")
    t24 = fields.Float(string="__24__")
    t25 = fields.Float(string="__25__")
    t26 = fields.Float(string="__26__")
    t27 = fields.Float(string="__27__")
    t28 = fields.Float(string="__28__")
    t29 = fields.Float(string="__29__")
    t30 = fields.Float(string="__30__")
    t31 = fields.Float(string="__31__")        
    
    invist29 = fields.Boolean(related='header_id.invist29',string='Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='Invis')


class sis_pps_fishmaterial(models.Model):
    _name='sis.pps.fishmaterial'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    
    header = fields.Integer(string="header")
    fish = fields.Char(size=20,string="Fish")
    uom = fields.Char(size=20,string="UoM")
    t1 = fields.Integer(string="__1__")
    t2 = fields.Integer(string="__2__")
    t3 = fields.Integer(string="__3__")
    t4 = fields.Integer(string="__4__")
    t5 = fields.Integer(string="__5__")
    t6 = fields.Integer(string="__6__")
    t7 = fields.Integer(string="__7__")
    t8 = fields.Integer(string="__8__")
    t9 = fields.Integer(string="__9__")
    t10 = fields.Integer(string="__10__")
    t11 = fields.Integer(string="__11__")
    t12 = fields.Integer(string="__12__")
    t13 = fields.Integer(string="__13__")
    t14 = fields.Integer(string="__14__")
    t15 = fields.Integer(string="__15__")
    t16 = fields.Integer(string="__16__")
    t17 = fields.Integer(string="__17__")
    t18 = fields.Integer(string="__18__")
    t19 = fields.Integer(string="__19__")
    t20 = fields.Integer(string="__20__")
    t21 = fields.Integer(string="__21__")
    t22 = fields.Integer(string="__22__")
    t23 = fields.Integer(string="__23__")
    t24 = fields.Integer(string="__24__")
    t25 = fields.Integer(string="__25__")
    t26 = fields.Integer(string="__26__")
    t27 = fields.Integer(string="__27__")
    t28 = fields.Integer(string="__28__")
    t29 = fields.Integer(string="__29__")
    t30 = fields.Integer(string="__30__")
    t31 = fields.Integer(string="__31__")        
    
    invist29 = fields.Boolean(related='header_id.invist29',string='Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='Invis')
    
    f1 = fields.Integer(compute='_compute_overcapacity1',string="__1__")
    f2 = fields.Integer(compute='_compute_overcapacity2',string="__1__")
    f3 = fields.Integer(compute='_compute_overcapacity3',string="__1__")
    f4 = fields.Integer(compute='_compute_overcapacity4',string="__1__")
    f5 = fields.Integer(compute='_compute_overcapacity5',string="__1__")
    f6 = fields.Integer(compute='_compute_overcapacity6',string="__1__")
    f7 = fields.Integer(compute='_compute_overcapacity7',string="__1__")
    f8 = fields.Integer(compute='_compute_overcapacity8',string="__1__")
    f9 = fields.Integer(compute='_compute_overcapacity9',string="__1__")
    f10 = fields.Integer(compute='_compute_overcapacity10',string="__1__")
    f11 = fields.Integer(compute='_compute_overcapacity11',string="__1__")
    f12 = fields.Integer(compute='_compute_overcapacity12',string="__1__")
    f13 = fields.Integer(compute='_compute_overcapacity13',string="__1__")
    f14 = fields.Integer(compute='_compute_overcapacity14',string="__1__")
    f15 = fields.Integer(compute='_compute_overcapacity15',string="__1__")
    f16 = fields.Integer(compute='_compute_overcapacity16',string="__1__")
    f17 = fields.Integer(compute='_compute_overcapacity17',string="__1__")
    f18 = fields.Integer(compute='_compute_overcapacity18',string="__1__")
    f19 = fields.Integer(compute='_compute_overcapacity19',string="__1__")
    f20 = fields.Integer(compute='_compute_overcapacity20',string="__1__")
    f21 = fields.Integer(compute='_compute_overcapacity21',string="__1__")
    f22 = fields.Integer(compute='_compute_overcapacity22',string="__1__")
    f23 = fields.Integer(compute='_compute_overcapacity23',string="__1__")
    f24 = fields.Integer(compute='_compute_overcapacity24',string="__1__")
    f25 = fields.Integer(compute='_compute_overcapacity25',string="__1__")
    f26 = fields.Integer(compute='_compute_overcapacity26',string="__1__")
    f27 = fields.Integer(compute='_compute_overcapacity27',string="__1__")
    f28 = fields.Integer(compute='_compute_overcapacity28',string="__1__")
    f29 = fields.Integer(compute='_compute_overcapacity29',string="__1__")
    f30 = fields.Integer(compute='_compute_overcapacity30',string="__1__")
    f31 = fields.Integer(compute='_compute_overcapacity31',string="__1__")
    
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
        rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.header_id.id),('t'+i,'!=',0)])
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
        