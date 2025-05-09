from odoo import api, fields, models, _


class ConcernActionWizard(models.TransientModel):
    _name = 'concern.action.wizard'
    _description = 'Wizard to create concern actions'

    name = fields.Char(string="Action Title", required=True)
    description = fields.Text(string="Action Description")
    action_date = fields.Date(string="Action Date", default=fields.Date.today, required=True)
    concern_type = fields.Selection([
        ('student', 'Student Concern'),
        ('employee', 'Employee Concern'),
        ('other', 'Other Concern')
    ], string="Concern Type", required=True)
    employee_report_id = fields.Many2one('employee.report', string="Related Report", required=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('canceled', 'Canceled')
    ], string="Status", default='in_progress', required=True)

    @api.model
    def default_get(self, fields_list):
        res = super(ConcernActionWizard, self).default_get(fields_list)
        active_id = self.env.context.get('active_id')
        if active_id:
            res['employee_report_id'] = active_id
        return res

    def action_apply(self):
        self.ensure_one()
        # Write all the wizard data to the employee.report record
        self.employee_report_id.write({
            'action_title': self.name,
            'action_description': self.description,
            'action_date': self.action_date,
            'action_state': self.state,
            'action_solved_by': self.env.user.employee_id.id,  # Set current user as solver
        })
        return {
            'type': 'ir.actions.act_window_close',
            'params': {
                'title': _('Success'),
                'message': _('Action recorded successfully!'),
                'type': 'success',
                'sticky': False,
            }
        }
    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})

    def action_mark_resolved(self):
        self.write({'state': 'resolved'})

    def action_mark_canceled(self):
        self.write({'state': 'canceled'})

    def action_reset_to_draft(self):
        self.write({'state': 'draft'})