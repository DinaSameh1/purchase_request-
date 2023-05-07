from odoo import api, models, fields


class RejectionReasons(models.TransientModel):
    _name = "rejection.reason"
    _description = "Write all the reasons for rejecting this purchase"

    reject_reasons = fields.Text(string='Rejection Reasons', required=True)

    # this function will execute when we press on wizard Cancel button, it will just close the wizard
    def action_cancel(self):
        return

    # this function will execute when we press on wizard Confirm button
    def action_create_field(self):
        purchase = self.env['purchase.request'].browse(self._context.get('active_id'))
        purchase.state = 'reject'
        # set the purchase request rejection reason field with the value entered in the wizard.
        purchase.reject_reason = self.reject_reasons

