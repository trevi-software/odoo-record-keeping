odoo.define('record_keeping_attachment.public_attachment', function (require) {
    'use strict';

    var FileWidget = require('wysiwyg.widgets.media').FileWidget

    FileWidget.include({
        _getAttachmentsDomain() {
            const domain = this._super(...arguments);
            domain.push(['document_id.matter_id', '=', false]);
            return domain;
        }
    })
})
