from odoo import models, fields, api
import time, datetime
from datetime import datetime
from PyPDF2.generic import char

class sis_master_time(models.Model):
    _name = 'sis.master.time'
    _rec_name = 'size'
    _inherit = 'mail.thread'
    
    
    size = fields.Char(string="Size")
    pre_cl_time = fields.Float(string="Pre-CL Time", store=True, compute='convertion_char_time_to_time')
    cl_time = fields.Float(string="CL Time", store=True, compute='convertion_char_time_to_time')
    delay_co_cl = fields.Float(string="Delay CO-CL", store=True, compute='convertion_char_time_to_time')
    cooking_time = fields.Float(string="Cooking Time", store=True, compute='convertion_char_time_to_time')
    delay_cu_co = fields.Float(string="Delay CU-CO", store=True, compute='convertion_char_time_to_time')
    cutting_time = fields.Float(string="Cutting Time", store=True, compute='convertion_char_time_to_time')
    delay_de_cu = fields.Float(string="Delay DE-CU", store=True, compute='convertion_char_time_to_time')
    defrost_time = fields.Float(string="Defrost Time", store=True, compute='convertion_char_time_to_time')
    cs_defrost = fields.Float(string="CS-Defrost", store=True, compute='convertion_char_time_to_time')
    tonase = fields.Float(string="Tonase")
    
    # Char tampungan sementara
    pre_cl_time_char = fields.Char()
    delay_co_cl_char = fields.Char()
    cooking_time_char = fields.Char()
    delay_cu_co_char = fields.Char()
    cutting_time_char = fields.Char()
    delay_de_cu_char = fields.Char()
    defrost_time_char = fields.Char()
    cs_defrost_char = fields.Char()
    cl_time_char = fields.Char()

    # Field compute
    total_time = fields.Float(string="Total Time", compute='compute_total_jam')
    de_pk = fields.Float(string="DE-PK", compute='compute_de_pk')
    cu_pk = fields.Float(string="CU-PK", compute='compute_cu_pk')
    co_pk = fields.Float(string="CO-PK", compute='compute_co_pk')
    pre_pk = fields.Float(string="Pre-PK", compute='compute_pre_pk')
    
    
    note = fields.Html(string="Note", readonly=True,
                       default="1. <span>CL</span> : <span>Cleaning</span><br>"+\
                       "2. <span>CO</span> : <span>Cooking</span><br>"+\
                       "3. <span>CU</span> : <span>Cutting</span><br>"+\
                       "4. <span>CS</span> : <span>Cold Storage</span><br>"+\
                       "5. <span>DE</span> : <span>Defrost</span><br>")
    
    
    @api.one
    @api.depends('pre_cl_time_char', 'delay_co_cl_char', 'cooking_time_char', 'delay_cu_co_char', 'cutting_time_char', 
                 'delay_de_cu_char', 'defrost_time_char', 'cs_defrost_char', 'cl_time_char')
    def convertion_char_time_to_time(self):
        for rec in self:
            pre_cl_time_char = (rec.pre_cl_time_char)
            delay_co_cl_char = rec.delay_co_cl_char
            cooking_time_char = rec.cooking_time_char
            delay_cu_co_char = rec.delay_cu_co_char
            cutting_time_char = rec.cutting_time_char
            delay_de_cu_char = rec.delay_de_cu_char
            defrost_time_char = rec.defrost_time_char
            cs_defrost_char = rec.cs_defrost_char
            cl_time_char = rec.cl_time_char
            
            
            if pre_cl_time_char:
                time_str = '13::55::26'
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(pre_cl_time_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.pre_cl_time = float_time
            
            if delay_co_cl_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(delay_co_cl_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.delay_co_cl = float_time
                
            if cooking_time_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(cooking_time_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.cooking_time = float_time
            
            if delay_cu_co_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(delay_cu_co_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.delay_cu_co = float_time
            
            if cutting_time_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(cutting_time_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.cutting_time = float_time
            
            if delay_de_cu_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(delay_de_cu_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.delay_de_cu = float_time
                
            if defrost_time_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(defrost_time_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.defrost_time = float_time
                
            if cs_defrost_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(cs_defrost_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.cs_defrost = float_time
                
            if cl_time_char:
                time_format = '%H:%M:%S'
                time_object = datetime.strptime(str(cl_time_char), time_format).time()
                float_time = time_object.hour+time_object.minute/60.0
                
                rec.cl_time = float_time
            
            pass
    
    
    @api.depends('cs_defrost', 'defrost_time', 'delay_de_cu', 'cutting_time', 
                 'delay_cu_co', 'cooking_time', 'delay_co_cl', 'pre_cl_time')
    def compute_total_jam(self):
        for rec in self:
            pre_cl_time = rec.pre_cl_time
            delay_co_cl = rec.delay_co_cl
            cooking_time = rec.cooking_time
            delay_cu_co = rec.delay_cu_co
            cutting_time = rec.cutting_time
            delay_de_cu = rec.delay_de_cu
            defrost_time = rec.defrost_time
            cs_defrost = rec.cs_defrost
            cl_time = rec.cl_time
        
            rec.total_time = pre_cl_time + delay_co_cl + cooking_time + delay_cu_co + cutting_time + delay_de_cu + defrost_time + cs_defrost
            
            result = '{0:02.0f}:{1:02.0f}'.format(*divmod(rec.total_time * 60, 60))
            print(result)
    
    
    @api.depends('total_time', 'cs_defrost')
    def compute_de_pk(self):
        for rec in self:
            total_time = rec.total_time
            cs_defrost = rec.cs_defrost
            
            de_pk = total_time - cs_defrost
            rec.de_pk = de_pk
            
            
    @api.depends('total_time', 'cs_defrost', 'defrost_time', 'delay_de_cu')
    def compute_cu_pk(self):
        for rec in self:
            total_time = rec.total_time
            cs_defrost = rec.cs_defrost
            defrost_time = rec.defrost_time
            delay_de_cu = rec.delay_de_cu
            
            cu_pk = total_time - (cs_defrost - defrost_time - delay_de_cu)
            rec.cu_pk = cu_pk
    
    
    @api.depends('total_time', 'delay_cu_co', 'cutting_time', 
                 'delay_de_cu', 'defrost_time', 'cs_defrost')
    def compute_co_pk(self):
        for rec in self:
            total_time = rec.total_time
            delay_cu_co = rec.delay_cu_co
            cutting_time = rec.cutting_time
            delay_de_cu = rec.delay_de_cu
            defrost_time = rec.defrost_time
            cs_defrost = rec.cs_defrost
            
            co_pk = total_time - (delay_cu_co + cutting_time + delay_de_cu + defrost_time + cs_defrost)
            rec.co_pk = co_pk
    
    
    @api.depends('total_time', 'cooking_time', 'delay_cu_co', 'cutting_time', 
                 'delay_de_cu', 'defrost_time', 'cs_defrost', 'delay_co_cl')  
    def compute_pre_pk(self):
        for rec in self:
            total_time = rec.total_time
            delay_cu_co = rec.delay_cu_co
            cutting_time = rec.cutting_time
            delay_co_cl = rec.delay_co_cl
            cooking_time = rec.cooking_time
            delay_de_cu = rec.delay_de_cu
            defrost_time = rec.defrost_time
            cs_defrost = rec.cs_defrost
            
            pre_pk = total_time - (delay_cu_co + cutting_time + delay_co_cl + cooking_time + delay_de_cu + defrost_time + cs_defrost)
            rec.pre_pk = pre_pk        
            
            