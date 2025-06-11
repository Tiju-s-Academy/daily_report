from odoo import api, fields, models, tools, _
import logging

_logger = logging.getLogger(__name__)

class ConcernAction(models.Model):
    """
    This model is a placeholder to handle migration from previous versions
    where 'concern.action' might have existed. It helps prevent KeyError during upgrades.
    
    Instead of deleting the model entirely, we keep it as a compatibility layer with
    all fields that might have been referenced in the database.
    """
    _name = 'concern.action'
    _description = 'Concern Action (Legacy)'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    
    # Fields that might have existed in the previous version
    name = fields.Char("Title", tracking=True)
    description = fields.Text("Description", tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('canceled', 'Canceled')
    ], string="Status", default='draft', tracking=True)
    action_date = fields.Date("Action Date", tracking=True)
    employee_report_id = fields.Many2one('employee.report', string="Related Report", tracking=True)
    concern_type = fields.Selection([
        ('student', 'Student Concern'),
        ('employee', 'Employee Concern'),
        ('other', 'Other Concern')
    ], string="Concern Type", tracking=True)
    
    # Add any other fields that might have been in the original model
    active = fields.Boolean(default=True)
    create_date = fields.Datetime("Created On", readonly=True)
    
    def action_mark_in_progress(self):
        self.write({'state': 'in_progress'})
        
    def action_mark_resolved(self):
        self.write({'state': 'resolved'})
        
    def action_mark_canceled(self):
        self.write({'state': 'canceled'})
        
    def action_reset_to_draft(self):
        self.write({'state': 'draft'})
    
    @api.model
    def _migrate_to_wizard(self):
        """
        Migrate any existing concern.action records to concern.action.wizard
        This ensures no data is lost during the upgrade
        """
        _logger.info("Checking for legacy concern.action records to migrate")
        try:
            # First check if this table exists
            self.env.cr.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'concern_action'
                );
            """)
            table_exists = self.env.cr.fetchone()[0]
            
            if table_exists:
                # Migrate data to the wizard model
                self.env.cr.execute("""
                    INSERT INTO concern_action_wizard 
                    (name, description, state, action_date, concern_type, employee_report_id, create_uid, create_date, write_uid, write_date)
                    SELECT name, description, state, action_date, concern_type, employee_report_id, create_uid, create_date, write_uid, write_date
                    FROM concern_action
                    WHERE id NOT IN (
                        SELECT ca.id FROM concern_action ca
                        JOIN concern_action_wizard caw ON ca.name = caw.name 
                                                      AND ca.employee_report_id = caw.employee_report_id
                                                      AND ca.action_date = caw.action_date
                    )
                """)
                _logger.info("Migration of concern.action data completed")
        except Exception as e:
            _logger.error("Error migrating concern.action data: %s", str(e))
    
    def init(self):
        """Initialize the model during installation or upgrade"""
        super(ConcernAction, self).init()
        # Migrate any existing data
        self._migrate_to_wizard()
