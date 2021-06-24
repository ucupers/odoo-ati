# -*- coding: utf-8 -*-
{
    'name': "sis_epi",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sis_ppic', 'mail', 'web'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/sequence.xml',
        'views/sis_master_item_inherit.xml',
        'views/sis_master_time.xml',
        'views/sis_budomari_master.xml',
#         'views/coba_print.xml',
        'wizard/message_fish_using.xml',
        'wizard/sis_epi_detail.xml',
        'wizard/urut_cutting_wizard.xml',
        'wizard/message_get_item.xml',
        'report/report.xml',
        'views/menu.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}