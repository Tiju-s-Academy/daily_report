from odoo import api, fields, models, _

class EmployeeAdditionalManager(models.Model):
    _name = 'employee.additional.manager'
    _description = 'Additional Reporting Manager'
    
    name = fields.Char("Name", compute="_compute_name", store=True)
    employee_id = fields.Many2one('hr.employee', string="Employee", required=True, ondelete='cascade')
    manager_id = fields.Many2one('hr.employee', string="Additional Manager", required=True)
    notes = fields.Text("Notes")
    active = fields.Boolean(default=True)
    
    @api.depends('employee_id', 'manager_id')
    def _compute_name(self):
        for record in self:
            if record.employee_id and record.manager_id:
                record.name = f"{record.employee_id.name} → {record.manager_id.name}"
            else:
                record.name = "New Additional Manager"
    
    _sql_constraints = [
        ('unique_employee_manager', 'unique(employee_id, manager_id)', 
         'This manager is already assigned to this employee!')
    ]
