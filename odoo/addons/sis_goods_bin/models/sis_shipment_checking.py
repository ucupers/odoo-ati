from odoo import models, fields, api
from odoo.exceptions import UserError
import pyodbc
import re
from datetime import datetime
    
SQLCONN='Driver={/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.4.so.2.1};'+\
                              'Server=10.0.0.12;'+\
                              'Database=NAV (9-0) ATI LIVE;'+\
                              'UID=Atidev;pwd=Ati1234;'    

class sis_shipment_header(models.Model):
    _name='sis.shipment.header'
    _rec_name='no'
    _order='no desc'
        
    no =fields.Char(size=20,string="PL No")
    sono =fields.Char(size=20,string="SO No") 
    invno =fields.Char(size=20,string="Inv.No") 
    pono =fields.Char(size=20,string="SO No") 

    solineno = fields.Integer(string="SO Line No.")
    shipmentno =fields.Char(size=20,string="Shipment No")
    error =fields.Char(size=100,string="Error")     
    containerno =fields.Char(string="Container No",required=True) 
    postingdate =fields.Date(string="Posting Date",store=True)
    actualdate =fields.Date(string="Actual Date")    
    remark=fields.Char(string="Remark",size=200)     
    uploadremark=fields.Char(string="Upload Remark",size=200)     
    note=fields.Text(string="Note")     
    #valid=fields.Boolean(string="Valid",compute='_compute_valid')
    bg=fields.Char(size=4,string="BG",store=True)
    selltono=fields.Char(size=20,string="Sell to No",store=True)
    selltoname=fields.Char(size=200,string="Sell to Name",store=True)
    discharging_port=fields.Char(size=100,string="Discharging Port",store=True)    
    shiptoname=fields.Char(size=200,string="Ship to name",store=True)
    extdocno=fields.Char(size=50,string="External Doc No",store=True)    
    status = fields.Selection([('draft','Draft'),('released','Released'),('picked','Pick Complete'),('checked','Checked'),('confirmed','Confirmed'),('stuffed','Stuff.Complete'),('nav','NAV'),('canceled','Canceled')],default='draft',string="Status",required=True)
    totalplanincase=fields.Float(compute='_compute_totalincase',string='Total Plan in Case',store=True)
    totalactincase=fields.Float(compute='_compute_totalincase',string='Total Actual in Case',store=True)
    newsh=fields.Boolean(string='New')

    draft= fields.Datetime(string='Draft')                            
    released = fields.Datetime(string='Released')
    picked = fields.Datetime(string='Pick Complete')
    checked = fields.Datetime(string='Checked')
    confirmed = fields.Datetime(string='Confirmed')
    stuffed = fields.Datetime(string='Stuff.Complete')
    nav = fields.Datetime(string='Uploaded to NAV')
    canceled = fields.Datetime(string='Canceled')

    
    detail_id=fields.One2many('sis.shipment.detail','header_id')
    proddate_id=fields.One2many('sis.shipment.proddate','header_id')

    @api.multi
    def run_sql(self):
        for s in self:
            if s.status not in ['draft','released']:
                raise UserError('Status must be DRAFT')
            totalplan=0
            totalplanincase=0
     
            s.proddate_id.unlink()
     
            dets=self.env['sis.shipment.detail'].search([('header_id','=',s.id)],order='description,proddate')
            was=None
            for d in dets:
                if d.itemno==False:
                    continue
                if was!=None and d.description+d.proddate!=was.description+was.proddate:
                    if was.variant!=False and len(was.variant)>0:
                        its=self.env['sis.item.variants.local'].search([('itemno','=',was.itemno),('variant','=',was.variant)])
                        if len(its)==0:
                            raise UserError('ERROR: Item on SO does not exist on NAV Item Master (1)')            
                    else:
                        its=self.env['sis.items.local'].search([('itemno','=',was.itemno)])
                        if len(its)==0:
                            raise UserError('ERROR: Item on SO does not exist on NAV Item Master (2)')
                    qtyperuom=0
                    for it in its:
                        qtyperuom=it.qtyperuom
                    if qtyperuom==0:
                        raise UserError('ERROR: Qty/UoM not found '+was.itemno+'(Contact IT)')
                    totalplanincase=((totalplan-int(totalplan/qtyperuom)*qtyperuom)/100+int(totalplan/qtyperuom))
                    totalplanindec=totalplan/qtyperuom
                    totalplan=0
                    v={'header_id':s.id,
                       'description':was.description,
                       'qtyincase':totalplanincase,
                       'qtyindec':totalplanindec
                       }
                    if d.proddate:
                        proddate=datetime.strptime(was.proddate,'%Y%m%d')
                        v.update({'proddate':proddate.strftime('%d %b %Y')})
                    else:
                        v.update({'proddate':'Unknown'})                        
                    s.proddate_id.create(v)
                totalplan+=d.quantity
                was=d
            if was==False:
                return
            if was.variant!=False and len(was.variant)>0:
                its=self.env['sis.item.variants.local'].search([('itemno','=',was.itemno),('variant','=',was.variant)])
                if len(its)==0:
                    raise UserError('ERROR: Item on SO does not exist on NAV Item Master (3)')            
            else:
                its=self.env['sis.items.local'].search([('itemno','=',was.itemno)])
                if len(its)==0:
                    raise UserError('ERROR: Item on SO does not exist on NAV Item Master (4)')
            qtyperuom=0
            for it in its:
                qtyperuom=it.qtyperuom
            if qtyperuom==0:
                raise UserError('ERROR: Qty/UoM not found '+d.itemno+'(Contact IT)')
            totalplanincase=((totalplan-int(totalplan/qtyperuom)*qtyperuom)/100+int(totalplan/qtyperuom))
            totalplanindec=totalplan/qtyperuom
            v={'header_id':s.id,
               'description':d.description,
               'qtyincase':totalplanincase,
               'qtyindec':totalplanindec
               }
            if d.proddate:
                proddate=datetime.strptime(d.proddate,'%Y%m%d')
                v.update({'proddate':proddate.strftime('%d %b %Y')})
            else:
                v.update({'proddate':'Unknown'})                        
            s.proddate_id.create(v)

    @api.multi
    @api.depends('detail_id.quantity','detail_id.qtyact')
    def _compute_totalincase(self):
        for s in self:
            totalplan=0
            totalact=0
            totalplanincase=0
            totalactincase=0
     
            dets=self.env['sis.shipment.detail'].search([('header_id','=',s.id)],order='description')
            was=None
            for d in dets:
                if d.itemno==False:
                    continue
                if was!=None and d.description!=was.description:
                    if was.variant!=False and len(was.variant)>0:
                        its=self.env['sis.item.variants.local'].search([('itemno','=',was.itemno),('variant','=',was.variant)])
                        if len(its)==0:
                            raise UserError('ERROR: Item on SO does not exist on NAV Item Master (1)')            
                    else:
                        its=self.env['sis.items.local'].search([('itemno','=',was.itemno)])
                        if len(its)==0:
                            raise UserError('ERROR: Item on SO does not exist on NAV Item Master (2)')
                    qtyperuom=0
                    for it in its:
                        qtyperuom=it.qtyperuom
                    if qtyperuom==0:
                        raise UserError('ERROR: Qty/UoM not found '+was.itemno+'(Contact IT)')
                    totalplanincase+=((totalplan-int(totalplan/qtyperuom)*qtyperuom)/100+int(totalplan/qtyperuom))
                    totalactincase+=((totalact-int(totalact/qtyperuom)*qtyperuom)/100+int(totalact/qtyperuom))                
                    totalplan=0
                    totalact=0
                    s.totalplanincase=totalplanincase
                    s.totalactincase=totalactincase
     
                totalplan+=d.quantity
                totalact+=d.qtyact
                was=d
            if was==None:
                return
            if was.variant!=False and len(was.variant)>0:
                its=self.env['sis.item.variants.local'].search([('itemno','=',was.itemno),('variant','=',was.variant)])
                if len(its)==0:
                    raise UserError('ERROR: Item on SO does not exist on NAV Item Master (3)')            
            else:
                its=self.env['sis.items.local'].search([('itemno','=',was.itemno)])
                if len(its)==0:
                    raise UserError('ERROR: Item on SO does not exist on NAV Item Master (4)')
            qtyperuom=0
            for it in its:
                qtyperuom=it.qtyperuom
            if qtyperuom==0:
                raise UserError('ERROR: Qty/UoM not found '+d.itemno+'(Contact IT)')
            totalplanincase+=((totalplan-int(totalplan/qtyperuom)*qtyperuom)/100+int(totalplan/qtyperuom))
            totalactincase+=((totalact-int(totalact/qtyperuom)*qtyperuom)/100+int(totalact/qtyperuom))                
            s.totalplanincase=totalplanincase
            s.totalactincase=totalactincase
            
            
    
    @api.multi
    @api.onchange('sono')
    def compute_valid(self):
        if self.sono:
            self.env.cr.execute("select postingdate,selltono,selltoname,shiptoname, discharging_port, extdocno,bg "+\
                        "from sis_so_header where no_='"+self.sono+"'")
            sos=self.env.cr.fetchall()
            if sos==False or len(sos)==0:
                raise UserError('Sales Order '+self.sono+' does not exist')
#             sh=self.env['sis.shipment.header'].search([('no','=',no)])
            for so in sos:
                (postingdate,selltono,selltoname,shiptoname, discharging_port,extdocno,bg)=so
                if self.postingdate!=postingdate: 
                    self.postingdate=postingdate 

                if self.selltono!=selltono: 
                    self.selltono=selltono 

                if self.selltoname!=selltoname: 
                    self.selltoname=selltoname 

                if self.shiptoname!=shiptoname: 
                    self.shiptoname=shiptoname 

                if self.discharging_port!=discharging_port: 
                    self.discharging_port=discharging_port 

                if self.extdocno!=extdocno:
                    self.extdocno=extdocno
                    
                if self.bg!=bg:
                    self.bg=bg


    @api.one
    @api.constrains('sono','containerno')
    def _constraint_sono_containerno(self):
        if self.sono and self.sono!='':
            if self.env['sis.shipment.header'].search_count([('sono','=',self.sono),('containerno','=',self.containerno),('status','!=','canceled')])>1:
                raise UserError('Already exist : SO='+self.sono+',container no='+self.containerno)
    
    @api.one
    def back_to_release(self):
        if self.status in ('checked','picked'):
            self.released=datetime.now()
            self.status='released'
        else:
            raise UserError('PL must be in checked status')

    
    @api.one
    def cancel(self):
        if self.status not in ['stuffed','nav']:
            self.canceled=datetime.now()
            self.status='canceled'
        else:
            raise UserError('PL is already stuffing')

    def get_item_so(self):
        iteminso={}
        self.env.cr.execute(" select itemno, variant,sum(quantity),qtyperuom,sum(qtyshipped) "+\
                            " from sis_so_line where docno='"+self.sono+"' group by itemno,variant,qtyperuom")
        sls=self.env.cr.fetchall()
        if sls==False or len(sls)==0:
            raise UserError('Sales Order Line '+self.no+' does not exist')
        for sl in sls:
            (itemno,variant,quantity,qtyperuom,qtyshipped)=sl
            try:
                iteminso[(itemno,variant)]['qty']+=quantity*qtyperuom-qtyshipped
            except:
                iteminso.update({(itemno,variant):{'qty':quantity*qtyperuom-qtyshipped}})
        return iteminso
    

    def check_double_lot(self,level):
        for d in self.detail_id:
            if level=='release':
                lotno=d.planlotno
                item=self.env['sis.shipment.detail'].search([('status','!=','canceled'),('planlotno','!=',lotno),('id','!=',d.id)])
                planact='Planned '
            if level=='confirm':
                if d.nodata:
                    lotno=d.planlotno
                else:
                    lotno=d.actlotno
                item=self.env['sis.shipment.detail'].search([('status','!=','canceled'),('actlotno','!=',lotno),('id','!=',d.id)])
                planact='Actual '
            if len(item)==0:
                for itm in item:
                    raise UserError(planact+lotno + ' already used in '+itm.plno)
            
            self.env.cr.execute("select item_no "+\
                        "from sis_temp_ile_rawfg where remaining_quantity>0 and lot_no='"+lotno.replace("'","''")+"'")
            item=self.env.cr.fetchall()
            if len(item)==0:
                raise UserError('Zero Qty : lot '+lotno)
    
    
    def isempty(self,var):
        if var==False or var==None:
            raise UserError('ERROR: Please check Ext.Doc.No, Sell To No, Sell To Name, Discharging Port, and Ship To Name')            
    
    @api.one
    def release(self):
        if self.status=='draft':
            self.isempty(self.selltono)
            self.isempty(self.selltoname)
            self.isempty(self.discharging_port)                        
            self.isempty(self.shiptoname)
            self.isempty(self.extdocno)                        
            if self.actualdate==False or self.actualdate==None:
                raise UserError('ERROR: Actual date empty')
            iteminso=self.get_item_so()
            iteminpl={}
            self.check_double_lot('release')
            hs=self.env['sis.shipment.header'].search([('sono','=',self.sono),('containerno','=',self.containerno),('status','!=','canceled')])
            for h in hs:
                for d in h.detail_id:
                    try:
                        iteminpl[(d.itemno,d.variant)]['qty']+=d.quantity
                    except:
                        iteminpl.update({(d.itemno,d.variant):{'qty':d.quantity}})
                    try:
                        iteminso[(d.itemno,d.variant)]['qty']
                    except:
                        variant=d.variant
                        if d.variant==False:
                            variant=''
                        raise UserError('Item '+d.itemno+' variant '+variant+' not in SO ')

                    #hs=self.env['sis.shipment.detail'].search([('sono','=',self.sono),('status','!=','canceled')])                    
                for d in h.detail_id:
                    num=self.env['sis.shipment.detail'].search([('status','!=','canceled'),('status','!=','nav'),('plno','!=',d.plno),('planlotno','=',d.planlotno)])
                    if len(num)>0:
                        for n in num:
                            if n.qtyact==n.remqtyact:
                                raise UserError('This lot already used in '+n.plno)

                    if iteminpl[(d.itemno,d.variant)]['qty']>iteminso[(d.itemno,d.variant)]['qty']:
                        raise UserError('ERROR: Qty PL('+str(iteminpl[(d.itemno,d.variant)]['qty'])+')> Qty SO('+str(iteminso[(d.itemno,d.variant)]['qty'])+') for '+d.description)

            #fifo setiap kota
            for d in self.detail_id:
                #iles=self.env['sis.temp.ile.remaining.quantity'].search([('item_no','=',d.itemno),('variant','=',d.variant),('proddate','<',d.proddate),('lot_no','ilike',d.header_id.bg)], order='lot_no')
                self.env.cr.execute(" select lot_no "+\
                            " from sis_temp_ile_remaining_quantity ile " +\
                            " where ile.item_no='"+d.itemno+"' and ile.variant='"+d.variant+"' and ile.proddate<'"+d.proddate+"' and ile.lot_no ilike '"+d.header_id.bg+"%' "+\
                            " and ile.lot_no not in ( select planlotno from sis_shipment_detail where status!='canceled') limit 1")
                iles=self.env.cr.fetchall()
                if len(iles)==0:
                    if d.warning!='' and d.warning!=False:  
                        d.warning=''                    
                else:
                    [(lot_no,)]=iles
                    if d.warning!='Prev.date:'+lot_no:
                        d.warning='Prev.date:'+lot_no
                print(datetime.now())

            for d in self.detail_id:
                #iles=self.env['sis.temp.ile.remaining.quantity'].search([('item_no','=',d.itemno),('variant','=',d.variant),('proddate','<',d.proddate),('lot_no','ilike',d.header_id.bg)], order='lot_no')
                self.env.cr.execute(" select lot_no "+\
                            " from sis_temp_ile_remaining_quantity ile " +\
                            " where ile.item_no='"+d.itemno+"' and ile.variant='"+d.variant+"' and ile.proddate<'"+d.proddate+"' and ile.lot_no ilike '"+d.header_id.bg+"%' "+\
                            " and ile.lot_no not in ( select planlotno from sis_shipment_detail where status!='canceled' and planlotno is not NULL ) order by ile.lot_no limit 1")
                iles=self.env.cr.fetchall()
                if len(iles)==0:
                    if d.warning!='' and d.warning!=False:  
                        d.warning=''                    
                else:
                    [(lot_no,)]=iles
                    if d.warning!='Prev.date:'+lot_no:
                        d.warning='Prev.date:'+lot_no

                self.env.cr.execute(" select lot_no "+\
                            " from sis_temp_ile_remaining_quantity ile " +\
                            " where ile.item_no='"+d.itemno+"' and ile.variant='"+d.variant+"' and ile.proddate<'"+d.proddate+"' "+\
                            " and ile.lot_no not in ( select planlotno from sis_shipment_detail where status!='canceled' and planlotno is not NULL ) order by ile.lot_no  limit 1")
                iles=self.env.cr.fetchall()
                if len(iles)==0:
                    if d.warningati!='' and d.warning!=False:  
                        d.warningati=''                    
                else:
                    [(lot_no,)]=iles
                    if d.warningati!='Prev.date:'+lot_no:
                        d.warningati='Prev.date:'+lot_no

            #CARA LAMA
#             for d in self.detail_id:
#                 iles=self.env['sis.temp.ile.remaining.quantity'].search([('item_no','=',d.itemno),('variant','=',d.variant),('proddate','<',d.proddate)],order='lot_no')
#                 if len(iles)==0:
#                     if d.warningati!='':                      
#                         d.warningati=''                    
#                     continue
#                 for ile in iles:
#                     nos=self.env['sis.shipment.detail'].search_count([('status','!=','canceled'),('planlotno','=',ile.lot_no)])
#                     if nos==0:
#                         if d.warningati!='Prev.date:'+ile.lot_no:
#                             d.warningati='Prev.date:'+ile.lot_no
#                             break
#                     else:
#                         if d.warningati!='':                        
#                             d.warningati=''


            self.released=datetime.now()
            self.status='released'
            
        else:
            raise UserError('PL must be in DRAFT')
        


    @api.one
    def confirm(self):
        if self.status not in ['checked','confirmed']:
            raise UserError('PL must be Checked')
        if self.status=='checked':
            self.check(False)
            self.check_double_lot('confirm')
        
        no=0
        conn = pyodbc.connect(SQLCONN)
        cursor = conn.cursor()

        row=cursor.execute(" UPDATE [PT_ Aneka Tuna Indonesia$Item Ledger Entry] set [Cross-Reference No_]=''"+\
                           " WHERE [Cross-Reference No_]='"+self.no+"'")
        
        for d in self.detail_id:
            if d.newlotno!=d.actlotno:
                label=",[Labeling Lot No_]='"+d.newlotno+"' "
                row=cursor.execute(" UPDATE [PT_ Aneka Tuna Indonesia$Item Ledger Entry] set [Cross-Reference No_]='"+d.plno+"'"+label+\
                                   " WHERE [Entry No_]="+str(d.entryno))
                if row.rowcount==0:
                    raise UserError('Failed to update ILE NAV (2), please try again later')                

                
            no+=1
        if no>0:
            conn.commit()
        self.confirmed=datetime.now()
        self.status='confirmed'

    @api.one
    def check(self,check=True):
        if check and self.status!='picked' and self.status!='checked':
            raise UserError('PL must be PICK COMPLETE')

        iteminso=self.get_item_so()
                
        #semua harus actual lot dan tidak boleh ada item diluar SO
        for d in self.detail_id:
            if d.actlotno==False or len(d.actlotno)==0:
                raise UserError('ERROR: BLANK Actual Lot No')
            if d.actlotno and len(d.actlotno)>0 and d.nodata:
                if d.planlotno==False and len(d.actlotno)==0:                
                    raise UserError('ERROR: noDt without Plan Lot No')
            try:
                iteminso[(d.itemno,d.variant)]['qty']+=0
            except:
                if d.description==False:
                    raise UserError('ERROR: Item with no description')
                raise UserError('ERROR: Item '+d.description+' NOT in SO :'+self.sono)
            
        #qty actual harus sama dengan qty so -- in RELEASE
        #tgl prod kota pasangan dalam 1 minggu
        pcs=self.env['sis.paircity'].search([])
        #pcs=[]
        for pc in pcs:
            if self.discharging_port.find(pc.new)!=-1:
                self.env.cr.execute(" select distinct sn.actlotno "+\
                                    " from sis_shipment_detail sn "+\
                                    " inner join sis_shipment_detail so on sn.plno!=so.plno and sn.status not in ('canceled') and sn.discharging_port ilike '%"+pc.new+"%' " + \
                                    " and so.discharging_port ilike '%"+pc.old+"%' and so.status not in ('canceled') " + \
                                    " and extract(WEEK FROM sn.postingdate)=extract(WEEK FROM so.postingdate) and" +\
                                    " sn.itemno=so.itemno and sn.variant=so.variant and sn.sono='"+self.sono+"' and " +\
                                    " sn.proddate<so.proddate")
                sls=self.env.cr.fetchall()
                err='Newer lot found for city '+pc.old
            if self.discharging_port.find(pc.old)!=-1:
                self.env.cr.execute(" select distinct sn.actlotno "+\
                                    " from sis_shipment_detail sn "+\
                                    " inner join sis_shipment_detail so on sn.plno!=so.plno and sn.status not in ('canceled') and sn.discharging_port ilike '%"+pc.old+"%' "+\
                                    " and so.discharging_port ilike '%"+pc.new+"%' and so.status not in ('canceled') " +\
                                    " and extract(WEEK FROM sn.postingdate)=extract(WEEK FROM so.postingdate) and" +\
                                    " sn.itemno=so.itemno and sn.variant=so.variant and sn.sono='"+self.sono+"' and "+\
                                    " sn.proddate>so.proddate")                                    
                sls=self.env.cr.fetchall()
                err='Older lot found for city '+pc.new
            if self.discharging_port.find(pc.old)!=-1 or self.discharging_port.find(pc.new)!=-1:
                lot=''
                for sl in sls:
                    (s,)=sl
                    if s==None:
                        continue
                    if len(s)>0:
                        lot+=s+",\n"
                if len(lot)>0:
                    raise UserError(err+" lot :\n"+lot)

        self.env.cr.execute('DROP TABLE IF EXISTS sis_temp_ile_rawfg')
        self.env.cr.execute("CREATE TABLE sis_temp_ile_rawfg as select *,substring(lot_no from '[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]') proddate from sis_ile_raw where itc='FG'")        
#         for d in self.detail_id:

        #fifo setiap kota
        for d in self.detail_id:
            #iles=self.env['sis.temp.ile.remaining.quantity'].search([('item_no','=',d.itemno),('variant','=',d.variant),('proddate','<',d.proddate),('lot_no','ilike',d.header_id.bg)])
            self.env.cr.execute(" select lot_no "+\
                        " from sis_temp_ile_remaining_quantity ile " +\
                        " where ile.item_no='"+d.itemno+"' and ile.variant='"+d.variant+"' and ile.proddate<'"+d.proddate+"' and ile.lot_no ilike '"+d.header_id.bg+"%' "+\
                        " and ile.lot_no not in ( select planlotno from sis_shipment_detail where status!='canceled' and planlotno is not NULL union all "+\
                        " select newlotno from sis_shipment_detail where status!='canceled' and newlotno is not NULL "+\
                        " union all select actlotno from sis_shipment_detail where status!='canceled' and actlotno is not NULL ) order by ile.lot_no limit 1")
            iles=self.env.cr.fetchall()
            if len(iles)==0:
                if d.warning!='' and d.warning!=False:  
                    d.warning=''                    
            else:
                [(lot_no,)]=iles
                if d.warning!='Prev.date:'+lot_no:
                    d.warning='Prev.date:'+lot_no
            
#             if len(iles)==0:
#                 continue
#             for ile in iles:
#                 nos=self.env['sis.shipment.detail'].search_count([('status','!=','canceled'),'|',('planlotno','=',ile.lot_no),'|',('newlotno','=',ile.lot_no),('actlotno','=',ile.lot_no)])
#                 if nos==0:
#                     d.warning='Prev.date:'+ile.lot_no
#                 else:
#                     d.warning=''
#             if d.quantity!=0 and d.qtyact!=d.quantity:
#                     d.warning='QTY and QTYACT not equal'


            self.env.cr.execute("select lot_no,quantity"+\
                        " from sis_temp_ile_rawfg where remaining_quantity>0 and lot_no='"+d.newlotno.replace("'","''")+"' and id!="+str(d.entryno))
            item=self.env.cr.fetchall()
            if len(item)>0:
                for itm in item:
                    (lot,quantity)=itm
                    if quantity>0:
                        raise UserError("New Lot "+lot+" duplicate found in NAV")                
            
        self.checked=datetime.now()
        self.status='checked'



    @api.model
    def create(self, values):

        if values['bg']!='ATI1' and values['bg']!='ATI2':
            raise UserError('Please fill Business Group / BG with ATI1 ot ATI2')


        no='PL/'+values['bg']+'/'+values['postingdate'][2:4]+values['postingdate'][5:7]+'/'
        rec=self.env['sis.shipment.header'].search([('no','ilike',no)],limit=1,order='no desc')
        if len(rec)==0:
            seq='0001'
        else:
            seq=str(int(rec['no'][-4:])+1).zfill(4)
        no+=seq

#            no=self.env['ir.sequence'].next_by_code('sis.shipment.ati1.seq')
        
        values.update({'no':no,'draft':datetime.now()}) 
        res_id = super(sis_shipment_header, self).create(values)
        return res_id

    @api.multi
    def write(self, vals):
        if self.status =='stuffed':
            for v in vals:
                if v not in ['status','uploadremark','nav']:
                    raise UserError('Cannot update this data')                     
        if self.status in ['nav']:
            for v in vals:
                if v not in ['error','shipmentno','uploadremark','newsh']:
                    raise UserError('Cannot update this data')                     

        return models.Model.write(self, vals)

    @api.multi
    def unlink(self):
        if self.status not in ['draft']:
            raise UserError('PL must be in draft')        
        return models.Model.unlink(self)

    @api.onchange('sono')
    def _compute_header(self):
        if self.sono:
            self.env.cr.execute("select postingdate,selltono,selltoname,shiptoname, discharging_port, extdocno,bg "+\
                        "from sis_so_header where no_='"+self.sono+"'")
            sos=self.env.cr.fetchall()
            if sos==False or len(sos)==0:
                raise UserError('Sales Order '+self.no+' does not exist')
            for so in sos:
                (postingdate,selltono,selltoname,shiptoname, discharging_port,extdocno,bg)=so
                self.posting_date=postingdate
                self.selltono=selltono
                self.selltoname=selltoname
                self.discharhing_port=discharging_port
                self.shiptoname=shiptoname
                self.extdocno=extdocno
                self.bg=bg

    def update_status_from_NAV(self):
        self.env.cr.execute(" update sis_shipment_header set newsh=False")

        self.env.cr.execute(" select distinct plno, shipmentno, error, realshipno "+\
                    " from sis_shipment_checking where shipmentno<>'' or error<>''")
        scs=self.env.cr.fetchall()
        for sc in scs:
            (plno,shipmentno,error,realshipno)=sc
            recs=self.env['sis.shipment.header'].search([('no','=',plno)])
            for rec in recs:
                vals={}
                if len(error)>0 and rec.error!=error:
                    vals.update({'error':error})
                if len(shipmentno)>0 and rec.shipmentno!=shipmentno:
                    vals.update({'shipmentno':shipmentno})
                if realshipno and len(realshipno)>0: 
                    vals.update({'newsh':True})
                if len(vals)>0:
                    rec.write(vals)
                    
    #def upload_to_NAV(self):
        no=0
        recs=self.env['sis.shipment.detail'].search([('status','=','stuffed')],order='plno')
        if len(recs)>0:
            conn = pyodbc.connect(SQLCONN)
            cursor = conn.cursor()
            plno='first'
        wasrec=False
        for rec in recs:
            if plno!=rec.plno and plno!='first':            
                wasrec.header_id.status='nav'

            upd=True
            self.env.cr.execute(" select count('A') "+\
                        " from sis_shipment_checking where plno='"+rec.plno+"' "+\
                        " and entryno="+str(rec.entryno)+"")
            scs=self.env.cr.fetchall()
            for sc in scs:
                (num,)=sc
                if num>0:
                    upd=False
            if upd==True:
                variant=rec.variant
                if rec.variant==None:
                    variant=""
                try:
#                     row=cursor.execute(" INSERT INTO [PT_ Aneka Tuna Indonesia$Shipment Checking]([PL No_],[Sales Order No_],[Sales Order Line No_],[Item Ledger Entry No_],[Container No_],[Item No_],[Variant Code],[Quantity],[Error],[Whs_ Shipment No_],[isGet],[is Error]) "+\
#                                        " VALUES('"+rec.plno+"','"+rec.sono+"',"+str(rec.solineno)+","+str(rec.entryno)+",'"+rec.containerno+"','"+rec.itemno+"','"+variant+"',"+str(rec.qtyact)+",'','',0,0)")

                    row=cursor.execute(" INSERT INTO [PT_ Aneka Tuna Indonesia$Shipment Checking]([Document Type],[Order No_],"+\
                                       " [Item Ledger Entry No_],[Container No_],[Line No_],[Component Line No_],[Variant Code]"+\
                                       ",[Item No_],[Quantity],[isGet],[Error],[Whs_ Shipment No_],[is Error],[PL No_],[Finished],[Remaining Qty_],[Finished Qty]"+\
                                       ",[Journal Batch Name]) "+\
                                       " VALUES(0,'"+rec.sono+"',"+\
                                       str(rec.entryno)+",'"+rec.containerno+"','"+str(rec.solineno)+"',0,'"+variant+"','"+\
                                       rec.itemno+"',"+str(rec.qtyact)+",0,'','',0,'"+rec.plno+"',0,0,0,'')")                
                    print(row)
                except:
                    pass
                if row.rowcount==0:
                    rec.error='Failed to update NAV, please try again later'
                else:                
                    no+=1
            wasrec=rec
            plno=rec.plno            
        if no>0:
            conn.commit()           
            wasrec.header_id.status='nav'            


   
class sis_shipment_detail(models.Model):
    _name='sis.shipment.detail'
        
    header_id=fields.Many2one('sis.shipment.header')
    plno=fields.Char(related='header_id.no',string='PL No.',store=True)
    sono=fields.Char(related='header_id.sono',string='SO No.',store=True)
    solineno=fields.Integer(related='header_id.solineno',string='SO Line No.',store=True)
    containerno=fields.Char(related='header_id.containerno',string='Container No.',store=True)
    postingdate=fields.Date(related='header_id.postingdate',string='Posting Date',store=True)
    status=fields.Selection(related='header_id.status',string='PL No.',store=True)    
    discharging_port=fields.Char(related='header_id.discharging_port',string='Discharging Port',store=True)
        
    lineno = fields.Integer(string='Line No')
    bin=fields.Char(size=10, string='Bin')
    entryno = fields.Integer(string='Entry No')
    itemno =fields.Char(size=20,string="Item No") 
    description =fields.Char(size=200,string="Description")
    variant=fields.Char(size=20,string="Variant")
    location =fields.Char(size=10,string="Location Code")
    quantity =fields.Float(string="Quantity")
    qtyincase =fields.Float(string="Qty/C",compute='_compute_qtyincase')
    qtyact =fields.Float(string="Qty Actual")
    qtyactincase =fields.Float(string="Qty.Act/C",compute='_compute_qtyactincase')    
    remaining_quantity =fields.Float(string="Remaining Quantity")
    remqtyact =fields.Float(string="Rem.Qty.Act")
    planlotno =fields.Char(size=50,string="Plan.Lot No")
    actlotno =fields.Char(size=50,string="Act.Lot No")
    newlotno =fields.Char(size=50,string="NEW Lot No")
    stufflotno =fields.Char(size=50,string="Stuff.Lot No")
    nodata=fields.Boolean(string="NoDt",default=False)
    stuffed=fields.Boolean(compute='_compute_stuffed',string="Stf",default=False)
    nobasket =fields.Char(size=50,string="No Basket")
    nocontract =fields.Char(size=50,string="No Contract")
    inkjetprint =fields.Char(size=50,string="Inkjet Print")    
    proddate =fields.Char(size=10,string="Prod.Date")    
    warning=fields.Char(size=100,string="Warning\nLocal")    
    warningati=fields.Char(size=100,string="Warning\nATI")    

    @api.one
    @api.depends('quantity')
    def _compute_qtyincase(self):
        if self.itemno==False or len(self.itemno)==0:
            return
        if self.variant!=False and len(self.variant)>0:
            its=self.env['sis.item.variants.local'].search([('itemno','=',self.itemno),('variant','=',self.variant)])
            if len(its)==0:
                raise UserError('ERROR: Item on SO does not exist on NAV Item Master (5)')            
        else:
            its=self.env['sis.items.local'].search([('itemno','=',self.itemno)])
            if len(its)==0:
                raise UserError('ERROR: Item on SO does not exist on NAV Item Master (6)')
        #pgcm=self.env['sis.pgc.case48'].search([('pgc','=',pgc)])
        #if len(pgcm)==0:
        for it in its:
            qty=self.quantity-int(self.quantity/it.qtyperuom)*it.qtyperuom
            qty/=100
            qty+=int(self.quantity/it.qtyperuom)
            self.qtyincase=qty

    @api.one
    @api.depends('qtyact')    
    def _compute_qtyactincase(self):
        if self.itemno==False or len(self.itemno)==0:
            return
        if self.variant!=False and len(self.variant)>0:
            its=self.env['sis.item.variants.local'].search([('itemno','=',self.itemno),('variant','=',self.variant)])
            if len(its)==0:
                raise UserError('ERROR: Item on SO does not exist on NAV Item Master(7)')            
        else:
            its=self.env['sis.items.local'].search([('itemno','=',self.itemno)])
            if len(its)==0:
                raise UserError('ERROR: Item on SO does not exist on NAV Item Master (8)')

        for it in its:
            qty=self.qtyact-int(self.qtyact/it.qtyperuom)*it.qtyperuom
            qty/=100
            qty+=int(self.qtyact/it.qtyperuom)
            self.qtyactincase=qty

    def move(self):
        return {
                'name': 'Move Line',
                'res_model': 'sis.move.line',
                'type': 'ir.actions.act_window',
                'context': {'source_line':self.id},
                'view_mode': 'form',
                'view_type': 'form',
                'view_id': self.env.ref('sis_goods_bin.sis_move_line_form').id,
                'target': 'new',
                'nodestroy':True
            }  
    
    
    @api.model
    def create(self, values):
        ss=self.env['sis.shipment.header'].browse([values['header_id']])
        for s in ss:
            if s.status in ['nav','canceled','confirmed','stuffed']:
                raise UserError('Cannot update this data') 
        res_id = super(sis_shipment_detail, self).create(values)
        return res_id

    @api.multi
    def write(self, vals):
        for s in self:
            try:
                vals['newlotno']
                raise UserError('Cannot update this data') 
            except:
                if s.status in ['nav','canceled']:
                    raise UserError('Cannot update this data') 
        return models.Model.write(self, vals)

    @api.multi
    def unlink(self):
        for s in self:
            if s.status in ['nav','canceled','confirmed','stuffed']:
                raise UserError('Cannot update this data') 
        return models.Model.unlink(self)

    @api.one
    @api.depends('stufflotno')
    def _compute_stuffed(self):
        if self.stufflotno and len(self.stufflotno)>0:
            self.stuffed=True
        else:
            self.stuffed=False            
    
    @api.one
    @api.constrains('itemno','variant')
    def _constrain_no_outside_so(self):
        if self.sono:
            self.env.cr.execute(" select count('A') "+\
                                " from sis_so_line where docno='"+self.sono+"' and itemno='"+self.itemno+"' and variant='"+self.variant+"'")
            sls=self.env.cr.fetchall()
            if len(sls)==0:
                raise UserError('ERROR: Item not in SO')

    
    @api.one
    @api.constrains('plno','planlotno','actlotno','newlotno')
    def _constrain_no_duplicate(self):
        if self.plno and self.plno!='':
            if self.planlotno and self.planlotno!='':
                if self.search_count([('plno','=',self.plno),('planlotno','=',self.planlotno),('id','!=',self.id)])>0:
                    raise UserError('No same Planned Lot No '+self.planlotno+'in one PL')
            if self.actlotno and self.actlotno!='':
                if self.search_count([('plno','=',self.plno),('actlotno','=',self.actlotno),('id','!=',self.id)])>0:
                    raise UserError('No same Actual Lot No '+self.actlotno+' in one PL')
            if self.newlotno and self.newlotno!='':
                if self.search_count([('plno','=',self.plno),('newlotno','=',self.newlotno),('id','!=',self.id)])>0:
                    raise UserError('No same New Lot No '+self.newlotno+' in one PL')


class sis_shipment_proddate(models.Model):
    _name='sis.shipment.proddate'
        
    header_id=fields.Many2one('sis.shipment.header')
    description=fields.Char(string='Item')
    proddate=fields.Char(string='Prod.Date')
    qtyincase=fields.Float(string='Qty/Cs')    
    qtyindec=fields.Float(string='Qty Dec.')    

class sis_move_line(models.TransientModel):
    _name='sis.move.line'
        
    lineno =fields.Integer(string="Line No") 

    def move(self):
        try:
            source_id=self._context['source_line']
        except:
            raise UserError('Source line error')
        s=self.env['sis.shipment.detail'].search([('id','=',source_id)])
        if s.nodata==False:
            raise UserError('Only No Data (NoDt) item can move ')            
        d=self.env['sis.shipment.detail'].search([('header_id','=',s.header_id.id),('lineno','=',self.lineno)])
        if len(d)!=1:
            raise UserError('No detail with line number '+str(d.lineno))
        if d.actlotno and d.actlotno!='':
            raise UserError('Destination already has actual lot : '+d.actlotno)            
        self.env.cr.execute("select item_no,variant,proddate "+\
                    "from sis_temp_ile_rawfg where quantity>0 and lot_no='"+s.actlotno+"'")
        item=self.env.cr.fetchall()
#         if len(item)==0:
#             raise UserError('Lot not found')                      
#         if len(item)>2:
#             raise UserError('Multiple lot not found')                      
        if len(item)==1:
            [(itemno,variant,proddate)]=item
            if d.itemno!=itemno or d.variant!=variant :#or d.proddate!=proddate :
                raise UserError('Item, variant, prod.date must match')          
        vals={'actlotno':s.actlotno,
              'newlotno':s.actlotno,
              'qtyact':s.qtyact,
              'nodata':s.nodata}
        s.unlink()
        d.write(vals)
        
    
class sis_forklift_scan(models.TransientModel):
    _name='sis.forklift.scan'
    
    plno =fields.Char(size=20,string="PL No")
    lotno =fields.Char(size=50,string="Lot No")
    qtyact=fields.Float(string="Qty Actual")  
    valid =fields.Boolean(string='in PL',compute='_compute_valid',default=False)
    qtyperuom =fields.Integer(string='Qty/Case',default=0)
    numscan=fields.Integer(string='# Scan',default=0)
    stagingbin =fields.Char(size=20,string="Staging Bin")

    
    @api.onchange("plno","lotno")
    def _onchange_qtyact(self):
        if self.plno and self.plno!='' :

            self.numscan=self.env['sis.shipment.detail'].search_count([('plno','=',self.plno),'|',('actlotno','!=',None),('actlotno','!=','')])

            if self.lotno and self.lotno!='':
                num=self.env['sis.shipment.detail'].search([('status','!=','canceled'),('status','!=','nav'),('actlotno','=',self.lotno),('plno','!=',self.plno)])
                if len(num)>0:
                    for n in num:
                        if n.qtyact==n.remaining_quantity:
                            raise UserError('ERROR:This lot already used in '+n.plno)

                num=self.env['sis.shipment.detail'].search([('status','!=','canceled'),('plno','!=',self.plno),('planlotno','=',self.lotno)])
                if len(num)>0:
                    for n in num:
                        num.error='Planned for '+n.plno

                
                iles=self.env['sis.temp.ile.remaining.quantity'].search([('lot_no','=',self.lotno)])
                if len(iles)==1:
                    if iles.variant!=False and len(iles.variant)>0:
                        its=self.env['sis.item.variants.local'].search([('itemno','=',iles.item_no),('variant','=',iles.variant)])
                        if len(its)==0:
                            raise UserError('ERROR: '+iles.description+'not in NAV Item Master')
                    else:
                        its=self.env['sis.items.local'].search([('itemno','=',iles.item_no)])
                        if len(its)==0:
                            raise UserError('ERROR: '+iles.description+'not in NAV Item Master')
                    for it in its:
                        self.qtyperuom=it.qtyperuom                    
                        qtyact=iles.remaining_quantity-int(iles.remaining_quantity/it.qtyperuom)*it.qtyperuom
                        qtyact/=100
                        qtyact+=int(iles.remaining_quantity/it.qtyperuom)
                        self.qtyact=qtyact
                        pass

    @api.depends('plno','lotno')
    def _compute_valid(self):
        if self.plno==False or self.lotno==False or self.plno=='' or self.lotno=='':
            return
        head=self.env['sis.shipment.header'].search([('no','=',self.plno)])
        if len(head)==0:
            raise UserError('PL Not found')
        if head.status!='released':
            raise UserError('PL must be released')                

        recs=self.env['sis.shipment.detail'].search([('header_id','=',head.id),('planlotno','=',self.lotno)])
        if len(recs)>0:
            self.valid=True

    def check_proddate(self,complete):
        if not complete:        
            p = re.findall(r'\d{8}',self.lotno)
            if len(p)==0:
                raise UserError('No Production date in Lot!!')                
            for nom in  p:
                proddate=nom
#             num=self.env['sis.shipment.detail'].search_count([('plno','=',self.plno),('proddate','=',proddate)])
#             if num==0:
#                 raise UserError('ERROR: Prod.Date outside PL')


    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        complete=False
        try:
            plno=vals['plno']
            if vals['plno'][-1:]=='#':
                vals.update({'plno':vals['plno'][:-1]})
                complete=True
        except:
            pass
        rec=models.TransientModel.create(self, vals)
        rec.check_proddate(complete)
        if complete==False:
            rec.write_shipment()
        return rec   
     
    @api.multi
    def write(self, vals):
        raise UserError('ERROR: No Edit')
        return models.TransientModel.write(self, vals)
   
    def write_shipment(self):
        if self.plno==False or self.lotno==False or self.plno=='' or self.lotno=='' or self.qtyact==0:
            raise UserError('ERROR: Cannot save, No PL / No Lot / No Qty')
        head=self.env['sis.shipment.header'].search([('no','=',self.plno)])
        if len(head)==0:
            raise UserError('PL Not found')
        if head.status!='released':
            raise UserError('PL must be released')                

        ln=self.env['sis.shipment.detail'].search([('header_id','=',head.id)],order='lineno desc',limit=1)
        if len(ln)==0:
            lineno=10000
        else:
            lineno=ln.lineno+10000

        rs=False
        iles=self.env['sis.temp.ile.remaining.quantity'].search([('lot_no','=',self.lotno)])
        if len(iles)==0:
            rs=self.env['sis.goods.bin'].search([('lot_no','=',self.lotno)],order='create_date desc',limit=1)
            if len(rs):
                iles=self.env['sis.temp.ile.remaining.quantity'].search([('id','=',rs.entry_no)])
                if len(iles)==0:                
                    vals={'header_id':head.id,
                          'lineno':lineno,
                          'actlotno':self.lotno}
                    self.env['sis.shipment.detail'].create(vals)                    
        if len(iles)>1:
            raise UserError('Double lot no!')

        qtyperuom=self.qtyperuom
        if self.lotno and self.lotno!='':
            iles=self.env['sis.temp.ile.remaining.quantity'].search([('lot_no','=',self.lotno)])
            if len(iles)==1:
                if iles.variant!=False and len(iles.variant)>0:
                    its=self.env['sis.item.variants.local'].search([('itemno','=',iles.item_no),('variant','=',iles.variant)])
                    if len(its)==0:
                        raise UserError('ERROR: '+iles.description+'not in NAV Item Master')
                else:
                    its=self.env['sis.items.local'].search([('itemno','=',iles.item_no)])
                    if len(its)==0:
                        raise UserError('ERROR: '+iles.description+'not in NAV Item Master')
                for it in its:
                    qtyperuom=it.qtyperuom

        
        recs=self.env['sis.shipment.detail'].search([('header_id','=',head.id),'|',('planlotno','=',self.lotno),('actlotno','=',self.lotno)])
        if not recs or len(recs)==0:
            p = re.findall(r'\d{8}',self.lotno)
            if len(p)==0:
                raise UserError('No Production date in Lot!')                
            for nom in  p:
                proddate=nom
            vals={'header_id':head.id,
                  'nodata':True,
                  'actlotno':self.lotno,
                  'newlotno':self.lotno,
                  'proddate':proddate}

 
                
            ibin=self.env['sis.goods.bin'].search([('entry_no','=',iles.id),('next_id','=',None),('out','=',False)])
            if len(ibin)>0:
                binloc=ibin.bin
            else:
                binloc=''
            qtyactcan=int(int(self.qtyact)*qtyperuom+round((self.qtyact-int(self.qtyact))*100))
            warning=''
            if iles.remaining_quantity<qtyactcan:
                warning='Qty Act LARGER than NAV remaining quantity'
            if len(iles)==1:
                vals.update({'nodata':False,
                  'entryno':iles.id,
                  'itemno':iles.item_no,
                  'description':iles.description,
                  'variant':iles.variant,
                  'location':iles.location_code,
                  'qtyact':qtyactcan,
                  'remqtyact':iles.remaining_quantity,
                  'nobasket':iles.no_basket,
                  'nocontract':iles.no_contract,
                  'inkjetprint':iles.inkjet_print,
                  'proddate':iles.proddate})

            vals.update({'lineno':lineno,
                  'bin':binloc,
                  'warning':warning,
                  'qtyact':qtyactcan})
 
            self.env['sis.shipment.detail'].create(vals)
        else:
            qtyactcan=int(int(self.qtyact)*qtyperuom+round((self.qtyact-int(self.qtyact))*100))
            warning=''
            if iles.remaining_quantity<qtyactcan:
                warning='Qty Act LARGER than NAV remaining quantity'          
            vals={'actlotno':self.lotno,
                'newlotno':self.lotno,
                'qtyact':qtyactcan,
                'warning':warning,
                'remqtyact':iles.remaining_quantity}
            recs.write(vals)
        
    def complete(self):
        head=self.env['sis.shipment.header'].search([('no','=',self.plno)])
        if len(head)==0:
            raise UserError('PL Not found')
        if head.status!='released':
            raise UserError('PL must be released')
        
        if self.stagingbin and len(self.stagingbin)>0:
            r=self.env['sis.bin'].search([('code','=',self.stagingbin)])
            if len(r)==1:
                self.bin_no=r.name
            else:
                raise UserError ('Staging Bin Error !')
        else:
            raise UserError ('Staging Bin Error !')
            
        for d in head.detail_id:
            if d.actlotno==False or d.actlotno==self.stagingbin or len(d.actlotno)<1:
                continue
            d.bin=self.stagingbin
            self.env['sis.goods.bin'].search([('entry_no','=',d.entryno)]).bin=self.stagingbin
            
#             vals={'ile':d.actlotno,
#                   'bin':self.stagingbin}
#             self.env['sis.goods.bin'].create(vals)           
            
        head.status='picked'
        
class sis_stuffing_scan(models.TransientModel):
    _name='sis.stuffing.scan'
    
    plno =fields.Char(size=20,string="PL No")
    lotno =fields.Char(size=50,string="Lot No")
    valid =fields.Boolean(string='in PL',compute='_compute_valid',default=False)
    numscan=fields.Integer(string='# Scan',default=0)
    numline=fields.Integer(string='# Line',default=0)        
    qtyact=fields.Float(string="Qty Actual") 

    @api.onchange('plno')
    def _onchange_plno(self):
        if self.plno and len(self.plno)>0:
            self.numscan=self.env['sis.shipment.detail'].search_count([('plno','=',self.plno),('stufflotno','!=',None),('stufflotno','!=','')])
            self.numline=self.env['sis.shipment.detail'].search_count([('plno','=',self.plno)])
    
    
    @api.one
    @api.depends('plno','lotno')
    def _compute_valid(self):
        if self.plno and len(self.plno)>0 and self.lotno and len(self.lotno)>0:
                recs=self.env['sis.shipment.detail'].search([('plno','=',self.plno),'|',('actlotno','=',self.lotno),('newlotno','=',self.lotno)])
                if not recs or len(recs)==0:
                    raise UserError('ERROR: Not valid lot for '+self.plno)
                else:
                    if recs.header_id.status!='confirmed':
                        raise UserError('PL must be confirmed')
                    vals={'stufflotno':self.lotno}
                    recs.write(vals)
                    self.valid=True
                    self.qtyact=recs.qtyactincase
                        
    def complete(self):
        head=self.env['sis.shipment.header'].search([('no','=',self.plno)])
        if len(head)==0:
            raise UserError('PL Not found')
        if head.status!='stuffed':
            if head.status!='confirmed':
                raise UserError('PL must be confirmed')
            for d in head.detail_id:
                if d.stuffed==False:
                    raise UserError('Not stuffed yet '+d.description+' lot '+d.actlotno)                   
            head.status='stuffed'
        #self.upload_to_NAV()
