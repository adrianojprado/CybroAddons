# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Anagha S (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
###############################################################################
import base64
import csv
import io

import xlrd

from odoo import fields, models, _
from odoo.exceptions import UserError


class ImportMeetingChecklist(models.TransientModel):
    """To import calendar meeting checklist,
      here we can upload the files in csv or xlsx format."""
    _name = 'import.meeting.checklist'
    _description = 'Import Meeting checklist from excel and csv.'

    file_type = fields.Selection(
        [('csv', 'CSV File'), ('xls', 'EXCEL File')],
        string='Import File Type', default='csv',
        help="Choose the type of the file.")
    file_content = fields.Binary(string='File Content', attachment=True,
                                 help="Upload the file.")
    filename = fields.Char(string='File Name', required=True,
                           help="File name of uploaded file content.")

    def action_import_meeting_checklist_xlsx(self):
        """To import meeting checklist in xlsx format,
         it will create a new checklist from this file."""
        try:
            book = xlrd.open_workbook(
                file_contents=base64.decodebytes(self.file_content))
        except xlrd.biffh.XLRDError as exc:
            raise UserError(_('Only excel files are supported.')) from exc
        for sheet in book.sheets():
            for row in range(sheet.nrows):
                if row >= 1:
                    row_values = sheet.row_values(row)
                    main = self.env['meeting.checklist'].sudo().search(
                        [('name', '=', row_values[0])])
                    name = main.mapped('name')
                    if row_values[0] not in name:
                        self.env['meeting.checklist'].sudo().create({
                            'name': row_values[0],
                            'description': row_values[1]})
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message':  _("Successfully Imported!"),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }

    def action_import_meeting_checklist_csv(self):
        """To import task checklist in csv format,
         it will create a new checklist from this file"""
        try:
            file = base64.b64decode(self.file_content)
            data = io.StringIO(file.decode("utf-8"))
            data.seek(0)
            file_reader = []
            csv_reader = csv.reader(data, delimiter=',')
            file_reader.extend(csv_reader)
            file_reader.pop(0)
            for row in file_reader:
                main = self.env['meeting.checklist'].sudo().search(
                    [('name', '=', row[0])])
                name = main.mapped('name')
                if row[0] not in name:
                    self.env['meeting.checklist'].sudo().create({
                        'name': row[0], 'description': row[1]})
        except Exception as exc:
            raise UserError(_('Only csv files are supported.')) from exc
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': _("Successfully Imported!"),
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
