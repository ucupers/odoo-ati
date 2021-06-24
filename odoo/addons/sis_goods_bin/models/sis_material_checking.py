from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import datetime

class sis_material_checking(models.Model):
    _name='sis.material.checking'
    _order='id desc'      
    
    rpono = fields.Char(string="RPO No",required=True)
    description = fields.Char(string="Item")
    lotno= fields.Char(string="Lot Component",required=True)
    compitemno=fields.Char(string='Component')
    compvariant=fields.Char(string='Component')
    compdescription=fields.Char(string='Component')
    proddate=fields.Char(string='Prod.Date')    
    status=fields.Char(string='Status')
    qstatus=fields.Char(string='Q.Status')
    qstatusa=fields.Char(string='Q.Status Analisa')
    qstatusp=fields.Char(string='Q.Status Process')            
        

class sis_material_scan(models.TransientModel):
    _name='sis.material.scan'
    
    rpono = fields.Char(string="RPO No",required=True)
    description = fields.Char(string="FG",compute='compute_description')
    lotno= fields.Char(string="Lot Component",required=True)
    compitemno=fields.Char(string='Item No', compute='compute_compdesc')
    compvariant=fields.Char(string='Variant', compute='compute_compdesc')
    compdescription=fields.Char(string='Description', compute='compute_compdesc')
    proddate=fields.Char(string='Prod.Date', compute='compute_compdesc')    
    status=fields.Char(string='Status', compute='compute_compdesc')    
    status=fields.Char(string='Status', compute='compute_compdesc')    
    qstatus=fields.Char(string='Q.Status', compute='compute_compdesc')    
    qstatusa=fields.Char(string='Q.Status Analisa', compute='compute_compdesc')    
    qstatusp=fields.Char(string='Q.Status Process', compute='compute_compdesc')
                    
    @api.depends('rpono')
    def compute_description(self):
        for s in self:    
            if s.rpono:
                s.env.cr.execute("select description "+\
                            "from sis_temp_released_production_order where no='"+s.rpono+"'")
                rpos=s.env.cr.fetchall()
                if len(rpos)==0:
                    raise UserError('RPO not found !')
                for rpo in rpos:
                    (description,)=rpo
                    continue
                s.description=description

    @api.depends('lotno','rpono')
    def compute_compdesc(self):
        for s in self:    
            if s.rpono and s.lotno:
                status='OK'
                s.env.cr.execute("select distinct item_no, variant, description,proddate "+\
                            "from sis_temp_ile_remaining_quantity where lot_no='"+s.lotno+"'")
                rpos=s.env.cr.fetchall()
                if len(rpos)==0:
                    status='ERROR : Lot Not Found'
#                 if len(rpos)>1:
#                     raise UserError('Multiple lot found !')

                if status=='OK':
                    for rpo in rpos:
                        (itemno, variant, description,proddate)=rpo

                    s.env.cr.execute("select count('a')"+\
                                "from sis_temp_released_production_order_component where no='"+s.rpono+"' and item_no='"+itemno+"' and variant='"+variant+"'")
                    rpos=s.env.cr.fetchall()
                    if len(rpos)==0:
                        status='ERROR'
                    for rpo in rpos:
                        (num,)=rpo
                    if num==0:
                        status='ERROR : Item not in RPO'
                
                    if status=='OK':
                        s.compitemno=itemno
                        s.compvariant=variant
                        s.compdescription=description
                        s.proddate=proddate

                        s.env.cr.execute("select status,status_analisa,status_process "+\
                                    "from sis_temp_ile_rawfg where lot_no='"+s.lotno+"' and remaining_quantity>0 order by id desc limit 1 ")
                        rpos=s.env.cr.fetchall()

                        if len(rpos)==0:
                            s.env.cr.execute("select status,status_analisa,status_process "+\
                                        "from sis_temp_ile_rawpkg where lot_no='"+s.lotno+"' and remaining_quantity>0 order by id desc limit 1 ")
                            rpos=s.env.cr.fetchall()

                            if len(rpos)==0:
                                status='ERROR'
        
                        if status=='OK':
                            for rpo in rpos:
                                (qstatus,qstatusa,qstatusp)=rpo

                            s.qstatus=qstatus
                            s.qstatusa=qstatusa
                            s.qstatusp=qstatusp                        
                s.status=status

    @api.model
    @api.returns('self', lambda value:value.id)
    def create(self, vals):
        rec= models.TransientModel.create(self, vals)
        vals={
            'rpono':rec.rpono,
            'description':rec.description,
            'lotno':rec.lotno,
            'compitemno':rec.compitemno,
            'compvariant':rec.compvariant,
            'compdescription':rec.compdescription,
            'proddate':rec.proddate,
            'status':rec.status

            }
        self.env['sis.material.checking'].create(vals)
        return rec