from odoo import api, fields, models,_
from odoo.exceptions import ValidationError
import re

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

    total_work_hours = fields.Char(string='Total Work Hours', compute='_compute_total_work_hours', store=True)

    @api.depends('name')
    def _compute_total_work_hours(self):
        for record in self:
            if record.name and record.name.resource_calendar_id:
                hours_per_day = record.name.resource_calendar_id.hours_per_day
                if record.is_half_day:
                    hours_per_day = hours_per_day / 2.0
                hours = int(hours_per_day)
                minutes = int((hours_per_day - hours) * 60)
                record.total_work_hours = f"{hours:02d}:{minutes:02d}"
            else:
                record.total_work_hours = "00:00"

    actual_work_hours = fields.Char(string='Actual Work Hours', compute='_compute_actual_work_hours', store=True)
    #
    @api.depends('report_ids.time_taken')
    def _compute_actual_work_hours(self):
        for record in self:
            total_minutes = 0
            for report in record.report_ids:
                if report.time_taken and isinstance(report.time_taken, str):
                    try:
                        hours, minutes = map(int, report.time_taken.split(':'))
                        total_minutes += hours * 60 + minutes
                    except (ValueError, AttributeError):
                        continue
            
            hours, minutes = divmod(total_minutes, 60)
            record.actual_work_hours = f"{hours:02d}:{minutes:02d}"

    def _compare_time_strings(self, time1, time2):
        """Compare two time strings in HH:MM format"""
        if not time1 or not time2:
            return False
        try:
            h1, m1 = map(int, time1.split(':'))
            h2, m2 = map(int, time2.split(':'))
            return (h1 * 60 + m1) < (h2 * 60 + m2)
        except (ValueError, AttributeError):
            return False

    @api.constrains('report_ids.time_taken')
    def _check_time_format(self):
        for record in self:
            for report in record.report_ids:
                if report.time_taken and not re.match(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', report.time_taken):
                    raise ValidationError(_("Time must be in HH:MM format (e.g., 02:00, 13:30)."))

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



    @api.constrains('name', 'date')
    def _check_unique_record_per_day(self):
        for record in self:
            if self.search_count([('name', '=', record.name.id), ('date', '=', record.date)]) > 1:
                raise ValidationError(_("An employee can only submit one report per day."))

    def action_submit(self):
        # Validate incomplete tasks
        for report in self.report_ids:
            if report.current_status.name.strip().lower() != 'completed':
                if not report.to_work_on or not report.expected_close_date:
                    raise ValidationError(_("For task '%s': When status is not 'Completed', both 'To Work On' and 'Expected Close Date' are mandatory.") % report.task_id)

        if self._compare_time_strings(self.actual_work_hours, self.total_work_hours):
            raise ValidationError(_("The Total work hours should be achieved by the employee."))
        
        self.state = 'submitted'
        self.prepared_by = self.env.user.employee_id.id
        manager = self.name.parent_id
        if manager:
            self.activity_schedule(
                'daily_report.mail_activity_work_log',
                user_id=manager.user_id.id,
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

    summary = fields.Html(string="Summary",store=True)



