from odoo import api,fields,models,_
from odoo.exceptions import ValidationError,UserError

class SupportStaff(models.Model):
    _name = 'support.staff'
    _description = 'Support Staff Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc'

    name = fields.Many2one('hr.employee', string="Employee", default=lambda self: self.env.user.employee_id,
                           readonly=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    default=lambda self: self.env.user.employee_id.department_id, readonly=True)
    branch_id = fields.Many2one('employee.branch', string="Branch", compute='_compute_branch_id', store=True)

    start_time = fields.Char(string="Start Time",
                              help="Specify the start time in 24-hour format (e.g., 7.0 for 7:00 AM)")
    end_time = fields.Char(string="End Time", help="Specify the end time in 24-hour format (e.g., 21.0 for 9:00 PM)")

    @api.depends('name')
    def _compute_branch_id(self):
        for record in self:
            if record.name:
                branch = self.env['hr.employee'].search([('id', '=', record.name.id)], limit=1)
                record.branch_id = branch.branch_id.id
            else:
                record.branch_id = False

    prepared_by = fields.Many2one('hr.employee', string="Prepared By", default=lambda self: self.env.user.employee_id)
    approved_by = fields.Many2one('hr.employee', string="Approved By")
    date = fields.Date(string='Date', default=fields.Date.today)
    state = fields.Selection([('draft', 'Draft'), ('submitted', 'Submitted'), ('approved', 'Approved')],
                             string='Status', default='draft', tracking=True)

    is_manager = fields.Boolean(string="Is Manager", compute="_compute_is_manager", store=False)
    is_director = fields.Boolean(string='Is Director', compute="_compute_is_manager", store=True)

    @api.depends('name', 'name.parent_id')
    def _compute_is_manager(self):
        for record in self:
            record.is_manager = record.name.parent_id.user_id == self.env.user
            record.is_director = self.env.user.has_group('daily_report.directors_report')

    @api.constrains('name', 'date')
    def _check_unique_record_per_day(self):
        for record in self:
            if self.search_count([('name', '=', record.name.id), ('date', '=', record.date)]) > 1:
                raise ValidationError(_("An employee can only submit one report per day."))

    yesterday_wrk_support_ids = fields.One2many('yesterday.wrk.support','employee_id',string='Pending in Yesterday')
    def _default_today_wrk_support_ids(self):
        # Default values if not 1st or 3rd Saturday
        return [(0, 0, {
            'name': 'Refreshment',
            'time_taken': '00:30',
            'current_status': self.env['job.status'].search([('name', '=', 'Completed')], limit=1).id
        })]

    today_wrk_support_ids = fields.One2many('today.wrk.support','employee_id',string='Today Report',default=_default_today_wrk_support_ids)

    balance_wrk_support_ids = fields.One2many('balance.wrk.support','employee_id',string='Balance Work')

    total_work_hours = fields.Char(
        string='Total Work Hours',
        compute='_compute_total_work_hours',
        store=True
    )

    @api.depends('yesterday_wrk_support_ids.time_taken', 'today_wrk_support_ids.time_taken')
    def _compute_total_work_hours(self):
        for record in self:
            total_minutes = 0

            # Process yesterday's work support records
            for line in record.yesterday_wrk_support_ids:
                if line.time_taken and isinstance(line.time_taken, str):
                    try:
                        hours, minutes = map(int, line.time_taken.split(':'))
                        total_minutes += hours * 60 + minutes
                    except (ValueError, AttributeError):
                        continue  # Skip invalid values

            # Process today's work support records
            for line in record.today_wrk_support_ids:
                if line.time_taken and isinstance(line.time_taken, str):
                    try:
                        hours, minutes = map(int, line.time_taken.split(':'))
                        total_minutes += hours * 60 + minutes
                    except (ValueError, AttributeError):
                        continue  # Skip invalid values

            # Convert total minutes back to HH:MM format
            hours, minutes = divmod(total_minutes, 60)
            record.total_work_hours = f"{hours:02d}:{minutes:02d}"
    summary1 = fields.Html(string="Summary", store=True)
    summary2 = fields.Html(string="Summary", store=True)
    summary3 = fields.Html(string="Summary", store=True)


    def action_submit(self):
        today = fields.Date.today()
        # Validate incomplete tasks
        if self.date != today:
            raise ValidationError(_("Previous Record Can not submit Today"))


        self.state = 'submitted'
        self.prepared_by = self.env.user.employee_id.id

    def action_approve(self):
        today = fields.Date.today()
        print("check", self.env.user.has_group('daily_report.directors_report'))
        if self.is_director:
            self.state = 'approved'
            self.approved_by = self.env.user.employee_id.id
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Approved',
                    'type': 'rainbow_man',
                }
            }
        elif self.is_manager:
            if self.date != today:
                raise UserError(_("You can only approve today's Reports"))
            self.state = 'approved'
            self.approved_by = self.env.user.employee_id.id
            return {
                'effect': {
                    'fadeout': 'slow',
                    'message': 'Approved',
                    'type': 'rainbow_man',
                }
            }
        else:
            raise ValidationError(_("You are not a Manger of the employee or Director"))

    def action_rejection(self):
        today = fields.Date.today()
        print("check", self.env.user.has_group('daily_report.directors_report'))
        if self.is_director:
            self.state = 'draft'
        elif self.is_manager:
            if self.date != today:
                raise UserError(_("You can only approve today's Reports"))
            self.state = 'draft'
        else:
            raise ValidationError(_("You are not a Manger of the employee or Director"))

    reject_reason = fields.Text(string='Reason', tracking=True)

