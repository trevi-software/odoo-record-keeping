# -*- coding: utf-8 -*-

from odoo import _, api, fields, models


class Project(models.Model):
    _name = 'project.project'
    _inherit = ['mail.thread', 'project.project']
    _inherits = {'rk.document': 'rk_id'}

    rk_id = fields.Many2one(
        comodel_name='rk.document',
        help='The record-keeping document of this project',
        ondelete='restrict',
        required=True,
        readonly=True,
        string='Record-keeping Document',
    )

    rk_ref = fields.Reference(
        help='The record-keeping document of this project',
        readonly=True,
        selection='_selection_target_model',
        string='Registration Number',
    )

    @api.model
    def _selection_target_model(self):
        models = self.env['ir.model'].search([('model', '=', 'rk.document')])
        return [(model.model, model.name) for model in models]

    @api.onchange('is_official')
    def _onchange_is_official(self):
        if not self.is_official:
            self.is_secret = False

    @api.onchange('is_secret')
    def _onchange_is_secret(self):
        if not self.is_secret:
            self.law_section_id = False
            self.secrecy_grounds = False

    @api.model
    def create(self, vals):
        project = super(Project, self).create(vals)
        project.rk_ref = f'{project.rk_id._name},{project.rk_id.id}'
        project.rk_res_model = project._name
        project.rk_res_id = project.id
        return project
