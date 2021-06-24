# -*- coding: utf-8 -*-
{
    'name'          : "SIS PO Requisition",
    'category'      : "",
    'version'       : "1.0.0",
    'depends'       : ["base","hr"],
    'author'        : "IT PT. ATI",
    'description'   : "PO Requisition System PT. Aneka Tuna Indonesia",
    'data'          : [
                      "views/sis_view_por.xml",
                      "reports/sis_print_por.xml",
                      "reports/sis_report_por.xml",
                      "reports/sis_report_por_rutin.xml",
                      "views/sis_po_requisition.xml"
                       ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}