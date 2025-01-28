from odoo import fields,models

class TodayWrkSupport(models.Model):
    _name = 'today.wrk.support'
    _description = 'Today Work Support'

    name = fields.Text(string='Work')
    time_taken = fields.Char(string='Time Taken (HH:MM)', help='Enter time in HH:MM format')
    current_status = fields.Many2one('job.status', string='Current Status', required=True)

    employee_id = fields.Many2one('support.staff', string='Employee')
