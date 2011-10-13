# -*- coding: utf-8 -*-
from plugin_catalog import Catalog
from gluon.tools import Auth
import unittest
from gluon.contrib.populate import populate
from plugin_solidtable import SOLIDTABLE
from plugin_multiselect_widget import hmultiselect_widget
from gluon.validators import Validator

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
table_variant.sku.requires = IS_NOT_EMPTY()

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
    
class IS_DELETE_OR(Validator):
    def __init__(self, deleted, other):
        self.deleted, self.other = deleted, other
        
    def __call__(self, value):
        if self.deleted:
            return (value, None)
        if isinstance(self.other, (list, tuple)):
            for item in self.other:
                value, error = item(value)
                if error: break
            return value, error
        else:
            return self.other(value)
    
def variants_widget(field, value, **attributes):
    _id = '%s_%s' % (field._tablename, field.name)
    attr = dict(_type = 'hidden', value = (value!=None and str(value)) or '',
                _id = _id, _name = field.name, requires = field.requires,
                _class = 'string')
    trigger = request.vars.option_groups
    if type(trigger) == list:
        trigger = ','.join(trigger)
        
    keyword = '_variants'
    disp_el_id='_variants_disp_el_id'
    ajax = (keyword in request.vars)
    
    def _get_variant_form(option_set_key):
        def _get_comment(name):
            if option_set_key != 'master':
                return INPUT(_type='button', _value='→ apply all',
                             _onclick='apply_for_all_variants("%s", "%s");' % (option_set_key, name))
        
        deleted = (option_set_key != 'master') and not request.vars.get('variant__%s__active' % option_set_key)
        fields = [Field('variant__%s__%s' % (option_set_key, f.name), f.type, 
                        readable=f.readable, writable=f.writable,
                        requires=IS_DELETE_OR(deleted, f.requires), label=f.label, 
                        comment=_get_comment(f.name))
                    for f in table_variant]
        
        if option_set_key != 'master':
            fields.insert(0, Field('variant__%s__active' % option_set_key, 
                                   'boolean', default=True if ajax else not deleted, 
                                    label='Active', comment=_get_comment('active')))
                                    
        return SQLFORM.factory( buttons=[], *fields).components[0]
        
    def _output():
        option_group_ids = [option_group_id for option_group_id 
                                in (trigger or request.vars.get(keyword, '')).split(',')
                                    if option_group_id]
        
        option_sets = catalog.get_option_sets(option_group_ids)
        if not option_sets:
            return _get_variant_form('master')
        
        option_set_keys = ['_'.join([str(r.id) for r in option_set])
                        for option_set in option_sets]
        
        script = SCRIPT(""" 
jQuery.fn.mod_val = function(value){
    var el = jQuery(this);
    if (value === undefined) {
        if(el.is("input[type=checkbox]")) { return el.is(":checked");}
        else { return el.val(); }
    } else {
        if(el.is("input[type=checkbox]")) { return el.prop('checked', value); }
        else { return el.val(value); }
    }
};
function apply_for_all_variants(option_set_key, name) { 
    var option_set_keys = %s;
    var value = jQuery("[name=variant__"+option_set_key+"__"+name+"]").mod_val();
    jQuery.each(option_set_keys, function() {
        jQuery("[name=variant__"+this+"__"+name+"]").mod_val(value);
    });
}""" % ('["%s"]' % '","'.join(option_set_keys)))
   
        inner = []
        for option_set_key, option_set in zip(option_set_keys, option_sets):
            inner.append(DIV(
                H4(' '.join([r.name for r in option_set])),
                _get_variant_form(option_set_key)))
                
        return DIV(script, *inner) 
        
    if ajax:
        raise HTTP(200, _output())
         
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
}); """ % dict(keyword=keyword, 
               url=URL(r=request, args=request.args), 
               disp_el_id=disp_el_id))
               
    option_fields = []
    for i in range(catalog.settings.max_options):
        option_fields.append(
            Field('option_group_%s' % i, table_option_group,
                  requires=IS_IN_DB(db, table_option_group.id, '%(name)s')))
    
    return SPAN(script, INPUT(**attr), DIV(_output(), _id=disp_el_id), **attributes)
    
def index():
    if not request.args(0):
        form = SQLFORM.factory(table_product, 
                               Field('option_groups', 'list:reference', 
                                     widget=option_groups_widget,
                                     requires=IS_EMPTY_OR(IS_IN_DB(db, 
                                                table_option_group.id, '%(name)s', multiple=True))),
                               Field('variants', widget=variants_widget))
        form.validate()
        if form.vars.option_groups:
            if all(not v for k, v in form.vars.items() 
                         if k.startswith('variant__') and k.endswith('__active')):
                form.accepted = False
                response.flash = 'Input at least one variant'
        
        if form.accepted:
            product_id = table_product.insert(**table_product._filter_fields(form.vars))
            
            if not form.vars.option_groups:
                # --- create a master variant ---
                reduced_vars = dict((k[len('variant__master__'):], v) for k, v 
                                            in form.vars.items() if k.startswith('variant__master__'))
                table_variant.insert(product=product_id, 
                                     **table_variant._filter_fields(reduced_vars))
            else:
                # --- create variants ---
                from collections import defaultdict
                reduced_vars_dict = defaultdict(dict)
                for k, v in form.vars.items():
                    if k.startswith('variant__'):
                        option_set_key, var_name = k.split('__')[1:3]
                        reduced_vars_dict[option_set_key][var_name] = v
                for option_set_key, reduced_vars in reduced_vars_dict.items():
                    updator = dict(product=product_id)
                    for i, option_id in enumerate(option_set_key.split('_')):
                        updator['option_%s' % (i + 1)] = option_id
                    updator.update(**table_variant._filter_fields(reduced_vars))
                    table_variant.insert(**updator)    
                    
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
        