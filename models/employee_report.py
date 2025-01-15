from odoo import api, fields, models,_
from odoo.exceptions import ValidationError

class EmployeeReport(models.Model):
    _name = 'employee.report'
    _description = 'Employee Report'
    _inherit = ['mail.thread','mail.activity.mixin']

    name = fields.Many2one('hr.employee', string="Employee",default=lambda self: self.env.user.employee_id,readonly=True)
    department_id = fields.Many2one('hr.department', string="Department",default=lambda self: self.env.user.employee_id.department_id,readonly=True)
    branch_id = fields.Many2one('employee.branch', string="Branch",compute='_compute_branch_id',store=True)

    @api.depends('name')
    def _compute_branch_id(self):
        for record in self:
            if record.name:
                branch = self.env['hr.employee'].search([('id','=',record.name.id)],limit=1)
                record.branch_id = branch.branch_id.id
            else:
                record.branch_id = False

    report_ids = fields.One2many('report', 'employee_id', string="Daily Report")

    total_work_hours = fields.Float(string='Total Work Hours', compute='_compute_total_work_hours', store=True)
    actual_work_hours = fields.Float(string='Actual Work Hours', compute='_compute_actual_work_hours', store=True)

    @api.depends('report_ids.task_id','report_ids.time_taken')
    def _compute_actual_work_hours(self):
        for record in self:
            total_minutes = sum(record.report_ids.mapped('time_taken'))
            record.actual_work_hours = total_minutes

    prepared_by = fields.Many2one('hr.employee', string="Prepared By", default=lambda self: self.env.user.employee_id)
    approved_by = fields.Many2one('hr.employee', string="Approved By")
    date = fields.Date(string='Date',default=fields.Date.today,readonly=True)
    state = fields.Selection([('draft', 'Draft'),('submitted','Submitted'), ('approved', 'Approved'),
                              ('rejected', 'Rejected')], string='Status', default='draft',tracking=True)
    is_manager = fields.Boolean(string="Is Manager",compute="_compute_is_manager",store=False)

    is_half_day = fields.Boolean(string="Half day report",compute="_compute_is_half_day")

    @api.depends('name')
    def _compute_is_half_day(self):
        print("half day check")
        today = fields.Date.today()
        leave = self.env['hr.leave'].sudo().search([
            ('employee_id', '=', self.name.id),  # For the specific employee
            ('state', '=', 'validate'),  # Only validated leaves
            ('request_date_from', '<=', today),  # Leave started on or before today
            ('request_date_to', '>=', today)  # Leave ends on or after today
        ])
        if leave.request_unit_half == True:
            self.is_half_day = True
            self.total_work_hours = self.name.resource_calendar_id.hours_per_day / 2.0
        else:
            self.is_half_day = False




    @api.depends('name', 'name.parent_id')
    def _compute_is_manager(self):
        for record in self:
            record.is_manager = record.name.parent_id.user_id == self.env.user

    @api.depends('name')
    def _compute_total_work_hours(self):
        for record in self:
            if record.name and record.name.resource_calendar_id:
                record.total_work_hours = record.name.resource_calendar_id.hours_per_day
            else:
                record.total_work_hours = 0.0

    @api.constrains('name', 'date')
    def _check_unique_record_per_day(self):
        for record in self:
            if self.search_count([('name', '=', record.name.id), ('date', '=', record.date)]) > 1:
                raise ValidationError(_("An employee can only submit one report per day."))

    def action_submit(self):

        if self.actual_work_hours < self.total_work_hours:
            raise ValidationError(_("The Total work hours should be achieved by the employee."))
        self.state = 'submitted'
        self.prepared_by = self.env.user.employee_id.id
        manager = self.name.parent_id
        if manager:
            self.activity_schedule(
                'daily_report.mail_activity_work_log',
                user_id= manager.user_id.id,
            )

    def action_approve(self):
        self.state = 'approved'
        self.approved_by = self.env.user.employee_id.id
        activity_ids = self.activity_ids
        if activity_ids:
            activity_ids.unlink()
        return {
            'effect': {
                'fadeout': 'slow',
                'message': 'Approved',
                'type': 'rainbow_man',
            }
        }
    def action_reject(self):
        self.state = 'rejected'
        activity_ids = self.activity_ids
        if activity_ids:
            activity_ids.unlink()



