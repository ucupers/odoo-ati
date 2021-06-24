
from odoo import models, fields, api, _
from odoo.exceptions import UserError




class MessageData(models.TransientModel):
    _name = 'message.get.data'

    name = fields.Char('Success')