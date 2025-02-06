from  odoo import models,fields,_
from odoo.exceptions import UserError


class ReportRejectWizard(models.Model):
    _name = 'report.reject.wizard'

    description = fields.Text(string="Reason",required=True)
    employee_report_id = fields.Many2one('employee.report', string='Employee Report', readonly=True)

    def action_reject_report(self):
        if self.employee_report_id:
            self.employee_report_id.write({
                'reject_reason': self.description,
                'state': 'draft',
            })

            return {
                'type': 'ir.actions.client',
                'tag': 'reload',
            }









