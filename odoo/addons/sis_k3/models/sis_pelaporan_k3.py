from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta

class pelaporan_k3(models.Model):
    _name  ='sis.pelaporan.k3'
    _description = 'Pelaporan K3'
    _rec_name='no_doc'
    _order = "no_doc desc"
    
    no_doc              = fields.Char(size=12, string='Doc No', default='K3/2021-XXXX', track_visibility="onchange",required=True)
    tgl_doc             = fields.Date(string='Tanggal', default=datetime.now()+relativedelta(hours=7),required=True)
    pabrik_id           = fields.Selection([('ATI-1','ATI-1'),('ATI-2','ATI-2')], string='Lokasi', default='ATI-1', track_visibility="onchange")
    section             = fields.Selection([
        ('Boiler','Boiler'),('CL','Cleaning'),('CS','Cold Storage'),('EC','Empty Can'),('FJ','Fish Juice'),('FM','Fish Meal'),
        ('GA','General Affairs'),('HR','Human Resources'),('IT','IT'),('MT','Maintenance'),('Office','Office'),('PPIC','PPIC'),
        ('packing','Packing'),('PreCL','Pre Cleaning'),('QT','Quality Technology'),('RM','Raw Material'),('Retort','Retort'),
        ('Seamer','Seamer'),('Seasoning','Seasoning'),('WH','Warehouse')], string='Bagian', required=True, track_visibility="onchange")
    potensi_bahaya_d    = fields.Html(string='Deskripsi Potensi Bahaya', default='-',required=True, track_visibility="onchange")
    potensi_bahaya_i1   = fields.Binary('Foto1 Potensi Bahaya', help='File(image format)')
    potensi_bahaya_i2   = fields.Binary('Foto2 Potensi Bahaya', help='File(image format)')
    potensi_bahaya_area = fields.Char(size=255, string='Area', default='-',required=True, track_visibility="onchange")
    review_k3           = fields.Html(string='Review K3', default='-',required=True, track_visibility="onchange")
    section_pic         = fields.Selection([
        ('Boiler','Boiler'),('CL','Cleaning'),('CS','Cold Storage'),('EC','Empty Can'),('FJ','Fish Juice'),('FM','Fish Meal'),
        ('GA','General Affairs'),('HR','Human Resources'),('IT','IT'),('MT','Maintenance'),('Office','Office'),('PPIC','PPIC'),
        ('packing','Packing'),('PreCL','Pre Cleaning'),('QT','Quality Technology'),('RM','Raw Material'),('Retort','Retort'),
        ('Seamer','Seamer'),('Seasoning','Seasoning'),('WH','Warehouse')], string='Bagian PJ', track_visibility="onchange")
    tgl_target          = fields.Date(string='Deadline', track_visibility="onchange")
    p2k3                = fields.Selection([('ya','YA'),('tidak','TIDAK')], string='P2K3', default='ya', track_visibility="onchange")
    info_p2k3           = fields.Html(string='Info P2K3', default='-',required=True, track_visibility="onchange")
    corrective_act_d    = fields.Html(string='Deskripsi Pengendalian Bahaya', default='-',required=True, track_visibility="onchange")
    corrective_act_d1   = fields.Binary('Foto1 Pengendalian Bahaya', help='File(image format)')
    corrective_act_d2   = fields.Binary('Foto2 Pengendalian Bahaya', help='File(image format)')
    tgl_act             = fields.Date(string='Tanggal Action', default=datetime.now()+relativedelta(hours=7))
    pabrik_id_reporter  = fields.Char(size=5, string='Lokasi Reporter')
    section_reporter    = fields.Char(size=18, string='Reporter')
    rpt_xlsx            = fields.Binary('File data', help='File(xlsx format)')
    step_state          = fields.Selection([('draft','Draft'),('confirmed','Confirmed'),('review','Reviewed by K3'),('action','Corrective Action'),('closed','Closed')], string='step_state', default='draft', track_visibility="onchange")

    def _get_prefix(self):
        tanggal=datetime.now()
        d_to = datetime.strptime(tanggal.strftime("%Y-%m"),"%Y-%m")
        d_tahun = d_to.year

        no_prefix = "K3/"+str(d_tahun)+"-"
        
        rec=self.env['sis.pelaporan.k3'].search([('no_doc','ilike',no_prefix)])
        if len(rec)>0:
            self.env.cr.execute("select max(cast(substring(no_doc,9,4) as integer)) from sis_pelaporan_k3 where no_doc like '"+no_prefix+"%'")
            rc=self.env.cr.fetchall()
              
            for b in rc :
                (x,)=b
            no_urut=x+1
            if no_urut<10:
                no_doc=no_prefix+"000"+str(no_urut)
            elif no_urut>9 and no_urut<100:
                no_doc=no_prefix+"00"+str(no_urut)
            elif no_urut>999 and no_urut<1000:
                no_doc=no_prefix+"0"+str(no_urut)
            else:
                no_doc=no_prefix+str(no_urut)
        else:
            no_urut=1
            no_doc=no_prefix+"000"+str(no_urut)
        
        return no_doc
    
    def _get_save_reporter(self):
        xuid = self.env.uid
        cSQL1="select a. pabrik_id,a.section_id from hr_employee as a, res_users as b, res_partner as c "
        cSQL2="where c.id=b.partner_id and a.address_id=c.id " 

        self.env.cr.execute(cSQL1+cSQL2+"and b.id="+str(xuid))
        rc_lokasi=self.env.cr.fetchall()
        
        for def_lokasi in rc_lokasi:
            (xpabrik_id,xsection_id)=def_lokasi
        
        if xpabrik_id=="ATI1":
            xlokasi="ATI-1"
        else:
            xlokasi="ATI-2"
        
        return xlokasi,xsection_id

    @api.multi
    def action_post(self):
        xlokasi, xsection_id=self._get_save_reporter()

        for me_id in self :
            if me_id.step_state == 'draft':
                if me_id.section_reporter==xsection_id:
                    me_id.write({'step_state':'confirmed'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.step_state == 'confirmed':
                if xsection_id=="GA":
                    me_id.write({'step_state':'review'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.step_state == 'review':
                if me_id.section_pic==xsection_id:
                    me_id.write({'step_state':'action'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.step_state == 'action':
                if xsection_id=="GA":
                    me_id.write({'step_state':'closed'})
                else:
                    raise UserError("Unauthorized User!")

    @api.multi
    def action_undo_post(self):
        xlokasi, xsection_id=self._get_save_reporter()

        for me_id in self :
            if me_id.step_state == 'action':
                if xsection_id=="GA":
                    me_id.write({'step_state':'review'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.step_state == 'review':
                if me_id.section_pic==xsection_id or me_id.section=='GA':
                    me_id.write({'step_state':'confirmed'})
                else:
                    raise UserError("Unauthorized User!")
            elif me_id.step_state == 'confirmed':
                if xsection_id=="GA":
                    me_id.write({'step_state':'draft'})
                else:
                    raise UserError("Unauthorized User!")
                
    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self,vals):
        xlokasi, xsection_id=self._get_save_reporter()
        
        nodoc=self._get_prefix()
        vals.update({'no_doc':nodoc, 'pabrik_id_reporter':xlokasi, 'section_reporter':xsection_id}) 
        res_id = models.Model.create(self, vals)
        return res_id

    @api.multi
    def write(self, vals):
        xstatus=0
        xlokasi, xsection_id=self._get_save_reporter()
        
        for me_id in self :
            if me_id.step_state=="draft":
                if me_id.section_reporter==xsection_id:
                    xstatus=1
            elif me_id.step_state=="confirmed" or me_id.step_state=="action":
                if xsection_id=="GA":
                    xstatus=1
            elif me_id.step_state=="review":
                if xsection_id==me_id.section_pic:
                    xstatus=1
            
            if xstatus==1:
                super(pelaporan_k3, self).write(vals)
            else:
                raise UserError("Unauthorized User!")

