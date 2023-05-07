# -*- coding: utf-8 -*-
{
    'name': "Purchase Request",
    'summary': "Purchase Request Workflow",
    'description': """
    Purchase Request You use this module if you wish to give notification of requirements of
    materials and or external services and keep track of such requirements. 
    Requests can be created either directly or indirectly. “Directly” means that someone from
    the requesting department enters a purchase request manually.
     """,
    'sequence': -120,
    'author': "Dina Sameh",
    'website': "http://www.zadsolutions.com",
    'category': 'Purchase',
    'version': '15.0.0.0.1',
    'depends': [
        'purchase', 'mail', 'product'
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/mail_template_data.xml',
        'wizards/rejection_view.xml',
        'views/purchase_request_view.xml',
        'views/purchase_order_view.xml',
        'report/purchase_request_pdf_report.xml',
        'report/report.xml',

    ],
    # our module is a submodule from purchases, so it is not a stand-alone application for this reason
    # we will set False as a value for application and if we made it false sequence wouldn't effect on our module
    'application': False,
    'license': 'LGPL-3',
}
