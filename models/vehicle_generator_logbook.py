# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

class VehicleGeneratorLogbook(models.Model):
    _name = 'vehicle.generator.logbook'
    _inherit = ['mail.thread']
    _description = 'Vehicle Generator Logbook'

    name = fields.Char(string='Name', default='New')
    logbook_type = fields.Selection([('vehicle', 'Vehicle'), ('generator', 'Generator')],
                    string='Type', required=True, default='vehicle', track_visibility='onchange')
    fuel_type = fields.Selection([('gasoline', 'Gasoline'), ('diesel', 'Diesel')],
            string='Fuel Type', track_visibility='onchange')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle', track_visibility='onchange',
            domain="[('check_availability', '=', True)]")
    driver_id = fields.Many2one('res.users', string='Driver', track_visibility='onchange',
            domain="[('portal_transportation_request_driver', '=', True)]")
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(),
            track_visibility='onchange')
    current_mileage = fields.Float(string='Current Mileage', track_visibility='onchange')

    amount_purchased = fields.Float(string='Amount Purchased (Liter)', track_visibility='onchange')
    price_per_liter = fields.Float(string='Price Per Liter', track_visibility='onchange')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', track_visibility='onchange')

    note = fields.Text(string='Note')

    @api.depends('amount_purchased', 'price_per_liter')
    def _compute_total_price(self):
        for rec in self:
            rec.total_price = rec.amount_purchased * rec.price_per_liter

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('vehicle.generator.logbook') or 'New'

        return super(VehicleGeneratorLogbook, self).create(vals)
