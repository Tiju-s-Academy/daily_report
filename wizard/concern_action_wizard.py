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
    
    def action_create(self):
        self.ensure_one()
        vals = {
            'name': self.name,
            'description': self.description,
            'action_date': self.action_date,
            'concern_type': self.concern_type,
            'employee_report_id': self.employee_report_id.id,
            'state': self.state,
        }
        action = self.env['concern.action'].create(vals)
        return {
            'type': 'ir.actions.act_window_close',
            'infos': {'success': True, 'message': _('Action recorded successfully!')}
        }
