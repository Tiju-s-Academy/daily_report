from odoo import models, fields, api

class DepartmentDashboard(models.Model):
    _name = 'department.dashboard'
    _description = 'Department Dashboard'

    name = fields.Many2one('hr.department', string="Department", required=True)
    employee_count = fields.Integer(string="Employee Count", compute="_compute_employee_count", store=True)
    total_reports_today = fields.Integer(string="Total Reports Today", compute="_compute_total_reports_today", store=True)
    total_support_staff_today = fields.Integer(string="Total Support Staff Today", compute="_compute_total_support_staff_today", store=True)
    not_submitted_count = fields.Integer(string="Not Submitted Count", compute="_compute_not_submitted_count", store=True)

    @api.depends('name')
    def _compute_not_submitted_count(self):
        for record in self:
            today = fields.Date.today()
            # Get all employees in the department
            employees = self.env['hr.employee'].search([('department_id', '=', record.name.id)])
            # Get employees who have submitted reports today
            submitted_employees = self.env['employee.report'].search([
                ('department_id', '=', record.name.id),
                ('date', '=', today)
            ]).mapped('name')
            # Calculate not submitted employees
            record.not_submitted_count = len(employees) - len(submitted_employees)

    def action_open_not_submitted_employees(self):
        today = fields.Date.today()
        # Get all employees in the department
        employees = self.env['hr.employee'].search([('department_id', '=', self.name.id)])
        # Get employees who have submitted reports today
        submitted_employees = self.env['employee.report'].search([
            ('department_id', '=', self.name.id),
            ('date', '=', today)
        ]).mapped('name')
        # Find employees who have not submitted reports
        not_submitted_employees = employees - submitted_employees

        # Return an action to open the list view of not submitted employees
        return {
            'type': 'ir.actions.act_window',
            'name': 'Not Submitted Employees',
            'res_model': 'hr.employee',
            'view_mode': 'tree,form',
            'domain': [('id', 'in', not_submitted_employees.ids)],
            'target': 'current',
        }