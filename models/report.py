from odoo import api,models,fields, _
from odoo.exceptions import ValidationError

class Report(models.Model):
    _name = 'report'
    _description = 'Report'

    sequence = fields.Integer(string="Sequence", default=10)
    project_id = fields.Char(string='Project | Objectives')
    task_id = fields.Char(string='Task')
    activity = fields.Char(string='Activities')
    time_taken = fields.Char(string='Time Taken (HH:MM)', help='Enter time in HH:MM format')
    current_status = fields.Many2one('job.status', string='Current Status', required=True)
    expected_close_date = fields.Date(string='Expected Close Date')
    to_work_on = fields.Char(string='To Work On')
    remarks_if_any = fields.Char(string='Remarks If Any')

    employee_id = fields.Many2one('employee.report', string='Employee')
    is_not_completed = fields.Boolean(compute='_compute_is_not_completed', store=True, default=True)

    @api.depends('current_status.name')
    def _compute_is_not_completed(self):
        for record in self:
            if record.current_status and record.current_status.name:
                record.is_not_completed = record.current_status.name.strip().lower() != 'completed'
            else:
                record.is_not_completed = True

    @api.constrains('current_status', 'to_work_on', 'expected_close_date')
    def _check_incomplete_task_fields(self):
        for record in self:
            if record.current_status and record.current_status.name:
                if record.current_status.name.strip().lower() != 'completed':
                    if not record.to_work_on or not record.expected_close_date:
                        raise ValidationError(_("For tasks not marked as 'Completed', both 'To Work On' and 'Expected Close Date' are mandatory."))




