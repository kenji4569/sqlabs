# -*- coding: utf-8 -*-
from plugin_catalog import Catalog
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate
from plugin_solidtable import SOLIDTABLE
from plugin_multiselect_widget import hmultiselect_widget

if request.function == 'test':
    db = DAL('sqlite:memory:')
    
### setup core objects #########################################################
auth = Auth(db)
catalog = Catalog(db)
catalog.settings.table_product_name = 'plugin_catalog_product'
catalog.settings.table_variant_name = 'plugin_catalog_product_variant'
catalog.settings.table_option_group_name = 'plugin_catalog_product_option_group'
catalog.settings.table_option_name = 'plugin_catalog_product_option'
catalog.settings.extra_fields = {
    'plugin_catalog_product': [
        Field('long_description', 'text'),
        Field('created_on', 'datetime', default=request.now,
              readable=False, writable=False),
        # --- Other possible fields ---
        # Field('status'),
        # Field('short_description', 'text'),
        # Field('large_image', 'upload'),
        # Field('small_image', 'upload'),
        # Field('manufacturer'),
        # Field('brand'),
        # Field('reward_point_rate'),
    ],
    'plugin_catalog_product_variant': [
        Field('sku'),
        Field('sale_price', 'integer'),
        Field('inventory_quantity', 'integer'),
        # --- Other possible fields ---
        # Field('retail_price', 'integer'),
        # Field('inventory_level', 'integer'),
        # Field('weight', 'integer'),
        # Field('taxable', 'boolean'),
    ],
    # 'plugin_catalog_product_option': [
        # Field('price_charge'),],
}

### define tables ##############################################################
catalog.define_tables()
table_product = catalog.settings.table_product
table_variant = catalog.settings.table_variant
table_option_group = catalog.settings.table_option_group
table_option = catalog.settings.table_option
table_product.name.requires = IS_NOT_EMPTY()

### populate records ###########################################################
import datetime
deleted = db(table_product.created_on<request.now-datetime.timedelta(minutes=60)).delete()
if deleted:
    table_variant.truncate()
    table_option_group.truncate()
    table_option.truncate()
    session.flash = 'the database has been refreshed'
    redirect(URL('index'))
    
if not db(table_option_group.id>0).count():
    data = {'color': ('red', 'green', 'blue'),
            'size': ('small', 'large'),
            'value': ('1', '2', '3', '4')}
    for option_group_name in data.keys():
        id = table_option_group.insert(name=option_group_name)
        for option_name in data[option_group_name]:
            table_option.insert(option_group=id, name=option_name)

### demo functions #############################################################

def option_groups_widget(field, value, **attributes):
    inner = hmultiselect_widget(field, value, **attributes)
    script = SCRIPT(""" 
jQuery(document).ready(function() {
    var buttons = jQuery('#%(id)s input[type=button]');
    buttons.click(function(){
        var options = jQuery(%(select_el_id)s).children();
        if (options.length >= %(max_options)s) {
            jQuery(%(unselected_el_id)s).prop('disabled', true);
            jQuery(buttons[0]).prop('disabled', true);
        } else {
            jQuery(%(unselected_el_id)s).prop('disabled', false);
            jQuery(buttons[0]).prop('disabled', false);
        }
        if (options.length <= %(max_options)s) {
            jQuery('body').trigger('option_groups_changed', 
                jQuery.map(options, function(val){return val.value}).join(','));
        }
    })
}); """ % dict(id=inner.attributes['_id'],
               select_el_id=field.name,
               unselected_el_id="unselected_%s" % field.name,
               max_options=catalog.settings.max_options))
    return SPAN(script, inner)

def variants_widget(field, value, **attributes):
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(_type = 'hidden', value = (value!=None and str(value)) or '',
                _id = _id, _name = field.name, requires = field.requires,
                _class = 'string')
    keyword = '_variants'
    disp_el_id = '_variants_disp_el_id'
    url = URL(r=request, args=request.args)
    
    def variants_inner():
        def get_variant_form(id):
            return SQLFORM.factory(buttons=[],
                    *[Field('variant__%s__%s' % (id, f.name), f.type, 
                          readable=f.readable, writable=f.writable,
                          requires=f.requires, label=f.label) 
                            for f in table_variant]).components[0]
        
        options_set = [db(table_option.option_group==option_group_id).select()
                        for option_group_id in request.vars.get(keyword, '').split(',')
                            if option_group_id]
        if not options_set:
            return get_variant_form('master')
            
        def itertools_product(*args, **kwds): # for python < 2.6
            pools = map(tuple, args) * kwds.get('repeat', 1)
            result = [[]]
            for pool in pools:
                result = [x+[y] for x in result for y in pool]
            for prod in result:
                yield tuple(prod)
        
        inner = []
        for option_set in itertools_product(*options_set):
            inner.append(DIV(
                H4(' '.join([r.name for r in option_set])),
                get_variant_form('_'.join([str(r.id) for r in option_set]))))
        return DIV(*inner) 
        
    if keyword in request.vars:
        raise HTTP(200, variants_inner())
         
    script = SCRIPT(""" 
jQuery(document).ready(function() {
    jQuery('body').bind('option_groups_changed', function(e, val) {
        var query = {}
        query["%(keyword)s"] = val;
        jQuery.ajax({type: "POST", url: "%(url)s", data: query, 
            success: function(html) {
              jQuery("#%(disp_el_id)s").html(html);
        }});
    });
}); """ % dict(keyword=keyword, url=url, disp_el_id=disp_el_id) )        
    option_fields = []
    for i in range(catalog.settings.max_options):
        option_fields.append(
            Field('option_group_%s' % i, table_option_group,
                  requires=IS_IN_DB(db, table_option_group.id, '%(name)s')))
    
    return SPAN(script, INPUT(**attr), DIV(variants_inner(), _id=disp_el_id), **attributes)
    
def index():
    if not request.args(0):
        
        form = SQLFORM.factory(table_product, 
                               Field('option_groups', 'list:reference', 
                                     widget=option_groups_widget,
                                     requires=IS_EMPTY_OR(IS_IN_DB(db, 
                                                table_option_group.id, '%(name)s', multiple=True))),
                               Field('variants', widget=variants_widget))
        if form.process().accepted:
            # product_id, master_variant_id = catalog.add_product(form.vars)
            session.flash = form.vars # T('Record Created')
            redirect(URL())
        
        extracolumns = [{'label':'Options',
                         'content':lambda row, rc: A('Options',
                            _href=URL('index', args=['options', row.id]))},     
                    ]
        products = SOLIDTABLE(db(table_product.id>0).select(), 
                              headers='labels', extracolumns=extracolumns)
        return dict(product_form=form, 
                    products=products,
                    unit_tests=[A('basic test', _href=URL('test'))])
                    
    elif request.args(0) == 'variants':
        form = SQLFORM.factory(Field('hoge'))
        info = ''
        if form.process().accepted:
            info = 'test'
            print 'A'
        return BEAUTIFY(dict(form=form, info=info))
                       
  
### unit tests #################################################################
class TestCatalog(unittest.TestCase):

    def setUp(self):
        table_product.truncate()
        
    def test_basic(self):
        pass
        
def run_test(TestCase):
    import cStringIO
    stream = cStringIO.StringIO()
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCase)
    unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
    return stream.getvalue()
    
def test():
    return dict(back=A('back', _href=URL('index')),
                output=CODE(run_test(TestCatalog)))
        