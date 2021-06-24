# -*- coding: utf-8 -*-
from odoo import http

# class SisBudomari(http.Controller):
#     @http.route('/sis_budomari/sis_budomari/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sis_budomari/sis_budomari/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sis_budomari.listing', {
#             'root': '/sis_budomari/sis_budomari',
#             'objects': http.request.env['sis_budomari.sis_budomari'].search([]),
#         })

#     @http.route('/sis_budomari/sis_budomari/objects/<model("sis_budomari.sis_budomari"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sis_budomari.object', {
#             'object': obj
#         })