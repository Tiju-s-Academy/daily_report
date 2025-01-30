from odoo import fields,models

class BalanceWrkSupport(models.Model):
    _name = 'balance.wrk.support'
    _description = 'Balance Work Report'

    name = fields.Text(string='Work')
    time_taken = fields.Char(string='Time Taken (HH:MM)', help='Enter time in HH:MM format')
    current_status = fields.Many2one('job.status', string='Current Status')

    employee_id = fields.Many2one('support.staff', string='Employee')