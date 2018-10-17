# -*- coding: utf-8 -*-
# Copyright 2017 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo import report


class TestAccountInvoiceReport(TransactionCase):
    def setUp(self, *args, **kwargs):
        super(TestAccountInvoiceReport, self).setUp()
        self.base_comment_model = self.env['base.comment.template']
        self.before_comment = self._create_comment('before_lines')
        self.after_comment = self._create_comment('after_lines')
        self.partner_id = self.env['res.partner'].create({
            'name': 'Partner Test'
        })
        self.sale_order = self.env.ref('sale.sale_order_7')
        self.sale_order.update({
            'comment_template1_id': self.before_comment.id,
            'comment_template2_id': self.after_comment.id
        })
        self.sale_order._set_note1()
        self.sale_order._set_note2()

        self.invoice_ids = self.sale_order.action_invoice_create()

    def _create_comment(self, position):
        return self.base_comment_model.create({
            'name': 'Comment ' + position,
            'position': position,
            'text': 'Text ' + position
        })

    def test_comments_in_sale_order(self):
        (res, _) = report. \
            render_report(self.env.cr, self.env.uid,
                          [self.sale_order.id], 'sale.report_saleorder', {})
        self.assertRegexpMatches(res, self.before_comment.text)
        self.assertRegexpMatches(res, self.after_comment.text)

    def test_comments_in_generated_invoice(self):
        (res, _) = report. \
            render_report(self.env.cr, self.env.uid,
                          self.invoice_ids, 'account.report_invoice', {})
        self.assertRegexpMatches(res, self.before_comment.text)
        self.assertRegexpMatches(res, self.after_comment.text)

    def test_onchange_partner_id(self):
        self.partner_id.comment_template_id = self.after_comment.id
        vals = {
            'partner_id': self.partner_id.id,
        }
        new_sale = self.env['sale.order'].new(vals)
        new_sale.onchange_partner_id_sale_comment()
        sale_dict = new_sale._convert_to_write(new_sale._cache)
        new_sale = self.env['sale.order'].create(sale_dict)
        self.assertEqual(new_sale.comment_template2_id, self.after_comment)
        self.partner_id.comment_template_id = self.before_comment.id
        new_sale = self.env['sale.order'].new(vals)
        new_sale.onchange_partner_id_sale_comment()
        sale_dict = new_sale._convert_to_write(new_sale._cache)
        new_sale = self.env['sale.order'].create(sale_dict)
        self.assertEqual(new_sale.comment_template1_id, self.before_comment)
