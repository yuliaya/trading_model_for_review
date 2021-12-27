from flask_wtf import FlaskForm
from wtforms import IntegerField, FloatField, BooleanField, SubmitField
from trading_simulator import PARAMS


class ParamsForm(FlaskForm):
    lifetime_period = IntegerField(label='Lifetime period (number of days):')
    platform_interest = FloatField(label='Platform commission')
    invest = BooleanField(label='Invest into items?', default=PARAMS['invest'])
    segmentation = BooleanField(label='User segmentation', default=PARAMS['segmentation'])
    lifetime_acc = FloatField(label='Lifetime prediction model accuracy')
    demand_acc = FloatField(label='Demand prediction model accuracy')
    epochs = IntegerField(label='Number of epochs:')
    submit = SubmitField(label='Run')
