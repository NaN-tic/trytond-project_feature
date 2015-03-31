# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from sql import Literal
from sql.conditionals import Case, Coalesce
from sql.aggregate import Min, Max
import datetime
from dateutil.relativedelta import relativedelta
from trytond.model import ModelView, ModelSQL, fields
from trytond.pool import Pool, PoolMeta
from trytond.tools import reduce_ids
from trytond.transaction import Transaction


__all__ = ['Feature', 'FeatureScenario', 'Work', 'ProjectCicle',
    'FeatureDelivery', 'FeatureRelations']

__metaclass__ = PoolMeta


class Work:
    __name__ = 'project.work'

    feature = fields.Many2One('project.feature', 'Feature')
    delivery = fields.Many2One('project.feature.delivery', 'Delivery')
    cicle = fields.Many2One('project.feature.cicle', 'Cicle')


class ProjectCicle(ModelSQL, ModelView):
    'Feature Cicle'

    __name__ = 'project.feature.cicle'

    name = fields.Char('Name', required=True)
    party = fields.Many2One('party.party', 'Party', required=True,
        select=True)
    tasks = fields.One2Many('project.work', 'cicle', 'Tasks',
        add_remove=[])


class FeatureDelivery(ModelSQL, ModelView):
    'Project Feature Delivery'
    __name__ = 'project.feature.delivery'

    delivery_date = fields.Date('Delivery Date', required=True)
    party = fields.Many2One('party.party', 'Party', required=True,
         select=True)
    features = fields.Function(fields.One2Many('project.feature', None,
        'Features'), 'get_features')
    tasks = fields.One2Many('project.work', 'delivery', 'Delivery',
        add_remove=[])
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('done', 'Done'),
            ('cancel', 'Cancel')], 'State')

    def get_features(self, name=None):
        features = set()
        for task in self.tasks:
            if task.feature:
                features.add(task.feature)
        return [x.id for x in features]


class Feature(ModelSQL, ModelView):
    'Project Feature'
    __name__ = 'project.feature'

    name = fields.Char('Name', translate=True, required=True)
    description = fields.Text('Description', translate=True)
    background = fields.Text('Background', translate=True)
    party = fields.Many2One('party.party', 'Party', required=True)
    tasks = fields.One2Many('project.work', 'feature', 'Tasks')
    origin = fields.One2Many('activity.activity', 'resource', 'Origin')
    component = fields.Many2One('project.work.component', 'Component')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('quote', 'Quotation'),
            ('confirm', 'Confirmed'),
            ('in_progress', 'In Progress'),
            ('to_review', 'To Review'),
            ('done', 'Done'),
            ('cancel', 'Cancel'),
            ], 'State', required=True, select=True)
    scenarios = fields.One2Many('project.feature.scenario', 'feature',
        'Scenarios', required=False)
    related = fields.Many2Many('project.feature_relations', 'source',
        'related', 'Related Features')


class FeatureRelations(ModelSQL):
        'Feature-Relations'
        __name__ = 'project.feature_relations'

        source = fields.Many2One('project.feature', 'Feature',
            ondelete='CASCADE', required=True, select=True)
        related = fields.Many2One('project.feature', 'Related',
            ondelete='CASCADE', required=True, select=True)


class FeatureScenario(ModelSQL, ModelView):
    'Project Feature Scenario'
    __name__ = 'project.feature.scenario'

    name = fields.Char('Name')
    file_name = fields.Char('File name')
    description = fields.Text('Description', translate=True)
    feature = fields.Many2One('project.feature', 'Feature', required=True,
        select=True)
    executions = fields.Function(fields.One2Many('project.test.build.result',
        None, 'Executions'), 'get_executions')

    def get_executions(self, name=None):
        TestResult = Pool().get('project.test.build.result')
        results = TestResult.search([
                ('name', 'like', "%" + self.file_name + "%"),
                ('build.component', '=', self.feature.component.id),
                ('type', '=', 'scenario')])
        return [r.id for r in results]
