from odoo import models, fields, api

class DepartmentDashboard(models.Model):
    _name = 'department.dashboard'
    _description = 'Department Dashboard'

    name = fields.Many2one('hr.department', string="Department", required=True)
    employee_count = fields.Integer(string="Total Employees", compute="_compute_employee_count", store=True)
    total_reports_today = fields.Integer(string="Reports Submitted Today", compute="_compute_total_reports_today", store=True)
    not_submitted_count = fields.Integer(string="Not Submitted Reports Today", compute="_compute_not_submitted_count", store=True)


    @api.depends('name')
    def _compute_employee_count(self):
        """ Computes the total number of employees in the department """
        for record in self:
            print("hellooo")
            record.employee_count = self.env['hr.employee'].search_count([('department_id', '=', record.name.id)])

    @api.depends('name')
    def _compute_total_reports_today(self):
        """ Computes the total number of reports submitted today for the department """
        today = fields.Date.today()
        for record in self:
            print("hellooo2")
            record.total_reports_today = self.env['employee.report'].search_count([
                ('department_id', '=', record.name.id),
                ('date', '=', today)
            ])

    @api.depends('name')
    def _compute_not_submitted_count(self):
        """ Computes employees who have not submitted reports today """
        today = fields.Date.today()
        for record in self:
            total_employees = self.env['hr.employee'].search_count([('department_id', '=', record.name.id)])
            submitted_reports = self.env['employee.report'].search([
                ('department_id', '=', record.name.id),
                ('date', '=', today)
            ]).mapped('employee_id')
            record.not_submitted_count = total_employees - len(submitted_reports)


    def action_open_employee_list(self):
        """ Opens the list view of employees in the department """
        return {
            'type': 'ir.actions.act_window',
            'name': 'Employees',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('department_id', '=', self.name.id)],
            'target': 'current',
        }
