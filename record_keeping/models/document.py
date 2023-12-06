# -*- coding: utf-8 -*-
from odoo import _, api, fields, models

import logging

_logger = logging.getLogger(__name__)


class Document(models.Model):
    _name = 'rk.document'
    _description = 'Document'
    _inherit = ['mail.activity.mixin', 'mail.thread', 'rk.mixin']

    name = fields.Char(
        copy=False,
        help='The format is [year]/[sequence]-[document_no] if this '
             'document is belongs to a matter',
        readonly=True,
        string='Name',
        tracking=True,
    )
    classification_id = fields.Many2one(
        comodel_name='rk.classification',
        copy=False,
        string='Classification',
        tracking=True,
    )
    description = fields.Char(
        copy=False,
        help='The description of this document',
        string='Description',
        tracking=True,
    )
    document_no = fields.Char(
        copy=False,
        help='The number assigned to this document',
        readonly=True,
        string='Document number',
        tracking=True,
    )
    document_type_id = fields.Many2one(
        comodel_name='rk.document.type',
        copy=False,
        string='Document Type',
        tracking=True,
    )
    matter_id = fields.Many2one(
        comodel_name='rk.matter',
        copy=False,
        help='The matter this document belongs to',
        string='Matter',
        tracking=True,
        index=True
    )
    res_id = fields.Integer(
        copy=False,
        help='The record id this document is attached to.',
        readonly=True,
        string='Resource ID',
    )
    res_model = fields.Char(
        copy=False,
        help='The record model this document is attached to.',
        readonly=True,
        string='Resource Model',
    )
    res_ref = fields.Reference(
        compute='_compute_res_ref',
        copy=False,
        help='The record this document is attached to.',
        selection='_selection_target_model',
        string='Resource Reference',
    )

    @api.depends('name', 'res_id', 'res_model')
    def _compute_res_ref(self):
        self = self.sudo()
        for document in self:
            name = document.get_name()
            if document.res_model and document.res_id:
                document.res_ref = f"{document.res_model},{document.res_id}"
                if res_ref := document.res_ref:
                    if document.res_model == 'ir.attachment':
                        name += ' ' + res_ref.rk_file_name if res_ref.rk_file_name else res_ref.name
                    else:
                        name += ' ' + res_ref.name
            else:
                document.res_ref = None
            document.name = name

    def _message_log(self, **kwargs):
        if kwargs:
            res = super(Document, self)._message_log(**kwargs)
        if self.matter_id:
            kwargs['body'] = _(
                '<p>Document (%s):</p>') % self.get_name()
            self.matter_id._message_log(**kwargs)
        return res

    def _message_log_batch(self, bodies, author_id=None, email_from=None,
                           subject=False, message_type='notification'):
        res = super()._message_log_batch(bodies,
                                         author_id,
                                         email_from,
                                         subject,
                                         message_type)
        if res and self.matter_id and message_type in ['notification']:
            self._next_document_no()
            for b in bodies.values():
                name = f"{self.matter_id.reg_no}-{self.document_no}"
                body = _('<p>Document (%s) created</p>') % name
                self.matter_id._message_log(body=body)

        return res

    def _next_document_no(self):
        self.ensure_one()
        if self.matter_id and not self.document_no:
            self.document_no = str(self.matter_id.document_no_next)
            self.matter_id.document_no_next += 1
            self._compute_res_ref()

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([])
        return [(model.model, model.name) for model in models]

    @api.model
    def create(self, vals):
        if 'matter_id' in vals.keys():
            vals['is_official'] = self.env['rk.matter'].browse(vals['matter_id']).is_official
        document = super().create(vals)
        document._next_document_no()
        return document

    def get_name(self):
        for document in self:
            return (f"{document.matter_id.reg_no}-{document.document_no}"
                    if document.matter_id else '')

    @api.model
    def search(self, args, offset=0, limit=80, order='id', count=False):
        """Override to be able to search old_value_char in mail.tracking.value"""
        dotted_field = 'message_ids.tracking_value_ids.old_value_char'
        if any(filter(lambda arg: dotted_field in arg, args)):
            self = self.sudo()
        return super().search(
            args,
            offset=offset,
            limit=limit,
            order=order,
            count=count
        )

    def unlink(self):
        for document in self:
            document.active = False
        return True

    def write(self, vals):
        if vals.get('matter_id'):
            vals['document_no'] = ''
        res = super().write(vals)
        for document in self:
            document._next_document_no()
        if 'is_official' in vals.keys():
            if self.res_model == 'ir.attachment':
                self.res_ref.public = vals['is_official']
        return res
