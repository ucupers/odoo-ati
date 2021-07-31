from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from _datetime import datetime, timedelta
import calendar

class sis_pps_detail_add(models.TransientModel):
    _name='sis.pps.detail.add'

    itm = fields.Many2one('sis.items.local',string='Item',domain=[('itc','=','FG')],required=True)
    variant = fields.Many2one('sis.item.variants.local',string='Variant', domain=lambda self: [('itemno','=',self.itm.itemno)])
    variant_code = fields.Char(related='variant.variant',string='Variant Code')
    line_id = fields.Char(size=20,string='Line')

#     def _get_default_line(self):
#         if self.item_no:
#             rs=self.env['sis.pps.item'].search([('item_no','=',self.item_no)])
#             if len(rs)==1:
#                 return rs.line

    def additem(self):
        try:
            head=self.env['sis.pps.header'].search([('id','=',self._context['insert_id'])])

        except:
            head=self.env['sis.pps.detail'].search([('id','=',self._context['active_id'])]).header_id            

        idd=head.id

        self.env.cr.execute("select max(detailnum) from sis_pps_detail where header_id="+str(idd))
        ds=self.env.cr.fetchall()
        if ds!=[(None,)]:
            [(detailnum,)]=ds
        else:
            detailnum=0
        detailnum+=1

        rs=self.env['sis.pps.item'].search([('item_no','=',self.itm.itemno),('ati12','=', head.ati12)])
        if len(rs)>1:
            raise UserError('Double in Item Settings !')
        if len(rs)==1:
            line= rs.line
        else:
            raise UserError('No Line in Item Settings !')
        
        if len(self.variant)>0:
            uom=self.variant.uom
            qtyperuom=self.variant.qtyperuom
        else:
            uom=self.itm.salesuom
            qtyperuom=self.itm.qtyperuom
        
        if head.ul=='unlabeled':
            uom=self.itm.purchuom
            qtyperuom=self.itm.purchqtyperuom
        for i in ('sales','inventory','production'):
            #if self.env['sis.pps.detail'].search_count([('header_id','=',idd),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('type','=',i)])==0:
                vals = {
                    'header_id':idd,
                    'header':idd,
                    'item_no':self.itm.itemno,
                    'variant_code':self.variant.variant,
                    'description':self.itm.description,     
                    'type':i,
                    'uom':uom,
                    'qtyperuom':qtyperuom,
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

                rec=self.env['sis.pps.detail'].create(vals)
        rec.header_id.sort_sequence()
            #else:
            #    raise UserError('Data already exist !')

class sis_pps_detail_add_new(models.Model):
    _name='sis.pps.detail.add.new'

    itm = fields.Many2one('sis.items.local',string='Item',domain=[('itc','=','FG')],required=True)
    variant = fields.Many2one('sis.item.variants.local',string='Variant', domain=lambda self: [('itemno','=',self.itm.itemno)])
#     item_no = fields.Char(related='itm.itemno',string="Item No.")
    variant_code = fields.Char(related='variant.variant',string='Variant Code')
    line_id = fields.Char(size=20,string='Line')

#     def _get_default_line(self):
#         if self.item_no:
#             rs=self.env['sis.pps.item'].search([('item_no','=',self.item_no)])
#             if len(rs)==1:
#                 return rs.line

    def additem(self):
        self.env['sis.pps.detail.add.new'].unlink()
        try:
            head=self.env['sis.pps.header'].search([('id','=',self._context['insert_id'])])

        except:
            head=self.env['sis.pps.detail'].search([('id','=',self._context['active_id'])]).header_id            

        idd=head.id

        self.env.cr.execute("select max(detailnum) from sis_pps_detail where header_id="+str(idd))
        ds=self.env.cr.fetchall()
        if ds!=[(None,)]:
            [(detailnum,)]=ds
        else:
            detailnum=0
        detailnum+=1

        rs=self.env['sis.pps.item'].search([('item_no','=',self.itm.itemno),('ati12','=', head.ati12)])
        if len(rs)>1:
            raise UserError('Double in Item Settings !')
        if len(rs)==1:
            line= rs.line
        else:
            raise UserError('No Line in Item Settings !')
        
        if len(self.variant)>0:
            uom=self.variant.uom
            qtyperuom=self.variant.qtyperuom
        else:
            uom=self.itm.salesuom
            qtyperuom=self.itm.qtyperuom
        
        if head.ul=='unlabeled':
            uom=self.itm.purchuom
            qtyperuom=self.itm.purchqtyperuom
        for i in ('sales','inventory','production'):
            #if self.env['sis.pps.detail'].search_count([('header_id','=',idd),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('type','=',i)])==0:
                vals = {
                    'header_id':idd,
                    'header':idd,
                    'item_no':self.itm.itemno,
                    'variant_code':self.variant.variant,
                    'description':self.itm.description,     
                    'type':i,
                    'uom':uom,
                    'qtyperuom':qtyperuom,
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

                rec=self.env['sis.pps.detail'].create(vals)
        rec.header_id.sort_sequence()
            #else:
            #    raise UserError('Data already exist !')

    
class sis_pps_header(models.Model):
    _name='sis.pps.header'
    _order = 'year desc,month desc,ati12'
    
    _rec_name='pp_no'

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
    qtyinfcl_id=fields.One2many('sis.pps.fcl','header_id')
    prodcapacity_id=fields.One2many('sis.pps.prod.capacity','header_id')
        
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
            'search_view_id': self.env.ref('sis_ppic.sis_pps_detail_search').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id),('type','in',['sales','inventory','production','alternative'])]
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
            'domain' : [('header_id','=',self.id),('inupdate','=',True)]
#            'domain' : [('header_id','=',self.id)]
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

    def open_fishmaterialtreeviewnew(self): 
        return {
            'name': 'Fish Material  '+self.ati12.upper()+'-'+self.ul.upper()+'-'+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.fishmaterial',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_fishmaterial_tree').id,
            'target': 'new',
            'domain' : [('header_id','=',self.id)]
        }

    def open_actual(self): 
        return {
            'name': 'Plan-Production  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.detail',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_actual_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id),('type','in',['production','plan','alternative'])]
        }

    def open_loin(self): 
        return {
            'name': 'Loin Usage  '+self.ati12.upper()+'-'+self.ul.upper()+'-'+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.loin',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_loin_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }


    def open_fcl(self): 
        return {
            'name': 'Qty In FCL  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.fcl',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_fcl_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }

    def open_prodcapacity(self): 
        return {
            'name': 'Plan Prod.Capacity Usage  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.prod.capacity',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_prodcapacity_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }

    def open_actualcapacity(self): 
        return {
            'name': 'Actual Prod.Capacity Usage  '+self.ati12.upper()+' - '+self.ul.upper()+' - '+str(self.year)+'/'+str(self.month),
            'res_model': 'sis.pps.actual.capacity',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_actualcapacity_tree').id,
            'target': 'current',
            'domain' : [('header_id','=',self.id)]
        }


    def additem(self): 
        vals= {
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
        return vals

    def additemnew(self): 
        vals= {
            'name': self.id,
            'res_model': 'sis.pps.detail.add.new',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_detail_add_form').id,
            'target': 'new',
            'nodestroy':True,
            'context':"{'insert_id':"+str(self.id)+"}"
        }
        return vals


    def countfcl(self):
        self.env.cr.execute('update sis_pps_fcl set total=0 where header_id='+str(self.id))
        
        itemfcl={'header_id' : self.id,
                    'sequence': 9999999,
                    'detailnum':9999999,
                    'header':self.id,
                    'item_no' : 'TOTAL',
                    'description':'TOTAL',
                    'total':0}
        for i in range(1,32):
            itemfcl.update({'t'+str(i):0})    
            
            
        valfcl={}    
        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),'|',('type','=','production'),('type','=','alternative')])
        for prod in prods:

            mitem=self.env['sis.pps.item'].search([('item_no','=',prod.item_no),('ati12','=',prod.ati12)])
            if len(mitem)==0:
                raise UserError("No SIS Master Item error for "+prod.item_no)
            item=self.env['sis.item.variants.local'].search([('itemno','=',prod.item_no),('variant','=',prod.variant_code)])
            if len(item)<1:
                item=self.env['sis.items.local'].search([('itemno','=',prod.item_no)])
                if not item or len(item)!=1:
                    raise UserError ('NAV Master Item error for '+prod.item_no)
                uomsales=item.salesuom
            else:
                uomsales=item.uom
                if len(item)>1:
                    raise UserError ('NAV Master Item error for '+prod.item_no+' variant '+prod.variant_code)                    

#             if item.qtyperuom==0 or item.qtyperfcl==0:
#                 if prod.variant_code:
#                     strplus=' variant '+prod.variant_code
#                 else:
#                     strplus=''
#                 raise UserError ('Please check Qty/FCL or Qty/UoM for '+prod.item_no+strplus)
            try:
                if len(valfcl[prod.item_no,prod.variant_code])>0:
                    valfcl[prod.item_no,prod.variant_code].update({'header_id' : self.id,
                        'sequence': prod.sequence,
                        'detailnum':prod.detailnum,
                        'header':self.id,
                        'item_no' : prod.item_no,
                        'variant_code' : prod.variant_code,
                        'description':prod.description,
                        'uomsales':uomsales,
                        'uomppic':prod.uom,
                        'qtyinfcl':item.qtyperfcl,
                        'qtyperuomppic':prod.qtyperuom,
                        'qtyperuom':item.qtyperuom
                        })
            except:
                valfcl.update({(prod.item_no,prod.variant_code):{}})
                valfcl[prod.item_no,prod.variant_code]={'header_id' : self.id,
                        'sequence': prod.sequence,
                        'detailnum':prod.detailnum,
                        'header':self.id,
                        'item_no' : prod.item_no,
                        'variant_code' : prod.variant_code,
                        'description':prod.description,
                        'uomsales':uomsales,
                        'uomppic':prod.uom,
                        'qtyinfcl':item.qtyperfcl,
                        'qtyperuomppic':prod.qtyperuom,
                        'qtyperuom':item.qtyperuom
                        }
                for i in range(1,32):
                    valfcl[prod.item_no,prod.variant_code].update({'t'+str(i):0})
            total=0
            if prod.type=='alternative':
                prodp = self.env['sis.pps.detail'].search([('header_id','=',prod.header_id.id),('detailnum','=',prod.detailnum),('type','=','production')])
            for i in range(1,32):
                if prod['t'+str(i)]==0:
                    continue
                if prod.type=='alternative':
                    if prodp['a'+str(i)]==True:
                        continue
#                 valfcl[prod.item_no,prod.variant_code]['t'+str(i)]+=float(format(prod['t'+str(i)]*prod.qtyperuom/item.qtyperuom/item.qtyperfcl*mitem.fclfactor,'.2f'))
                valfcl[prod.item_no,prod.variant_code]['t'+str(i)]+=float(format(prod['t'+str(i)]/mitem.qtyperfcl*mitem.fclfactor,'.2f'))

        for (itm,variant),valwrite in valfcl.items():
            total=0
            for i in range(1,32):
                if valwrite['t'+str(i)]==0:
                    continue
                itemfcl['t'+str(i)]+=valwrite['t'+str(i)]
                total+=valwrite['t'+str(i)]
                itemfcl['total']+=valwrite['t'+str(i)]
                
            valwrite.update({'total':total})
            rec=self.env['sis.pps.fcl'].search([('header_id','=',self.id),('item_no','=',itm),('variant_code','=',variant)])
            if rec :
                if len(rec)==1:
                    rec.write(valwrite)
            else:
                self.env['sis.pps.fcl'].create(valwrite)
                    
        rec=self.env['sis.pps.fcl'].search([('header_id','=',self.id),('item_no','=','TOTAL')])
        if rec :
            if len(rec)==1:
                rec.write(itemfcl)
        else:
            self.env['sis.pps.fcl'].create(itemfcl)
        self.env.cr.execute('delete from sis_pps_fcl where total=0 and header_id='+str(self.id))
                    
    def upload_from_NAV(self):
        self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_mat")
        self.env.cr.execute("CREATE TABLE sis_ile_mat AS SELECT * FROM sis_ile where itc in ('PKG','SS','WIP'); ")
        self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_temp")
        self.env.cr.execute("CREATE TABLE sis_ile_temp AS SELECT * FROM sis_ile where itc='FG'; ")

    def countfgstock(self):
#         self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_temp")
#         self.env.cr.execute("CREATE TEMP TABLE sis_ile_temp AS SELECT * FROM sis_ile where itc='FG'; ")


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
                    self.env.cr.execute("select extract(day from posting_date),sum(quantity) from sis_ile_temp "+ \
                                    " where extract(month from posting_date)="+str(self.month)+ \
                                    " and extract(year from posting_date)="+str(self.year)+ \
                                    " and item_no='"+prod.item_no+"' and variant='"+variant+"'" \
                                    " and (entrytype ='Output' or (entrytype='Negative Adj' and docno like 'ADJO%' and extdocno like 'ATI%-PRO/%'))" + " and bg='"+prod.ati12.upper()+"'"+ \
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
        self.sort_sequence()
        self.countfcl()
        self.countcapacity()
        self.countactualcapacity()

    def update_inventory(self,calclabeled):

#sql so 
        self.env.cr.execute("DROP TABLE IF EXISTS sis_so_header_fg")
        self.env.cr.execute("CREATE TEMP TABLE sis_so_header_fg AS SELECT * FROM sis_so_header; ")

        self.env.cr.execute("DROP TABLE IF EXISTS sis_so_line_fg")
        self.env.cr.execute("CREATE TEMP TABLE sis_so_line_fg AS SELECT * FROM sis_so_line; ")

        
        invs=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','inventory')])
        for inv in invs:
            if calclabeled:
                self.calc_include_labeled(inv)
            valsrun={}
            rs=self.env['sis.pps.detail'].search([('header_id','=',inv.header_id.id),('detailnum','=',inv.detailnum),('type','!=','inventory')])
            #prod=self.env['sis.pps.detail'].search([('header_id','=',inv.header_id.id),('detailnum','=',inv.detailnum),('type','=','production')])
            #alt=self.env['sis.pps.detail'].search([('header_id','=',inv.header_id.id),('detailnum','=',inv.detailnum),('type','=','alternative')])
            alt=False
            for s in rs:
                if s.type=='sales':
                    sales=s
                if s.type=='production':
                    prod=s
                if s.type=='alternative':
                    alt=s
            valsrun={'t0':inv['t0']}

            vs=sales.so_based_posting_date(sales)

            for it in range(1,32):
                if inv['a'+str(it)]==False:
                    if alt and len(alt)==1:
                        valsrun.update({'t'+str(it):valsrun['t'+str(it-1)]+prod['t'+str(it)]+alt['t'+str(it)]-vs[it]})
                    else:
                        valsrun.update({'t'+str(it):valsrun['t'+str(it-1)]+prod['t'+str(it)]-vs[it]})                    
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
            invs+=[(label.itemno,label.description,variant,False)]
            variants=self.env['sis.item.variants.local'].search([('itemno','=',label.itemno)])
            for var in variants:            
                if  var.variant==False:
                    variant=''
                else:
                    variant=var.variant
                invs+=[(var.itemno,label.description,variant,var.variant)]

        valsinv={}

        ##inisialisasi
        t0=0
        for counter in range (0,32):
            valsinv.update({'t'+str(counter):0})
        for counter in range (1,32):
            valsinv.update({'a'+str(counter):False})
        self.env.cr.execute("delete from sis_pps_inv_detail "+ \
                    " where header_id="+str(invori.id))

        
        tgl='0001-12-31'
        #cari tanggal max
        for (itemno,description,variant,variant_code) in invs:
            ## UPDATE ACTUAL INVENTORY FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_temp"+ \
                            " where item_no='"+itemno+"' and variant='"+variant+"'" \
                            " and bg='"+invori.ati12.upper()+"'")
            invdates=self.env.cr.fetchall()
            for invdate in invdates:
                (tgltemp,)=invdate
            if tgltemp and tgltemp>tgl:
                tgl=tgltemp
        if tgl=='0001-12-31':
            tgl=str(self.year)+'-'+('0'+str(self.month))[-2:]+'-01'

        runyear=self.year
        runmonth=self.month

         
        if tgl!=None:
            year=int(tgl[:4])
            month=int(tgl[5:7])
            day=int(tgl[8:10])

            if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                for runday in range(1,32):
                    if year*10000+month*100+day<runyear*10000+runmonth*100+runday:
                        break
                    valsinv.update({'a'+str(runday):True})
            
            #perhitungan per item no per variant
            for (itemno,description,variant,variant_code) in invs:
                #CALCULATE T0
                if year*10000+month*100+day>=runyear*10000+runmonth*100+1:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp"+ \
                                    " where item_no='"+itemno+"' and variant='"+variant+"'" \
                                    " and bg='"+invori.ati12.upper()+"'" +\
                                    " and posting_date<'"+str(runyear)+"-"+str(runmonth)+"-01'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0run,)=stock
                    if t0run!=0 and t0run!=None:
                        t0run/=invori.qtyperuom
                    else:
                        t0run=0;                    
                else:
                    self.env.cr.execute("select sum(quantity) from sis_ile_temp"+ \
                                    " where item_no='"+itemno+"' and variant='"+variant+"'" \
                                    " and bg='"+invori.ati12.upper()+"'" +\
                                    " and posting_date<='"+str(year)+"-"+str(month)+"-"+str(day)+"'")
                    stocks=self.env.cr.fetchall()
                    for stock in stocks:
                        (t0run,)=stock
                    if t0run!=0 and t0run!=None:
                        t0run/=invori.qtyperuom
                    else:
                        t0run=0;
                        
                    t0year=year
                    t0month=month

                    while t0year*100+t0month<runyear*100+runmonth:
                        prods=self.env['sis.pps.detail'].search([('ati12','=',self.ati12),('item_no','=',itemno),('variant_code','=',variant_code),('type','=','production'),('year','=',t0year),('month','=',t0month)])
                        sales=self.env['sis.pps.detail'].search([('ati12','=',self.ati12),('item_no','=',itemno),('variant_code','=',variant_code),('type','=','sales'),('year','=',t0year),('month','=',t0month)])
                        t0inc=0
                        if len(prods)>0:
                            for t0day in range(1,32):
                                if (t0year==year and t0month==month and t0day>day) or (t0year!=year or t0month!=month) :
                                    for prod in prods:
                                        t0inc+=prod['t'+str(t0day)]                                        
                                    for sale in sales:
                                        vs=sale.so_based_posting_date(sale)
                                        t0inc-=vs[t0day]                                        
                        t0month+=1
                        if t0month>12:
                            t0month=1
                            t0year+=1
                        t0run+=t0inc
#                 if t0run!=0:
#                     t0run/=invori.qtyperuom
#                 else:
#                     t0run=0;
                t0+=t0run
                
                # CALCULATE ACTUAL INVENTORY
                


                ##UPDATE INVENTORY
                self.env.cr.execute("select extract(day from posting_date), sum(quantity) from sis_ile_temp "+ \
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

                valsinv['t0']+=valsrun['t0']  

                for counter in range (1,32):
                    if valsinv['a'+str(int(counter))]==True:
                        valsrun['t'+str(counter)]+=valsrun['t'+str(counter-1)]                   
                    valsinv['t'+str(counter)]+=valsrun['t'+str(counter)]

                    
            #--------------------------------------------------------------------------------------------------------------------------------
                ##UPDATE INVENTORY DETAIL
               
                self.env.cr.execute("select extract(day from posting_date), entrytype, sum(quantity) from sis_ile_temp "+ \
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

    def countmaterial(self):

        #self.env['sis.pps.material'].search([('header_id','=',self.id)]).unlink()
        self.env.cr.execute("update sis_pps_material set inupdate=False where header_id="+str(self.id))
        self.env.cr.execute('delete from sis_pps_material_need where header_id='+str(self.id))
        #self.env['sis.pps.material.need'].search([('header_id','=',self.id)]).unlink()        
        self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id)]).unlink()     
        
        #self.env.cr.execute('delete from sis_temp_items')
        #self.env.cr.execute('insert into sis_temp_items select * from sis_items')   
        self.env.cr.execute('delete from sis_temp_production_bom')
        self.env.cr.execute("insert into sis_temp_production_bom(id,itemno,description,uom,qtyperuom,variant,variantdesc,variantuom,variantqtyperuom,linenum,lineitem,linedesc,linevar,lineqty,linerouting,lineqtyper,lineuom,lineitc,linepgc) "+\
        "select id,itemno,description,uom,qtyperuom,variant,variantdesc,variantuom,variantqtyperuom,linenum,lineitem,linedesc,linevar,lineqty,linerouting,lineqtyper,lineuom,lineitc,linepgc from sis_production_bom")   

#        shs=self.env['sis.so.header'].search([('shipmentdate','&lt;',datetime.strftime(str(self.year)+'-'+str(self.month+1)+'-01')), ('shipmentdate','&gt;=',datetime.strftime(str(self.year)+'-'+str(self.month)+'-01'))])
#        for sh in shs:
        vals={}
        be={}
        detmaterial={}
        uoms={}
        for d in self.detail_id:
            if d.type!='production' and d.type!='alternative' :
                continue
            if d.variant_code==False:
                variant1=''
            else:
                variant1=d.variant_code
            pb=self.env['sis.temp.production.bom'].search([('itemno','=',d.item_no),('variant','=',variant1)])
            if len(pb)==0:
                continue
                raise UserError('There is Item in Plan without BoM')
            else:
                for pl in pb:
                    for i in range(1,32):
                        if d.type=='alternative':
                            dp = self.env['sis.pps.detail'].search([('header_id','=',d.header_id.id),('detailnum','=',d.detailnum),('type','=','production')])
                            if dp['a'+str(i)]==True:
                                continue
                        if d['t'+str(i)]!=0:
                            #fprd=self.env['sis.temp.items'].search([('itemno','=',d.item_no)])
                            fitem=self.env['sis.pps.item'].search([('ati12','=',d.ati12),('item_no','=',d.item_no)])
                            if len(fitem)==1 and pl.lineitc=='WIP' and pl.linepgc!='':
                                if fitem.fishmaterial==False or fitem.fishmaterial=='':
                                    raise UserError('Error in Fish Material : '+d.item_no)
                                fish=fitem.fishmaterial
                            else:
                                fish=''

                            if pl.linepgc=='CAN' or pl.linepgc=='POUCH':
                                sitem=self.env['sis.items.local'].search([('itemno','=',pl.itemno)])
                                if len(sitem)!=1:
                                    raise ValidationError('Material Calc : Master items error')
                                caseitem=self.env['sis.pgc.case48'].search_count([('pgc','=',sitem.pgc)])
                                if caseitem>0:
                                    lineuom='CASE'
                                    qtyper=48
                                else:
                                    lineuom=sitem.purchuom
                                    qtyper=sitem.purchqtyperuom
                            else:
                                if pl.lineuom=='GR':
                                    lineuom='KG'
                                    qtyper=1000
                                else:
                                    lineuom=pl.lineuom
                                    qtyper=1
                            
                            if not (pl.lineitem,fish) in vals:
                                vals.update({(pl.lineitem,fish) : {}})
                                for j in range(1,32):
                                    vals[(pl.lineitem,fish)].update({'t'+str(j):0})
                                uoms.update({pl.lineitem : (lineuom,pl.linedesc,qtyper)})
                            if pl.variantuom==d.uom:
                                dettotal=pl.lineqtyper*d['t'+str(i)]/qtyper
                            else:                                
                                dettotal=d['t'+str(i)]*d.qtyperuom/pl.variantqtyperuom*pl.lineqtyper/qtyper
                            vals[(pl.lineitem,fish)]['t'+str(i)]+=dettotal

                            try:
                                detmaterial[(pl.lineitem,fish,d.item_no,d.description,variant1)]['t'+str(i)]+=dettotal
                            except:
                                detmaterial.update({(pl.lineitem,fish,d.item_no,d.description,variant1) : {}})
                                for j in range(1,32):
                                    detmaterial[(pl.lineitem,fish,d.item_no,d.description,variant1)].update({'t'+str(j):0})
                                detmaterial[(pl.lineitem,fish,d.item_no,d.description,variant1)]['t'+str(i)]=dettotal
        
        for (item,fish),v in vals.items():
            #insert to material
            s=self.env['sis.pps.material'].search([('item_no','=',item),('fish','=',fish),('header_id','=',self.id),('type','=','material')])
            
            (uom,desc,qtyper)=uoms[item]
            v.update({'item_no':item,
                      'fish':fish,
                  'type':'material',
                  'description':desc,
                  'uom':uom,
                  'qtyperuom':qtyper,
                  'inupdate':True
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
                    raise UserError('Budomari = 0 or does not exist ('+str(self.month)+'/'+str(self.year)+'): Item='+item+' - '+fish1)
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
                    for i in range(1,32):
                        v1['t'+str(i)]+=s['t'+str(i)]
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


        for (litem,fish,item,desc,variant_code),v in detmaterial.items():
            s=self.env['sis.pps.material'].search([('item_no','=',litem),('fish','=',fish),('header','=',self.id),('type','=','material')])

#detmaterial problem
            dm=self.env['sis.pps.material.need'].search([('item_no','=',item),('variant_code','=',variant_code),('material_id','=',s.id)])
            v.update({'item_no':item,
                      'variant_code':variant_code,
                      'description':desc
                })
  
            if len(dm)==1:
                s.write(v)
            else:
                v.update({
                  'material_id':s.id,
                  'header_id':self.id
                })
                if len(dm)==0:
                    self.env['sis.pps.material.need'].create(v)
                else:
                    raise UserError('Double material record !!')

            if fish!='':
                fitem=self.env['sis.pps.item'].search([('ati12','=',self.ati12),('item_no','=',item)])
                bepercent=fitem.bepercent
                if bepercent>0:
                    for k in range(1,32):
                        if 't'+str(k) in be:
                            be.update({'t'+str(k):be['t'+str(k)]+v['t'+str(k)]*bepercent/100})
                        else:
                            for l in range(1,32):
                                be.update({'t'+str(l):0.0})                                        
                            be.update({'t'+str(k):v['t'+str(k)]*bepercent/100})

        if 't1' in be:
            bebudomari=self.env['sis.budomari'].search([('month','=',self.month),('year','=',self.year),('ati12','=',self.ati12),('fish','ilike','YFB')])
            if len(bebudomari)>0:
                bebudomari=bebudomari.budomari
                for i in range(1,32):
                    be.update({'t'+str(i) : be['t'+str(i)]*100/bebudomari})
            else:
                raise UserError('Please Check YFB Budomari')

#detmaterial problem
        ss=self.env['sis.pps.material'].search([('header','=',self.id),('type','=','material')])
        for s in ss:
            valstotal={'item_no':'[***]',
                      'variant_code':'[***]',
                      'description':'TOTAL',
                      'material_id': s.id,
                      'header_id':self.id
                }
            for counter in range(1,32):
                valstotal.update({'t'+str(counter):0})
 
            dms=self.env['sis.pps.material.need'].search([('material_id','=',s.id)])
            for dm in dms:
                for counter in range(1,32):
                    valstotal['t'+str(counter)]+=dm['t'+str(counter)]
            self.env['sis.pps.material.need'].create(valstotal)

        s=self.env['sis.pps.material'].search([('item_no','=','WIP-017'),('header','=',self.id),('type','=','material')])
        if len(s)>0:                
            v1.update({'fish':'SHR',
                       'type':'TOTAL',
                       'uom':'KG',
                       'header':self.id,
                       'header_id':self.id
                })
            
            for i in range(1,32):
                if s['uom']=='GR':
                    v1.update({'t'+str(i): s['t'+str(i)]/1000})
                if s['uom']=='KG':
                    v1.update({'t'+str(i): s['t'+str(i)]})                    
            self.env['sis.pps.fishmaterial'].create(v1)

        pct="0.02"
        self.env.cr.execute(" select left(fish,2), sum(t1)*"+pct+",sum(t2)*"+pct+",sum(t3)*"+pct+",sum(t4)*"+pct+","+ \
                            "sum(t5)*"+pct+",sum(t6)*"+pct+",sum(t7)*"+pct+",sum(t8)*"+pct+",sum(t9)*"+pct+",sum(t10)*"+pct+","+\
                            "sum(t11)*"+pct+",sum(t12)*"+pct+",sum(t13)*"+pct+",sum(t14)*"+pct+",sum(t15)*"+pct+",sum(t16)*"+pct+","+\
                            "sum(t17)*"+pct+",sum(t18)*"+pct+",sum(t19)*"+pct+",sum(t20)*"+pct+",sum(t21)*"+pct+",sum(t22)*"+pct+","+\
                            "sum(t23)*"+pct+",sum(t24)*"+pct+",sum(t25)*"+pct+",sum(t26)*"+pct+",sum(t27)*"+pct+",sum(t28)*"+pct+","+\
                            "sum(t29)*"+pct+",sum(t30)*"+pct+",sum(t31)*"+pct+",sum(total)*"+pct+" from sis_pps_fishmaterial "+\
                            "where header_id="+str(self.id)+" and type='FISH' group by left(fish,2)")
        fs=self.env.cr.fetchall()
        for f in fs:
            (ff,t1,t2,t3,t4,t5,t6,t7,t8,t9,t10,t11,t12,t13,t14,t15,t16,t17,t18,t19,t20,t21,t22,t23,t24,t25,t26,t27,t28,t29,t30,t31,total)=f
            if ff not in ('SJ','YF'):
                continue
            v2={'fish':'SHR '+ff,
                       'type':'OUTPUT',
                       'uom':'KG',
                       'header':self.id,
                       'header_id':self.id,
                       't1':t1,'t2':t2,'t3':t3,'t4':t4,'t5':t5,'t6':t6,'t7':t7,'t8':t8,'t9':t9,'t10':t10,
                       't11':t11,'t12':t12,'t13':t13,'t14':t14,'t15':t15,'t16':t16,'t17':t17,'t18':t18,'t19':t19,'t20':t20,                       
                       't21':t21,'t22':t22,'t23':t23,'t24':t24,'t25':t25,'t26':t26,'t27':t27,'t28':t28,'t29':t29,'t30':t30,'t31':t31,'total':total
                }
            
            self.env['sis.pps.fishmaterial'].create(v2)
            for i in range(1,32):
                if v2['t'+str(i)]!=None:
                    v1['t'+str(i)]-=v2['t'+str(i)]
        v1.update({'fish':'NEED SHR',
                   'type':'TOTAL'})
        self.env['sis.pps.fishmaterial'].create(v1)        

        if len(be)>0:
            totalbe=0
            v2={'fish':'NEED YFB',
               'type':'TOTAL',
               'uom':'KG',
               'header':self.id,
               'header_id':self.id,
                }
            for i in range(1,32):
                v2.update({'t'+str(i):be['t'+str(i)]})
                totalbe+=be['t'+str(i)]
            v2.update({'total':totalbe})
            self.env['sis.pps.fishmaterial'].create(v2)

        self.env.cr.execute("delete from sis_pps_material_note note using sis_pps_material mat where note.header_id=mat.id and mat.inupdate=False and mat.header_id="+str(self.id))
        self.env.cr.execute("delete from sis_pps_material where inupdate=False and header_id="+str(self.id))
        
        self.calc_material_order_inventory()
        self.sort_sequence_material()


    def sort_sequence_material(self):
        seq=1
        
        recs=self.env['sis.pps.material'].search([('header_id','=',self.id),('type','=','material')],order='item_no')        
        for rec in recs:
            upds=self.env['sis.pps.material'].search([('header_id','=',self.id),('item_no','=',rec.item_no)])
            for upd in upds:
                if upd.type=='order':
                    sequence=seq*10+2
                    hideline=True
                if upd.type=='material':
                    sequence=seq*10+1
                    hideline=False
                if upd.type=='inventory':
                    sequence=seq*10+3
                    hideline=True
                upd.write({'sequence':sequence,
                           'hideline':hideline
                           })
            seq+=1

    def calc_material_order(self,mat):
        self.env.cr.execute("select extract(day from requested_receipt_date), sum(quantity),sum(outstanding_quantity),uom,qtyperuom from sis_purchase_order_mat "+ \
                        " where extract(month from requested_receipt_date)="+str(self.month)+ \
                        " and extract(year from requested_receipt_date)="+str(self.year)+ \
                        " and item_no='"+mat.item_no+"' "+ \
                        " and bg='"+self.ati12.upper()+"'"+ \
                        " group by extract(day from requested_receipt_date), uom, qtyperuom")
        actpos=self.env.cr.fetchall()
       
        valsorder={}
        for i in range(1,32):
            valsorder.update({'t'+str(i):0})
        for actpo in actpos:
            (tgl,qty,remqty,uom,qtyperuom)=actpo
            qtyperuom=float(qtyperuom)
            if qtyperuom==0 and uom=='PCS':
                qtyperuom=1
            day=int(tgl)
            qtyperuom=float(qtyperuom)
            valsorder.update({'t'+str(day):remqty*qtyperuom/mat.qtyperuom})
        order=self.env['sis.pps.material'].search([('header_id','=',mat.header_id.id),('item_no','=',mat.item_no),('type','=','order')])
        valsorder.update({
            'inupdate':True
            })
        if len(order)==0:
            valsorder.update({
                'header_id':mat.header_id.id,
                'header':mat.header_id.id,
                'item_no':mat.item_no,
                'uom':mat.uom,
                'description':mat.description,
                'type':'order',
                'fish':''
                })
            self.env['sis.pps.material'].create(valsorder)
        else:
            order.write(valsorder)

    
    def calc_material_order_inventory(self):
#         self.env.cr.execute("DROP TABLE IF EXISTS sis_ile_mat")
#         self.env.cr.execute("CREATE TEMP TABLE sis_ile_mat AS SELECT * FROM sis_ile where itc in ('PKG','SS','WIP'); ")

        self.env['sis.pps.material.order'].get_material_order()

        self.env.cr.execute("delete from sis_pps_material_detail "+ \
                    " where header_id="+str(self.id))
        #self.env.cr.execute("delete from sis_pps_material_order "+ \
        #            " where header_id="+str(self.id))

#        self.env.cr.execute("DROP TABLE IF EXISTS sis_po_local")
#        self.env.cr.execute("CREATE TEMP TABLE sis_po_local AS SELECT * FROM sis_po where itc='PKG'; ")



        mats=self.env['sis.pps.material'].search([('header_id','=',self.id),('type','=','material')])
        for mat in mats:
            self.calc_material_order(mat)
            
            ## UPDATE ACTUAL MATERIAL FLAG
            self.env.cr.execute("select max(posting_date) from sis_ile_mat"+ \
                            " where item_no='"+mat.item_no+"' " \
#                            " and entrytype = 'Purchase'" + \
                            " and bg='"+self.ati12.upper()+"'  and location_code not ilike '%RJCT%' ")        
            matdates=self.env.cr.fetchall()
            for matdate in matdates:
                (tgl,)=matdate
             
            valsmat={
                'header_id':mat.header_id.id,
                'header':mat.header_id.id,
                'item_no':mat.item_no,
                'uom':mat.uom,
                'description':mat.description,
                'type':'inventory',
                'fish':'',
                'inupdate':True}

            if tgl!=None:
                year=int(tgl[:4])
                month=int(tgl[5:7])
                day=int(tgl[8:10])
                
                runyear=self.year
                runmonth=self.month

                for runday in range(1,32):
                    valsmat.update({'t'+str(runday):0})
                    if year*10000+month*100+day<runyear*10000+runmonth*100+runday:
                        valsmat.update({'a'+str(runday):False})
                    else:
                        valsmat.update({'a'+str(runday):True})
            
                ##UPDATE PRODUCTION
                #t0
                self.env.cr.execute("select sum(quantity) from sis_ile_mat "+ \
                                " where ((extract(month from posting_date)<"+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ ") "+
                                " or extract(year from posting_date)<"+str(self.year)+")"+\
                                " and item_no='"+mat.item_no+"'  and location_code not ilike '%RJCT%' " \
                                " and bg='"+self.ati12.upper()+"'")
                t0mats=self.env.cr.fetchall()
                t0=False
                for t0mat in t0mats:
                    (t0,)=t0mat

                if t0==None:
                    t0=0
                    
                t0/=mat.qtyperuom
                t0year=year
                t0month=month

                while t0year*100+t0month<self.year*100+self.month:
                    orders=self.env['sis.pps.material'].search([('ati12','=',self.ati12),('item_no','=',mat.item_no),('type','=','order'),('year','=',t0year),('month','=',t0month)])
                    if mat['fish']=='':
                        matp=self.env['sis.pps.material'].search([('ati12','=',self.ati12),('item_no','=',mat.item_no),('type','=','material'),('year','=',t0year),('month','=',t0month)])
                    else:
                        matp=self.env['sis.pps.material'].search([('ati12','=',self.ati12),('item_no','=',mat.item_no),('fish','=',mat.fish),('type','=','material'),('year','=',t0year),('month','=',t0month)])                        
                    for t0day in range(1,32):
                        if (t0year==year and t0month==month and t0day>day) or (t0year!=year or t0month!=month):
                            t0+=orders['t'+str(t0day)]-matp['t'+str(t0day)]                                        
                    t0month+=1
                    if t0month>12:
                        t0month=1
                        t0year+=1
                
                if t0:
                    valsmat.update({'t0':t0})
                else:
                    valsmat.update({'t0':0})                        

                #t1-t31
                self.env.cr.execute("select extract(day from posting_date),sum(quantity) from sis_ile_mat "+ \
                                " where extract(month from posting_date)="+str(self.month)+ \
                                " and extract(year from posting_date)="+str(self.year)+ \
                                " and item_no='"+mat.item_no+"' " \
                                " and bg='"+self.ati12.upper()+"' and location_code not ilike '%RJCT%' "+ \
                                " group by extract(day from posting_date)")
                actmats=self.env.cr.fetchall()

                for actmat in actmats:
                    (tgl,qty)=actmat
                    try:
                        if valsmat['a'+str(int(tgl))]==True:
                            valsmat['t'+str(int(tgl))] = qty/mat.qtyperuom
                    except:
                        pass

                ordermats=self.env['sis.pps.material'].search([('header_id','=',self.id),('item_no','=',mat.item_no),('type','=','order')])                           
                if len(ordermats)>1:
                    raise UserError('Order data on Material is Error !')
                for counter in range (1,32):
                    if valsmat['a'+str(int(counter))]==False:
                        invqty=valsmat['t'+str(counter-1)]-mat['t'+str(counter)]
                        if len(ordermats)!=0:
                            invqty=invqty+ordermats['t'+str(counter)]
                        valsmat.update({'t'+str(counter):invqty})
                    else:
                        valsmat['t'+str(counter)] += valsmat['t'+str(counter-1)]                        
            matinv=mat.env['sis.pps.material'].create(valsmat)

            #--------------------------------------------------------------------------------------------------------------------------------
                ##UPDATE INVENTORY DETAIL
               
            self.env.cr.execute("select extract(day from posting_date), entrytype, sum(quantity) from sis_ile_mat "+ \
                            " where extract(month from posting_date)="+str(self.month)+ \
                            " and extract(year from posting_date)="+str(self.year)+ \
                            " and item_no='"+mat.item_no+"' " \
                            " and bg='"+self.ati12.upper()+"'  and location_code not ilike '%RJCT%' "+ \
                            " group by extract(day from posting_date), entrytype" +\
                            " order by entrytype, extract(day from posting_date)")
            actinvs=self.env.cr.fetchall()
            
            valsinvdetail={}
            currentrytype=''
            for actinv in actinvs:
                (tgl,entrytype,qty)=actinv
                if currentrytype!=entrytype:
                    if currentrytype!='':
                        valsinvdetail.update({'entrytype':currentrytype})
                        self.env['sis.pps.material.detail'].create(valsinvdetail)
                    valsinvdetail={'item_no':mat.item_no,
                             'description':mat.description,
                             'material_id':matinv.id,
                             'header_id':self.id
                             }
                    currentrytype=entrytype                    
                valsinvdetail.update({'t'+str(int(tgl)): qty/mat.qtyperuom})
            valsinvdetail.update({'entrytype':currentrytype})
            self.env['sis.pps.material.detail'].create(valsinvdetail)

        
    def calculate_loin_need(self):

        #CALCULATE LOIN NEEDED AND FISH REDUCE
        vf={}
        vl={}
        totalall={'header_id':self.id,
               'header':self.id,
               'type':'TOTAL',
               'fish':'ALL',
               'uom':'KG'}
       
        if self.ul!='unlabeled':
            return
        for j in range(1,32):
            i=str(j)
            rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('t'+i,'!=',0)])
            total=0
            for r in rs:
                total+=r['t'+i]
            
            totalall.update({'t'+i:total})
            
            l=self.env['sis.clean.capacity'].search([('ati12','=',self.ati12),('month','=',self.month),('year','=',self.year)])
            #look for workhours
            try:
                dt=datetime.strptime(str(self.year)+'-'+str(self.month)+'-'+i,'%Y-%m-%d')
            except:
                continue
            days=self.env['sis.pps.exhour'].search([('workdate','=',dt),('ati12','=',self.ati12)])
            if len(days)==0:
                ordi=self.env['sis.pps.option'].search([('ati12','=',self.ati12)])
                if ordi and len(ordi)==1:
                    if dt.weekday()==4:
                        hourlimit=ordi.fri
                    else:
                        if dt.weekday()==5:
                            hourlimit=ordi.sat
                        else:
                            if dt.weekday()>=0 and dt.weekday()<4:
                                hourlimit=ordi.montothu
                            else:
                                hourlimit=0   
                else:
                    raise UserError('Option Error !')
            else:
                if days and len(days)==1:
                    hourlimit=days.hours
                else:
                    raise UserError('Hours option error !')            
            
            capacity=l.capacity/13*hourlimit
            
                        
            if len(l)>0 and len(rs)>0:
                if capacity<total:
                    overfish=total-capacity
                    #ppsitems=self.env['sis.pps.item'].search([('ati12','=',self.ati12),('priority','!=',0)],order="fishmaterial, priority, item_no")
                    #ppsitems=self.env['sis.pps.detail'].search([('header_id','=',self.id),('prioloin','!=',0),('type','=','production')],order="prioloin")
                    ppsitems=self.env['sis.pps.loin'].search([('header_id','=',self.id),('t'+i,'!=',0),('type','=','number')],order="t"+i)
                    for ppsitem in ppsitems:
                        orders=self.env['sis.pps.detail'].search([('header_id','=',self.id),('item_no','=',ppsitem.item_no),('variant_code','=',ppsitem.variant_code),('t'+i,'!=',0),('type','=','production')])
                        for order in orders:
                            ppsitempct=self.env['sis.pps.loin'].search([('detail_id','=',ppsitem.detail_id.id),('type','=','percent')])
                            if len(ppsitempct)==0:
                                raise UserError('%L for item '+ppsitem.item_no+' not found !')
                            if ppsitempct['t'+i]==0:
                                raise UserError('%L for item '+ppsitem.item_no+' = 0 !')
                            
                            #look to NAV item master
                            #fprd=self.env['sis.temp.items'].search([('itemno','=',order.item_no)])
                            fitem=self.env['sis.pps.item'].search([('ati12','=',self.ati12),('item_no','=',order.item_no)])
                            #if fprd and len(fprd)==1:
                                #pass
                            #else:
                                #raise UserError('Error item '+fprd.item_no+' In Item Master NAV !')
                            if fitem and len(fitem)==1:
                                pass
                            else:
                                raise UserError('Error item '+fitem.item_no+' In Item Master SIS!')

                            if fitem.fishmaterial=='':
                                raise UserError('Item '+ppsitem.item_no+' does not have fish material!')

                            if fitem.fz==False or fitem.fz=='':
                                raise UserError('Item '+ppsitem.item_no+' does not have loin material!')

    
                            if order.variant_code==False:
                                variant1=''
                            else:
                                variant1=order.variant_code
                                
                            #look for type of fish
                            fish=fitem.fishmaterial
                            fish1=fish
                            if len(fish1)>2:
                                fish1=fish1[:2]
                        
                            budomari=self.env['sis.budomari'].search([('month','=',self.month),('year','=',self.year),('ati12','=',self.ati12),('fish','=',fish1)]).budomari        
                            pb=self.env['sis.temp.production.bom'].search([('itemno','=',order.item_no),('variant','=',variant1),('lineitc','=','WIP'),('linepgc','!=',''),('linepgc','=',fish1)])

                            loin4order=order['t'+i]*order.qtyperuom*pb.lineqtyper*ppsitempct['t'+i]/100#ppsitem.pctloin/100 #fitem.fzpercent/100
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
                            except:
                                vf.update({fish: {}})                                
                                for counter in range(1,32):
                                    vf[fish].update({'t'+str(counter):0})                                
                                vf[fish].update({'t'+i:fish2reduce})                                

                            try:
                                vl[fitem.fz]['t'+i] += loin4order                                
                            except:
                                vl.update({fitem.fz : {}})
                                for counter in range(1,32):
                                    vl[fitem.fz].update({'t'+str(counter):0})
                                vl[fitem.fz].update({'t'+i:loin4order})

                                                                                            
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
        for loin,tx in vl.items():
            valfish={'type':'LOIN',
                     'fish':loin,
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
        for counter in range(1,32):
            total.update({'t'+str(counter):0})
        rs=self.env['sis.pps.fishmaterial'].search([('header_id','=',self.id),('header_id','!=',None),('type','=','LOIN')])       
        for r in rs:      
            for counter in range(1,32):
                if r['t'+str(counter)]!=0:
                    total['t'+str(counter)]+=r['t'+str(counter)]
        self.env['sis.pps.fishmaterial'].create(total)
        self.env['sis.pps.fishmaterial'].create(totalall)

    def sort_sequence(self):
        seq=1
        
        recs=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','production')],order='line_id, description')        
        for rec in recs:
            upds=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',rec.detailnum)])
            for upd in upds:
                if upd.type=='sales':
                    sequence=seq*10+1
                if upd.type=='production':
                    sequence=seq*10+2
                if upd.type=='alternative':
                    sequence=seq*10+3
                if upd.type=='inventory':
                    sequence=seq*10+4
                if upd.type=='plan':
                    sequence=seq*10+5
                upd.sequence=sequence
            seq+=1
  
    def getso(self):
#        shs=self.env['sis.so.header'].search([('shipmentdate','&lt;',datetime.strftime(str(self.year)+'-'+str(self.month+1)+'-01')), ('shipmentdate','&gt;=',datetime.strftime(str(self.year)+'-'+str(self.month)+'-01'))])
#        for sh in shs:

        self.env.cr.execute("DROP TABLE IF EXISTS sis_so_header_temp")
        self.env.cr.execute("CREATE TEMP TABLE sis_so_header_temp AS SELECT * FROM sis_so_header; ")

        self.env.cr.execute("DROP TABLE IF EXISTS sis_so_line_temp")
        self.env.cr.execute("CREATE TEMP TABLE sis_so_line_temp AS SELECT * FROM sis_so_line; ")

        
        self.env.cr.execute("select max(detailnum) from sis_pps_detail where header_id="+str(self.id))
        ds=self.env.cr.fetchall()
        if ds!=[(None,)]:
            [(detailnum,)]=ds
        else:
            detailnum=0

        if self.ati12=='ati2':
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from postingdate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_so_header_temp sh "+ \
                                " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                                " and extract(year from postingdate)="+str(self.year)+ \
                                " and bg='ATI2'" \
                                " group by extract(day from postingdate), itemno, variant, uom, qtyperuom, pgc "+ \
                                " order by itemno, variant, extract(day from postingdate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), itemnoun, '', sum(quantity), uom, qtyperuom, pgc from sis_so_header_temp sh "+ \
                                " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                                " and extract(year from itemrequireddate)="+str(self.year)+ \
                                " and bg='ATI2'" \
                                " group by extract(day from itemrequireddate), itemnoun, uom, qtyperuom, pgc "+ \
                                " order by itemnoun, extract(day from itemrequireddate)")
        else:
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from postingdate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_so_header_temp sh "+ \
                                " inner join sis_so_line sl_temp on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                                " and extract(year from postingdate)="+str(self.year)+ \
                                " and bg<>'ATI2'" \
                                " group by extract(day from postingdate), itemno, variant, uom, qtyperuom, pgc "+ \
                                " order by itemno, variant, extract(day from postingdate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), itemnoun, '', sum(quantity), uom, qtyperuom, pgc from sis_so_header_temp sh "+ \
                                " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                                " and extract(year from itemrequireddate)="+str(self.year)+ \
                                " and bg<>'ATI2'" \
                                " group by extract(day from itemrequireddate), itemnoun, uom, qtyperuom, pgc "+ \
                                " order by itemnoun, extract(day from itemrequireddate)")
        rs=self.env.cr.fetchall()
        
        #load so buffer
        if self.ati12=='ati2':
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from itemrequireddate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year ="+str(self.year)+ \
                            " and ati12='ati2'" \
                            " group by extract(day from itemrequireddate), itemno, variant, uom, qtyperuom, pgc "+ \
                            " order by itemno, variant, extract(day from itemrequireddate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), uitemno, '', sum(quantity), uom, qtyperuom, pgc from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year ="+str(self.year)+ \
                            " and ati12='ati2'" \
                            " group by extract(day from itemrequireddate), uitemno, variant, uom, qtyperuom, pgc "+ \
                            " order by uitemno, variant, extract(day from itemrequireddate)")
        else:
            if self.ul=='labeled':
                self.env.cr.execute("select extract(day from itemrequireddate), itemno, variant, sum(quantity), uom, qtyperuom, pgc from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year ="+str(self.year)+ \
                            " and ati12<>'ati2'" \
                            " group by extract(day from itemrequireddate), itemno, variant, uom, qtyperuom, pgc "+ \
                            " order by itemno, variant, extract(day from itemrequireddate)")
            else:
                self.env.cr.execute("select extract(day from itemrequireddate), uitemno, '', sum(quantity), uom, qtyperuom, pgc from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year ="+str(self.year)+ \
                            " and ati12<>'ati2'" \
                            " group by extract(day from itemrequireddate), uitemno, variant, uom, qtyperuom, pgc "+ \
                            " order by uitemno, variant, extract(day from itemrequireddate)")
                
            
        rsb=self.env.cr.fetchall()
        #insert to main so
        while len(rsb)>0:
            rb=rsb.pop()
            (rd,ritem,rvariant,rqty,ruom, rqtyperuom, pgc)=rb
            inserted=False
            rssb=[]

            for r in rs:
                (d,item,variant,qty,uom, qtyperuom, pgc)=r
                if rvariant==None:
                    rvariant=''
                if self.ul=='labeled':
                    if d==rd and item==ritem and variant==rvariant:
                        rqty=qty+rqty
                        rssb+=[(d,item,variant,rqty,uom, qtyperuom, pgc)]
                        inserted=True
                    else:
                        rssb+=[r]
                else:
                    if d==rd and item==ritem:
                        rqty=qty+rqty*rqtyperuom/qtyperuom
                        rssb+=[(d,item,'',rqty,uom, qtyperuom, pgc)]
                        inserted=True
                    else:
                        rssb+=[r]
            if inserted==False:
                rssb+=[rb]
            rs=rssb
        
        #update flag NAV
        sql="update sis_pps_so_current c set existnav=False from sis_pps_detail d where c.header_id=d.id and d.header_id="+str(self.id)
        self.env.cr.execute(sql)

        #nolkan line sales
        nol={}
        for i in range(1,32):
            nol.update({'t'+str(i):0})
        dets=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','sales')])
        for det in dets:
            det.write(nol)

        
        curritem="first"
        vals={}
        wvart=None
        vart=None
        wit=None
        wuom=None
        wqtyperuom=None
        for r in rs:
            (d,item,variant,qty,uom, qtyperuom, pgc)=r
            
            if item and len(item)>0:
                it=self.env['sis.items.local'].search([('itemno','=',item)])
                if len(it)==0:
                    raise UserError('Item on SO does not exist on NAV Item Master')
                    continue
                if len(it)>1:
                    raise UserError('Double item !')
                    continue
               
            else:
                continue

            if variant!='':
                if self.ul=='labeled':
                    vart=self.env['sis.item.variants.local'].search([('itemno','=',item),('variant','=',variant)])
                    if len(vart)==0:
                        raise UserError('Variant on SO does not exist on NAV Variant Master')
                        continue                        
                else:
                    raise UserError('Error: Unlabeled production planning with variant:item='+item+',variant='+variant)                        
            
            pgcm=self.env['sis.pgc.case48'].search([('pgc','=',pgc)])
            if len(pgcm)==0:
                if self.ul=='unlabeled' or (self.ul=='labeled' and len(vart)==0):
                    if uom!=it.purchuom:
                        qty=qty*qtyperuom/it.purchqtyperuom
                        qtyperuom=it.purchqtyperuom
                        uom=it.purchuom
                else:
                    if self.ul=='labeled':
                        if len(vart)>0:
                            if uom!=vart.uom:
                                qty=qty*qtyperuom/vart.qtyperuom
                                qtyperuom=vart.qtyperuom
                                uom=vart.uom
            else:
                if len(pgcm)==1:
                    qty=qty*qtyperuom/48
                    qtyperuom=48
                    uom='CASE'
                else:
                    if len(pgcm)>1:
                        raise UserError('PGC double on PGC Case48 master')                
            
            if item+variant!=curritem or curritem=='first':
                if curritem!='first':
                    detailnum=self.insert_data(vals,variant, item,wit,wvart, wuom, wqtyperuom, detailnum)  
                vals={}
                for i in range(1,32):
                    vals.update({'t'+str(i):0})
                curritem=item+variant
                wvart=vart
                wit=it
                wuom=uom
                wqtyperuom=qtyperuom
            vals['t'+str(int(d))]=qty
            
        #insert last item
        if curritem!='first':
            detailnum=self.insert_data(vals,variant, item,wit,wvart, wuom,wqtyperuom,detailnum)      
            
        self.lastupdate=datetime.now()+timedelta(hours=7)     
        
#        self.update_so_buffer()
        self.update_inventory(calclabeled=False)
        self.sort_sequence()
                 

    def insert_data(self, vals, variant, item,wit,wvart, uom,qtyperuom, detailnum):            
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
                
        for i in ['sales','inventory','production']:
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
                            'qtyperuom':qtyperuom,
                            'detailnum':detailnum
                            })
                rs=self.env['sis.pps.item'].search([('item_no','=',wit.itemno),('ati12','=',self.ati12)])
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
                    vals.update({'uom':uom,
                    'qtyperuom':qtyperuom})
                    sl.write(vals)
                    sid=sl.id
                else:
                    pvals={}
                    if uom!=sl.uom or qtyperuom!=sl.qtyperuom:
                        pvals.update({'uom':uom,
                                      'qtyperuom':qtyperuom})
                    if i=='production':
                        rs=self.env['sis.pps.item'].search([('item_no','=',wit.itemno),('ati12','=',self.ati12)])
                        if len(rs)==1:
                            if rs.line!=sl.line_id:
                                pvals.update({'line_id':rs.line})
                    else:
                        pvals.update({'line_id':''})                        
                    if len(pvals)>0:
                        sl.write(pvals)

        
        #update history SO
        if self.ati12=='ati2':
            if self.ul=='labeled':
                sql= "select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom, pgc, whshipno from sis_so_header_temp sh "+ \
                            " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                            " and extract(year from postingdate)="+str(self.year)+" and itemno='"+wit.itemno+"' and bg='ATI2' " 
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
                sql+=" union select id::text, itemrequireddate, itemrequireddate, selltoname, selltoname, selltoname, '', upper(ati12), '', itemno, description, variant, quantity, qtyperuom, uom, pgc, '' from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year="+str(self.year)+" and itemno='"+wit.itemno+"' and upper(ati12)='ATI2' "
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
            else:
                sql="select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom, pgc, whshipno from sis_so_header_temp sh "+ \
                            " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                            " and extract(year from itemrequireddate)="+str(self.year) +" and itemnoun='"+wit.itemno+"' and bg='ATI2' "
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
                sql+=" union select id::text, itemrequireddate, itemrequireddate, selltoname, selltoname, selltoname, '', upper(ati12), '', itemno, description, variant, quantity, qtyperuom, uom, pgc, '' from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year="+str(self.year)+" and uitemno='"+wit.itemno+"' and upper(ati12)='ATI2' "                        
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
        else:
            if self.ul=='labeled':
                sql= "select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom, pgc, whshipno from sis_so_header_temp sh "+ \
                            " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from postingdate)="+str(self.month)+ \
                            " and extract(year from postingdate)="+str(self.year)+" and itemno='"+wit.itemno+"' and bg<>'ATI2' " 
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
                sql+=" union select id::text, itemrequireddate, itemrequireddate, selltoname, selltoname, selltoname, '', upper(ati12), '', itemno, description, variant, quantity, qtyperuom, uom, pgc, '' from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year="+str(self.year)+" and itemno='"+wit.itemno+"' and upper(ati12)<>'ATI2' "
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
            else:
                sql="select no_, postingdate, itemrequireddate , selltono, selltoname, shiptoname, extdocno, bg, lineno, itemno, description, variant, quantity, qtyperuom, uom, pgc, whshipno from sis_so_header_temp sh "+ \
                            " inner join sis_so_line_temp sl on sh.id=sl.header_id and extract(month from itemrequireddate)="+str(self.month)+ \
                            " and extract(year from itemrequireddate)="+str(self.year) +" and itemnoun='"+wit.itemno+"' and bg<>'ATI2' "
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
                sql+=" union select id::text, itemrequireddate, itemrequireddate, selltoname, selltoname, selltoname, '', upper(ati12), '', itemno, description, variant, quantity, qtyperuom, uom, pgc, '' from sis_pps_so_buffer sh "+ \
                            " where month ="+str(self.month)+ " and year="+str(self.year)+" and uitemno='"+wit.itemno+"' and upper(ati12)<>'ATI2' "                        
                if wvart!=None:
                    sql+=" and variant='"+variant+"' "
            
        self.env.cr.execute(sql)
        ss=self.env.cr.fetchall()

        for s in ss:
            (no, pd, ird, custcode, custname, shiptoname, extdocno, bg, lineno, itemno, description, variant, qty, qtyperuom, uom, pgc, whshipno)=s

            qtyppic=qtyperuom
            qtyperuomppic=qtyperuom
            uomppic=uom

            pgcm=self.env['sis.pgc.case48'].search([('pgc','=',pgc)])
            if len(pgcm)==0:
                if self.ul=='unlabeled' or (self.ul=='labeled' and len(wvart)==0):
                    if uomppic!=wit.purchuom:
                        qtyppic=qty*qtyperuom/wit.purchqtyperuom
                        qtyperuomppic=wit.purchqtyperuom
                        uomppic=wit.purchuom
                else:
                    if self.ul=='labeled':
                        if len(wvart)>0:
                            if uomppic!=wvart.uom:
                                qtyppic=qty*qtyperuom/wvart.qtyperuom
                                qtyperuomppic=wvart.qtyperuom
                                uomppic=wvart.huom
            else:
                if len(pgcm)==1:
                    qtyppic=qty*qtyperuom/48
                    qtyperuomppic=48
                    uomppic='CASE'
                else:
                    if len(pgcm)>1:
                        raise UserError('PGC double on PGC Case48 master')     
            
            scs=self.env['sis.pps.so.current'].search([('header_id','=',sid),('no','=',no),('lineno','=',lineno),('itemno','=',itemno),('variant','=',variant)],order='id desc',limit=1)
            if len(scs)==1:
                if scs.postingdate==pd and scs.itemrequireddate==ird and scs.bg==bg and scs.quantity==qty and scs.uom==uom and scs.whshipno==whshipno:
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
                        'quantity':scs.quantity,
                        'qtyperuom': scs.qtyperuom,
                        'uom':scs.uom,
                        'qtyppic':scs.qtyppic,
                        'qtyperuomppic': scs.qtyperuomppic,
                        'uomppic':scs.uomppic,
                        'ati1qty':scs.ati1qty,
                        'ati1qtyppic':scs.ati1qtyppic,
                        'ati1date':scs.ati1date,
                        'ati2qty':scs.ati2qty,
                        'ati2qtyppic':scs.ati2qtyppic,
                        'remark':scs.remark,                                                                                                
                        'existnav':False,
                        'changetime':scs.write_date,
                        'curr_id':scs.id,
                        'whshipno':scs.whshipno                        
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
                        'qtyppic':qtyppic,
                        'qtyperuomppic':qtyperuomppic,
                        'uomppic':uomppic,
                        'existnav':True,
                        'whshipno':whshipno
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
                    'qtyppic':qtyppic,
                    'qtyperuomppic': qtyperuomppic,
                    'uomppic':uomppic,
                    'existnav':True,
                    'whshipno':whshipno
                  }
                self.env['sis.pps.so.current'].create(valso)               
        return detailnum

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

    def countcapacity(self):
        used={}
        hour={}
        lines={}
        for i in range(1,32):
            try:
                dt=datetime.strptime(str(self.year)+'-'+str(self.month)+'-'+str(i),'%Y-%m-%d')
            except:
                hour[i]=0
                continue
            days=self.env['sis.pps.exhour'].search([('workdate','=',dt),('ati12','=',self.ati12)])
            if len(days)==0:
                ordi=self.env['sis.pps.option'].search([('ati12','=',self.ati12)])
                if ordi and len(ordi)==1:
                    if dt.weekday()==4:
                        hourlimit=ordi.fri
                    else:
                        if dt.weekday()==5:
                            hourlimit=ordi.sat
                        else:
                            if dt.weekday()>=0 and dt.weekday()<4:
                                hourlimit=ordi.montothu
                            else:
                                hourlimit=0                
                else:
                    raise UserError('Option Error !')
            else:
                if days and len(days)==1:
                    hourlimit=days.hours
                else:
                    raise UserError('Hours option error !')                
            hour.update({i:hourlimit})
        
        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','plan')])
        for prod in prods:
            p=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',prod.detailnum),('type','=','production')])
            capacity=p.capacity
            linenum=p.linenum
            line_id=p.line_id
            for i in range(1,32):
                if prod['t'+str(i)]==0:
                    continue
                if capacity==0:
                    continue
                    raise UserError('Capacity = 0 for '+prod.item_no)
                if hour[i]!=0:
                    try:
                        used[line_id]['t'+str(i)]+=prod['t'+str(i)]/(capacity*hour[i]*linenum)
                    except:
                        used.update({line_id:{}})
                        for j in range(1,32):
                            used[line_id].update({'t'+str(j):0})
                        used[line_id].update({'linenum':linenum})
                        used[line_id]['t'+str(i)]=prod['t'+str(i)]/(capacity*hour[i]*linenum)   

        alts=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','alternative')])
        for prod in alts:
            p=self.env['sis.pps.detail'].search([('header_id','=',self.id),('detailnum','=',prod.detailnum),('type','=','production')])
            for i in range(1,32):
                if prod.capacity==0:
                    continue
                if hour[i]!=0:
                    if p['a'+str(i)]==False:
                        try:
                            used[prod.line_id]['t'+str(i)]+=prod['t'+str(i)]/(prod.capacity*hour[i]*prod.linenum)
                        except:
                            used.update({prod.line_id:{}})
                            for j in range(1,32):
                                used[prod.line_id].update({'t'+str(j):0})
                            used[prod.line_id].update({'linenum':prod.linenum})
                            used[prod.line_id]['t'+str(i)]=prod['t'+str(i)]/(prod.capacity*hour[i]*prod.linenum)   
        
        pls=self.env['sis.pps.packingline'].search([('ati12','=',self.ati12)])
        if len(pls)<1:
            raise UserError('Please fill Packing Lines for '+self.ati12.upper())
        for pl in pls:
            lines.update({pl.line:{}})
            lines[pl.line].update({'linenum':pl.linenum})
            for j in range(1,32):
                lines[pl.line].update({'t'+str(j):0})

        for use,ts in used.items():
            for dline,dts in lines.items():
                if set(use.split(",")) <= set(dline.split(",")):
                    break
            if set(use.split(",")) <= set(dline.split(",")):
                for i in range(1,32):
                    lines[dline]['t'+str(i)]+=ts['t'+str(i)]*ts['linenum']/dts['linenum']

        num=self.env['sis.pps.num.work.days'].search([('month','=',self.month),('year','=',self.year)]).num_work_days
        if num<1:
            raise UserError('Please define correct number of work days for'+str(self.year)+'/'+str(self.month))
        for dline,dts in lines.items():
            total=0
            totalhour=0
            for i in range(1,32):
                dts['t'+str(i)]*=100
                total+=dts['t'+str(i)]*hour[i]
                totalhour+=hour[i]
            if totalhour==0:
                totalhour=1
            lines[dline].update({'avg':total/totalhour})
            lines[dline].update({'header_id':self.id,
                                 'line':dline})
            
            rec=self.env['sis.pps.prod.capacity'].search([('header_id','=',self.id),('line','=',dline)])
            if len(rec)==1:
                rec.write(lines[dline])
            else:
                if len(rec)==0:
                    self.env['sis.pps.prod.capacity'].create(lines[dline])
                else:
                    raise UserError('Error data in production capacity usage')

    def countactualcapacity(self):
        used={}
        hour={}
        lines={}
        for i in range(1,32):
            try:
                dt=datetime.strptime(str(self.year)+'-'+str(self.month)+'-'+str(i),'%Y-%m-%d')
            except:
                hour[i]=0
                continue
            days=self.env['sis.pps.exhour'].search([('workdate','=',dt),('ati12','=',self.ati12)])
            if len(days)==0:
                ordi=self.env['sis.pps.option'].search([('ati12','=',self.ati12)])
                if ordi and len(ordi)==1:
                    if dt.weekday()==4:
                        hourlimit=ordi.fri
                    else:
                        if dt.weekday()==5:
                            hourlimit=ordi.sat
                        else:
                            if dt.weekday()>=0 and dt.weekday()<4:
                                hourlimit=ordi.montothu
                            else:
                                hourlimit=0                
                else:
                    raise UserError('Option Error !')
            else:
                if days and len(days)==1:
                    hourlimit=days.hours
                else:
                    raise UserError('Hours option error !')                
            hour.update({i:hourlimit})
        
        prods=self.env['sis.pps.detail'].search([('header_id','=',self.id),'|',('type','=','production'),('type','=','alternative')])
        for prod in prods:
            if prod.type=='alternative':
                prodp=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','production'),('detailnum','=',prod.detailnum)])                
            for i in range(1,32):
                if prod.type=='alternative':
                    if prodp['a'+str(i)]==True:
                        continue
                if prod.capacity==0:
                    continue
                    raise UserError('Capacity = 0 for '+prod.item_no)
                if hour[i]!=0:
                    try:
                        used[prod.line_id]['t'+str(i)]+=prod['t'+str(i)]/(prod.capacity*hour[i]*prod.linenum)
                    except:
                        used.update({prod.line_id:{}})
                        for j in range(1,32):
                            used[prod.line_id].update({'t'+str(j):0})
                        used[prod.line_id].update({'linenum':prod.linenum})
                        used[prod.line_id]['t'+str(i)]=prod['t'+str(i)]/(prod.capacity*hour[i]*prod.linenum)   


        pls=self.env['sis.pps.packingline'].search([('ati12','=',self.ati12)])
        if len(pls)<1:
            raise UserError('Please fill Packing Lines for '+self.ati12.upper())
        for pl in pls:
            lines.update({pl.line:{}})
            lines[pl.line].update({'linenum':pl.linenum})
            for j in range(1,32):
                lines[pl.line].update({'t'+str(j):0})

        for use,ts in used.items():
            for dline,dts in lines.items():
                if set(use.split(",")) <= set(dline.split(",")):
                    break
            if set(use.split(",")) <= set(dline.split(",")):
                for i in range(1,32):
                    lines[dline]['t'+str(i)]+=ts['t'+str(i)]*ts['linenum']/dts['linenum']

        num=self.env['sis.pps.num.work.days'].search([('month','=',self.month),('year','=',self.year)]).num_work_days
        if num<1:
            raise UserError('Please define correct number of work days for'+str(self.year)+'/'+str(self.month))
        for dline,dts in lines.items():
            total=0
            totalhour=0
            for i in range(1,32):
                dts['t'+str(i)]*=100
                total+=dts['t'+str(i)]*hour[i]
                totalhour+=hour[i]
                
            if totalhour==0:
                totalhour=1
            lines[dline].update({'avg':total/totalhour})
            lines[dline].update({'header_id':self.id,
                                 'line':dline})
            
            rec=self.env['sis.pps.actual.capacity'].search([('header_id','=',self.id),('line','=',dline)])
            if len(rec)==1:
                rec.write(lines[dline])
            else:
                if len(rec)==0:
                    self.env['sis.pps.actual.capacity'].create(lines[dline])
                else:
                    raise UserError('Error data in production capacity usage')

        
class sis_pps_detail(models.Model):
    _name='sis.pps.detail'
    _order='header_id,sequence'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month', store=True)
    year=fields.Integer(related='header_id.year', string='year',store=True)
    ati12=fields.Selection(related='header_id.ati12', string='ati',store=True)

    sequence=fields.Integer(string='Display Sequence')

    detailnum = fields.Integer(string='#')
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    uom = fields.Char(size=20,string="___UoM___")
    qtyperuom = fields.Float(string='Qty/UoM')
    #line_id = fields.Many2one('sis.pps.line',string='___Line___')#fields.Char(size=10,string='Line')    
    line_id = fields.Char(size=20,string='Line')    
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('sales','Sales'),('production','Production'),('alternative','Alt.Prod'),('plan','Plan'),('inventory','Inventory')],default='sales',string="Type")

    actualdate = fields.Date('Actual Date')
    qtyactual = fields.Float(string='Actual Qty')
    t0 = fields.Integer(string="Beg.Bal") #saldo awal
    capacity = fields.Float(compute='_compute_capacity',string='Capacity/Line/Hour')
    linenum = fields.Integer(compute='_compute_linenum',string='Line num')
    prioloin = fields.Integer(string='#/L',default=0)
    pctloin = fields.Integer(string='%/L',default=0)
    
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
    total = fields.Integer(string="Total", compute='_compute_total')    
    
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
    is_production = fields.Boolean(compute='_compute_is_production',string='Is Production')
    active_production = fields.Boolean(compute='_compute_active_production',string='Active Production',store=True)

    hideline = fields.Boolean(string='Hide Line') 
    
    readonlyall=fields.Boolean(compute='',string='Readonly')   
    so_current_id=fields.One2many('sis.pps.so.current','header_id')
    so_history_id=fields.One2many('sis.pps.so.history','header_id')
#     updateinvent1=fields.Boolean(string='Readonly',store=True)   
#     updateinvent=fields.Boolean(compute='_compute_inventory1',string='Readonly') 

    def getso(self): 
        self.env['sis.pps.detail'].search([('id','=',self._context['active_id'])]).header_id.getso()

    def calcmaterial(self): 
        self.env['sis.pps.detail'].search([('id','=',self._context['active_id'])]).header_id.countmaterial()

    def calcfgstock(self): 
        self.env['sis.pps.detail'].search([('id','=',self._context['active_id'])]).header_id.countfgstock()

    def update_items(self): 
        self.env['sis.items.local'].upload_from_NAV()
        
    def addalternative(self):
        rec=False
        ss=self.env['sis.pps.detail'].search([('id','=',self._context['active_ids'])])
        for r in ss:
            if self.env['sis.pps.detail'].search_count([('header_id','=',r.header_id.id),('detailnum','=',r.detailnum),('type','=','alternative')])==0: 
                vals = {
                    'header_id':r.header_id.id,
                    'header':r.header_id.id,
                    'item_no':r.item_no,
                    'variant_code':r.variant_code,
                    'description':r.description,     
                    'type':'alternative',
                    'uom':r.uom,
                    'qtyperuom':r.qtyperuom,
                    'detailnum':r.detailnum,
                    'hideline':True
                    }    
                line=self.env['sis.pps.item'].search([('item_no','=',r.item_no),('ati12','=',r.header_id.ati12)])
                if line and len(line)==1 and line.altline!=False and line.altline!='':
                    vals.update({'line_id':line.altline})
                else:
                    raise UserError('Please check SIS Item Master for '+r.item_no)
                rec=self.env['sis.pps.detail'].create(vals)
        if rec:
            rec.header_id.sort_sequence()

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        idd=models.Model.create(self, vals)
        if idd.type=='production':
            vals.pop('line_id',None)
            vals.update({'type':'plan'})
            self.env['sis.pps.detail'].create(vals)
            idd._recalc_inventory()
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
            self._recalc_inventory()
        if self.type=='alternative':
            self._recalc_inventory()
        return idd

    def so_based_posting_date(self,ss):
        vs={}
        for it in range(1,32):
            vs.update({it:0})
        
        for s in ss.so_current_id:
            mso=int(s.postingdate[5:7])  
            yso=int(s.postingdate[:4])              
            if mso!=int(ss.month) or yso!=int(ss.year) or s.existnav==False:
                continue
            dso=int(s.postingdate[8:10])    
            vs[dso]+=s.qtyppic
        return vs

    def _recalc_inventory(self):
        for r in self:
            header_id=r.header
            alt=False

#             s=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',r.detailnum),('type','=','sales')])
#             inv=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',r.detailnum),('type','=','inventory')])
#             if r.type=='production':
#                 alt=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',r.detailnum),('type','=','alternative')])
#             else:
#                 prod=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',r.detailnum),('type','=','production')])
            rs=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',r.detailnum)])
            for ss in rs:
                if ss.type=='sales':
                    s=ss
                if ss.type=='production':
                    prod=ss
                if ss.type=='inventory':
                    inv=ss
                if ss.type=='alternative':
                    alt=ss  

            vs=s.so_based_posting_date(s)                  
 
            vals={'t0':inv['t0']}
            run=inv['t0']
            for i in range(1,32):
                if inv['a'+str(i)]==False:
                    if r.type=='production':
                        if alt and len(alt)==1:
                            run+=(r['t'+str(i)]+alt['t'+str(i)]-vs[i])
                            vals.update({'t'+str(i):run})
                        else:
                            run+=(r['t'+str(i)]-vs[i])
                            vals.update({'t'+str(i):run})
                    else:
                        run+=(r['t'+str(i)]+prod['t'+str(i)]-vs[i])
                        vals.update({'t'+str(i):run})
                else:
                    run=inv['t'+str(i)]
            inv.write(vals)

    @api.one
    @api.constrains('header_id','item_no','variant_code',)
    def _constrain_double_items(self):
        if self.type=='sales':
            sl=self.env['sis.pps.detail'].search_count([('header_id','=',self.header_id.id),('item_no','=',self.item_no),('variant_code','=',self.variant_code),('type','=','sales'),('id','!=',self.id)])
            if sl>0:
                raise UserError('Item added already exists !')

    @api.one
    @api.constrains('line_id')
    def _constrain_line_id(self):
        if self.item_no and self.header_id.ati12 and self.line_id:
            s=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=',self.header_id.ati12)])
            if s and len(s)==1:
                if s.line==False or s.line=='':
                    raise UserError('No Def. Line for item '+self.item_no)
                lines=s.line.split(',')
                if s.altline!=False and s.altline!='':
                    altline=s.altline.split(',')
                if lines:
                    found=True
                    for line in self.line_id.split(','):
                        if  line in lines:    
                            pass
                        else:
                            found = False
                    if found==False and altline!=False and altline!='':
                        found=True
                        for line in self.line_id.split(','):
                            if  line in altline:    
                                pass
                            else:
                                found = False
                    if found==False:
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
    def _compute_total(self):
        total=0
        if self.type!='inventory':
            for i in range(1,32):
                total+=self['t'+str(i)]
        self.total=total

    @api.one
    @api.depends('type')
    def _compute_is_production(self):
        if self.type!='production' and self.type!='alternative' :
            self.is_production=False
        else:
            self.is_production=True

    @api.one
    @api.depends('total')
    def _compute_active_production(self):
        if self and len(self)>0:
            t=self
            if t.type!='production':
                t=self.env['sis.pps.detail'].search([('header_id','=',self.header_id.id),('detailnum','=',self.detailnum),('type','=','production')])
            if t and t.total>0:
                self.active_production=True
            else:
                self.active_production=False

    @api.one
    @api.depends('item_no','line_id','header_id.ati12')
    def _compute_capacity(self):
        if self.item_no and self.header_id.ati12 and self.line_id:
            ss=self.env['sis.pps.item'].search([('item_no','=',self.item_no),('ati12','=',self.header_id.ati12)])
            if ss and len(ss)==1:
                for s in ss:
                    found=True
                    for lin in self.line_id.split(','):
                        if lin not in s.line.split(','):
                            found=False 
                            break
                    if found:
                        self.capacity=s.capacity
                        break
                    else:
                        if s.altline != False and s.altline!='':
                            found=True
                            for lin in self.line_id.split(','):
                                if lin not in s.altline.split(','):
                                    found=False 
                                    break
                        if found:
                            self.capacity=s.altcapacity
                            break
                       
                if not found:
                    #raise UserError('Cannot find capacity for '+ self.item_no)
                    self.capacity=1
            else:
                raise UserError('Capacity Error!')
            
    @api.one
    @api.depends('line_id')
    def _compute_linenum(self):
        if self.line_id :
            if self.type=='production' or self.type=='alternative' :        
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
                'domain':"[('header_id','=',"+str(self.id)+")]"
            }

    def insert_loin(self):
        dets=self.env['sis.pps.detail'].search([('header_id','=',self.id),('type','=','production')])
        for det in dets:
            loins=self.env['sis.pps.loin'].search([('header_id','=',self.id),('item_no','=',det.item_no),('variant_code','=',det.variant_code),('type','=','number')])
            if len(loins)==0:
                vals={'header_id':self.id,
                      'item_no':det.item_no,
                      'variant_code':det.variant_code,
                      'description':det.description,
                      'type':'number'}
                self.env['sis.pps.loin'].create(vals)
                vals.update({'type':'percent'})
                self.env['sis.pps.loin'].create(vals)


    def open_note(self): 
        if self.variant_code:
            variant=self.variant_code
        else:
            variant=''
            
        if self.type=='sales':
            note=self.env['sis.pps.note'].search([('header_id','=',self.id)])
            if len(note)<1:
                note=self.env['sis.pps.note'].create({'header_id':self.id})
            return {
                'name': 'Note '+self.description + ' - '+variant,
                'res_model': 'sis.pps.note',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_note_form').id,
                'target': 'new',
                'nodestroy':True,
                'res_id':note.id
            }
        if self.type=='production':
            loins=self.env['sis.pps.loin'].search_count([('detail_id','=',self.id)])
            if loins==0:
                vals={'header_id':self.header_id.id,
                      'detail_id':self.id,
                      'item_no':self.item_no,
                      'variant_code':self.variant_code,
                      'description':self.description,
                      'type':'number'}
                self.env['sis.pps.loin'].create(vals)
                vals.update({'type':'percent'})
                self.env['sis.pps.loin'].create(vals)
            
            return {
                'name': 'Loin Usage '+self.description + ' - '+variant,
                'res_model': 'sis.pps.loin',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_loin_tree').id,
                'target': 'current',
                'nodestroy':True,
                'domain':"[('detail_id','=',"+str(self.id)+")]"
            }


    def open_add_item(self): 
        vals={
            'name': 'Add Item',
            'res_model': 'sis.pps.detail.add',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_detail_add_form').id,
            'target': 'new',
            'nodestroy':True
            #'domain':"[('header_id','=',"+str(self.id)+")]"
        }
        return vals

#     #@api.multi
#     @api.depends('t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13','t14','t15','t16','t17','t18','t19','t20','t21','t22','t23','t24','t25','t26','t27','t28','t29','t30','t31')
#     def _onchange_inventory1(self):
#         for r in self:
#             header_id=self._origin.header
#             s=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',self._origin.detailnum),('type','=','sales')])
#             inv=self.env['sis.pps.detail'].search([('header_id','=',header_id),('detailnum','=',self._origin.detailnum),('type','=','inventory')])
#             vals={'t0':inv['t0']}
#             run=inv['t0']
#             for i in range(1,32):
#                 if inv['a'+str(i)]==False:
#                     vals.update({'t'+str(i):run+r['t'+str(i)]-s['t'+str(i)]})
#                     run+=(r['t'+str(i)]-s['t'+str(i)])
#                 else:
#                     run=inv['t'+str(i)]
#             inv.write(vals)

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
            
        if test and len(test)==1 and ( self.type=='production' or self.type=='alternative' ):#and self.ul=='unlabeled':
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
                days=self.env['sis.pps.exhour'].search([('workdate','=',dt),('ati12','=',self.ati12)])
                if len(days)==0:
                    ordi=self.env['sis.pps.option'].search([('ati12','=',test.ati12)])
                    if ordi and len(ordi)==1:
                        if dt.weekday()==4:
                            hourlimit=ordi.fri
                        else:
                            if dt.weekday()==5:
                                hourlimit=ordi.sat
                            else:
                                if dt.weekday()>=0 and dt.weekday()<4:
                                    hourlimit=ordi.montothu
                                else:
                                    hourlimit=0
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
                    rs=self.env['sis.pps.detail'].search([('header_id','=',self.header),('line_id','!=',''),('t'+i,'!=',0),'|',('type','=','production'),('type','=','alternative')])
                    for r in rs:
                        if set(r.line_id.split(',')) <= set(ls):
                            strerror='Capacity = 0 for '+r.item_no+' '
                            if r.variant_code:
                                strerror+=r.variant_code
                            if r['capacity']==0:
                                raise UserError(strerror)
                            total+=r['t'+i]/r['linenum']/r['capacity']
 
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
                    s=self.env['sis.pps.detail'].search([('header','=',self.header),('detailnum','=',self.detailnum),('type','=','sales')])
                    if s['t'+str(i)]>self['t'+str(i)]:
                        self['f'+i]=3                        
                        

    @api.multi
    def unlink(self):
        for r in self:
            if r.type=='sales':               
                ds=self.env['sis.pps.detail'].search([('header_id','=',r.header_id.id),('detailnum','=',r.detailnum),('type','!=','sales')])
                for d in ds:
                    d.unlink()
            return models.Model.unlink(self)   
        
class sis_pps_material(models.Model):
    _name='sis.pps.material'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    #detail_need_id=fields.Many2one('sis.pps.material.need',string='Detail')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    year=fields.Integer(related='header_id.year', string='year')
    ati12=fields.Selection(related='header_id.ati12', string='ATI1/ATI2')
    
    sequence=fields.Integer(string='Sequence')
    
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No.___")
    uom = fields.Char(size=20,string="UoM______")
    qtyperuom = fields.Float(string="Qty/UoM")
    description = fields.Char(size=200,string="Description________________________")
    type = fields.Selection([('order','PO'),('material','Requirement'),('inventory','Inventory')],default='material',string="Type")
    inupdate=fields.Boolean('In Update',default=False)
    
    fish = fields.Char(size=20,string="Fish Type")
    t0 = fields.Float(string="BegBal")
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
    total = fields.Float(compute='_compute_total',string="Total")        

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
    
    hideline= fields.Boolean(string='__Invis')
    invist29 = fields.Boolean(related='header_id.invist29',string='__Invis')
    invist30 = fields.Boolean(related='header_id.invist30',string='__Invis')
    invist31 = fields.Boolean(related='header_id.invist31',string='__Invis')

    @api.one
    def _compute_total(self):
        self.total=self['t1']+self['t2']+self['t3']+self['t4']+self['t5']+self['t6']+self['t7']+self['t8']+self['t9']+\
            self['t10']+self['t11']+self['t12']+self['t13']+self['t14']+self['t15']+self['t16']+self['t17']+self['t18']+self['t19']+\
            self['t20']+self['t21']+self['t22']+self['t23']+self['t24']+self['t25']+self['t26']+self['t27']+self['t28']+self['t29']+\
            self['t30']+self['t31']

    def open_detmaterial(self):

        
        if self.type=='order' :
            dates=calendar.monthrange(self.year,self.month)
            (_,last)=dates
            return {
                'name': 'ORDER '+self.item_no +' - ' +self.description + ' - '+self.fish,
                'res_model': 'sis.pps.material.order',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_material_order_tree').id,
                'target': 'new',
                'nodestroy':False,
                'domain':"[('item_no','=','"+self.item_no+"'),('requested_receipt_date','>=','"+str(self.year)+"-"+str(self.month)+"-1'),"+\
                            "('requested_receipt_date','<=','"+str(self.year)+'-'+str(self.month)+"-"+str(last)+"')]"
            }
        if self.type=='material' :
            return {
                'name': 'MATERIAL '+self.item_no +' - ' +self.description + ' - '+self.fish,
                'res_model': 'sis.pps.material.need',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_detmaterial_tree').id,
                'target': 'current',
                'nodestroy':False,
                'domain':"[('material_id','=',"+str(self.id)+")]"
            }
        if self.type=='inventory' :
            return {
                'name': 'INVENTORY '+self.item_no +' - ' +self.description + ' - '+self.fish,
                'res_model': 'sis.pps.material.detail',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'tree',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_material_detail_tree').id,
                'target': 'new',
                'nodestroy':False,
                'domain':"[('material_id','=',"+str(self.id)+")]"
            }

    def open_etcmaterial(self):
        if self.type=='material':
            note=self.env['sis.pps.material.note'].search([('header_id','=',self.id)])
            if len(note)<1:
                note=self.env['sis.pps.material.note'].create({'header_id':self.id})
            return {
                'name': 'Note '+self.description ,
                'res_model': 'sis.pps.material.note',
                'type': 'ir.actions.act_window',
                'context': {},
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('sis_ppic.sis_pps_material_note_form').id,
                'target': 'new',
                'nodestroy':True,
                'res_id':note.id
            }        

    def calc_material(self):
        header=self.env['sis.pps.material'].search([('id','=',self._context['active_id'])]).header_id
        header.countmaterial()
       
class sis_pps_fishmaterial(models.Model):
    _name='sis.pps.fishmaterial'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    ati12=fields.Selection(related='header_id.ati12', string='ati')
    
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
    total = fields.Integer(string="Total", compute='_compute_total',store=True)  
    
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
    @api.depends('t1','t2','t3','t4','t5','t6','t7','t8','t9','t10','t11','t12','t13','t14','t15','t16','t17','t18','t19','t20','t21','t22','t23','t24','t25','t26','t27','t28','t29','t30','t31')
    def _compute_total(self):
        self.total=self['t1']+self['t2']+self['t3']+self['t4']+self['t5']+self['t6']+self['t7']+self['t8']+self['t9']+\
            self['t10']+self['t11']+self['t12']+self['t13']+self['t14']+self['t15']+self['t16']+self['t17']+self['t18']+self['t19']+\
            self['t20']+self['t21']+self['t22']+self['t23']+self['t24']+self['t25']+self['t26']+self['t27']+self['t28']+self['t29']+\
            self['t30']+self['t31']

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
            #look for workhours
            try:
                dt=datetime.strptime(str(self.header_id.year)+'-'+str(self.header_id.month)+'-'+i,'%Y-%m-%d')
            except:
                return
            days=self.env['sis.pps.exhour'].search([('workdate','=',dt),('ati12','=',self.ati12)])
            if len(days)==0:
                ordi=self.env['sis.pps.option'].search([('ati12','=',self.header_id.ati12)])
                if ordi and len(ordi)==1:
                    if dt.weekday()==4:
                        hourlimit=ordi.fri
                    else:
                        if dt.weekday()==4:
                            hourlimit=ordi.sat
                        else:
                            if dt.weekday()>=0 and dt.weekday()<4:
                                hourlimit=ordi.montothu
                            else:
                                hourlimit=0   
                else:
                    raise UserError('Option Error !')
            else:
                if days and len(days)==1:
                    hourlimit=days.hours
                else:
                    raise UserError('Hours option error !')            
            
            capacity=l.capacity/13*hourlimit
            
            if len(l)>0 and len(rs)>0:
                if capacity<total:
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

class sis_pps_prod_capacity(models.Model):
    _name='sis.pps.prod.capacity'
    _order='header_id,line'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    line = fields.Char(size=20,string="Line")
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
    avg = fields.Float(string="AVG")

class sis_pps_actual_capacity(models.Model):
    _name='sis.pps.actual.capacity'
    _order='header_id,line'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    line = fields.Char(size=20,string="Line")
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
    avg = fields.Float(string="AVG")
    
class sis_pps_item_fcl(models.Model):
    _name='sis.pps.fcl'
    _order='header_id,sequence'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    year=fields.Integer(related='header_id.year', string='year')
    ati12=fields.Selection(related='header_id.ati12', string='ati')

    sequence=fields.Integer(string='Display Sequence')

    detailnum = fields.Integer(string='#')
    header = fields.Integer(string="header")
    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    description = fields.Char(size=200,string="_______________Item________________")

    uomppic = fields.Char(size=10,string="UoM PPIC")
    uomsales = fields.Char(size=10,string="UoM Sales")
    qtyinfcl= fields.Integer(string='Qty-in-FCL/UoM Sales')        
    qtyperuom = fields.Float(string="Qty/UoM Sales")
    qtyperuomppic = fields.Float(string="Qty/UoM PPIC")

    t1 = fields.Float(string="1____")
    t2 = fields.Float(string="2____")
    t3 = fields.Float(string="3____")
    t4 = fields.Float(string="4____")
    t5 = fields.Float(string="5____")
    t6 = fields.Float(string="6____")
    t7 = fields.Float(string="7____")
    t8 = fields.Float(string="8____")
    t9 = fields.Float(string="9____")
    t10 = fields.Float(string="10__")
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
    total = fields.Float(string="Total")    

    def open_fclinfo(self): 
        if self.variant_code:
            variant=self.variant_code
        else:
            variant=''

        return {
            'name': self.description + ' - '+variant,
            'res_model': 'sis.pps.fcl',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'form',
            'view_type': 'form',
            'view_id': self.env.ref('sis_ppic.sis_pps_fcl1_form').id,
            'target': 'new',
            'nodestroy':True,
            'res_id':self.id
        }

class sis_pps_loin(models.Model):
    _name='sis.pps.loin'
    _order='header_id,item_no,type'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    detail_id=fields.Many2one('sis.pps.detail',string='Detail')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    year=fields.Integer(related='header_id.year', string='year')
    ati12=fields.Selection(related='header_id.ati12', string='ati')

    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    description = fields.Char(size=200,string="_______________Item________________")
    type = fields.Selection([('number','#L'),('percent','%L')],string="Type")

    t1 = fields.Float(string="1____")
    t2 = fields.Float(string="2____")
    t3 = fields.Float(string="3____")
    t4 = fields.Float(string="4____")
    t5 = fields.Float(string="5____")
    t6 = fields.Float(string="6____")
    t7 = fields.Float(string="7____")
    t8 = fields.Float(string="8____")
    t9 = fields.Float(string="9____")
    t10 = fields.Float(string="10__")
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

    def open_fish(self): 
        return self.header_id.open_fishmaterialtreeviewnew()

    def calc_material(self):
        header=self.env['sis.pps.loin'].search([('id','=',self._context['active_id'])]).header_id
        header.countmaterial()
#        self.888material()


class sis_pps_material_need(models.Model):
    _name='sis.pps.material.need'
    _order='header_id,material_id,item_no'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    material_id=fields.Many2one('sis.pps.material',string='Detail')
    ul=fields.Selection(related='header_id.ul', string='Unlabeled/Labeled')
    month=fields.Selection(related='header_id.month', string='month')
    year=fields.Integer(related='header_id.year', string='year')
    ati12=fields.Selection(related='header_id.ati12', string='ati')

    item_no = fields.Char(size=20,string="Item No")
    variant_code = fields.Char(size=20,string="___Variant___")
    description = fields.Char(size=200,string="_______________Item________________")

    t1 = fields.Float(string="1____")
    t2 = fields.Float(string="2____")
    t3 = fields.Float(string="3____")
    t4 = fields.Float(string="4____")
    t5 = fields.Float(string="5____")
    t6 = fields.Float(string="6____")
    t7 = fields.Float(string="7____")
    t8 = fields.Float(string="8____")
    t9 = fields.Float(string="9____")
    t10 = fields.Float(string="10__")
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


class sis_pps_note(models.Model):
    _name='sis.pps.note'

    header_id=fields.Many2one('sis.pps.detail',string='Header',required=True)
    note=fields.Text(string='Note')

class sis_pps_material_note(models.Model):
    _name='sis.pps.material.note'

    header_id=fields.Many2one('sis.pps.material',string='Header',required=True)
    note=fields.Text(string='Note')

    
class sis_pps_material_detail(models.Model):
    _name='sis.pps.material.detail'

    header_id=fields.Many2one('sis.pps.header',string='Header')
    material_id=fields.Many2one('sis.pps.material',string='Material')    
    item_no = fields.Char(size=20,string="Item No")
    description= fields.Char(size=200,string="Description")
    variant = fields.Char(size=20,string="Variant")
    entrytype = fields.Char(size=50,string="Entry Type")
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
    

        