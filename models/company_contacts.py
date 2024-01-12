# -*- coding: utf-8 -*-

from odoo import models, fields, api, _, exceptions, tools
from datetime import date, timedelta, datetime
from random import randint


class CompanyContacts(models.Model):
    _name = 'company.contacts'
    _inherit = [
        'mail.thread',  # views.xml message_ids ve message_follower_ids'yi görmesi için inherit edildi.
        'mail.activity.mixin'  # views.xml activity_ids'yi görmesi için inherit edildi.
    ]
    _description = 'Customers & Suppliers'
    _rec_name = 'name'

    def _get_default_color(self):
        return randint(1, 11)

    @api.model
    def default_get(self, default_fields):
        """Add the company of the parent as default if we are creating a child partner.
        Also take the parent lang by default if any, otherwise, fallback to default DB lang."""
        values = super().default_get(default_fields)
        parent = self.env["company.contacts"]
        if 'parent_id' in default_fields and values.get('parent_id'):
            parent = self.browse(values.get('parent_id'))
            values['company_id'] = parent.company_id.id
        return values

    @api.model
    def create(self, vals):
        rec = super(CompanyContacts, self).create(vals)
        rec.compute_address()
        return rec

    name = fields.Char(index=True)
    display_name = fields.Char(compute='_compute_display_name', recursive=True, store=True, index=True)
    parent_id = fields.Many2one('company.contacts', string='Related Company', index=True)
    parent_name = fields.Char(related='parent_id.name', readonly=True, string='Parent name')
    child_ids = fields.One2many('company.contacts', 'parent_id', string='Contact', domain=[
        ('active', '=', True)])
    user_id = fields.Char(string='Satış Sorumlusu',
                              help='Şirket bünyesinde çalışan ve tedarikçi ile ilgilenecek kişi.')
    user_id_team = fields.Char(string='Satış Ekibi')
    marketing_campaign = fields.Char(string='Kampanya')
    marketing_medium = fields.Char(string='Ortam')
    payment_method = fields.Char(string='Ödeme Yöntemi')
    website = fields.Char('Website Link')
    comment = fields.Html(string='Notes')
    active = fields.Boolean(default=True)
    image = fields.Image()
    function = fields.Char(string='Pozisyonu')

    street = fields.Char()
    street2 = fields.Char()
    city = fields.Char()
    state = fields.Char()
    zip = fields.Char()
    country_id = fields.Many2one('res.country', string='Country')

    country_code = fields.Char(related='country_id.code', string="Country Code")
    email = fields.Char()
    email_formatted = fields.Char('Formatted Email', compute='_compute_email_formatted')
    phone = fields.Char(string='Telefon')

    is_company = fields.Boolean(string='Is a Company', default=False)
    company_type = fields.Selection(string='Company Type',
                                    selection=[('person', 'Individual'), ('company', 'Company')],
                                    compute='_compute_company_type', inverse='_write_company_type', store=True)

    contact_type = fields.Selection([
        ('customer', 'Customer'),
        ('supplier', 'Supplier'),

    ], string="Contact Type",
    )

    company_id = fields.Many2one('res.company', 'Company', index=True)
    color = fields.Integer(string='Color Index', default=_get_default_color)
    user_ids = fields.One2many('res.users', 'partner_id', string='Users', auto_join=True)
    contact_address = fields.Char(string='Complete Address')
    company_name = fields.Char('Company Name')

    def address_get(self, adr_pref=None):
        """ Find contacts/addresses of the right type(s) by doing a depth-first-search
        through descendants within company boundaries (stop at entities flagged ``is_company``)
        then continuing the search at the ancestors that are within the same company boundaries.
        Defaults to partners of type ``'default'`` when the exact type is not found, or to the
        provided partner itself if no type ``'default'`` is found either. """
        adr_pref = set(adr_pref or [])
        if 'contact' not in adr_pref:  # Contact zaten listede olmayacak IF adr_pref'e uygun olması açısından yapıldı.
            adr_pref.add('contact')
        result = {}
        visited = set()
        for partner in self:
            current_partner = partner
            # Child Scan
            while current_partner:
                to_scan = [current_partner]
                while to_scan:
                    record = to_scan.pop(0)
                    visited.add(record)
                    if len(result) == len(adr_pref):
                        return result
                    to_scan = [c for c in record.child_ids
                               if c not in visited
                               if not c.is_company] + to_scan
                # Parent Scan - Mevcut kayıt olmadığı takdirde aramaya devam eder.
                if current_partner.is_company or not current_partner.parent_id:
                    break
                current_partner = current_partner.parent_id
        default = result.get('contact', self.id or False)
        for adr_type in adr_pref:
            result[adr_type] = result.get(adr_type) or default
        return result

    def _get_company_address_field_names(self):
        """ Return a list of fields coming from the address partner to match
        on company address fields. Fields are labeled same on both models. """
        return ['street', 'street2', 'city', 'zip', 'state', 'country_id']

    def _get_company_address_update(self, partner):
        return dict((fname, partner[fname])
                    for fname in self._get_company_address_field_names())

    def compute_address(self):
        for company in self.filtered(lambda company: company.parent_id):
            address_data = company.parent_id.sudo().address_get(adr_pref=['contact'])
            if address_data['contact']:
                partner = company.parent_id.browse(address_data['contact']).sudo()
                company.update(company._get_company_address_update(partner))

    @api.depends('is_company', 'name', 'parent_id.display_name', 'company_name')
    def _compute_display_name(self):
        diff = dict(show_address=None, show_address_only=None, show_email=None, html_format=None)
        names = dict(self.with_context(**diff).name_get())
        for partner in self:
            partner.display_name = names.get(partner.id)

    @api.depends('name', 'email')
    def _compute_email_formatted(self):
        for partner in self:
            if partner.email:
                partner.email_formatted = tools.formataddr((partner.name or u"False", partner.email or u"False"))
            else:
                partner.email_formatted = ''

    @api.depends('is_company')
    def _compute_company_type(self):
        for partner in self:
            partner.company_type = 'company' if partner.is_company else 'person'

    def _write_company_type(self):
        for partner in self:
            partner.is_company = partner.company_type == 'company'

    @api.model
    def _fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        if (not view_id) and (view_type == 'form') and self._context.get('force_email'):
            view_id = self.env.ref('base.view_partner_simple_form').id
        res = super(CompanyContacts, self)._fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                            submenu=submenu)
        return res

    @api.onchange('parent_id', 'company_id')
    def _onchange_company_id(self):
        if self.parent_id:
            self.company_id = self.parent_id.company_id.id

    @api.onchange('company_type')
    def onchange_company_type(self):
        self.is_company = (self.company_type == 'company')
