from odoo import api, fields, models, tools
import logging

_logger = logging.getLogger(__name__)

class ConcernAction(models.Model):
    """
    This model is a placeholder to handle migration from previous versions
    where 'concern.action' might have existed. It helps prevent KeyError during upgrades.
    """
    _name = 'concern.action'
    _description = 'Concern Action (Legacy)'
    
    name = fields.Char("Title")
    description = fields.Text("Description")
    
    @api.model
    def _clean_up_old_records(self):
        """Clean up any old IR records that point to this model"""
        _logger.info("Cleaning up old concern.action references")
        try:
            # Clean up any ir.model.data records that point to this model
            self.env.cr.execute("""
                DELETE FROM ir_model_data
                WHERE model = 'concern.action';
            """)
            
            # Clean up any ir.model.fields that reference this model
            self.env.cr.execute("""
                DELETE FROM ir_model_fields
                WHERE relation = 'concern.action';
            """)
            
            # Get the model ID for concern.action
            self.env.cr.execute("""
                SELECT id FROM ir_model WHERE model = 'concern.action'
            """)
            model_id = self.env.cr.fetchone()
            
            if model_id:
                model_id = model_id[0]
                # Clean up any ir.model.constraint records
                self.env.cr.execute("""
                    DELETE FROM ir_model_constraint
                    WHERE model = %s
                """, (model_id,))
                
                # Clean up any ir.model.relation records
                self.env.cr.execute("""
                    DELETE FROM ir_model_relation
                    WHERE model = %s
                """, (model_id,))
        except Exception as e:
            _logger.error("Error cleaning up concern.action references: %s", e)
    
    def init(self):
        """Initialize the model during installation or upgrade"""
        # During module installation/upgrade, clean up any old references
        if not tools.config.get('without_demo', False):
            self._clean_up_old_records()
