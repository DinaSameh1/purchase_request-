from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Orders(models.Model):
    _inherit = 'purchase.order'

    request_id = fields.Many2one(comodel_name='purchase.request', string='Request ID')


class OrderLine(models.Model):
    _inherit = 'purchase.order.line'

    request_line_id = fields.Many2one('purchase.request.line')
    product_quantity = fields.Integer(string='Quantity', default='1')
    @api.constrains('product_qty')
    def cons_qty(self):
        qty_sum = 0
        for rec in self:
            if rec.product_qty:
                x = self.env['purchase.order.line'].search([('request_line_id', '=', rec.request_line_id.id)])
                qty_sum = qty_sum + x.product_quantity
                if x.product_qty > rec.request_line_id.product_quantity:
                    raise ValidationError(_('This quantity is not accepted'))
                elif qty_sum > rec.request_line_id.product_quantity:
                    raise ValidationError(_('This quantity is not accepted'))
