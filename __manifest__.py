{
    'name': 'Pay Order Management',
    'version': '1.0',
    'summary': 'Portal & Internal Pay Order Workflow',
    'author': 'Bilal',

    'depends': [
        'base',
        'mail',
        'project',
        'account',
        'portal',
        'uom',          # 🔥 REQUIRED for uom_id field
    ],

    'data': [

        # SECURITY
        'security/ir.model.access.csv',

        # SEQUENCE
        'data/sequence.xml',

        # INTERNAL UI
        'views/pay_order_views.xml',
        'views/pay_order_menus.xml',

        # PORTAL
        'views/pay_order_portal_templates.xml',

        # REPORT
        'report/pay_order_report.xml',
        'report/pay_order_report_template.xml',
    ],

    'assets': {
        'web.assets_frontend': [],
    },

    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
