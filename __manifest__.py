# -*- coding: utf-8 -*-
{
    'name': 'DemoERP',
    'version': '1.0',
    'summary': 'Demo',
    'sequence': -100,
    'description': """Demo""",
    'category': 'Productivity',
    'website': '',
    'license': 'LGPL-3',
    'depends': ['mail', 'base', 'web', 'web_domain_field'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/approved_products_view.xml',
        'views/company_contacts_view.xml',
        'views/menu.xml',
        'views/purchases_menu.xml'
    ],
    'demo': [],
    'qweb': [],
    'installable': True,
    'application': True,
    'auto_install': False,

}
