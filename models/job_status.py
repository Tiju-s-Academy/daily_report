from odoo import fields,models

class JobStatus(models.Model):
    _name = 'job.status'
    _description = 'Job Status'

    name = fields.Char('Status Name', required=True)

