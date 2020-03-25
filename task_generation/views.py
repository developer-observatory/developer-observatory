#! Copyright (C) 2017 Lukas Löhle
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

import re
import unicodedata
from flask import render_template, flash, redirect, url_for, request
from flask.blueprints import Blueprint
from forms import CellForm, TaskForm, TemplateForm, OrderOptionForm, ConditionForm, NotebookOptionsForm
import os
import errno
import json
import copy
from pygments.lexers.python import PythonLexer
from pygments.formatters.html import HtmlFormatter
from pygments import highlight
from database import db
from models import Cell, CellType, Task, TaskCell, NotebookTemplate, OrderOption, Condition, StringPair, NotebookFile

nb_gen = Blueprint('nbg', __name__, template_folder='templates', static_folder='static')


@nb_gen.route('/')
@nb_gen.route('/index')
@nb_gen.route('/home')
def index():
    return render_template('home.html')


@nb_gen.route('/tutorial')
def show_tutorial():
    return render_template('tutorial.html')


@nb_gen.route('/notebooks/new', methods=['GET', 'POST'])
def create_notebook():
    form = TemplateForm()
    task_list = Task.query.order_by(Task.short).all()
    form.tasks.choices = [(task.id, "[{}] {}".format(task.short, task.name)) for task in task_list]
    for subform in form.order_options:
        subform.tasks_random.choices = [(task.id, task.name) for task in task_list]
        subform.tasks_fixed.choices = [(task.id, task.name) for task in task_list]
    if form.validate_on_submit():
        if NotebookTemplate.query.filter_by(name=form.name.data).first():
            flash('A notebook template with this name already exists', 'danger')
        else:
            notebook = NotebookTemplate(form.name.data)
            for task_id in form.tasks.data:
                notebook.tasks.append(Task.query.get(task_id))
                db.session.add(notebook)
            db.session.commit()
            for idx, option in enumerate(form.order_options.entries):
                order_option = OrderOption(idx, option.order_type.data == 'random')
                order_option.notebook = notebook.id
                if order_option.random:
                    for task_id in option.tasks_random.data:
                        order_option.tasks.append(Task.query.get(task_id))
                else:
                    order_option.tasks.append(Task.query.get(option.tasks_fixed.data))
                db.session.add(order_option)
            db.session.commit()
            flash('Template created', 'success')
            return redirect(url_for('nbg.list_notebooks'))
    if not form.tasks.data:
        form.tasks.data = [task_list[0].id]
    selected_tasks = [task_id for task_id in form.tasks.data]
    return render_template('notebook.html', form=form, selected_tasks=selected_tasks,
                           action=url_for('nbg.create_notebook'))


@nb_gen.route('/tasks/new', methods=['GET', 'POST'])
def create_task():
    form = TaskForm()
    cell_list = Cell.query.order_by(Cell.name).all()
    for field in form.cells.entries:
        field.choices = [(cell.id, "{} ({})".format(cell.name, cell.cell_type)) for cell in cell_list]

    if form.validate_on_submit():
        if Task.query.filter_by(name=form.name.data).first():
            flash('A task with this name already exists.', 'danger')
        else:
            cell_ids = []
            for field in form.cells.entries:
                if field.data in cell_ids:
                    flash('You cannot add a cell to a task twice.', 'danger')
                    return render_template('task.html', form=form, action=url_for('nbg.create_task'))
                cell_ids.append(field.data)
            task = Task(form.name.data, form.short.data)
            task.description = form.description.data
            for idx, field in enumerate(form.cells.entries):
                task_cell = TaskCell(position=idx)
                task_cell.cell = Cell.query.filter_by(id=field.data).first()
                task.cells.append(task_cell)
            db.session.add(task)
            db.session.commit()
            flash('Task created', 'success')
            return redirect(url_for('nbg.list_tasks'))

    return render_template('task.html', form=form, action=url_for('nbg.create_task'))


@nb_gen.route('/notebooks', methods=['GET', 'POST'])
def list_notebooks():
    if request.method == 'POST':
        if request.form['delete']:
            notebook = NotebookTemplate.query.get_or_404(request.form['delete'])
            name = notebook.name
            db.session.delete(notebook)
            db.session.commit()
            flash('Deleted "{}"'.format(name), 'info')
    tasks_exist = Task.query.first() is not None
    notebook_list = NotebookTemplate.query.order_by(NotebookTemplate.name).all()
    return render_template('notebooks.html', notebooks=notebook_list, tasks_exist=tasks_exist)


@nb_gen.route('/tasks', methods=['GET', 'POST'])
def list_tasks():
    if request.method == 'POST' and request.form['delete']:
        task = Task.query.get_or_404(request.form['delete'])
        task_name = task.name
        db.session.delete(task)
        db.session.commit()
        flash('Deleted "{}"'.format(task_name), 'info')
    cells_exist = Cell.query.first() is not None
    task_list = Task.query.order_by(Task.short).all()
    return render_template('tasks.html', task_list=task_list, cells_exist=cells_exist)


@nb_gen.route('/cells', methods=['GET', 'POST'])
def list_cells():
    if request.method == 'POST' and request.form['delete']:
        cell = Cell.query.get_or_404(request.form['delete'])
        cell_name = cell.name
        db.session.delete(cell)
        db.session.commit()
        flash('Deleted "{}"'.format(cell_name), 'info')
    cell_list = Cell.query.order_by(Cell.name).all()
    return render_template('cells.html', cell_list=cell_list)


@nb_gen.route('/conditions', methods=['GET', 'POST'])
def list_conditions():
    if request.method == 'POST' and request.form['delete']:
        condition = Condition.query.get_or_404(request.form['delete'])
        condition_name = condition.name
        db.session.delete(condition)
        db.session.commit()
        flash('Deleted "{}"'.format(condition_name), 'info')
    condition_list = Condition.query.order_by(Condition.name).all()
    return render_template('conditions.html', condition_list=condition_list)


@nb_gen.route('/tasks/<int:task_id>')
def view_task(task_id):
    task = Task.query.filter_by(id=task_id).first_or_404()
    code_cells = {}
    css = None
    for task_cell in task.cells:
        if task_cell.cell.cell_type == 'code':
            code, css = highlight_code(task_cell.cell.source)
            code_cells[task_cell.cell.id] = code
    return render_template('task_view.html', task=task, css=css, code_cells=code_cells)


@nb_gen.route('/cells/<int:cell_id>')
def view_cell(cell_id):
    cell = Cell.query.filter_by(id=cell_id).first_or_404()
    code = None
    css = None
    if cell.cell_type == 'code':
        code, css = highlight_code(cell.source)
    return render_template('cell_view.html', cell=cell, code=code, css=css)


@nb_gen.route('/notebooks/<int:nb_id>/generate', methods=['GET', 'POST'])
def generate_notebooks(nb_id):
    nb = NotebookTemplate.query.get_or_404(nb_id)
    form = NotebookOptionsForm()
    conditions = Condition.query.all()
    form.conditions.choices = [(condition.id, condition.name) for condition in conditions]
    if form.validate_on_submit():
        include_fixed = form.include_fixed.data
        file_prefix = form.file_prefix.data
        if form.conditions.data:
            selected_conditions = Condition.query.filter(Condition.id.in_(form.conditions.data)).all()
        else:
            selected_conditions = None
        nb_names = generate_notebook_names(nb, fileprefix=file_prefix,
                                           include_fixed=include_fixed, conditions=selected_conditions)
        if request.form.get('generate', False):
            number = generate_notebook_files(nb, fileprefix=file_prefix,
                                             include_fixed=include_fixed, conditions=selected_conditions)
            flash('{} notebooks have been generated'.format(number), 'success')
    else:
        if form.errors:
            print(form.errors)
        form.file_prefix.data = slugify(nb.name)
        nb_names = generate_notebook_names(nb)
    return render_template('nb_generator.html', nb_names=nb_names, nb=nb, form=form)


@nb_gen.route('/notebooks/<int:nb_id>/edit', methods=['GET', 'POST'])
def edit_notebook(nb_id):
    nb = NotebookTemplate.query.get_or_404(nb_id)
    form = TemplateForm(obj=nb)
    task_list = Task.query.order_by(Task.short).all()
    form.tasks.choices = [(task.id, "[{}] {}".format(task.short, task.name)) for task in task_list]
    selected_tasks = [task.id for task in nb.tasks]
    if request.method == 'GET':
        form.tasks.data = [task.id for task in nb.tasks]
        for _ in form.order_options:
            form.order_options.pop_entry()
        for order_option in nb.options:
            option_field = OrderOptionForm()
            option_field.order_type = 'random' if order_option.random else 'fixed'
            form.order_options.append_entry(option_field)
    for (idx, subform) in enumerate(form.order_options):
        subform.tasks_random.choices = [(task.id, task.name) for task in task_list]
        subform.tasks_fixed.choices = [(task.id, task.name) for task in task_list]
        if request.method == 'GET':
            subform.tasks_random.data = [task.id for task in nb.options[idx].tasks] if nb.options[idx].random else None
            subform.tasks_fixed.data = nb.options[idx].tasks[0].id if not nb.options[idx].random else None
    if form.validate_on_submit():
        if form.name.data != nb.name and NotebookTemplate.query.filter_by(name=form.name.data).first():
            flash('A notebook with this name already exists.', 'danger')
        else:
            nb.name = form.name.data
            selected_tasks = form.tasks.data
            nb.tasks = Task.query.filter(Task.id.in_(selected_tasks)).all()
            to_remove = len(nb.options) - len(form.order_options.entries)
            if to_remove > 0:
                nb.options = nb.options[:-to_remove]
            for (idx, subform) in enumerate(form.order_options.entries):
                is_random = subform.order_type.data == 'random'
                option_tasks = subform.tasks_random.data if is_random else [subform.tasks_fixed.data]
                if idx >= len(nb.options):
                    # new option
                    option = OrderOption(idx, is_random)
                    nb.options.append(option)
                else:
                    option = nb.options[idx]
                    option.random = is_random
                option.tasks = Task.query.filter(Task.id.in_(option_tasks)).all()
            db.session.commit()
            flash('Saved changes', 'success')
    return render_template('notebook.html', form=form, notebook=nb, selected_tasks=selected_tasks,
                           action=url_for('nbg.edit_notebook', nb_id=nb_id))


@nb_gen.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm(obj=task)
    cell_list = Cell.query.order_by(Cell.name).all()
    for idx, field in enumerate(form.cells.entries):
        field.choices = [(cell.id, "{} ({})".format(cell.name, cell.cell_type)) for cell in cell_list]
        if request.method == 'GET':
            field.data = task.cells[idx].cell.id if len(task.cells) > idx else None
    if form.validate_on_submit():
        if form.name.data != task.name and Task.query.filter_by(name=form.name.data).first():
            flash('A task with this name already exists.', 'danger')
        else:
            task.name = form.name.data
            task.description = form.description.data
            task.short = form.short.data
            for task_cell in task.cells:
                db.session.delete(task_cell)
            for idx, field in enumerate(form.cells.entries):
                task_cell = TaskCell(position=idx)
                task_cell.cell = Cell.query.filter_by(id=field.data).first()
                task.cells.append(task_cell)
            db.session.commit()
            flash('Saved changes', 'success')
    return render_template('task.html', form=form, task=task, action=url_for('nbg.edit_task', task_id=task_id))


@nb_gen.route('/cells/<int:cell_id>/edit', methods=['GET', 'POST'])
def edit_cell(cell_id):
    cell = Cell.query.get_or_404(cell_id)
    form = CellForm(obj=cell)
    if request.method == 'POST':
        if form.validate():
            if form.name.data != cell.name and Cell.query.filter_by(name=form.name.data).first():
                flash('Cell with this name already exists', 'danger')
            else:
                cell.name = form.name.data
                cell.collapsed = form.collapsed.data
                cell.cell_type = form.cell_type.data
                cell.source = form.source.data
                cell.set_metadata(form.cell_metadata.data)
                db.session.commit()
                flash('Saved changes', 'success')
        return render_template('cell.html', form=form, cell=cell, action=url_for('nbg.edit_cell', cell_id=cell_id))
    else:
        for i in range(len(form.cell_metadata.entries)):
            form.cell_metadata.pop_entry()
        celldata = cell.get_metadata()
        for entry in celldata:
            form.cell_metadata.append_entry(entry)
        if not celldata:
            form.cell_metadata.append_entry({})
        return render_template('cell.html', form=form, cell=cell, action=url_for('nbg.edit_cell', cell_id=cell_id))


@nb_gen.route('/conditions/<int:condition_id>/edit', methods=['GET', 'POST'])
def edit_condition(condition_id):
    condition = Condition.query.get_or_404(condition_id)
    form = ConditionForm(obj=condition)
    if form.validate_on_submit():
        if form.name.data != condition.name and Condition.query.filter_by(name=form.name.data).first():
            flash('Condition with this name already exists', 'danger')
        else:
            condition.name = form.name.data
            to_remove = len(condition.pairs) - len(form.pairs.entries)
            if to_remove > 0:
                condition.pairs = condition.pairs[:-to_remove]
            for idx, pair in enumerate(form.pairs.entries):
                if idx >= len(condition.pairs):
                    new_pair = StringPair(pair.key.data, pair.value.data)
                    condition.pairs.append(new_pair)
                else:
                    condition.pairs[idx].key = pair.key.data
                    condition.pairs[idx].value = pair.value.data
            db.session.commit()
            flash('saved changes', 'success')
    return render_template('condition.html', form=form, action=url_for('nbg.edit_condition', condition_id=condition_id))


@nb_gen.route('/cells/new', methods=['GET', 'POST'])
def create_cell():
    form = CellForm()
    if form.validate_on_submit():
        if Cell.query.filter_by(name=form.name.data).first():
            flash('A cell with this name already exists.', 'danger')
            return render_template('cell.html', action=url_for('nbg.create_cell'), form=form)
        cell = Cell(form.name.data, CellType(form.cell_type.data), form.source.data)
        cell.collapsed = form.collapsed.data
        cell.set_metadata(form.cell_metadata.data)
        db.session.add(cell)
        db.session.commit()
        flash('Cell created', 'success')
        return redirect(url_for('nbg.list_cells'))
    return render_template('cell.html', action=url_for('nbg.create_cell'), form=form)


@nb_gen.route('/conditions/new', methods=['GET', 'POST'])
def create_condition():
    form = ConditionForm()
    if form.validate_on_submit():
        if Condition.query.filter_by(name=form.name.data).first():
            flash('A condition with this name already exists.', 'danger')
            return render_template('condition.html', action=url_for('nbg.create_condition'), form=form)
        condition = Condition(form.name.data)
        for field in form.pairs:
            condition.pairs.append(StringPair(field.key.data, field.value.data))
        db.session.add(condition)
        db.session.commit()
        flash('Condition created', 'success')
        return redirect(url_for('nbg.list_conditions'))
    return render_template('condition.html', action=url_for('nbg.create_condition'), form=form)


def highlight_code(code):
    # TODO: refactor this into a code cell model to support multiple languages
    """
    Creates html and css for python code highlighting.
    :param code: The python code to highlight
    :return: A dictionary with html code and css styling
    """
    lexer = PythonLexer()
    formatter = HtmlFormatter()
    code_html = highlight(code, lexer, formatter)
    code_css = formatter.get_style_defs()
    return code_html, code_css


def generate_notebook_names(notebook, fileprefix=None, include_fixed=True, conditions=None):
    if not fileprefix:
        fileprefix = notebook.name
    fileprefix = slugify(fileprefix)
    if conditions:
        names = []
        for condition in conditions:
            names += [fileprefix + '_' + slugify(condition.name)]
    else:
        names = [fileprefix]
    first_task = True
    for option in notebook.options:
        if not option.random and include_fixed:
            task_short = slugify(option.tasks[0].short)
            if first_task:
                task_short = '_[' + task_short
                first_task = False
            else:
                task_short = '_' + task_short
            names = [name + task_short for name in names]
        elif option.random:
            new_names = []
            orders = latin_squares[min(5, len(option.tasks))]
            for name in names:
                for order in orders:
                    if first_task:
                        new_name = name + '_' + '['
                    else:
                        new_name = name + '_'
                    for idx in order:
                        new_name += slugify(option.tasks[idx].short)
                    new_names.append(new_name)
            first_task = False
            names = new_names
    names = [name + '].ipynb' if '[' in name else name + '.ipynb' for name in names]
    return names


def generate_notebook_files(notebook, fileprefix=None, include_fixed=True, conditions=None):
    if not fileprefix:
        fileprefix = notebook.name
    fileprefix = slugify(fileprefix)
    nb_base = {'metadata': notebook_metadata,
               'nbformat': notebook_nbformat,
               'nbformat_minor': notebook_nbformat_minor,
               'cells': []}
    if conditions:
        files = {}
        task_replace_ops = {}
        for condition in conditions:
            file_name = fileprefix + '_' + slugify(condition.name)
            files[file_name] = copy.deepcopy(nb_base)
            task_replace_ops[file_name] = get_condition_replace_ops(condition)
    else:
        files = {fileprefix: nb_base}
        task_replace_ops = {fileprefix: []}
    task_index = 0
    first_task = True
    for option in notebook.options:
        if not option.random:
            if include_fixed:
                task_short = slugify(option.tasks[0].short)
                for filename in list(files.keys()):
                    if first_task:
                        new_filename = filename + '_[' + task_short
                    else:
                        new_filename = filename + '_' + task_short
                    files[new_filename] = files.pop(filename)
                    task_replace_ops[new_filename] = task_replace_ops.pop(filename)
                first_task = False
            fixed_replace_ops = get_task_replace_ops(task_index, option.tasks[0])
            for operations in task_replace_ops.values():
                operations.extend(fixed_replace_ops)
            task_index += 1
            cells = option.tasks[0].get_cell_list()
            for nb in list(files.values()):
                nb['cells'].extend(cells)
        elif option.random:
            tasks_short = [slugify(task.short) for task in option.tasks]
            tasks_cells = [task.get_cell_list() for task in option.tasks]
            task_orders = latin_squares[min(5, len(option.tasks))]
            files_new = {}
            replace_ops_new = {}
            for task_order in task_orders:
                order = ''
                for idx in task_order:
                    order += tasks_short[idx]
                for filename, content in files.items():
                    if first_task:
                        new_filename = filename + '_[' + order
                    else:
                        new_filename = filename + '_' + order
                    files_new[new_filename] = copy.deepcopy(content)
                    reordered_cells = []
                    for idx in task_order:
                        reordered_cells.extend(tasks_cells[idx])
                    files_new[new_filename]['cells'].extend(reordered_cells)
                    replace_ops_new[new_filename] = copy.deepcopy(task_replace_ops[filename])
                    for (idx, task_idx) in enumerate(task_order):
                        replace_ops_new[new_filename].extend(
                            get_task_replace_ops(task_index + idx, option.tasks[task_idx]))
            first_task = False
            files = files_new
            task_replace_ops = replace_ops_new
            task_index += len(option.tasks)
    for filename in list(files.keys()):
        apply_replace_ops(files[filename], task_replace_ops[filename])
        new_filename = filename + ']' + '.ipynb' if '[' in filename else filename + '.ipynb'
        files[new_filename] = files.pop(filename)
    save_notebook_files(notebook, files)
    write_db_schema()
    return len(files.keys())


def get_task_replace_ops(task_index, task):
    result = []
    placeholder_task_name = '%task' + str(task_index) + '%'
    placeholder_task_short = '%task' + str(task_index) + '.short%'
    placeholder_task_desc = '%task' + str(task_index) + '.description%'
    result.append((placeholder_task_name, task.name if task.name else ''))
    result.append((placeholder_task_short, task.short if task.short else ''))
    result.append((placeholder_task_desc, task.description if task.description else ''))
    return result


def get_condition_replace_ops(condition):
    result = []
    for pair in condition.pairs:
        replace_op = ('%' + pair.key + '%', pair.value)
        result.append(replace_op)
    return result


def apply_replace_ops(nb_element, replace_ops):
    """
    :param nb_element: A notebook dict or one of its elements
    :param replace_ops: A list of tuples in the form (placeholder, value). Those are applied to any string in
     the provided element.
    """
    if isinstance(nb_element, list):
        for idx, element in enumerate(nb_element):
            if isinstance(element, str):
                nb_element[idx] = apply_ops_to_string(element, replace_ops)
            else:
                apply_replace_ops(element, replace_ops)
    if isinstance(nb_element, dict):
        for key in list(nb_element.keys()):
            if isinstance(nb_element[key], str):
                nb_element[key] = apply_ops_to_string(nb_element[key], replace_ops)
            else:
                apply_replace_ops(nb_element[key], replace_ops)


def apply_ops_to_string(string, replace_ops):
    for (placeholder, value) in replace_ops:
        string = string.replace(placeholder, value)
    return string


def save_notebook_files(notebook, files):
    # create directory if it does not exist
    try:
        os.makedirs('generated')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    nb_files = NotebookFile.query.filter_by(category=notebook.id)
    for nb_file in nb_files:
        file_path = os.path.join('generated', nb_file.filename)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Error deleting file {}: {}'.format(file_path, e))
        db.session.delete(nb_file)
    for filename, notebook_content in files.items():
        with open(os.path.join('generated', filename), 'w', encoding='utf-8') as outfile:
            json.dump(notebook_content, outfile, indent=4, separators=(',', ': '))
        nb_file = NotebookFile(notebook.id, filename)
        db.session.add(nb_file)
    db.session.commit()


def write_db_schema(filename='dbSchema.sql'):
    try:
        os.makedirs('generated')
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    files = NotebookFile.query.all()
    with open(os.path.join('generated', filename), 'w', encoding='utf-8') as outfile:
        #outfile.write(NotebookFile.get_table_string() + '\n')
        i = 0
        for file in files:
            file_path = os.path.join('generated', file.filename)
            try:
                if os.path.isfile(file_path):
                    outfile.write(file.get_insert_string(i) + '\n')
                    i += 1
            except Exception as e:
                print('Error trying to check on file {}: {}'.format(file_path, e))


def slugify(value):
    value = str(value)
    value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip().lower()
    value = value.replace(' ', '_')
    return value


notebook_metadata = {
    "kernelspec": {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3"
    },
    "language_info": {
        "codemirror_mode": {
            "name": "ipython",
            "version": 3
        },
        "file_extension": ".py",
        "mimetype": "text/x-python",
        "name": "python",
        "nbconvert_exporter": "python",
        "pygments_lexer": "ipython3",
        "version": "3.6.9"
    }
}

notebook_nbformat = 4
notebook_nbformat_minor = 2

latin_squares = {
    1: [[0]],
    2: [[0, 1], [1, 0]],
    3: [[0, 1, 2], [1, 2, 0], [2, 0, 1]],
    4: [[0, 1, 2, 3], [1, 0, 3, 2], [2, 3, 0, 1], [3, 2, 1, 0]],
    5: [[0, 1, 2, 3, 4], [1, 2, 4, 0, 3], [2, 4, 3, 1, 0], [3, 0, 1, 4, 2], [4, 3, 0, 2, 1]]}
