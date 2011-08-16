# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget

db = DAL('sqlite:memory:')
db.define_table('product', Field('description', 'text'))

# --- inject the elrte widget ---
db.product.description.widget = ElrteWidget(lang='jp')
# ------------------------------------------

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        print request.vars.description, len(request.vars.description)
        session.flash = 'submitted : %s' % request.vars.description
        redirect(URL('index'))
    return dict(form=form)
