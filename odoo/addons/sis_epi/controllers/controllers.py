# -*- coding: utf-8 -*-
from odoo import http

# class SisEpi(http.Controller):
#     @http.route('/sis_epi/sis_epi/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sis_epi/sis_epi/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sis_epi.listing', {
#             'root': '/sis_epi/sis_epi',
#             'objects': http.request.env['sis_epi.sis_epi'].search([]),
#         })

#     @http.route('/sis_epi/sis_epi/objects/<model("sis_epi.sis_epi"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sis_epi.object', {
#             'object': obj
#         })