from odoo import models, fields, api
from odoo.exceptions import UserError
from psycopg2.sql import NULL
from datetime import datetime
from dateutil.relativedelta import relativedelta

class sis_ile_remaining_quantity(models.Model):
    _name='sis.ile.remaining.quantity'
    _table='sis_ile_remaining_quantity'
    _auto=False
    _rec_name='lot_no'

    item_no =fields.Char(size=20,string="Item No",readonly=True) 
    posting_date =fields.Date(string="Posting Date", readonly=True)
    document_no =fields.Char(size=20,string="Document No",readonly=True)
    description =fields.Char(size=200,string="Description",readonly=True)
    variant =fields.Char(size=50,string="Variant",readonly=True)
    location_code =fields.Char(size=20,string="Location Code",readonly=True)
    quantity =fields.Float(string="Quantity",readonly=True)
    remaining_quantity =fields.Float(string="Remaining Quantity",readonly=True)
    lot_no =fields.Char(string="Lot No",readonly=True)
    fish_box_no =fields.Char(size=20,string="Fish Box No",readonly=True)
    vessel_no =fields.Char(size=25,string="Vessel No",readonly=True)
    container_no =fields.Char(size=40,string="Container No",readonly=True)
    voyage_no =fields.Char(size=20,string="Voyage No",readonly=True)
    hatch_no =fields.Char(size=20,string="Hatch No",readonly=True)
    no_basket =fields.Char(size=20,string="No Basket",readonly=True)
    no_contract =fields.Char(size=20,string="No Contract",readonly=True)
    inkjet_print =fields.Char(size=250,string="Inkjet Print",readonly=True)      
    itc=fields.Char(size=20,string="Item Cat.",readonly=True)
    pgc=fields.Char(size=20,string="Product Grp.",readonly=True)         
    

class sis_temp_ile_remaining_quantity(models.Model):
    _name='sis.temp.ile.remaining.quantity'

    item_no =fields.Char(size=20,string="Item No") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(size=20,string="Document No")
    description =fields.Char(size=200,string="Description")
    variant =fields.Char(size=50,string="Variant")
    location_code =fields.Char(size=20,string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    lot_no =fields.Char(string="Lot No")
    fish_box_no =fields.Char(size=20,string="Fish Box No")
    vessel_no =fields.Char(size=25,string="Vessel No")
    container_no =fields.Char(size=40,string="Container No")
    voyage_no =fields.Char(size=20,string="Voyage No")
    hatch_no =fields.Char(size=20,string="Hatch No")
    no_basket =fields.Char(size=20,string="No Basket")
    no_contract =fields.Char(size=20,string="No Contract")
    inkjet_print =fields.Char(size=250,string="Inkjet Print")     
    itc=fields.Char(size=20,string="Item Cat.")
    pgc=fields.Char(size=20,string="Product Grp.")
    proddate=fields.Char(size=10,string="Prod.Date")    
    bin=fields.Char(size=10,string='Bin')
    plno=fields.Char(size=20,string='PL No.',compute='_compute_plno')

    def update_stock_list(self):
        self.env['sis.goods.bin'].update_outbound()

    @api.one
    def _compute_plno(self):
        recs=self.env['sis.shipment.detail'].search([('status','!=','canceled'),'|',('planlotno','=',self.lot_no),('newlotno','=',self.lot_no)],order='create_date desc',limit=1)
        for rec in recs:
            self.plno=rec.plno

        
#     @api.one
#     def compute_bin(self):
#         recs=self.env['sis.goods.bin'].search([('entry_no','=',self.id),('out','=',False)])
#         for rec in recs:
#             self.bin=rec.bin
        
class sis_so_header_local(models.Model):
    _name='sis.so.header.local'
        
    sono =fields.Char(size=20,string="SO No") 
    postingdate =fields.Date(string="Posting Date",store=True)

    bg=fields.Char(size=4,string="BG",store=True)
    selltono=fields.Char(size=20,string="Sell to No",store=True)
    selltoname=fields.Char(size=200,string="Sell to Name",store=True)
    discharging_port=fields.Char(size=100,string="Discharging Port",store=True)    
    shiptoname=fields.Char(size=200,string="Ship to name",store=True)
    extdocno=fields.Char(size=50,string="External Doc No",store=True)   
    
    name=fields.Char(compute='_compute_name',string='Name') 

    @api.one
    def _compute_name(self):
        self.name=self.sono+' : '+self.extdocno

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        args=args or []
        recs=self.browse()
        if name:
            recs=self.search([('sono',operator,name)]+args,limit=limit)
        if len(recs)==0:
            recs=self.search([('extdocno',operator,name)]+args,limit=limit)
        return recs.name_get()  

class sis_add_pl(models.TransientModel):
    _name='sis.add.pl'
        
    pl =fields.Many2one('sis.shipment.header',string="PL No",ondelete='SET NULL') 
    #sono =fields.Integer(string="SO No") 

        
    def add_to_pl(self):
        sh=self.pl
        
        if len(sh):
            if sh.sono and len(sh.sono)>0:
                #prepare lookup dict
                iteminso={}
                self.env.cr.execute(" select itemno, variant, quantity, qtyperuom "+\
                                    " from sis_so_line where docno='"+sh.sono+"'")
                sls=self.env.cr.fetchall()
                if sls==False or len(sls)==0:
                    raise UserError('Sales Order Line '+self.no+' does not exist')
                for sl in sls:
                    (itemno,variant,quantity,qtyperuom)=sl
                    try:
                        iteminso[(itemno,variant)]['quantity']+=quantity*qtyperuom
                    except:
                        iteminso.update({(itemno,variant):{'quantity':quantity*qtyperuom, 'qtyinpl':0,'qtyperuom':qtyperuom}})
            
            iles=self.env['sis.temp.ile.remaining.quantity'].browse(self._context['active_ids'])
            if iles==False or len(iles)==0:
                raise UserError('Please select Stock list')
            if sh.sono and len(sh.sono)>0:
                for ile in iles:
                    try:
                        iteminso[(ile.item_no,ile.variant)]['qtyinpl']+=ile.remaining_quantity
                    except:
                        raise UserError('Item '+ile.item_no+'/'+ile.variant+':'+ile.description+' does not exist in SO '+sh.sono)
                
            ln=self.env['sis.shipment.detail'].search([('header_id','=',sh.id)],order='lineno desc',limit=1)
            if len(ln)==0:
                lineno=0
            else:
                lineno=ln.lineno
            for ile in iles:
                lineno+=10000
                bin1=self.env['sis.goods.bin'].search([('entry_no','=',ile.id),('next_id','=',None),('out','=',False)])
                if bin1.bin and len(bin1.bin)>0:
                    #for bin2 in bin1;
                    if bin1.bin[:1] in ['K','R']:
                        raise UserError('ERROR: Cannot use Item in KARANTINA/REJECT Area !!')
                    binloc=bin1.bin
                else:
                    binloc=''
                vals={'header_id':sh.id,
                      'lineno':lineno,
                      'bin':binloc,
                      'entryno':ile.id,
                      'itemno':ile.item_no,
                      'description':ile.description,
                      'variant':ile.variant,
                      'location':ile.location_code,
                      'quantity':ile.remaining_quantity,
                      'remaining_quantity':ile.remaining_quantity,
                      'planlotno':ile.lot_no,
                      'newlotno':ile.lot_no,
                      'nobasket':ile.no_basket,
                      'nocontract':ile.no_contract,
                      'inkjetprint':ile.inkjet_print,
                      'proddate':ile.proddate}
                self.env['sis.shipment.detail'].create(vals)        
#             return {
#                 'name': sh.no,
#                 'res_model': 'sis.shipment.header',
#                 'type': 'ir.actions.act_window',
#                 'context': {},
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'view_id': self.env.ref('sis_goods_bin.sis_shipment_header_form').id,
#                 'target': 'current',
#                 'nodestroy':False,
#                 'res_id':sh.id
#             }          
        else:
            raise UserError('Please choose correct PL')        

    
class sis_make_pl(models.TransientModel):
    _name='sis.make.pl'
        
    sono =fields.Many2one('sis.so.header.local',string="SO No",ondelete='SET NULL') 
    containerno =fields.Char(string="Container No") 
    bg =fields.Char(string="BG",size=5)   
    postingdate =fields.Date(string="Posting Date")      
    remark =fields.Char(string="Remark",size=200) 
    
    def update_so(self):
        self.env.cr.execute("delete from sis_so_header_local")
        self.env.cr.execute(" insert into sis_so_header_local(id,sono,postingdate,selltono,selltoname,shiptoname, discharging_port, extdocno,bg)"+\
                            " select id,no_,postingdate,selltono,selltoname,shiptoname, discharging_port, extdocno,bg "+\
                            " from sis_so_header where status='Released'")
        

    def make_pl(self):
        vals={'remark':self.remark,
              'containerno':self.containerno,
              'postingdate':self.postingdate,
              'bg':self.bg
              }
        iles=self.env['sis.temp.ile.remaining.quantity'].browse(self._context['active_ids'])
        if self.sono:
            #insert header
            self.env.cr.execute("select postingdate,selltono,selltoname,shiptoname, discharging_port, extdocno,bg,invno,pono "+\
                        "from sis_so_header where no_='"+self.sono.sono+"'")
            sos=self.env.cr.fetchall()
            if sos==False or len(sos)==0:
                raise UserError('Sales Order '+self.no+' does not exist')
            for so in sos:
                (postingdate,selltono,selltoname,shiptoname, discharging_port,extdocno,bg,invno,pono)=so
                vals.update({'sono':self.sono.sono,

                      'postingdate':postingdate,
                      'selltono':selltono,
                      'selltoname':selltoname,
                      'discharging_port':discharging_port,
                      'shiptoname':shiptoname,
                      'extdocno':extdocno,
                      'invno':invno,
                      'pono':pono,
                      'bg':bg})

            sh=self.env['sis.shipment.header'].create(vals)

            #prepare lookup dict
            iteminso={}
            self.env.cr.execute(" select itemno, variant, quantity, qtyperuom "+\
                                " from sis_so_line where docno='"+self.sono.sono+"'")
            sls=self.env.cr.fetchall()
            if sls==False or len(sls)==0:
                raise UserError('Sales Order Line '+self.no+' does not exist')
            for sl in sls:
                (itemno,variant,quantity,qtyperuom)=sl
                try:
                    iteminso[(itemno,variant)]['quantity']+=quantity*qtyperuom
                except:
                    iteminso.update({(itemno,variant):{'quantity':quantity*qtyperuom, 'qtyinpl':0}})
            
            if iles==False or len(iles)==0:
                raise UserError('Please select Stock list')
            for ile in iles:
                try:
                    iteminso[(ile.item_no,ile.variant)]['qtyinpl']+=ile.remaining_quantity
                except:
                    raise UserError('Item '+ile.item_no+'/'+ile.variant+':'+ile.description+' does not exist in SO '+sh.sono)
#                 if iteminso[(ile.itemno,ile.variant)]['qtyinpl']>iteminso[(ile.itemno,ile.variant)]['quantity']:
#                     raise UserError('Quantity item '+ile.itemno+' - '+ile.variant+' larger than qty in SO '+sh.sono)                    
        else:
            sh=self.env['sis.shipment.header'].create(vals)
                
        lineno=0
        for ile in iles:
            lineno+=10000
            bin=self.env['sis.goods.bin'].search([('entry_no','=',ile.id),('next_id','=',None),('out','=',False)])

            if bin.bin and len(bin.bin)>0:
                if bin.bin[:1] in ['K','R']:
                    raise UserError('ERROR: Cannot use Item in KARANTINA/REJECT Area !!')
                binloc=bin.bin
            else:
                binloc=''
            vals={'header_id':sh.id,
                  'lineno':lineno,
                  'bin':binloc,
                  'entryno':ile.id,
                  'itemno':ile.item_no,
                  'variant':ile.variant,
                  'description':ile.description,
                  'location':ile.location_code,
                  'quantity':ile.remaining_quantity,
                  'remaining_quantity':ile.remaining_quantity,
                  'planlotno':ile.lot_no,
                  'newlotno':ile.lot_no,
                  'nobasket':ile.no_basket,
                  'nocontract':ile.no_contract,
                  'inkjetprint':ile.inkjet_print,
                  'proddate':ile.proddate}
            self.env['sis.shipment.detail'].create(vals)                
                

#         return {
#                 'name': sh.no,
#                 'res_model': 'sis.shipment.header',
#                 'type': 'ir.actions.act_window',
#                 'context': {},
#                 'view_mode': 'form',
#                 'view_type': 'form',
#                 'view_id': self.env.ref('sis_goods_bin.sis_shipment_header_form').id,
#                 'target': 'current',
#                 'nodestroy':False,
#                 'res_id':sh.id
#             }  

    
class sis_goods_bin(models.Model):
    _name='sis.goods.bin'
    _rec_name='description'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin')
    next_id=fields.Many2one('sis.goods.bin',string='Next')
    entry_no = fields.Integer(string='Entry No')
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    item_no =fields.Char(string="Item No") 
    posting_date =fields.Date(string="Posting Date")
    document_no =fields.Char(string="Document No")
    description =fields.Char(compute='_compute_description',string="Description",store=True)
    variant=fields.Char(compute='_compute_variant',string="Variant",store=True)
    location_code =fields.Char(string="Location Code")
    quantity =fields.Float(string="Quantity")
    remaining_quantity =fields.Float(string="Remaining Quantity")
    lot_no =fields.Char(string="Lot No")
    fish_box_no =fields.Char(string="Fish Box No")
    vessel_no =fields.Char(string="Vessel No")
    container_no =fields.Char(string="Container No")
    voyage_no =fields.Char(string="Voyage No")
    hatch_no =fields.Char(string="Hatch No")
    no_basket =fields.Char(string="No Basket")
    no_contract =fields.Char(string="No Contract")
    inkjet_print =fields.Char(string="Inkjet Print")    
    out=fields.Boolean(string="Out",default=False)        
    ul=fields.Char(compute='_compute_ul',string="Un/Labeled",store=True)    
#     inkubasi = fields.Boolean(compute='_compute_inkubasi',string="Inkubasi")

    #@api.one
#     def _compute_inkubasi(self):
#         d=datetime.today()-datetime.strptime(self.posting_date,"%Y-%m-%d")
#         if self.item_no[:2]=='UC' and d.days<14:
#             self.inkubasi = True
#         else:
#             self.inkubasi = False

    def open_history(self): 
        return {
            'name': self.description + ' - '+self.lot_no,
            'res_model': 'sis.goods.bin.history',
            'type': 'ir.actions.act_window',
            'context': {},
            'view_mode': 'tree',
            'view_type': 'form',
            'view_id': self.env.ref('sis_goods_bin.sis_goods_bin_history_tree').id,
            'target': 'new',
            'nodestroy':True,
            'domain':"[('header_id','=',"+str(self.id)+")]"
        }

    def update_from_old_data(self):
        #update yang masih ada
        nn=0
        rs=self.env['sis.goods.bin'].search([('next_id','=',None)])
        for r in rs:
            #membersihkan yg sudah keluar
            nn+=1
            self.env.cr.execute("select bin from sis_goods_bin_backup "+\
                                "where next_id is null and entry_no="+str(r.entry_no))
                                
            recs=self.env.cr.fetchall()
            for rec in recs:
                (binn,)=rec
                if binn in ['14501','14502','14503','14504','14505']:
                    continue
                r.bin=binn
                
            self.env.cr.execute("select bin,remaining_quantity,lot_no from sis_goods_bin_backup "+\
                                "where next_id is not null and entry_no="+str(r.entry_no))
            recs=self.env.cr.fetchall()
            for rec in recs:
                (binn,remaining_quantity,lot_no)=rec

                vals={'header_id':r.id,
                      'bin_no':binn,
                      'remaining_quantity':remaining_quantity,
                      'lot_no':lot_no}
                self.env['sis.goods.bin.history'].create(vals)
 
            print(nn)

    def update_outbound(self):
       
        self.env.cr.execute('delete from sis_temp_ile_remaining_quantity')
         
        self.env.cr.execute("insert into sis_temp_ile_remaining_quantity(id,item_no,posting_date,document_no,description,variant,inkjet_print,itc,pgc, "+\
                            "location_code, quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,proddate) "+\
                             "select id,item_no,posting_date,document_no,description,variant,inkjet_print,itc,pgc, "+\
                            "location_code, quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,substring(lot_no from '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]') from sis_ile_remaining_quantity")
 
        self.env.cr.execute('update sis_temp_ile_remaining_quantity ile set bin=gb.bin from sis_goods_bin gb where ile.id=gb.entry_no and gb.out=False')        
 
        self.env.cr.execute('drop table if exists sis_temp_ile_rawfg')
        self.env.cr.execute("create table sis_temp_ile_rawfg as select *,substring(lot_no from '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]') proddate from sis_ile_raw")        

        self.env.cr.execute('drop table if exists sis_temp_released_production_order')
        self.env.cr.execute("create table sis_temp_released_production_order as select * from sis_released_production_order")        

        self.env.cr.execute('drop table if exists sis_temp_released_production_order_component')
        self.env.cr.execute("create table sis_temp_released_production_order_component as select * from sis_released_production_order_component")        
        
        
        rs=self.env['sis.goods.bin'].search([('remaining_quantity','>',0)])
        for r in rs:
            vals={}
  
            iles=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',r.entry_no)])
            if len(iles)==0:                  
                vals.update({'remaining_quantity':0})                    
  
            if len(iles)==1:
                if r.remaining_quantity==0:
                    continue
                if r.lot_no!=iles.lot_no:
                    vals.update({'lot_no':iles.lot_no})
                if r.remaining_quantity!=iles.remaining_quantity:
                    vals.update({'remaining_quantity':iles.remaining_quantity})                    
            if len(vals)>0:
                r.write(vals)


        #insert new records 
        self.env.cr.execute("select ile.id,item_no,posting_date,document_no,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print "+\
                            "from sis_temp_ile_remaining_quantity ile " + \
                             #"inner join sis_items_local it on it.itemno=ile.item_no and it.refitem!='' "+\
                            "where remaining_quantity>0 and ile.itc='FG'and ile.id not in (select distinct entry_no from sis_goods_bin ssm where entry_no is not NULL)")
                            
        recs=self.env.cr.fetchall()
        for rec in recs:
            (idd,item_no,posting_date,document_no,location_code,quantity,remaining_quantity,lot_no,fish_box_no,vessel_no,container_no,voyage_no,hatch_no,no_basket,no_contract,inkjet_print)=rec
            vals={
                'item_no':item_no, 
                'posting_date':posting_date,
                'document_no': document_no,
                'location_code': location_code,
                'quantity':quantity,
                'remaining_quantity':remaining_quantity,
                'lot_no':lot_no,
                'ile':lot_no,                
                'fish_box_no':fish_box_no,
                'vessel_no':vessel_no,
                'container_no':container_no,
                'voyage_no':voyage_no,
                'hatch_no':hatch_no,
                'no_basket':no_basket,
                'no_contract':no_contract,
                'inkjet_print':inkjet_print,
                'out':False,
                'entry_no':idd
            }
            self.env['sis.goods.bin'].create(vals)
        
        self.env['sis.goods.bin.free'].upload_to_goods_bin()

    @api.one
    @api.depends('item_no')
    def _compute_ul(self):
        its=self.env['sis.items.local'].search([('itemno','=',self.item_no)])
        if its.refitem=='' or its.refitem==None:
            self.ul='UNLABELED'
        else:
            self.ul='LABELED'

    @api.one
    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.bin'].search([('code','=',self.bin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Bin Error !')

    @api.one
    @api.depends('ile')
    def _compute_variant(self):
        if self.ile!=None and self.ile!=False:
            if self.ile[len(self.ile)-1]=="\n":
                self.ile=self.ile[:len(self.ile)-1]

            ile=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',self.entry_no)])
 
            if len(ile)==1:
                self.variant=ile.variant
#             else:
#                 if len(ile)>1:
#                     raise UserError('Multiple lot found!')
#                 else:
#                     raise UserError('Lot not found!')

    @api.one
    @api.depends('ile')
    def _compute_description(self):
        if self.ile!=None and self.ile!=False:
            if self.ile[len(self.ile)-1]=="\n":
                self.ile=self.ile[:len(self.ile)-1]

            ile=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',self.entry_no)])
 
            if len(ile)==1:
                self.description=ile.description
            else:
                if len(ile)>1:
                    raise UserError('Multiple lot found!')
                else:
                    self.variant=''
                    raise UserError('Lot not found!')

    
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        ile=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',vals['entry_no'])])
        if len(ile)==0:
            raise UserError ('Lot no does not exist!')
        if len(ile)>1:
            raise UserError ('Double lot no!')

        return models.Model.create(self, vals)


    @api.multi
    def write(self, vals):
        for s in self:
            valshist={'header_id':s.id,
                  'remaining_quantity':s.remaining_quantity,
                  'bin_no':s.bin,
                  'lot_no':s.lot_no,                  
                }
            self.env['sis.goods.bin.history'].create(valshist)
        return models.Model.write(self, vals)

    def opname(self):
        recs=self.env['sis.goods.bin'].browse(self._context['active_ids'])
        for rec in recs:
            vals={'ile':rec.lot_no,
                  'bin':'OPNAME'}
            self.env['sis.goods.bin'].create(vals)

    @api.constrains('bin')
    def _constrain_bin(self):
        for s in self:
            if s.bin and len(s.bin)>0:
                r=self.env['sis.bin'].search([('code','=',s.bin)])
                if len(r)==0:
                    raise UserError('Bin Not Found !')        

class sis_goods_bin_scan(models.TransientModel):
    _name='sis.goods.bin.scan'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin',required=True)
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    description =fields.Char(compute='_compute_description',string="Description",store=True)

    @api.one
    @api.depends('bin')
    def _compute_bin(self):
        if self.bin and len(self.bin)>0:
            r=self.env['sis.bin'].search([('code','=',self.bin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Bin Error !')

    @api.one
    @api.depends('ile')
    def _compute_description(self):
        if self.ile!=None and self.ile!=False:
            if self.ile[len(self.ile)-1]=="\n":
                self.ile=self.ile[:len(self.ile)-1]
            ile=self.env['sis.goods.bin'].search([('lot_no','=',self.ile),('remaining_quantity','>',0)])
            if len(ile)==1:
                self.description=ile.description
            else:
                if len(ile)>1:
                    raise UserError('Multiple lot found!')
                else:
                    raise UserError('Lot not found!')
    
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        ile=self.env['sis.goods.bin'].search([('lot_no','=',vals['ile'])])
        if len(ile)==0:
            raise UserError ('Lot no does not exist!')
        if len(ile)>1:
            raise UserError ('Double lot no!')
        bin1=self.env['sis.bin'].search([('code','=',vals['bin'])])
        if len(bin1)==0:
            raise UserError ('Bin not found!')
        if len(bin1)>1:
            raise UserError ('Double bin!')
        ile.write({'bin':vals['bin']})
        return models.Model.create(self, vals)

class sis_goods_bin_history(models.Model):
    _name='sis.goods.bin.history'
        
    header_id=fields.Many2one('sis.goods.bin',string='Header')
    bin_no =fields.Char(string="Bin") 
    remaining_quantity =fields.Float(string="Remaining Quantity")
    lot_no =fields.Char(string="Lot No")

    
class sis_goods_bin_free(models.Model):
    _name='sis.goods.bin.free'
        
    ile=fields.Char(string='Lot No',required=True)
    bin=fields.Char(string='Bin',required=True)
    bin_no =fields.Char(compute='_compute_bin', string="Bin") 
    error =fields.Char(size=50,string="Error Message") 

    @api.constrains('bin')
    def _constrain_bin(self):
        for s in self:
            if s.bin and len(s.bin)>0:
                r=self.env['sis.bin'].search([('code','=',s.bin)])
                if len(r)==0:
                    raise UserError('Bin Not Found !')        
    
    @api.multi
    def write(self, vals):
        try:
            rec=self.env['sis.goods.bin.free'].search([('ile','=',vals['ile'])])
            if len(rec)>0:
                rec.unlink()
        except:
            pass
        return models.Model.write(self, vals)

    def upload_to_goods_bin(self):
        self.env.cr.execute('drop table if exists sis_temp_item_journals')
        self.env.cr.execute('create table sis_temp_item_journals as select * from sis_item_journals')

        rs=self.env['sis.goods.bin.free'].search([])
        for r in rs:
            error=False
            ile=self.env['sis.goods.bin'].search([('lot_no','=',r['ile'])])
            if len(ile)==0:
                error='Lot no not found!'
            else:
                if len(ile)>1:
                    error='Double lot no!'
                else:
                    self.env.cr.execute("select remaining_quantity "+\
                        "from sis_temp_ile_rawfg where lot_no='"+r['ile']+"'")
                    itms=self.env.cr.fetchall()
                    qty=0
                    for itm in itms:
                        (qty,)=itm
                        if qty>0:
                            break
                    if qty==0:
                        error='Remaining qty = 0!'

            sql="select count('a')"+\
                "from sis_temp_item_journals where lot_no='"+r['ile']+"'"
            self.env.cr.execute(sql)
            itms=self.env.cr.fetchall()
            if itms and len(itms)>0:
                [(itm,)]=itms
                if itm!=0:
                    error='Not posted yet !'

            if not error:
                vals={'ile':r.ile,
                      'bin':r.bin
                      }
                ile.write(vals)
                r.unlink()
            else:
                r.error=error

    @api.depends('bin')
    def _compute_bin(self):
        for s in self:
            if s.bin and len(s.bin)>0:
                r=self.env['sis.bin'].search([('code','=',s.bin)])
                if len(r)==1:
                    s.bin_no=r.name
                else:
                    s.error='Bin Error !'


                    

class sis_opname_report(models.TransientModel):
    _name='sis.opname.report'
        
    bin=fields.Char(string='Bin')
    description=fields.Char(string='Description')
    qtyincase=fields.Float(string='Qty/Case',)
    qtyinlot=fields.Float(string='Qty/Lot',)
                    
class sis_opname_wizard(models.TransientModel):
    _name='sis.opname.wizard'
        
    bins=fields.Char(string='Bin',required=True)
    
    @api.multi
    def open_report(self):
        bins=self.bins.split(",")
        fixbins=''
        wildbins=''
        for bin1 in bins:
            if bin1.find('*')==-1:
                fixbins+=",'"+bin1+"'"
            else:
                wildbins+="or code like '"+bin1.replace('*','%')+"' "
                
        if len(fixbins)>0:
            fixbins=fixbins[1:]
        if len(wildbins)>0:
            wildbins=wildbins[3:]
        
        sql="select b.code,item_no,coalesce(variant, ''),description,sum(quantity),count(gb.id) "+\
            "from sis_bin b "+\
            "left outer join sis_goods_bin gb on b.code=gb.bin and gb.remaining_quantity>0"
            
        if len(fixbins)>0:
            sql+=" where code in ("+fixbins+") "
        if len(wildbins)>0:
            if len(fixbins)>0:
                sql+=" or "
            else:
                sql+=" where "                                
            sql+=" "+wildbins+" "
        
        sql+="  group by b.code,item_no,coalesce(variant, ''),description "
        sql+="  order by b.code,description "


        self.env.cr.execute(sql)
        
        datas=self.env.cr.fetchall()
        ids=[]
        for data in datas:
            (binn,itemno,variant,description,qty,lot)=data
            qtyincase,description1=self.calc_qtyincase(itemno,variant,qty)
            vals={
                'bin':binn,
                'description':description if description else description1,
                'qtyincase':qtyincase,
                'qtyinlot':lot
                }
            idd=self.env['sis.opname.report'].create(vals)
            ids+=[idd.id]

#         data = {'ids' : ids}
        data = {
                'ids': ids,
                'model': 'sis.opname.report'
            }
        print(self.env.ref('sis_goods_bin.action_opname_checklist').id)
#         return self.env.ref('sis_goods_bin.action_opname_checklist').report_action(self, data=data)        
#         return self.env['ir.actions.report'].browse(self.env.ref('sis_goods_bin.action_opname_checklist').id).report_action(self, data=data)    
#         self.env['ir.actions.report']._get_report_from_name('sis_goods_bin.action_opname_checklist')    
        return self.env.ref('sis_goods_bin.action_opname_checklist').report_action(docids=self.env['sis.opname.report'].search([('id','in',ids)]),config=False)
#         return {
#             'type': 'ir.actions.report.xml',
#             'report_name': 'sis.opname.checklist',
#             'datas': datas,
#         }

    def calc_qtyincase(self,itemno,variant,quantity):
        if itemno==None or itemno==False or len(itemno)==0:
            return 0,''
        if variant!=None and variant!=False and len(variant)>0:
            its=self.env['sis.item.variants.local'].search([('itemno','=',itemno),('variant','=',variant)])
            if len(its)==0:
                raise UserError('ERROR: Item does not exist on NAV Item Master (1)')            
        else:
            its=self.env['sis.items.local'].search([('itemno','=',itemno)])
            if len(its)==0:
                raise UserError('ERROR: Item does not exist on NAV Item Master (2)')
        qtyincase=0
        for it in its:
            qty=quantity-int(quantity/it.qtyperuom)*it.qtyperuom
            qty/=100
            qty+=int(quantity/it.qtyperuom)
            qtyincase=qty        
        return qtyincase,it.description
        
    
    
                    
                    
                    
                    