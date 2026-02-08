from odoo import models, fields, api


class PayOrderLine(models.Model):
    _name = 'pay.order.line'
    _description = 'Pay Order Line'
    _order = 'sequence, id'   # lines ordered properly

    pay_order_id = fields.Many2one(
        'pay.order',
        string="Pay Order",
        ondelete='cascade',
        required=True
    )

    sequence = fields.Integer(string="#", default=10)

    description = fields.Char(
        string="Item & Description",
        required=True
    )

    uom_id = fields.Many2one(
        'uom.uom',
        string="Unit"
    )

    quantity = fields.Float(
        string="Qty",
        default=1
    )

    price_unit = fields.Float(
        string="Unit Price"
    )

    line_total = fields.Float(
        string="Total",
        compute="_compute_total",
        store=True
    )

    is_deduction = fields.Boolean(
        string="Deduction"
    )

    # 🔢 COMPUTE TOTAL
    @api.depends('quantity', 'price_unit', 'is_deduction')
    def _compute_total(self):
        for line in self:
            total = line.quantity * line.price_unit
            if line.is_deduction:
                total = -total
            line.line_total = total
