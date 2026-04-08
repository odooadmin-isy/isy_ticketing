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
        # domain = ['|', ('create_uid', '=', request.env.user.id), ('driver_id', '=', request.env.user.id)]
        domain = []
        vehicle_generator_logbooks_count = request.env['vehicle.generator.logbook'].search_count(domain)
        values['vehicle_generator_logbooks_count'] = vehicle_generator_logbooks_count
        return values

    @http.route(['/my/vehicle_generator_logbooks', '/my/vehicle_generator_logbooks/page/<int:page>'], type='http', auth="user", website=True)
    def portal_vehicle_generator_logbooks(self, page=1, sortby=None, filterby=None, search=None, search_in='all', **kw):
        domain = []
        values = self._prepare_portal_layout_values()
        ISYVehicleGeneratorLogbook = request.env['vehicle.generator.logbook']

        #domain needo to modify for create user records only.
        searchbar_filters = {
            'all': {'label': _('All Status'), 'domain': []},
            'logbook_type_vehicle': {'label': _('Vehicle'), 'domain': [('logbook_type', '=', 'vehicle')]},
            'logbook_type_generator': {'label': _('Generator'), 'domain': [('logbook_type', '=', 'generator')]},
            }

        searchbar_sortings = {
            'date': {'label': _('Date'), 'order': 'date desc'},
            'name': {'label': _('Reference'), 'order': 'name desc'},
            'logbook_type': {'label': _('Logbook Type'), 'order': 'logbook_type'},
        }

        searchbar_inputs = {
            'logbook_type': {'input': 'logbook_type', 'label': _('Search <span class="nolabel"> (in Logbook Type)</span>')},
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
            if search_in in ('logbook_type', 'all'):
                search_domain = OR([search_domain, [('logbook_type', 'ilike', search)]])
            if search_in in ('name', 'all'):
                search_domain = OR([search_domain, [('name', 'ilike', search)]])
            domain += search_domain

        # count for pager
        vehicle_generator_logbooks_count = ISYVehicleGeneratorLogbook.sudo().search_count(domain)
        # pager

        pager = portal_pager(
            url="/my/vehicle_generator_logbooks",
            url_args={'sortby': sortby},
            total=vehicle_generator_logbooks_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        vehicle_generator_logbooks = ISYVehicleGeneratorLogbook.sudo().search(
            domain, order=order, limit=self._items_per_page, offset=pager['offset'])
        request.session['my_vehicle_generator_logbooks_history'] = vehicle_generator_logbooks.ids[:100]

        values.update({
            'vehicle_generator_logbooks': vehicle_generator_logbooks,
            'page_name': 'vehicle_generator_logbook',
            'pager': pager,
            'default_url': '/my/vehicle_generator_logbooks',
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'searchbar_sortings': searchbar_sortings,
            'sortby': sortby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby
        })
        return request.render("isy_ticketing.portal_my_vehicle_generator_logbook", values)
