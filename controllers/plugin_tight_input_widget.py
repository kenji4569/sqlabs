# -*- coding: utf-8 -*-
from plugin_tight_input_widget import tight_input_widget

db = DAL('sqlite:memory:')
db.define_table('product',
    Field('string_default', default='ABCDEFGHIJKLMN'),
    Field('string_7', length=7, default='ABCDEFG'),
    Field('int_default', 'integer', default=1234567890),
    Field('int_5', 'integer', default=12345,
          requires=IS_INT_IN_RANGE(0, 100000)),
    Field('int_5_minus', 'integer', default=-12345,
          requires=IS_INT_IN_RANGE(-99999, 0)),
    Field('int_5_nullable', 'integer',
          requires=IS_NULL_OR(IS_INT_IN_RANGE(-99999, 100000))),
    Field('double_5', 'double', default=12345.678,
          requires=IS_FLOAT_IN_RANGE(0, 99999.999)),
    Field('decimal_8_3', 'decimal(8,3)', default=12345678.901),
    Field('decimal_5_3', 'decimal(8,3)', default=12345.678,
          requires=IS_DECIMAL_IN_RANGE(0, 99999.999)),
)

################################ The core ######################################
# Inject the adjusted input widget
for field in db.product.fields:
    db.product[field].widget = tight_input_widget
################################################################################


def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
