# -*- coding: utf-8 -*-
from odoo import _, api, fields, models


class DocumentMixin(models.AbstractModel):
    _name = 'rk.document.mixin'
    _description = 'Document Mixin'
    _inherits = {'rk.document': 'document_id'}

    document_id = fields.Many2one(
        comodel_name='rk.document',
        copy=False,
        help='The record-keeping document id',
        ondelete='restrict',
        required=True,
        string='Document',
    )
    document_ref = fields.Reference(
        compute='_compute_document_ref',
        copy=False,
        help='The record-keeping document reference',
        selection='_selection_target_model',
        string='Document Reference',
    )

    @api.depends('document_id')
    def _compute_document_ref(self):
        for record in self:
            record.document_ref = f"rk.document,{record.document_id.id or 0}"

    def _get_default_param(self, field):
        param = f"record_keeping.{self._name.replace('.', '_')}_default_{field}"
        if (res := self.env['ir.config_parameter'].sudo().get_param(param)):
            res = int(res)
        return res

    def _get_document_link(self):
        self.ensure_one()
        document = self.document_id
        if not document.res_model or not document.res_id:
            return dict(res_model=self._name, res_id=self.id)

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([('model', '=', 'rk.document')])
        return [(model.model, model.name) for model in models]

    @api.model
    def create(self, vals):
        for field in ['classification_id', 'document_type_id']:
            if not field in vals:
                vals[field] = self._get_default_param(field)
        record = super().create(vals)
        if (document_vals := record._get_document_link()):
            record.document_id.write(document_vals)
        return record

    def write(self, vals):
        for record in self:
            if (document_vals := record._get_document_link()):
                if record.document_id:
                    vals.update(document_vals)
                else:
                    vals['document_id'] = self.env['rk.document'].create(
                        document_vals)
        result = super().write(vals)
        return result
