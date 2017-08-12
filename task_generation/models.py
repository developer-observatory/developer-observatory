#! Copyright (C) 2017 Lukas Löhle
#!
#! This software may be modified and distributed under the terms
#! of the MIT license.  See the LICENSE file for details.

from database import db
from enum import Enum
from datetime import datetime
from sqlalchemy.ext.orderinglist import ordering_list
import hashlib
import json


class CellType(Enum):
    MD = 'markdown'
    CD = 'code'


class TaskCell(db.Model):
    """
    Association class used to hold the positions of cells in a task
    """
    __tablename__ = 'nbgen_taskcells'
    task_id = db.Column(db.Integer, db.ForeignKey('nbgen_tasks.id'), primary_key=True)
    cell_id = db.Column(db.Integer, db.ForeignKey('nbgen_cells.id'), primary_key=True)
    position = db.Column(db.Integer)
    cell = db.relationship('Cell')


option_tasks = db.Table('nbgen_task_association',
                        db.Column('option_id', db.Integer, db.ForeignKey('nbgen_orderoptions.id')),
                        db.Column('task_id', db.Integer, db.ForeignKey('nbgen_tasks.id'))
                        )

template_tasks = db.Table('nbgen_template_tasks',
                          db.Column('notebook_id', db.Integer, db.ForeignKey('nbgen_nbtemplates.id')),
                          db.Column('task_id', db.Integer, db.ForeignKey('nbgen_tasks.id'))
                          )


class NotebookFile(db.Model):
    __tablename__ = 'nbgen_files'
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.Text, nullable=False)
    hash = db.Column(db.Text, nullable=False)

    def __init__(self, category, filename):
        self.category = category
        self.filename = filename
        self.hash = hashlib.sha256(filename.encode('utf-8')).hexdigest()

    def get_insert_string(self, condition):
        return 'INSERT INTO "conditions" VALUES({:d}, {:d}, \'{}\', \'{}\');' \
            .format(self.category, condition, self.filename, self.hash)

    @staticmethod
    def get_table_string():
        return 'CREATE TABLE "conditions" (category INTEGER, condition INTEGER, filename TEXT, hash TEXT, PRIMARY KEY(category, condition));'


class StringPair(db.Model):
    """
    Models a simple key-value pair. Keys are limited to 100 characters.
    """
    __tablename__ = 'nbgen_pairs'
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text)
    condition = db.Column(db.Integer, db.ForeignKey('nbgen_conditions.id'))

    def __init__(self, key, value=''):
        self.key = key
        self.value = value


class Condition(db.Model):
    """
    Models a study condition by holding a list of key-value pairs. Those pairs are used to replace strings in notebooks
    depending on the condition.
    """
    __tablename__ = 'nbgen_conditions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    pairs = db.relationship('StringPair', cascade='all, delete-orphan')

    def __repr__(self):
        return '<{}>'.format(self.name)

    def __init__(self, name):
        self.name = name


class Cell(db.Model):
    """
    Model for simple jupyter notebook cells, containing either code or markdown.
    """
    __tablename__ = 'nbgen_cells'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    cell_type = db.Column(db.String(10), nullable=False, default='markdown')
    collapsed = db.Column(db.Boolean, default=False)
    source = db.Column(db.Text)
    cell_metadata = db.Column(db.Text)
    created = db.Column(db.DateTime, default=datetime.utcnow())

    def __repr__(self):
        return '<{}>'.format(self.name)

    def set_metadata(self, form_data):
        """
        Populates cell metadata
        :param form_data: list of pairs in the form {'key': 'myKey', 'value': 'myValue'}
        :return:
        """
        metadata = {}
        for pair in form_data:
            if pair['key'] and pair['value']:
                metadata[str(pair['key'])] = pair['value']
        self.cell_metadata = json.dumps(metadata)

    def get_metadata(self):
        """
        Returns cell metadata in a format suitable for wtforms
        :return: [{'key': key1, 'value': value1}, ...]
        """
        loaded_data = []
        if self.cell_metadata:
            json_data = json.loads(self.cell_metadata)
            for key, value in json_data.items():
                loaded_data.append({'key': key, 'value': value})
        return loaded_data

    def get_as_dict(self):
        result = {'cell_type': self.cell_type}
        is_code = self.cell_type == 'code'
        if is_code:
            result['execution_count'] = 0
            result['outputs'] = []
        metadata = {}
        if self.cell_metadata:
            metadata = json.loads(self.cell_metadata)
        if is_code:
            metadata['collapsed'] = self.collapsed
        result['metadata'] = metadata
        result['source'] = self.source
        return result

    def __init__(self, name, cell_type: CellType, source=''):
        self.name = name
        self.cell_type = cell_type.value
        self.source = source


class Task(db.Model):
    """
    Model for tasks in a study notebook. A task is a collection of cells.
    """

    __tablename__ = 'nbgen_tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    short = db.Column(db.String(3), nullable=False)
    description = db.Column(db.Text)
    cells = db.relationship('TaskCell', order_by='TaskCell.position', collection_class=ordering_list('position'),
                            cascade="all, delete-orphan")

    def __repr__(self):
        return '<[{}] {}>'.format(self.short, self.name)

    def get_cell_list(self):
        result = []
        for task_cell in self.cells:
            result.append(task_cell.cell.get_as_dict())
        return result

    def __init__(self, name, short):
        self.name = name
        self.short = short


class NotebookTemplate(db.Model):
    """
    Model for a notebook template that is used to generate notebooks with tasks in different orders.
    """
    __tablename__ = 'nbgen_nbtemplates'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    tasks = db.relationship('Task', secondary=template_tasks, order_by='Task.short',
                            collection_class=ordering_list('short'))
    options = db.relationship('OrderOption', order_by='OrderOption.position',
                              collection_class=ordering_list('position'), cascade='all, delete-orphan')

    def __repr__(self):
        return '<{}>'.format(self.name)

    def __init__(self, name):
        self.name = name


class OrderOption(db.Model):
    """
    Model for an ordering option used in notebook templates.
    Order of associated task(s) can be random or fixed and the position relative to other ordering options is fixed.
    """
    __tablename__ = 'nbgen_orderoptions'
    id = db.Column(db.Integer, primary_key=True)
    notebook = db.Column(db.Integer, db.ForeignKey('nbgen_nbtemplates.id'))
    random = db.Column(db.Boolean, default=False)
    position = db.Column(db.Integer)
    tasks = db.relationship('Task', secondary=option_tasks, order_by='Task.short',
                            collection_class=ordering_list('short'))

    def __repr__(self):
        if self.random:
            return '<random: {}>'.format(str(self.tasks))
        else:
            return '<fixed: {}>'.format(str(self.tasks[0]))

    def __init__(self, position, random=False):
        self.position = position
        self.random = random
