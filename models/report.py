from odoo import api,models,fields

class Report(models.Model):
    _name = 'report'
    _description = 'Report'

    project_id = fields.Char(string='Project | Objectives')
    task_id = fields.Char(string='Task')
    activity = fields.Char(string='Activities')
    time_taken = fields.Char(string='Time Taken (HH:MM)', help='Enter time in HH:MM format')
    current_status = fields.Many2one('job.status', string='Current Status')
    expected_close_date = fields.Date(string='Expected Close Date')
    to_work_on = fields.Char(string='To Work On')
    remarks_if_any = fields.Char(string='Remarks If Any')

    employee_id = fields.Many2one('employee.report', string='Employee')




