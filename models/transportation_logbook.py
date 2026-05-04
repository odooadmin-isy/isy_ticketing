# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class TransportationDestination(models.Model):
    _name = 'isy.destination'
    _description = 'ISY Transportation Destination'

    name = fields.Char(string='Name')
    is_other_destination = fields.Boolean(string='Is Other Destination', default=False)
    active = fields.Boolean(string='Active', default=True)

class TransportationLogbook(models.Model):
    _name = 'transportation.logbook'
    _inherit = ['mail.thread']
    _description = 'Transportation Logbook'

    def _get_vehicle_selection(self):
        vehicles = self.env['fleet.vehicle'].sudo().search([
            ('check_availability', '=', True)
        ])

        return [(str(v.id), v.name) for v in vehicles]

    name = fields.Char(string='Name', default='New')
    date = fields.Datetime(string='Date', required=True, default=lambda self: fields.Datetime.now(),
            track_visibility='onchange')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', track_visibility='onchange',
            domain="[('check_availability', '=', True)]")
    vehicle_selection = fields.Selection(
                            selection='_get_vehicle_selection',
                            string='Vehicle Selection',
                            required=True
                        )
    driver_id = fields.Many2one('res.users', string='Driver', track_visibility='onchange',
            domain="[('portal_transportation_request_driver', '=', True)]")
    destination_id = fields.Many2one('isy.destination', string='Destination', required=True, track_visibility='onchange')
    start_mileage = fields.Float(string='Start Mileage', track_visibility='onchange', required=True)
    end_mileage = fields.Float(string='End Mileage', track_visibility='onchange', required=True)
    is_other_destination = fields.Boolean(related='destination_id.is_other_destination', string='Is Other Destination', store=True)
    other_destination = fields.Text(string='Other Destination')
    note = fields.Text(string='Note')

    @api.onchange('vehicle_selection')
    def _onchange_vehicle_selection(self):
        if self.vehicle_selection:
            self.vehicle_id = int(self.vehicle_selection)

    def check_mileage(self, start_mileage, end_mileage):
        if end_mileage == 0.00 or start_mileage >= end_mileage:
            raise ValidationError('End Mileage must be greater than 0.00 and Start Mileage must be less than End Mileage.')

    @api.model
    def create(self, vals):
        self.check_mileage(vals.get('start_mileage', 0.00), vals.get('end_mileage', 0.00))

        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('transportation.logbook') or 'New'

        return super(TransportationLogbook, self).create(vals)

    def write(self, vals):
        start_mileage = vals.get('start_mileage', self.start_mileage)
        end_mileage = vals.get('end_mileage', self.end_mileage)
        self.check_mileage(start_mileage, end_mileage)
        return super(TransportationLogbook, self).write(vals)
