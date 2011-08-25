# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget

db = DAL('sqlite:memory:')
db.define_table('product', Field('description', 'text'))

################################ The core ######################################
# Inject the elrte widget
db.product.description.widget = ElrteWidget(lang='jp')
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
