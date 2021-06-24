# -*- coding: utf-8 -*-
from odoo import http

# class SisCoba(http.Controller):
#     @http.route('/sis_coba/sis_coba/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sis_coba/sis_coba/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sis_coba.listing', {
#             'root': '/sis_coba/sis_coba',
#             'objects': http.request.env['sis_coba.sis_coba'].search([]),
#         })

#     @http.route('/sis_coba/sis_coba/objects/<model("sis_coba.sis_coba"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sis_coba.object', {
#             'object': obj
#         })