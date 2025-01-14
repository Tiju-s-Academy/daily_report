{
    'name': 'Daily Report',
    'version': '17.0.1.0.0',
    'summary': 'Daily Report',
    'depends': ['base', 'web', 'mail', 'project', 'hr'],
    'author': 'Tijus Academy',
    'data': [
        'data/activity.xml',
        'security/group.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'views/job_status_view.xml',
        'views/report_view.xml',
        'views/employee_report_view.xml',
        'views/daily_report_menu.xml',
    ],
    'application': True,
    'license': 'LGPL-3',
}
