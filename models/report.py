from odoo import models,fields

class Report(models.Model):
    _name = 'report'
    _description = 'Report'

    project_id = fields.Many2one('project.project', string='Project')
    task_id = fields.Many2one('project.task', string='Task')
    activity = fields.Char(string='Activity')
    time_taken = fields.Float(string='Time Taken(Hour)')
    current_status = fields.Many2one('job.status', string='Current Status')
    completion = fields.Boolean(string='Completion')
    to_work_on = fields.Char(string='To Work On')
    remarks_if_any = fields.Char(string='Remarks If Any')

    employee_id = fields.Many2one('employee.report', string='Employee')


