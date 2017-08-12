#! Copyright (C) 2017 Lukas Löhle
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from wtforms import SelectField, TextAreaField, BooleanField, StringField, FieldList, FormField, validators, \
    SelectMultipleField, RadioField, widgets, ValidationError
from flask_wtf import FlaskForm


class KeyValueForm(FlaskForm):
    key = StringField(u'Key')
    value = StringField(u'Value')

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(KeyValueForm, self).__init__(*args, **kwargs)


class CustomRadioField(RadioField):
    """
    Works like a RadioField but allows nothing to be selected
    """

    def pre_validate(self, form):
        if self.data:
            for v, _ in self.choices:
                if self.data == v:
                    break
            else:
                raise ValueError(self.gettext('Not a valid choice'))


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class OrderOptionForm(FlaskForm):
    order_type = SelectField(u'Order', choices=[('fixed', 'Fixed'), ('random', 'Latin Square')], default='fixed')
    tasks_random = MultiCheckboxField(u'Tasks', coerce=int)
    tasks_fixed = CustomRadioField(u'Tasks', coerce=int)

    def validate_tasks_random(self, field):
        if self.order_type.data == 'random':
            if not field.raw_data or not field.raw_data[0]:
                raise ValidationError("Select at least one task")

    def validate_tasks_fixed(self, field):
        if self.order_type.data == 'fixed':
            if not field.raw_data or not field.raw_data[0]:
                raise ValidationError("Select at least one task")

    def __init__(self, *args, **kwargs):
        kwargs['csrf_enabled'] = False
        super(OrderOptionForm, self).__init__(*args, **kwargs)


class CellForm(FlaskForm):
    name = StringField(u'Name', [validators.Length(min=1, max=100), validators.InputRequired()])
    cell_type = SelectField(u'Cell Type', choices=[('markdown', 'Markdown'), ('code', 'Code')], default='markdown')
    collapsed = BooleanField(u'Collapsed')
    source = TextAreaField(u'Source', render_kw={"rows": 10})
    cell_metadata = FieldList(FormField(KeyValueForm), min_entries=1)


class ConditionForm(FlaskForm):
    name = StringField(u'Name', [validators.Length(min=1, max=100), validators.InputRequired()])
    pairs = FieldList(FormField(KeyValueForm), min_entries=1)


class TaskForm(FlaskForm):
    name = StringField(u'Name', [validators.Length(min=1, max=100), validators.InputRequired()])
    short = StringField(u'Short Identifier', [validators.Length(min=1, max=3), validators.InputRequired()])
    description = StringField(u'Description')
    cells = FieldList(SelectField(u'Cell', coerce=int), label=u'Cells', min_entries=1)


class NotebookOptionsForm(FlaskForm):
    file_prefix = StringField(u'File Prefix')
    include_fixed = BooleanField(u'Include fixed tasks in filename', default=True)
    conditions = MultiCheckboxField(u'Conditions', coerce=int)


class TemplateForm(FlaskForm):
    name = StringField(u'Name', [validators.Length(min=1, max=100), validators.InputRequired()])
    tasks = MultiCheckboxField(u'Tasks', [validators.InputRequired(message='Select at least one task')], coerce=int)
    order_options = FieldList(FormField(OrderOptionForm), min_entries=1, label=u'Option')
