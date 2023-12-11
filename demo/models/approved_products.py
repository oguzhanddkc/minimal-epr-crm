# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class ApprovedProducts(models.Model):
    _name = "approved.products"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Approved Products"
    _order = "id desc"
    _rec_name = 'product_name'

    # first widget -----------------------------------------------------------------------
    reference_code = fields.Char(string='Reference Code', required=True, copy=False, readonly=True,
                                 default=lambda self: _('New Product'))
    product_image = fields.Image(string="Parça Resmi", tracking=True)
    created_by = fields.Char(string='Formu Oluşturan: ')
    product_type = fields.Selection([
        ('0', "Ürün Türünü Seçiniz"),
        ('1', "1 - Dünya Çapında Geçerli Ürünler"),
        ('2', "2 - Dünya Çapında Geçerli Hammadeler"),
        ('3', "3 - Spesifik Ürünler")
    ], string="Ürün Türü: ", default="0")
    product_class = fields.Selection([
        ('A', 'A Grubu Ürünler: Detaylı kontrol edilmesi gerekenler (Ölçüsel Kontrol, Estetik, Fonksiyonel)'),
        ('B', 'B Grubu Ürünler: Kontrol edilmesi gerekenler ((Ölçüsel Kontrol (Boy, çap, kalınlık, hatve adım))'),
        ('C',
         'C Grubu Ürünler: Kalite kontrol gerektirmeyenler (Boy Ölçüsü, irsaliye (sayı ve ürün kodu), satın alma formu, ezik, kırık) sevkiyat birimi tarafından kontrolü yapılmaktadır.'),
    ], string="Grup: ", store=True, tracking=True)
    can_be_purchased = fields.Boolean(string="Can Be Purchased", default=False)
    can_be_sold = fields.Boolean(string="Can Be Sold", default=False)

    # product information -------------------------------------------------------------------
    product_name = fields.Char(string='Ürün Adı')
    brand = fields.Char(string="Marka: ", required=True)
    product_code = fields.Char(string="Model / Ürün Kodu: ", tracking=True, required=True)
    technical_details = fields.Text(string="Teknik Özellikler: ", tracking=True, store=True, required=True)
    length_of_term = fields.Char(string="Termin Süresi: ")
    unit = fields.Selection([
        ('adet', 'Adet'),
        ('metre', 'Metre'),
        ('litre', 'Litre'),
        ('metrekare', 'Metrekare'),
        ('kg', 'Kg'),
    ], string="Birim: ", tracking=True, default='adet', store=True, required=True)

    # buy page --------------------------------------------------------------------------------

    # buy page - price section ----------------------------------------------------------------
    currency_type = fields.Selection([
        ('try', 'Türk Lirası'),
        ('eur', 'Euro'),
        ('usd', 'Dolar'),
    ], string='Döviz Cinsi: ', required=True, default="try")
    exchange_rate_euro = fields.Float(string='Döviz Kuru (€)', readonly=True, store=True)
    exchange_rate_dollar = fields.Float(string='Dolar Kuru ($)', readonly=True, store=True)
    unit_price = fields.Float(string="Birim Fiyat: ", tracking=True, store=True)
    unit_price_eur = fields.Float(string="Birim Fiyat(€): ", tracking=True, store=True)

    # buy page - stock section ----------------------------------------------------------------
    is_stocked = fields.Selection([
        ('0', 'Hayır'),
        ('1', 'Evet'),
    ], string="Stoklu mu?: ", default="0")

    # teknik data sheet page ------------------------------------------------------------------
    technical_datasheet = fields.Binary("Teknik Data Sheet:")

    # statinfo widgets ------------------------------------------------------------------------
    quantity_widget = fields.Integer(string='Stoktaki Miktar')
    purchased_quantity_widget = fields.Integer(string='Satın Alınan Miktar')

    @api.model
    def create(self, vals):
        if vals.get('reference_code', _('New Product')) == _('New Product'):
            vals['reference_code'] = self.env['ir.sequence'].next_by_code('seq.approved.products') or _('New Product')
        res = super(ApprovedProducts, self).create(vals)
        return res

    def action_quantity_widget(self):
        return {
            'name': _('Stok'),
            'res_model': 'approved.products',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    def action_purchased_quantity_widget(self):
        return {
            'name': _('Stok'),
            'res_model': 'approved.products',
            'view_mode': 'tree',
            'type': 'ir.actions.act_window',
            'target': 'current'
        }

    contacts_ids = fields.One2many('product.contact.lines', 'contact_id',
                                                string="Supplier and Customer Lines")


class ProductContact(models.Model):
    _name = "product.contact.lines"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Product Customer Or Supplier Lines"

    contact_id = fields.Many2one('approved.products', string="Line id")
    name = fields.Many2one('company.contacts', string="Supplier Or Customer Name")
    contact_type = fields.Selection(related="name.contact_type")
    price = fields.Float('Price')

