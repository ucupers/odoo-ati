# -*- coding: utf-8 -*-
{
    'name'          : "SIS Traceability",
    'category'      : "",
    'version'       : "1.0.0",
    'depends'       : ["base",
                       "sis_fish_status"],
    'author'        : "IT PT. ATI",
    'description'   : "Traceablity System PT. Aneka Tuna Indonesia",
    'data'          : ["views/sis_cs.xml",
                       "views/sis_defrost.xml",
                       "views/sis_hr_employee.xml",
                       "views/sis_traceability.xml",
                       "views/sis_cutting.xml",
                       "views/sis_cutting_basket.xml",
                       "views/sis_cooker_basket.xml",
                       "views/sis_cutting_tangki.xml",
                       "views/sis_cooker.xml",
                       "views/sis_pre_cleaning.xml",
                       "views/sis_crosscheck_cutting.xml",
                       "views/sis_pre_line_cleaning.xml",
                       "views/sis_cs_no_loin.xml",
                       "views/sis_cleaning.xml",
                       "views/sis_vendor.xml",
                       "views/sis_master_product.xml",
                       "views/sis_packing.xml",
                       "views/sis_packing_supply.xml",
                       "views/sis_unpacking_defrost_loin.xml",
                       "views/sis_retort.xml",
                       "views/sis_retort_loading_basket.xml",
                       "views/sis_wh_bongkar_produk.xml",
                       "views/sis_wh_labeling.xml",
                       "views/sis_ec_pouch_hd.xml",
                       "wizard/sis_bbtstandard.xml",
                       "reports/report_traceability_form.xml",
                       "reports/cs_outgoing.xml",
                       "reports/report.xml",
                       "reports/report_check_cutting_form.xml"
                       ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    "qweb"          : ['static/src/xml/qweb.xml'],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}