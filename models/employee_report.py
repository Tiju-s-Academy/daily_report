import re
import tz
from datetime import date, datetime, timedelta
import calendar

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError


class EmployeeReport(models.Model):
    _name = 'employee.report'
    _description = 'Employee Report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id,
                           readonly=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    default=lambda self: self.env.user.employee_id.department_id, readonly=True)
    branch_id = fields.Many2one('employee.branch', string="Branch", compute='_compute_branch_id', store=True)
    reporting_manager_id = fields.Many2one('hr.employee', string="Reporting Manager", 
                                         help="Select the specific manager this report is intended for. If you have only one manager, it will be automatically selected.")

    @api.depends('name')
    def _compute_branch_id(self):
        for record in self:
            if record.name:
                branch = self.env['hr.employee'].search([('id', '=', record.name.id)], limit=1)
                record.branch_id = branch.branch_id.id
            else:
                record.branch_id = False

    def _default_report_ids(self):
        # Get today's date
        today = date.today()

        # Check if today is 1st or 3rd Saturday
        if today.weekday() == calendar.SATURDAY:  # Check if today is Saturday
            month_calendar = calendar.Calendar()
            saturdays = [
                day for day in month_calendar.itermonthdays2(today.year, today.month)
                if day[0] != 0 and day[1] == calendar.SATURDAY
            ]
            if (today.day == saturdays[0][0] or (len(saturdays) > 2 and today.day == saturdays[2][0])):
                # Return an empty list if it's the 1st or 3rd Saturday
                return []

        # Default values if not 1st or 3rd Saturday
        return [(0, 0, {
            'project_id': 'Refreshment',
            'activity': 'Interval',
            'time_taken': '00:30',
            'current_status': self.env['job.status'].search([('name', '=', 'Completed')], limit=1).id
        })]

    report_ids = fields.One2many('report', 'employee_id', string="Daily Report", default=_default_report_ids)

    total_work_hours = fields.Char(string='Total Work Hours', compute='_compute_total_work_hours', store=True)

    @api.depends('name')
    def _compute_total_work_hours(self):
        """ Compute total work hours based on default 08:00 hours and half-day conditions """
        for record in self:
            hours_per_day = 8.0  # Default working hours (08:00)

            today = date.today()

            # Check if today is 1st or 3rd Saturday
            if today.weekday() == calendar.SATURDAY:
                month_calendar = calendar.Calendar()
                saturdays = [
                    day for day in month_calendar.itermonthdays2(today.year, today.month)
                    if day[0] != 0 and day[1] == calendar.SATURDAY
                ]
                if today.day == saturdays[0][0] or (len(saturdays) > 2 and today.day == saturdays[2][0]):
                    hours_per_day /= 2.0  # Half-day rule for 1st and 3rd Saturday

            # Apply half-day leave rule
            if record.is_half_day:
                hours_per_day /= 2.0

            # Convert to HH:MM format
            hours = int(hours_per_day)
            minutes = int((hours_per_day - hours) * 60)
            record.total_work_hours = f"{hours:02d}:{minutes:02d}"

    actual_work_hours = fields.Char(string='Actual Work Hours', compute='_compute_actual_work_hours', store=True)

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

    total_work_minutes = fields.Integer(string='Total Work Minutes', compute='_compute_actual_work_hours', store=True)

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

            record.total_work_minutes = total_minutes  # Store total minutes
            hours, minutes = divmod(total_minutes, 60)
            record.actual_work_hours = f"{hours:02d}:{minutes:02d}"


    @api.constrains('report_ids.time_taken')
    def _check_time_format(self):
        for record in self:
            for report in record.report_ids:
                if report.time_taken and not re.match(r'^([0-9]|0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$', report.time_taken):
                    raise ValidationError(_("Time must be in HH:MM format (e.g., 02:00, 13:30)."))

    prepared_by = fields.Many2one('hr.employee', string="Prepared By", default=lambda self: self.env.user.employee_id)
    approved_by = fields.Many2one('hr.employee', string="Approved By")
    date = fields.Date(string='Date', default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved')],
                             string='Status', default='draft', tracking=True)
    is_manager = fields.Boolean(string="Is Manager", compute="_compute_is_manager", store=False)

    is_half_day = fields.Boolean(string="Half day report", compute="_compute_is_half_day")
    is_director = fields.Boolean(string='Is Director', compute="_compute_is_manager", store=True)
    is_md = fields.Boolean(string='Is MD',compute="_compute_is_manager", store=True)
    is_hod = fields.Boolean(string='Is HOD',compute="_compute_is_manager", store=True)
    submitted_time = fields.Datetime(string='Submission On',readonly=True,tracking=True)
    approved_time = fields.Datetime(string='Approved On',readonly=True,tracking=True)
    available_manager_ids = fields.Many2many('hr.employee', compute='_compute_available_manager_ids')
    
    @api.depends('name')
    def _compute_available_manager_ids(self):
        """
        Compute the list of available managers for this employee
        If there's only one manager available, automatically select that manager
        """
        for record in self:
            available_managers = []
            if record.name:
                # Add direct manager if exists
                if record.name.parent_id:
                    available_managers.append(record.name.parent_id.id)
                
                # Add additional managers from new model
                add_managers = self.env['employee.additional.manager'].search([
                    ('employee_id', '=', record.name.id),
                    ('active', '=', True)
                ])
                for add_manager in add_managers:
                    available_managers.append(add_manager.manager_id.id)
            
            record.available_manager_ids = available_managers
            
            # Auto-select manager if there's only one available and the field is empty
            if len(available_managers) == 1 and not record.reporting_manager_id and record.state == 'draft':
                record.reporting_manager_id = available_managers[0]

    @api.onchange('name')
    def _onchange_name(self):
        """
        Auto-select the reporting manager when employee changes
        If there's only one available manager, select it automatically
        """
        if self.name and not self.reporting_manager_id:
            available_managers = []
            
            # Add direct manager if exists
            if self.name.parent_id:
                available_managers.append(self.name.parent_id.id)
            
            # Add additional managers
            add_managers = self.env['employee.additional.manager'].search([
                ('employee_id', '=', self.name.id),
                ('active', '=', True)
            ])
            
            for add_manager in add_managers:
                available_managers.append(add_manager.manager_id.id)
            
            if len(available_managers) == 1:
                self.reporting_manager_id = available_managers[0]

    @api.depends('name')
    def _compute_is_half_day(self):

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

    @api.depends('name', 'name.parent_id', 'reporting_manager_id')
    def _compute_is_manager(self):
        for record in self:
            # Check if user is direct manager
            is_direct_manager = record.name.parent_id.user_id == self.env.user
            
            # Check if user is the specific reporting manager for this report
            is_reporting_manager = False
            if record.reporting_manager_id and record.reporting_manager_id.user_id == self.env.user:
                is_reporting_manager = True
                
            # Check if user is an additional manager
            is_additional_manager = False
            if record.name:
                additional_manager_recs = self.env['employee.additional.manager'].search([
                    ('employee_id', '=', record.name.id),
                    ('manager_id.user_id', '=', self.env.user.id)
                ])
                is_additional_manager = bool(additional_manager_recs)
            
            record.is_manager = is_direct_manager or is_reporting_manager or is_additional_manager
            record.is_director = self.env.user.has_group('daily_report.directors_report')
            record.is_md = self.env.user.has_group('daily_report.admin_report')
            record.is_hod = self.env.user.has_group('daily_report.hod_report')

    @api.constrains('name', 'date', 'reporting_manager_id')
    def _check_unique_record_per_day(self):
        for record in self:
            # Base domain for duplicate check
            domain = [
                ('name', '=', record.name.id),
                ('date', '=', record.date),
                ('id', '!=', record.id),  # Exclude current record
            ]
            
            # If reporting to specific manager, only check for duplicates with same manager
            if record.reporting_manager_id:
                domain.append(('reporting_manager_id', '=', record.reporting_manager_id.id))
            else:
                # If not reporting to a specific manager, check for duplicates with no specific manager
                domain.append(('reporting_manager_id', '=', False))
                
            if self.search_count(domain) > 0:
                if record.reporting_manager_id:
                    raise ValidationError(_("You have already submitted a report for this day to the manager %s.") % record.reporting_manager_id.name)
                else:
                    raise ValidationError(_("You have already submitted a general report for this day."))



    def action_submit(self):
        today = fields.Date.today()
        yesterday = fields.Date.today() - timedelta(days=1)
        
        # Validate incomplete tasks
        for report in self.report_ids:
            # Directors can submit reports for any date
            if not self.is_director:
                # HODs can submit reports for today and yesterday only
                if self.is_hod:
                    if self.date not in [today, yesterday]:
                        raise ValidationError(_("As HOD, you can only submit reports for today and yesterday"))
                # Regular users can only submit reports for today
                elif self.date != today:
                    raise ValidationError(_("Previous Record Can not submit Today"))
            if report.current_status.name.strip().lower() != 'completed':
                if not report.to_work_on or not report.expected_close_date:
                    raise ValidationError(
                        _("For task '%s': When status is not 'Completed', both 'To Work On' and 'Expected Close Date' are mandatory.") % report.task_id)
        if self.student_concerns or self.employee_concerns or self.other_concerns:
            self.has_concerns = True
        self.write({
            'state': 'submitted',
            'prepared_by': self.env.user.employee_id.id,
            'submitted_time': fields.datetime.now()
        })
        # manager = self.name.parent_id
        # if manager:
        #     self.activity_schedule(
        #         'daily_report.mail_activity_work_log',
        #         user_id=manager.user_id.id,
        #     )

    def action_approve(self):
        today = fields.Date.today()
        print("check", self.env.user.has_group('daily_report.directors_report'))
        if self.is_director or self.is_md:
            self.state = 'approved'
            self.approved_by = self.env.user.employee_id.id
            self.approved_time=  fields.datetime.now()
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
        elif self.is_manager:
            yesterday = fields.Date.today() - timedelta(days=1)
            
            # HODs can approve reports for today and yesterday
            if self.is_hod:
                if self.date not in [today, yesterday]:
                    raise UserError(_("As HOD, you can only approve reports for today and yesterday"))
            # Regular managers can only approve today's reports
            elif self.date != today:
                raise UserError(_("You can only approve today's Reports"))
                
            self.state = 'approved'
            self.approved_by = self.env.user.employee_id.id
            self.approved_time = fields.datetime.now()
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
        else:
            raise ValidationError(_("You are not a Manger of the employee or Director"))

    reject_reason = fields.Text(string='Reason', tracking=True)

    def action_reject(self):
        today = fields.Date.today()
        if self.is_director or self.is_md:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Reason'),
                'res_model': 'report.reject.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_employee_report_id': self.id},
            }
        elif self.is_manager:
            yesterday = fields.Date.today() - timedelta(days=1)
            
            # HODs can reject reports for today and yesterday
            if self.is_hod:
                if self.date not in [today, yesterday]:
                    raise UserError(_("As HOD, you can only reject reports for today and yesterday"))
            # Regular managers can only reject today's reports
            elif self.date != today:
                raise UserError(_("You can only reject today's Reports"))
            return {
                'type': 'ir.actions.act_window',
                'name': _('Reason'),
                'res_model': 'report.reject.wizard',
                'target': 'new',
                'view_mode': 'form',
                'context': {'default_employee_report_id': self.id},
            }
        else:
            raise ValidationError(_("You are not a Manger of the employee or Director"))

    summary = fields.Html(string="Summary", store=True)

    # Complaint Fields
    student_concerns = fields.Text(string="Student Concerns")
    employee_concerns = fields.Text(string="Employee Concerns")
    other_concerns = fields.Text(string="Other Concerns")
    has_concerns = fields.Boolean(string="Has Concerns")



    def action_quick_create_concern(self):
        """Open a form to quickly create a concern action record"""
        self.ensure_one()

        # Format employee name properly
        employee_name = self.name
        if hasattr(self, 'employee_id') and self.employee_id and self.employee_id.name:
            employee_name = self.employee_id.name

        # Generate default title: "Action against [Employee Name]'s concern on [Date]"
        default_title = _("Action against {}'s concern on {}").format(
            employee_name,
            self.date.strftime('%d-%m-%Y') if self.date else ''
        )

        return {
            'name': _('Create Action'),
            'type': 'ir.actions.act_window',
            'res_model': 'concern.action.wizard',
            'view_mode': 'form',
            'target': 'new',  # Opens as a dialog/popup
            'context': {
                'default_employee_report_id': self.id,
                'default_name': default_title,
            },
        }

    action_title = fields.Char(string="Action Title")
    action_description = fields.Text(string="Action Description")
    action_date = fields.Date(string="Action Date")
    action_state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('canceled', 'Canceled')
    ], string="Status")
    action_solved_by = fields.Many2one('hr.employee', string="Action Solved By")
    concern_type = fields.Selection([
        ('student', 'Student Concern'),
        ('employee', 'Employee Concern'),
        ('other', 'Other Concern')
    ], string="Concern Type")