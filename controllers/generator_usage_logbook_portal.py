# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from collections import OrderedDict

from odoo import http, _
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from odoo.osv.expression import OR

class CustomerPortal(CustomerPortal):

    def _prepare_portal_layout_values(self):
        values = super(CustomerPortal, self)._prepare_portal_layout_values()
        domain = []
        generator_usage_logbooks_count = request.env['generator.usage.logbook'].search_count(domain)
        values['generator_usage_logbooks_count'] = generator_usage_logbooks_count
        return values

    @http.route(['/my/generator_usage_logbooks', '/my/generator_usage_logbooks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_generator_usage_logbooks(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):
        domain = []
        values = self._prepare_portal_layout_values()
        ISYGeneratorUsageLogbook = request.env['generator.usage.logbook']

        #domain needo to modify for create user records only.
        searchbar_filters = {
            'all': {'label': _('All Status'), 'domain': []},
            'generator_location_isy': {'label': _('ISY'), 'domain': [('generator_location', '=', 'isy')]},
            'generator_location_residence': {'label': _('Housing/Residence'), 'domain': [('generator_location', '=', 'residence')]},
            }

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'generator_location': {'label': _('Location'), 'order': 'generator_location'},
        }

        searchbar_inputs = {
            'generator_location': {'input': 'generator_location', 'label': _('Search <span class="nolabel"> (in Location)</span>')},
            'name': {'input': 'name', 'label': _('Search in Ref #')},
            'all': {'input': 'all', 'label': _('Search in All')},
        }
        # domain += ['|', ('create_uid', '=', request.env.user.id), ('driver_id', '=', request.env.user.id)]
        domain += []
        # default sort by date
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']
        # default filter by value
        if not filterby:
            filterby = 'all'
        domain += searchbar_filters[filterby]['domain']

        # search
        if search and search_in:
            search_domain = []
            if search_in in ('generator_location', 'all'):
                search_domain = OR([search_domain, [('generator_location', 'ilike', search)]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        generator_usage_logbooks_count = ISYGeneratorUsageLogbook.sudo().search_count(domain)
        # pager

        pager = portal_pager(
            url="/my/generator_usage_logbooks",
            url_args={'sortby': sortby},
            total=generator_usage_logbooks_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        generator_usage_logbooks = ISYGeneratorUsageLogbook.sudo().search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_generator_usage_logbooks_history'] = generator_usage_logbooks.ids[:100]

        values.update({
            'generator_usage_logbooks': generator_usage_logbooks,
            'page_name': 'generator_usage_logbook',
            'pager': pager,
            'default_url': '/my/generator_usage_logbooks',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby
        })
        return request.render("isy_ticketing.portal_my_generator_usage_logbook", values)
