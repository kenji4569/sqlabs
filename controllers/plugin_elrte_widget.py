# -*- coding: utf-8 -*-
from plugin_elrte_widget import ElrteWidget

db = DAL('sqlite:memory:')
db.define_table('product', Field('description', 'text'))

try:
    lang = T.accepted_language.split('-')[0].replace('ja', 'jp')
except:
    lang = 'en'

################################ The core ######################################
# Inject the elrte widget
# You can specify the language for the editor.
db.product.description.widget = ElrteWidget(lang=lang)
################################################################################

def index():
    form = SQLFORM(db.product)
    if form.accepts(request.vars, session):
        session.flash = 'submitted %s' % form.vars
        redirect(URL('index'))
    return dict(form=form)
