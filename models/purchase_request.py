from odoo import fields, models, api


# Create new Model Called Purchase Request with a new menuitem called
# "Purchase Requests" placed under Purchase -> Orders menu
class PurchaseRequest(models.Model):
    _name = "purchase.request"
    _description = "It is a form to be filled to request a purchase"

    # mandatory means it is a required field
    name = fields.Char(string="Request Name", required=True)
    requested_by_id = fields.Many2one(comodel_name='res.users', string='Requested by', required=True)
    start_date = fields.Date(string='Request date', default=fields.Date.today, required=True)
    end_date = fields.Date(string='End date')
    # Rejection Reason should be readonly and invisible except in reject state.
    reject_reason = fields.Text(string="Reject Reason")
    # total price is the sum of order lines total that we computed it in purchase.request.line model
    total_price = fields.Float(string="Total Price", required=True, compute="sum_total", )
    # request_lines_ids One to Many field from (Purchase Request Line)
    request_lines_ids = fields.One2many("purchase.request.line", "purchase_request_line_id", string="Request Line")
    # po_ids = fields.One2many(comodel_name="purchase.order", inverse_name="request_id", string="po_ids", required=False)

    # these fields are mandatory in purchase order model that we inherited our order model from
    partner_id = fields.Many2one('res.partner', string='Vendor', required=True)
    partner_ref = fields.Char('Vendor Reference', copy=False)
    company_id = fields.Many2one('res.company', 'Company', required=True)
    currency_id = fields.Many2one('res.currency', 'Currency', required=True)

    # po_count field is (to show the related number of created purchase orders)
    po_count = fields.Integer(string="Purchase Orders Count", compute='compute_count')
    state = fields.Selection([
        ("draft", "Draft"),
        ("to_be_approved", "To be Approved"),
        ("approve", "Approve"),
        ("reject", "Reject"),
        ("cancel", "Cancel"),
    ], default="draft")

    def action_submit(self):
        for record in self:
            record.state = 'to_be_approved'

    def action_cancel(self):
        for record in self:
            record.state = 'cancel'

    def action_approve(self):
        template = self.env.ref('purchase_request.purchase_request_mail_template')
        for record in self:
            if record.requested_by_id.email:
                email_values = {'subject': 'Purchases Request',
                                'email_from': record.env.user.email,
                                'email_to': record.env.ref('purchase.group_purchase_manager')}
                template.send_mail(record.id, force_send=True, email_values=email_values)
            record.state = 'approve'

    # if we pressed Create PO button a new draft PO "purchase.order" (model already exists,
    # you have to install purchase module), will be created with the same values as the PR
    def action_create_purchase_order(self):
        # this list to take the values of all lines
        lines = []
        for line in self.request_lines_ids:
            lines.append((0, 0, {
                "product_id": line.product_id.id,
                "name": line.product_description or line.product_id.name,
                "price_unit": line.cost_price,
                "product_qty": line.product_quantity,
                "request_line_id": line.id,
            }))
        vals = {
            # key: value
            "request_id": self.id,
            "name": self.name,
            "user_id": self.requested_by_id.id,
            "date_order": self.start_date,
            "date_approve": self.end_date,
            # it is a required field in purchase order model that we inherited our order model from
            "partner_id": self.partner_id.id,
            "partner_ref": self.partner_ref,
            # purchase request send to purchase order - request_lines_ids it is like order_line
            "currency_id": self.currency_id.id,
            "company_id": self.company_id.id,
            "order_line": lines,  # lines came from upper list
        }
        x = self.env['purchase.order'].create(vals)
        return self.action_view_po()

    def action_reject(self):
        for record in self:
            record.state = 'reject'

    def action_reset_to_default(self):
        for record in self:
            record.state = 'draft'

    # if smart button pressed, a tree view will be shown for the related created POs
    def action_view_po(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Orders',
            'res_model': 'purchase.order',
            'view_mode': 'list,form',
            'context': {},
            'domain': [('request_id', '=', self.id)],
            'target': 'current',
        }

    def compute_count(self):
        for record in self:
            record.po_count = self.env['purchase.order'].search_count([('request_id', '=', self.id)])

    @api.depends('request_lines_ids')
    def sum_total(self):
        for rec in self:
            total_price = 0.0
            for line in rec.request_lines_ids:
                total_price += line.total  # line.total is total that we computed it in purchase.request.line model
            rec.total_price = total_price


class PurchaseRequestLine(models.Model):
    _name = "purchase.request.line"
    _description = "Select the purchases that you want"

    # product_id is a Many2one field from product.product model, and it is a mandatory field
    product_id = fields.Many2one("product.product", required=1)
    # Description is a Char field takes name of selected product
    product_description = fields.Text(string="Description")
    product_quantity = fields.Integer(string='Quantity', default='1')
    # cost_price is a readonly field that reads from products cost price
    cost_price = fields.Float(string="Cost Price", readonly=1, related="product_id.standard_price")
    # total is a readonly field, it's value comes from quantity * cost price
    total = fields.Float(string="Total", readonly=1, compute="_get_price_total")
    purchase_request_line_id = fields.Many2one("purchase.request")

    @api.depends("cost_price", "product_quantity")
    def _get_price_total(self):
        for rec in self:
            rec.total = rec.product_quantity * rec.cost_price
