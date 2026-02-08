from odoo import models, fields, api, _
from odoo.exceptions import UserError


class PayOrder(models.Model):
    _name = 'pay.order'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Pay Order'
    _order = 'id desc'

    # BASIC INFO
    name = fields.Char(string="Order #", default="New", readonly=True, tracking=True)
    date = fields.Date(default=fields.Date.today, tracking=True)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    # PROJECT
    project_id = fields.Many2one('project.project', required=True)
    stage_id = fields.Many2one('project.task.type', domain="[('project_ids','in',project_id)]")

    # VENDOR
    vendor_id = fields.Many2one('res.partner', required=True)
    vendor_mobile = fields.Char()
    vendor_bank_name = fields.Char()
    vendor_account_number = fields.Char()

    currency_id = fields.Many2one('res.currency', default=lambda self: self.env.company.currency_id)

    # LINES
    line_ids = fields.One2many('pay.order.line', 'pay_order_id')
    total_amount = fields.Monetary(
        compute="_compute_total",
        store=True,
        currency_field='currency_id'
    )

    # APPROVALS
    progress_notes = fields.Text()
    site_engineer_name = fields.Char(default=lambda self: self.env.user.name)
    project_engineer_name = fields.Char()

    cfo_approved_by = fields.Many2one('res.users')
    cfo_approved_date = fields.Datetime()

    # ACCOUNTING LINK
    vendor_bill_id = fields.Many2one('account.move', readonly=True)

    # WORKFLOW
    state = fields.Selection([
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('review', 'Under Review'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected')
    ], default='draft', tracking=True)

    # TOTAL COMPUTE
    @api.depends('line_ids.line_total')
    def _compute_total(self):
        for rec in self:
            rec.total_amount = sum(rec.line_ids.mapped('line_total'))

    # ONCHANGE
    @api.onchange('vendor_id')
    def _onchange_vendor(self):
        if self.vendor_id:
            self.vendor_mobile = self.vendor_id.mobile

    # SEQUENCE
    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('pay.order')
        return super().create(vals)

    # WORKFLOW ACTIONS
    def action_submit(self): self.state = 'submitted'
    def action_review(self): self.state = 'review'
    def action_reject(self): self.state = 'rejected'

    def action_approve(self):
        self.state = 'approved'
        self.cfo_approved_by = self.env.user
        self.cfo_approved_date = fields.Datetime.now()

    def action_paid(self): self.state = 'paid'

    # ACCOUNTING INTEGRATION
    def action_create_vendor_bill(self):
        self.ensure_one()

        if not self.vendor_id:
            raise UserError(_("Vendor required"))

        if not self.line_ids:
            raise UserError(_("Add at least one line before creating a bill."))

        if self.vendor_bill_id:
            raise UserError(_("Vendor Bill already exists."))

        bill_lines = [(0, 0, {
            'name': l.description,
            'quantity': l.quantity,
            'price_unit': l.price_unit,
        }) for l in self.line_ids]

        bill = self.env['account.move'].create({
            'move_type': 'in_invoice',
            'partner_id': self.vendor_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': bill_lines,
        })

        self.vendor_bill_id = bill.id

        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': bill.id,
            'view_mode': 'form',
        }

    def action_view_vendor_bill(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': self.vendor_bill_id.id,
            'view_mode': 'form',
        }
