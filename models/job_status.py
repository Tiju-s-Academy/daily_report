from odoo import fields, models

class JobStatus(models.Model):
    _name = 'job.status'
    _description = 'Job Status'
    _order = 'sequence, id'

    name = fields.Char('Status Name', required=True)
    active = fields.Boolean(default=True)
    sequence = fields.Integer(default=10)

