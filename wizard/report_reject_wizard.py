from  odoo import models,fields,_
from odoo.exceptions import UserError


class ReportRejectWizard(models.Model):
    _name = 'report.reject.wizard'

    description = fields.Text(string="Reason",required=True)
    employee_report_id = fields.Many2one('employee.report', string='Employee Report', readonly=True)

    def action_reject_report(self):
        if self.employee_report_id:
            today = fields.Date.today()
            print("hellooo")
            if self.employee_report_id.date != today:
                raise UserError(_("You can only reject today's Reports"))
            self.employee_report_id.write({
                'reject_reason': self.description,
                'state': 'draft',
            })
            # activities = self.env['mail.activity'].search([
            #     ('res_id', '=', self.employee_report_id.id),
            #     ('res_model', '=', 'employee.report'),
            # ])

            # Unlink the activities
            # if activities:
            #     activities.unlink()

            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }





