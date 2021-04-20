import re
from odoo import models, fields, api, tools
from odoo.exceptions import UserError
from datetime import datetime

class sis_thawing_header(models.Model):
    _inherit    = ['mail.thread']
    _name       ='sis.defrost.header'
    _rec_name    ='defrost_id'
    _order      ='tgl_produksi desc'

    defrost_id      = fields.Char(string="Defrost ID", size=16, default='/')
    tgl_produksi    = fields.Date(string="Tanggal Produksi",required=True, default=fields.Datetime.now)
    pabrik_id       = fields.Char(string="Lokasi", size=4, compute="_get_pabrik_id", store=True)
    nopotong_header = fields.Char(string="No Potong", compute="get_nopotong", store=True)
    defrost_state   = fields.Selection([('draft','Draft'),('confirm','Confirmed')], string='State', default='draft')
    user_checker = fields.Boolean(string="Checker", compute="_checker")
    user_unchecker = fields.Boolean(string="Unchecker", compute="_unchecker")
    defrost_detail  = fields.One2many('sis.defrost.detail', 'detail_id', string='Detail ID')
    header_status = fields.Boolean(string="status", default=0)

    @api.one
    def get_nopotong(self):
        xnopotong=""
        for xdetail in self.defrost_detail:
            if xdetail.no_potong:
                if xnopotong=="":
                    xnopotong=str(xdetail.no_potong)
                    temp = xdetail.no_potong
                else:
                    if temp != xdetail.no_potong:                        
                        temp = xdetail.no_potong
                        xnopotong=xnopotong+", "+str(xdetail.no_potong)
        self.nopotong_header=xnopotong
        
    @api.depends('tgl_produksi')
    def _checker(self):
        self.user_checker=False

        xuid = self.env.uid
        cSQL1="select d.checker from hr_employee as a, res_users as b, res_partner as c, hr_employee as d "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id and d.name=c.name " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_check=self.env.cr.fetchall()
        if len(rc_check)==0:
            self.user_checker=False
        else:
            for cs_checker in rc_check:
                    (xchecker,)=cs_checker
            self.user_checker=xchecker
                
                
    @api.depends('tgl_produksi')
    def _unchecker(self):
        xuid = self.env.uid
        cSQL1="select d.unchecker from hr_employee as a, res_users as b, res_partner as c, hr_employee as d "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id and d.name=c.name " 
     
        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_uncheck=self.env.cr.fetchall()
        if len(rc_uncheck)==0:
            self.user_unchecker=False
        else:
            for cs_unchecker in rc_uncheck:
                (xunchecker,)=cs_unchecker
            self.user_unchecker=xunchecker

    @api.one
    @api.depends('tgl_produksi')
    def _get_pabrik_id(self):
        if self.tgl_produksi:
            xuid = self.env.uid
            cSQL1="select a.pabrik_id from hr_employee as a, res_users as b, res_partner as c "
            cSQL2="where c.id=b.partner_id and a.address_id=c.id " 
    
            self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
            rc_lokasi=self.env.cr.fetchall()
            
            for def_lokasi in rc_lokasi:
                (xpabrik_id,)=def_lokasi
            
            self.pabrik_id=xpabrik_id
        
        
    @api.model
    def _get_tgl_produksi(self):
        lst_tglprod=list()
        
        cSQL1="select distinct a.tgl_produksi from sis_fish_status_header as a, sis_cs_detail as b, sis_fish_status as c "
        cSQL2="where b.status_id=a.id and c.barcode_no=b.barcode_no and (c.quantity-b.quantity)>0"
        self.env.cr.execute(cSQL1+cSQL2)
        rc_tglprod=self.env.cr.fetchall()
        
        if len(rc_tglprod)==0:
            raise UserError("Tanggal Produksi belum diinput!")
        else:
            for def_tglprod in rc_tglprod:
                (xtglprod,)=def_tglprod
                lst_tglprod.append((xtglprod, xtglprod))
            
            return lst_tglprod
            
    def _get_defrost_id(self,pabrik):
        if pabrik:
            tanggal=datetime.now()
            d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
            d_tahun = d_to.year
            d_bulan=""
            no_prefix=""
            if d_to.month<10 :
                d_bulan="0"+str(d_to.month)
            else :
                d_bulan=str(d_to.month)
         
            if pabrik=="ATI1":
                no_prefix = "DEF1/"+str(d_tahun)+str(d_bulan)+"-"
            elif pabrik=="ATI2":
                no_prefix = "DEF2/"+str(d_tahun)+str(d_bulan)+"-"
 
            rec=self.env['sis.defrost.header'].search([('defrost_id','ilike',no_prefix)])
            if len(rec)>0:
                self.env.cr.execute("select max(cast(substring(defrost_id,13,4) as integer)) from sis_defrost_header where defrost_id like '"+no_prefix+"%'")
                rc=self.env.cr.fetchall()
                  
                for def_max in rc :
                    (x,)=def_max
                
                no_urut=x+1
                if no_urut<10:
                    defros_id=no_prefix+"000"+str(no_urut)
                elif no_urut>9 and no_urut<100:
                    defros_id=no_prefix+"00"+str(no_urut)
                elif no_urut>999 and no_urut<1000:
                    defros_id=no_prefix+"0"+str(no_urut)
                else:
                    defros_id=no_prefix+str(no_urut)
            else:
                no_urut=1
                defros_id=no_prefix+"000"+str(no_urut)
 
            return defros_id

    @api.model
    def create(self,vals):
        xpabrik_id, xsection_id=self._get_save_pabrik_id()
        
        z=self._get_save_barcode(vals['tgl_produksi'],xpabrik_id)
        if z==True:
            if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":
                no_defrost=self._get_defrost_id(xpabrik_id)
                vals.update({'defrost_id':no_defrost})
                
#                 self._get_nopotong()
                
                res_id = models.Model.create(self, vals)
                return res_id
            else:
                raise UserError("Unauthorized User!")
        else:
            raise UserError("Data CS pada tanggal Produksi "+vals['tgl_produksi']+" tidak ada/sudah diinput ke defrost")

    @api.multi
    def write(self, vals):
        for me_id in self :
            xpabrik_id, xsection_id=self._get_save_pabrik_id()
            if xpabrik_id==self.pabrik_id:
                if xsection_id=="Admin" or xsection_id=="Prod1" or xsection_id=="CSD" or xsection_id=="Defrost":  
                    if me_id.defrost_state != 'draft' :
                        if vals.get('defrost_state') and vals['defrost_state']=='draft':
                            return super(sis_thawing_header, self).write(vals)
                        else:
                            raise UserError("Cannot update!")
                    else:
                        vals_defrost={}
                    
                        if vals.get('tgl_produksi'):
                            if vals.get('tgl_produksi')!=self.tgl_produksi:
                                raise UserError("Tgl. Produksi : "+self.tgl_produksi+" can not update!")
                        if vals.get('shift'):
                            vals_defrost.update({'shift':vals['shift']})
                        if vals.get('tgl_start'):             
                            vals_defrost.update({'tgl_start':vals['tgl_start']})
                        if vals.get('tgl_finish'):             
                            vals_defrost.update({'tgl_finish':vals['tgl_finish']})
                    
                        cr_data=self.env['sis.defrost.header'].search([('defrost_id','=',self.defrost_id)])
                        if len(cr_data)>0:
                            xdef_id=cr_data.id
                                
                        cr_data2=self.env['sis.defrost.detail'].search([('detail_id','=',xdef_id)])
                        if len(cr_data2)>0:
                            for x in cr_data2:
                                x.write(vals_defrost)
                    
                        return super(sis_thawing_header, self).write(vals)
                else:
                    raise UserError("Unauthorized User!")
            else:
                raise UserError("Data "+self.pabrik_id+" tidak bisa di edit oleh user "+xpabrik_id)
    
    @api.multi
    def unlink(self):
        for me_id in self :
            if me_id.defrost_state != 'draft' :
                raise UserError("Cannot delete!")
            else:
                rs=self.env['sis.defrost.detail'].search([('detail_id','=',me_id.id)])
                for defrost in rs:
                    defrost.unlink()
                
                return super(sis_thawing_header, self).unlink()

    @api.multi
    def action_confirm(self):
        for me_id in self :
            if me_id.defrost_state == 'draft':
                me_id.write({'defrost_state':'confirm'})
     
    @api.multi
    def action_unconfirm(self):
        for me_id in self :
            if me_id.defrost_state == 'confirm':
                me_id.write({'defrost_state':'draft'})


    def _get_save_pabrik_id(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id, a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
        
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
        
        return xpabrik_id,xsection_id

    def _get_save_barcode(self, tgl_produksi, pabrik_id):
        cSQL1="select distinct a.barcode_no, a.no_potong, a.fish_box_no, a.quantity, a.tgl_keluar, a.hatch_no "
        cSQL2="from sis_cs_detail a left join sis_defrost_detail b on b.barcode_no=a.barcode_no and b.quantity=a.quantity "
        cSQL3="where b.no_tangki is null and b.quantity is null and a.tgl_produksi='"+tgl_produksi+"' and a.pabrik_id='"+pabrik_id+"'"
        self.env.cr.execute(cSQL1+cSQL2+cSQL3)
        the_barcode=self.env.cr.fetchall()
        if len(the_barcode)==0:
            return False
        else:
            return True
    
    def get_barcode(self):
        if self.tgl_produksi:
            cSQL1="""select distinct cs.id, cs.barcode_no, cs.no_potong, cs.fish_box_no, cs.quantity, cs.tgl_keluar, cs.hatch_no from sis_cs_detail as cs 
                    left join sis_defrost_detail as def on def.defrost_link_id=cs.id
                    where cs.tgl_produksi='"""+self.tgl_produksi+"' and def.id is null and cs.pabrik_id='"+self.pabrik_id+"' and cs.real_itemno not like '%L' and cs.real_itemno not like '%F'"
            self.env.cr.execute(cSQL1)
            the_barcode=self.env.cr.fetchall()
            if len(the_barcode)>0:
                new_lines = self.env['sis.defrost.detail']
                for ff_data in the_barcode:
                    (xid,xbarcode,xnopotong,xfish_box_no,xquantity, xtgl_keluar, xhatch)=ff_data
                    if xhatch[-3:]=="P&L":
                        xstatus_pl=True
                    else:
                        xstatus_pl=False
                    if xhatch[-3:]=="P&L":
                        xstatus_pl=True
                    else:
                        xstatus_pl=False
                     
                    vals = {'defrost_link_id': xid,
                            'barcode_no'    : xbarcode,
                            'tgl_keluar'    : xtgl_keluar,
                            'quantity'      : xquantity,
                            'no_potong'     : xnopotong,
                            'fish_box_no'   : xfish_box_no,
                            'no_tangki'     : "-",
                            'suhu_before'   : 0,
                            'suhu_after'    : 0,
                            'tgl_produksi'  : self.tgl_produksi,
                            'pabrik_id'     : self.pabrik_id,
                            'hatch_no'      : xhatch,
                            'status_pl'     : xstatus_pl,
                            'detail_id'     : self.id
                            }
                    new_lines += new_lines.new(vals)
                    print(new_lines.new(vals))
                self.defrost_detail = new_lines
                self.header_status = 1
                self.get_nopotong()

class sis_thawing_detail(models.Model):
    _name='sis.defrost.detail'
    _rec_name    ='no_tangki'
    _order      ='no_potong, barcode_no'

    detail_id       = fields.Many2one('sis.defrost.header', string="Detail ID")
    defrost_link_id = fields.Many2one('sis.cs.detail', string="Defrost Link ID")
    tangki_cut      = fields.One2many('sis.cutting.tangki', 'rel_defrost', string='Tangki')
    
    
    tgl_produksi    = fields.Date(string="Tanggal Produksi")
    pabrik_id       = fields.Selection(string="Lokasi", selection=[('ATI1', 'ATI1'),('ATI2', 'ATI2')])
    fresh_fish      = fields.Selection(string="Fish Type", selection=[(True, 'Fresh'),(False, 'Frozen')])
    tgl_keluar      = fields.Datetime(string="Tanggal Keluar CS")
    barcode_no      = fields.Char(string="Barcode No",size=40,required=True)
    no_tangki       = fields.Char(string="No. Tangki", size=7, required=True)
    no_line         = fields.Char(string="No. Line", default=' ')
    no_potong       = fields.Integer(related="defrost_link_id.no_potong",string="No. Potong", store=True)
    fish_box_no     = fields.Char(size=20,string="Fish Box No.",store=True)
    hatch_no        = fields.Char(size=100,string="Hatch No.")
    quantity        = fields.Float(compute="update_qty_cs",string='Quantity',store=True)
    suhu_before     = fields.Float(string="Suhu Before", required=True, default=100)     
    tgl_start       = fields.Datetime(string="Tanggal Mulai", default=fields.Datetime.now, required=True)
    suhu_after      = fields.Float(string="Suhu Before", required=True, default=100)     
    tgl_finish      = fields.Datetime(string="Tanggal Selesai", default=fields.Datetime.now, required=True)
    tgl_tuang       = fields.Datetime(string="Tanggal Tuang Hoper", default=fields.Datetime.now, required=True)
    remark          = fields.Char(string="Remark",size=100, default='-', required=True)
    durasi_jam      = fields.Float(string="Durasi", compute="_get_durasi", store=True)
    status_pl       = fields.Boolean(string="Pole & Line")
    status_input    = fields.Boolean(string="Status Input", default=True)
    jenis_ikan      = fields.Char('Jenis Ikan', compute='_get_jenis_ikan', store=True)
    ukuran_ikan      = fields.Char('Ukuran Ikan', compute='_get_ukuran_ikan', store=True)
    
    @api.one
    @api.depends('defrost_link_id.product_group_code')
    def _get_jenis_ikan(self):
        if self.defrost_link_id.product_group_code:
            self.jenis_ikan = self.defrost_link_id.product_group_code  
              
    @api.one
    @api.depends('defrost_link_id.real_item_no')
    def _get_ukuran_ikan(self):
        if self.defrost_link_id.real_item_no:
            self.ukuran_ikan = self.defrost_link_id.real_item_no
    
    @api.one
    @api.depends('tgl_keluar','tgl_finish')
    def _get_durasi(self):
        if self.tgl_keluar and self.tgl_tuang:
            t1 = datetime.strptime(self.tgl_keluar, "%Y-%m-%d %H:%M:%S")
            t2 = datetime.strptime(self.tgl_finish, "%Y-%m-%d %H:%M:%S")
            if t2 > t1:
                t3 = t2-t1
            else:
                t3 = t1 - t2
             
            self.durasi_jam = float(t3.days) * 24 + (float(t3.seconds) / 3600)

    @api.onchange('barcode_no')
    def onchange_barcode_no(self):
        if self.barcode_no:
            rec=self.env['sis.cs.detail'].search([('barcode_no','=',self.barcode_no),('no_potong','=',self.no_potong),('tgl_produksi','=',self.detail_id.tgl_produksi)])
            if len(rec)==0:
                raise UserError("Barcode : "+self.barcode_no+" tidak untuk Tanggal Produksi "+self.detail_id.tgl_produksi)
            

    @api.onchange('tgl_produksi')
    def onchange_defrost_line(self):
        domain = []
        domain.append(('tgl_produksi','=',self.detail_id.tgl_produksi))
        return {'domain':{'defrost_link_id':domain}}


    @api.onchange('no_tangki')
    def regexnotangki(self):
        if self.no_tangki:
            regex = '^[0-9]*$'
            if(re.search(regex, self.no_tangki)):
                exit 
            else:
                raise UserError('No Tangki harus menggunakan Angka')
            
    
    @api.onchange('barcode_no')
    def _get_header_data(self):
        if self.barcode_no:
            self.tgl_produksi=self.detail_id.tgl_produksi
            self.pabrik_id=self.detail_id.pabrik_id
        
    @api.multi
    def write(self, vals):
        orders = self.mapped('detail_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.detail_id == order)
            msg = ""
            for line in order_lines:
                if vals.get('barcode_no'):
                    msg += "Barcode" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (line.barcode_no, vals['barcode_no'],)
                if vals.get('no_tangki'):
                    msg += "No. Tangki" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_tangki), str(vals['no_tangki']),)
                if vals.get('no_line'):
                    msg += "Line" + ": %s → %s <b>[ <i>updated</i> ]</b><br/>" % (str(line.no_line), str(vals['no_line']),)
            
            if msg!="":
                order.message_post(body=msg)
            return super(sis_thawing_detail, self).write(vals)


    @api.multi
    def unlink(self):
        orders = self.mapped('detail_id')
        for order in orders:
            order_lines = self.filtered(lambda x: x.detail_id == order)
            msg = ""
            for line in order_lines:
                msg += "Barcode" + ": %s <b>[ <i>deleted</i> ]</b><br/>" % (line.barcode_no,)
            if msg!="":
                order.message_post(body=msg)
        return super(sis_thawing_detail, self).unlink()
    
    def copydata(self):
        rdef=self.env['sis.defrost.detail'].search([('id','=',self.id)])
        if len(rdef)>0:
            self.env.cr.execute("select id from sis_cs_detail where tgl_produksi='"+rdef.tgl_produksi+"' and barcode_no='"+rdef.barcode_no+"' and no_potong="+str(rdef.no_potong)+" and pabrik_id='"+rdef.pabrik_id+"'")
            cs=self.env.cr.fetchall()
            if len(cs)>0:
                for def_data in cs:
                    (xid,)=def_data
 
                vals = {'tgl_produksi'   : rdef.tgl_produksi,
                        'pabrik_id'      : rdef.pabrik_id,
                        'fresh_fish'     : rdef.fresh_fish,
                        'tgl_keluar'     : rdef.tgl_keluar,
                        'barcode_no'     : rdef.barcode_no,
                        'no_tangki'      : rdef.no_tangki,
                        'no_line'        : rdef.no_line,
                        'no_potong'      : rdef.no_potong,
                        'fish_box_no'    : rdef.fish_box_no,
                        'quantity'       : rdef.quantity,
                        'suhu_before'    : rdef.suhu_before,
                        'tgl_start'      : rdef.tgl_start,
                        'suhu_after'     : rdef.suhu_after,
                        'tgl_finish'     : rdef.tgl_finish,
                        'tgl_tuang'      : rdef.tgl_tuang,
                        'remark'         : rdef.remark,
                        'durasi_jam'     : rdef.durasi_jam,
                        'status_pl'      : rdef.status_pl,
                        'defrost_link_id': xid,
                        'detail_id'      : self.detail_id.id
                    }
                self.env['sis.defrost.detail'].create(vals)


class sis_defrost_view_alert(models.Model):
    _name = 'sis.defrost.view.alert'
    _description = 'View data yang belum diinput defrost'
    _order = 'tgl_produksi desc' 
    _auto = False
    
    tgl_produksi = fields.Date('Tanggal Produksi')
    pabrik_id = fields.Char('Lokasi')
    barcode_no = fields.Char('Barcode No')
    no_potong = fields.Integer('No Potong')
    fish_box_no = fields.Char('Fishbox No')
    quantity = fields.Float('Quantity')
    tgl_keluar = fields.Datetime('Tanggal Keluar')
    item_no = fields.Char('Item No')
    description =  fields.Char('Description')
    vessel_no =   fields.Char('Vessel No')
    hatch_no =   fields.Char('Hatch No')
    create_date =   fields.Datetime('Create Date')
    
    @api.model_cr   
    def init(self):
        cSQL="""
        CREATE OR REPLACE VIEW sis_defrost_view_alert as (
        SELECT DISTINCT
        row_number() OVER () as id, 
        a.tgl_produksi, a.pabrik_id, a.barcode_no, a.no_potong, a.fish_box_no, a.quantity, a.tgl_keluar, a.item_no, a.description, a.vessel_no,a.hatch_no, a.create_date
        from sis_cs_detail a left join sis_defrost_detail b on b.barcode_no=a.barcode_no and b.tgl_produksi=a.tgl_produksi and b.pabrik_id=a.pabrik_id and b.quantity=a.quantity
        where b.no_tangki is null and b.quantity is null and a.real_itemno not like '%L' and a.real_itemno not like '%F' order by tgl_produksi desc)"""
        
        tools.sql.drop_view_if_exists(self._cr, 'sis_defrost_view_alert')
        self._cr.execute(cSQL)
    
