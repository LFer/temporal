# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-
import tools
from osv import osv
from osv import fields
from tools.translate import _
from openerp import SUPERUSER_ID
import logging

_logger = logging.getLogger(__name__)

def format_date_tz(date, tz=None):
    if not date:
        return 'n/a'
    format = tools.DEFAULT_SERVER_DATETIME_FORMAT
    return tools.server_to_local_timestamp(date, format, format, tz)


class mail_message(osv.osv):

    def _get_display_text(self, cr, uid, ids, name, arg, context=None):
        if context is None:
            context = {}
        tz = context.get('tz')
        result = {}
        _logger.info('!!!!!porqueeeeee****'+str(ids))
        # Read message as UID 1 to allow viewing author even if from different company

        for message in self.browse(cr, SUPERUSER_ID, ids):
            msg_txt = ''
            if message.email_from:
                msg_txt += _('%s wrote on %s: \n Subject: %s \n\t') % (message.email_from or '/', format_date_tz(message.date, tz), message.subject)
                if message.body:
                    msg_txt += truncate_text(message.body)
            else:

                #msg_txt = (message.author_id.name or '/') + _(' en ') + format_date_tz(message.date, tz) + ':\n\t'
                #msg_txt = (message.author_id.name or '/') + _(' en ') + format_date_tz(message.date, tz) + ':\n\t'
                msg_txt = (message.author_id.name or '/') + _(' en ') + format_date_tz(message.date, tz) + ':' + (message.subject or '') + '\n\t'
            result[message.id] = msg_txt

        return result

    _name = "mail.message"
    _inherit = "mail.message"

    _columns = {
        'display_text': fields.function(_get_display_text, method=True, type='text', size="512", string='Display Text'),
    }
mail_message()
