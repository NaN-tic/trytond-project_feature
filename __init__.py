# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from feature import *


def register():
    Pool.register(
        Feature,
        FeatureScenario,
        ProjectCicle,
        FeatureDelivery,
        FeatureRelations,
        Work,
        module='project_feature', type_='model')
