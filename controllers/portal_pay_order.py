from odoo import http
from odoo.http import request


class PortalPayOrder(http.Controller):

    # LIST PAGE
    @http.route(['/my/pay_orders'], type='http', auth="user", website=True)
    def portal_pay_orders(self, **kw):
        orders = request.env['pay.order'].sudo().search([
            ('create_uid', '=', request.env.user.id)
        ])
        return request.render("pay_order.portal_my_pay_orders", {
            'pay_orders': orders
        })

    # CREATE FORM PAGE
    @http.route(['/my/pay_orders/new'], type='http', auth="user", website=True)
    def portal_pay_order_form(self, **kw):
        projects = request.env['project.project'].sudo().search([])
        vendors = request.env['res.partner'].sudo().search([('supplier_rank', '>', 0)])
        return request.render("pay_order.portal_pay_order_create", {
            'projects': projects,
            'vendors': vendors,
        })

    # SAVE FORM
    @http.route(['/my/pay_orders/submit'], type='http', auth="user", website=True, methods=['POST'])
    def portal_pay_order_submit(self, **post):
        order = request.env['pay.order'].sudo().create({
            'project_id': int(post.get('project_id')),
            'vendor_id': int(post.get('vendor_id')),
            'progress_notes': post.get('progress_notes'),
        })

        # Add one line (basic)
        request.env['pay.order.line'].sudo().create({
            'pay_order_id': order.id,
            'description': post.get('description'),
            'quantity': float(post.get('quantity')),
            'price_unit': float(post.get('price')),
        })

        order.action_submit()

        return request.redirect('/my/pay_orders')
