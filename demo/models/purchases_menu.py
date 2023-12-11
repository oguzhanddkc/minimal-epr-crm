# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import json


class PurchasesMenu(models.Model):
    _name = "purchases.menu"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "RFQ"
    _order = "id desc"
    _rec_name = 'reference_code'

    # first widget -----------------------------------------------------------------------
    reference_code = fields.Char(string='Reference Code', required=True, copy=False, readonly=True,
                                 default=lambda self: _('New RFQ'))
    purchase_type = fields.Selection([
        ('0', 'Full Step Project'),
        ('01', 'Short Step Project'),
        ('1', 'Teklif'),
        ('2', 'Genel Gider'),
        ('3', 'Yatırım'),
        ('4', 'Finansman'),
    ], string="Satın Alma Türü", default="0", required=True)

    # second widget -----------------------------------------------------------------------
    created_by = fields.Char(string='Created By: ')
    department = fields.Selection([
        ('adet', 'Adet'),
        ('metre', 'Metre'),
        ('litre', 'Litre'),
        ('metrekare', 'Metrekare'),
        ('kg', 'Kg'),
    ], string="Unit: ", tracking=True, default='adet', store=True, required=True)

    state = fields.Selection([
        ('rfq', 'RFQ'),
        ('po', 'Purchase Order'),
        ('cancel', 'Cancel')
    ],
        default="rfq",
        string="Status",
        tracking=True
    )
    purchase_date = fields.Date(string='Order Date', default=fields.Datetime.now, readonly=True)
    product_name_id = fields.Many2one('approved.products', string='Product Name')
    contact_id = fields.Many2one('company.contacts', string="Contact Name")
    price = fields.Float(compute="_compute_price", string="Price")
    contact_id_domain = fields.Char(compute="_compute_contact_id_domain", readonly=True, store=False)

    @api.depends('contact_id')
    def _compute_price(self):
        lines = self.purchased_product_ids.search([('name', '=', self.contact_id.name)])
        for rec in self:
            rec.price = lines.price

    @api.depends('product_name_id')
    def _compute_contact_id_domain(self):
        lines = self.purchased_product_ids
        domain = []
        for line in lines:
            domain.append(line.display_name)

        for rec in self:
            rec.contact_id_domain = json.dumps([('name', 'in', domain)])

    def action_rfq(self):
        for rec in self:
            rec.state = 'rfq'

    def action_po(self):
        for rec in self:
            rec.state = 'po'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'

    @api.model
    def create(self, vals):
        if vals.get('reference_code', _('New RFQ')) == _('New RFQ'):
            vals['reference_code'] = self.env['ir.sequence'].next_by_code('seq.purchases.menu') or _('New RFQ')
        res = super(PurchasesMenu, self).create(vals)
        return res

    purchased_product_ids = fields.One2many(related="product_name_id.contacts_ids",
                                            string="Supplier and Customer Lines")
