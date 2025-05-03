from odoo import api, fields, models, _

class ConcernAction(models.Model):
    _name = 'concern.action'
    _description = 'Actions taken on employee concerns'
    _order = 'action_date desc, id desc'
    _inherit = ['mail.thread']

    # Make name not required
    name = fields.Char(string="Action Title", required=False, tracking=True)
    description = fields.Text(string="Action Description", tracking=True)
    action_date = fields.Date(string="Action Date", default=fields.Date.today, required=True, tracking=True)
    taken_by = fields.Many2one('res.users', string="Taken By", 
                              default=lambda self: self.env.user.id, 
                              readonly=True, required=True)
    concern_type = fields.Selection([
        ('student', 'Student Concern'),
        ('employee', 'Employee Concern'),
        ('other', 'Other Concern')
    ], string="Concern Type", required=True)
    employee_report_id = fields.Many2one('employee.report', string="Related Report", required=True, ondelete='cascade')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('canceled', 'Canceled')
    ], string="Status", default='draft', tracking=True)
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            # Auto-generate name if not provided
            if not vals.get('name'):
                # Get employee report to generate title
                report_id = vals.get('employee_report_id')
                if report_id:
                    report = self.env['employee.report'].browse(report_id)
                    vals['name'] = _("Action against {}'s concern on {}").format(
                        report.name, fields.Date.to_string(vals.get('action_date', fields.Date.today()))
                    )
                else:
                    vals['name'] = _("Action on {}").format(
                        fields.Date.to_string(vals.get('action_date', fields.Date.today()))
                    )
        return super(ConcernAction, self).create(vals_list)
    
    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})
    
    def action_mark_resolved(self):
        self.write({'state': 'resolved'})
    
    def action_mark_canceled(self):
        self.write({'state': 'canceled'})
    
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
