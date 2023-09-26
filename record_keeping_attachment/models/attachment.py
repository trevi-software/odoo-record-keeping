# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)


class Attachment(models.Model):
    _name = 'ir.attachment'
    _inherit = ['ir.attachment', 'mail.thread', 'rk.document.mixin']

    rk_file_name = fields.Char(string="Original file Name", readonly=True)

    def _find_matter(self, values):
        _model = values.get('active_model') or values.get('res_model')
        _id = values.get('active_id') or values.get('res_id')
        if _model and _id and (record := self.env[_model].browse(_id)):
            if hasattr(record, 'matter_id'):
                return record.matter_id.id

    def _prepare_values(self, vals):
        matter_id = self.env.context.get('active_matter')

        for v in [self.env.context, vals]:
            if not matter_id:
                matter_id = self._find_matter(v)

        if matter_id:
            vals['matter_id'] = matter_id
            _logger.warning(f"TEST 1 {vals}")
            vals['public'] = self.env['rk.matter'].browse(matter_id).is_official
        return vals

    @api.model
    def create(self, vals):
        if not vals.get('matter_id'):
            vals = self._prepare_values(vals)
        if 'is_official' in vals.keys():
            _logger.warning(f"TEST 2 {vals}")
            vals['public'] = vals['is_official']
        elif 'matter_id' in vals.keys():
            _logger.warning(f"TEST 3 {vals}")
            vals['public'] = self.env['rk.matter'].browse(vals['matter_id']).is_official
        return super().create(vals)

    def write(self, vals):
        for rec in self:
            if hasattr(rec, 'matter_id') and not rec.matter_id and not vals.get('matter_id'):
                vals = self._prepare_values(vals)
            if 'is_official' in vals.keys():
                _logger.warning(f"TEST 4 {vals}")
                vals['public'] = vals['is_official']
                _logger.warning(f"TEST 5")
            return super().write(vals)
