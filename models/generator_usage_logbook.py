# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

import logging
_logger = logging.getLogger(__name__)

GENERATOR_LOCATION = [('isy', 'ISY'), ('residence', 'Housing/Residence')]

class Generator(models.Model):
    _name = 'isy.generator'
    _description = 'ISY Generator'

    name = fields.Char(string='Name')
    generator_location = fields.Selection(GENERATOR_LOCATION,
            string='Location', required=True, track_visibility='onchange', default='isy')
    active = fields.Boolean(string='Active', default=True)

class GeneratorUsageLogbook(models.Model):
    _name = 'generator.usage.logbook'
    _inherit = ['mail.thread']
    _description = 'Generator Usage Logbook'

    name = fields.Char(string='Name', default='New')
    generator_location = fields.Selection(GENERATOR_LOCATION,
            string='Location', required=True, track_visibility='onchange', default='isy')
    date = fields.Date(string='Date', required=True, default=lambda self: fields.Date.today(),
            track_visibility='onchange')
    generator_id = fields.Many2one('isy.generator', string='Generator', required=True,
            track_visibility='onchange',
            domain="[('generator_location', '=', generator_location)]")
    total_usage = fields.Float(string='Total Usage (Liters)', required=True, track_visibility='onchange')
    price_per_liter = fields.Float(string='Price Per Liter (MMK)', required=True, track_visibility='onchange')
    total_cost = fields.Float(string='Total Cost', compute='_compute_total_cost', track_visibility='onchange')

    note = fields.Text(string='Note')

    @api.depends('total_usage', 'price_per_liter')
    def _compute_total_cost(self):
        for rec in self:
            rec.total_cost = rec.total_usage * rec.price_per_liter

    @api.model
    def create(self, vals):
        if vals.get('name', 'New') == 'New':
            vals['name'] = self.env['ir.sequence'].next_by_code('generator.usage.logbook') or 'New'

        return super(GeneratorUsageLogbook, self).create(vals)
