# -*- coding: utf-8 -*-

from odoo import _, api, fields, models
import logging

_logger = logging.getLogger(__name__)


class RecordKeepingMail(models.Model):
    _name = 'rk.mail'
    _description = 'Saves mail for Record-Keeping'
    _inherit = ['rk.document.mixin']

    attachment_ids = fields.Many2many(
        comodel_name='ir.attachment',
        readonly=1,
    )
    author_id = fields.Many2one(
        comodel_name='res.partner',
        readonly=1,
    )
    auto_delete = fields.Boolean(
        readonly=1,
        string='Auto Delete',
    )
    body_html = fields.Text(
        readonly=1,
        string='Rich-text Contents',
    )
    date = fields.Datetime(
        default=fields.Datetime.now,
        readonly=1,
    )
    email_cc = fields.Char(
        readonly=1,
        string='Cc',
    )
    email_from = fields.Char(
        readonly=1,
        string='From',
    )
    email_to = fields.Text(
        readonly=1,
        string='To',
    )
    headers = fields.Text(
        readonly=1,
    )
    mail_server_id = fields.Many2one(
        comodel_name='ir.mail_server',
        readonly=1,
        string='Outgoing mail server',
    )
    message_id = fields.Char(
        readonly=1,
        string='Message-Id',
    )
    message_type = fields.Selection([
        ('email', 'Email'),
        ('comment', 'Comment'),
        ('notification', 'System notification'),
        ('user_notification', 'User Specific Notification')],
        default='email',
        readonly=1,
        string='Type',
    )
    model = fields.Char(
        readonly=1,
        string='Related Document Model',
    )
    name = fields.Char(
        readonly=1,
        string='Name'
    )
    notification = fields.Boolean(
        readonly=1,
        string='Is Notification',
    )
    recipient_ids = fields.Many2many(
        comodel_name='res.partner',
        context={'active_test': False},
        readonly=1,
        string='To (Partners)',
    )
    record_name = fields.Char(
        readonly=1,
        string='Message Record Name',
    )
    references = fields.Text(
        readonly=1,
    )
    reply_to = fields.Char(
        readonly=1,
        string='Reply-To',
    )
    res_id = fields.Many2oneReference(
        model_field='model',
        readonly=1,
        string='Related Document ID',
    )
    scheduled_date = fields.Char(
        readonly=1,
        string='Scheduled Send Date',
    )
    subject = fields.Char(
        readonly=1,
    )


class Mail(models.Model):
    _inherit = 'mail.mail'

    @api.model
    def create(self, vals):
        rk_mail_val_list = []

        res = super().create(vals)
        try:
            fields = self.env['rk.mail'].fields_get()
            for mail in res:
                values = {'name': mail['subject']}
                for key in fields.keys():
                    if hasattr(mail, key):
                        if fields[key]['type'] in ['many2many']:
                            values[key] = mail[key].ids
                        elif fields[key]['type'] in ['many2one']:
                            values[key] = mail[key].id
                        else:
                            values[key] = mail[key]
                values['sender'] = mail.email_from
                receivers = [mail.email_to] if mail.email_to else []
                recipients = [
                    recipient_id.email_formatted for recipient_id in mail.recipient_ids if recipient_id.email_formatted
                ]
                unique_recipients = list(set(receivers + recipients))
                values['receiver'] = ', '.join(unique_recipients)

                if (model := mail.model) and (res_id := mail.res_id):
                    if rec := self.env[model].browse(res_id):
                        if hasattr(rec, 'matter_id'):
                            values['matter_id'] = rec.matter_id.id
                            values['is_official'] = True
                rk_mail_val_list.append(values)
            for rk_vals in rk_mail_val_list:
                self.env['rk.mail'].create(rk_vals)
        except Exception as e:
            _logger.error(f"Error in create for rk.mail method for res.id {res.id}: {str(e)}")
        return res
