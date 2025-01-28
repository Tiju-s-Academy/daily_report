from traceback import format_exc

from odoo import fields,models

class YesterdayWrkSupport(models.Model):
    _name = 'yesterday.wrk.support'
    _desc = 'Yesterday Work Support'

    name = fields.Text(string='Work')
    time_taken = fields.Char(string='Time Taken (HH:MM)', help='Enter time in HH:MM format')
    current_status = fields.Many2one('job.status', string='Current Status', required=True)

    employee_id = fields.Many2one('support.staff', string='Employee')

