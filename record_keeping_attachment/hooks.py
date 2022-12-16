# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID, api
import logging

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    """
    This post-init-hook will create a rk.document for existing attachments.
    """
    env = api.Environment(cr, SUPERUSER_ID, dict())
    models = ['ir.attachment']

    for model in models:
        records = env[model].search([], order='id')
        for record in records:
            if not record.document_id:
                vals = {'res_model': model, 'res_id': record.id}
                record.document_id = env['rk.document'].create(vals)
                _logger.warning("hook created matter"*99)

