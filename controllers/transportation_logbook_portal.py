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
        transportation_logbooks_count = request.env['transportation.logbook'].search_count(domain)
        values['transportation_logbooks_count'] = transportation_logbooks_count
        return values

    @http.route(['/my/transportation_logbooks', '/my/transportation_logbooks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_transportation_logbooks(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):
        domain = []
        values = self._prepare_portal_layout_values()
        ISYTransportationLogbook = request.env['transportation.logbook']

        #domain needo to modify for create user records only.
        searchbar_filters = {
            'all': {'label': _('All Status'), 'domain': []},
            'destination_id': {'label': _('Destination'), 'domain': [('destination_id', 'ilike', search)]},
            'vehicle_id': {'label': _('Vehicle'), 'domain': [('vehicle_id', 'ilike', search)]},
            'driver_id': {'label': _('Driver'), 'domain': [('driver_id', 'ilike', search)]},
            }

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'destination_id': {'label': _('Destination'), 'order': 'destination_id'},
            'vehicle_id': {'label': _('Vehicle'), 'order': 'vehicle_id'},
            'driver_id': {'label': _('Driver'), 'order': 'driver_id'},
        }

        searchbar_inputs = {
            'all': {'input': 'all', 'label': _('Search in All')},
            'name': {'input': 'name', 'label': _('Search in Ref #')},
            'destination_id': {'input': 'destination_id', 'label': _('Search <span class="nolabel"> (in Destination)</span>')},
            'vehicle_id': {'input': 'vehicle_id', 'label': _('Search <span class="nolabel"> (in Vehicle)</span>')},
            'driver_id': {'input': 'driver_id', 'label': _('Search <span class="nolabel"> (in Driver)</span>')},
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
                search_domain = OR([search_domain, [('destination_id', 'ilike', search)]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        transportation_logbooks_count = ISYTransportationLogbook.sudo().search_count(domain)
        # pager

        pager = portal_pager(
            url="/my/transportation_logbooks",
            url_args={'sortby': sortby},
            total=transportation_logbooks_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        transportation_logbooks = ISYTransportationLogbook.sudo().search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_transportation_logbooks_history'] = transportation_logbooks.ids[:100]

        values.update({
            'transportation_logbooks': transportation_logbooks,
            'page_name': 'transportation_logbook',
            'pager': pager,
            'default_url': '/my/transportation_logbooks',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby
        })
        return request.render("isy_ticketing.portal_my_transportation_logbook", values)
