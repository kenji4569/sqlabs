# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

def _gridbutton(buttonclass, buttontext, buttonurl, **attr):
    if '_class' not in attr:
        attr['_class'] = 'btn w2p_trap'
    return A(SPAN(_class='ui-icon  %s' % buttonclass),
             SPAN(buttontext, _class='ui-button-text'),
             _href=buttonurl, _style='float:left;margin-right:20px;', **attr)

def _recordbutton(buttonclass, buttontext, buttonurl, showbuttontext=True, **attr):
    if showbuttontext:
        inner = SPAN(buttontext, _class='ui-button-text') 
    else:
        inner = SPAN(XML('&nbsp'), _style='padding:6px;')
    if '_class' not in attr:
        attr['_class'] = 'ui-btn w2p_trap'
        
    return A(SPAN(_class='ui-icon ' + buttonclass), 
             inner, 
            _title=buttontext, _href=buttonurl, **attr)
                
class SolidGrid(object):

    def __init__(self, renderstyle=False):
        settings = self.settings = Storage()
        settings.gridbutton = _gridbutton
        settings.recordbutton = _recordbutton
        
        if renderstyle:
            _url = URL('static','plugin_solidgrid/solidgrid.css')
            if _url not in current.response.files:
                current.response.files.append(_url)

    def _build_query_by_form(self, db, form, queries={}, field_sep='___',
                              exclude_var_pattern='^.+_page$', formname='form'):
        
        request = current.request
        if form.accepts(request.vars, keepvalues=True, formname=formname):
            new_vars = request.get_vars.copy()
            if 'page' in new_vars:
                del new_vars['page']
            
            for key, value in form.vars.items(): 
                if key != 'id':
                    new_key = '%s_%s' % (formname, key)
                    if value is not None:
                        new_vars[new_key] = value
                    elif new_key in new_vars:
                        del new_vars[new_key]
                    
            import re
            p = re.compile(exclude_var_pattern)
            for key in new_vars.keys(): 
                if p.match(key):
                    del new_vars[key]
                
            redirect(URL(args=request.args, vars=new_vars))
        
        new_queries = []
        for input_el in form.elements('input[type=text]'):
            if '_name' in input_el.attributes:
                key = input_el.attributes['_name']
                request_key = '%s_%s' % (formname, key)
                _key = key.split(field_sep)
                if request_key in request.get_vars:
                    val = request.get_vars[request_key]
                    if val:
                        if len(_key)>=2:
                            tablename, fieldname = _key[:2]
                            field = db[tablename][fieldname]
                            if len(_key)==3:
                                if _key[2] == 'from':
                                    new_queries.append(field>=val)
                                elif _key[2] == 'to':
                                    new_queries.append(field<=val)
                                else:
                                    raise RuntimeError
                            else:
                                if field.unique:
                                    new_queries.append(field==val)
                                else:
                                    new_queries.append(db[tablename][fieldname].like('%'+val+'%'))
                        else:
                            new_queries.append(queries[key](val))
                        input_el.attributes['_value'] = val
                        input_el.attributes['value'] = val
                    
                if len(_key)>=2:
                    tablename, fieldname = _key[:2]
                    requires = db[tablename][fieldname].requires
                    
        for input_el in form.elements('input[type=checkbox]'):
            if '_name' in input_el.attributes:
                key = input_el.attributes['_name']
                request_key = '%s_%s' % (formname, key)
                if request_key in request.get_vars:
                    val = True if str(request.get_vars[request_key]) == 'True' else False
                else:
                    val = False
                if val:    
                    _key = key.split(field_sep)
                    if len(_key)==2:
                        tablename, fieldname = _key
                        new_queries.append(db[tablename][fieldname] == val)
                    else:
                        new_queries.append(queries[key](val))
                input_el.attributes['_checked'] = 'checked' if val else None
                    
        input_els = form.elements('input[type=radio]')
        if input_els:
            from collections import defaultdict
            radios = defaultdict(list)      
            for input_el in input_els:
                radios[input_el.attributes['_name']].append(input_el)
            for key, els in radios.items():
                request_key = '%s_%s' % (formname, key)
                val = request.get_vars.get(request_key, '')
                _key = key.split(field_sep)
                if len(_key)==2:
                    tablename, fieldname = _key
                    if val:
                        new_queries.append(db[tablename][fieldname] == val) 
                else:
                    if val:
                        new_queries.append(queries[key](val))
                for el in els:
                    if el.attributes['_value'] == val:
                        el.attributes['_checked'] = 'checked'
                    else:
                        el.attributes['_checked'] = None
                
        for select_el in form.elements('select'):
            key = select_el.attributes.get('_name')
            if not key:
                continue
            request_key = '%s_%s' % (formname, key)
            if request_key in request.get_vars:
                val = request.get_vars[request_key]
                _key = key.split(field_sep)
                if len(_key)==2:
                    tablename, fieldname = _key
                    new_queries.append(db[tablename][fieldname] == val)
                else:
                    new_queries.append(queries[key](val))
                for option in select_el.elements('option'):
                    if option.attributes['_value'] == val:
                        option.attributes['_selected'] = 'selected'
                    else:
                        option.attributes['_selected'] = None
                   
        if new_queries:
            return reduce(lambda a, b: a & b, new_queries)
        else:
            return None
            
    def get_default_not_empty_marker(self):
        from plugin_notemptymarker import default_not_empty_marker
        return default_not_empty_marker
        
    def mark_not_empty(self, table, marker=None):
        from plugin_notemptymarker import mark_not_empty
        return mark_not_empty(table, marker or self.get_default_not_empty_marker())
    
    def unmark_not_empty(self, table, marker=None):
        from plugin_notemptymarker import unmark_not_empty
        return unmark_not_empty(table)
        
    def url_factory(self, args=[], user_signature=True, hmac_key=None):
        def _url(**b):
            b['args'] = args + b.get('args',[])
            b['user_signature'] = user_signature
            b['hmac_key'] = hmac_key
            return URL(**b)
        return _url
        
    def inline(self, form, table, fields, label, sep=' ', wrapper=None):
        els = []
        for field in fields:
            els.append(form.elements('#%s_%s__label' % (table, field))[0].parent.parent)
        
        children = []
        if form.formstyle == 'table3cols' or type(form.formstyle) == type(lambda:None):
            for el in els:
                children.append(el.elements('td'))
        elif form.formstyle == 'divs':
            for el in els:
                children.append(el.elements('div')[1:])
        else:
            raise RuntimeError, 'formstyle not supported'
        
        child0 = children[0]
        child0[0].components = [label]
        components = []
        for child in children:
            components += child[1].components
            components.append(sep)
        child0[1].components = components[:-1]
        if wrapper:
            child0[1].components = [wrapper(*child0[1].components)]
        
        for el in els[1:]:
            el.attributes['_style'] = 'display:none;'
        for child in children[1:]:
            child[1].components = ''
        
    def __call__(self, 
                query,
                fields=None,
                field_id=None,
                left=None,
                headers={},
                columns=None,
                orderby=None, # EXTENDED for permutation
                searchable=True, # EXTENDED ex) [table.id, table.name, ...]
                sortable=True, # EXTENDED ex) [table.id, table.name, ...]
                paginate=(10, 25, 50, 100), # EXTENDED
                deletable=True,
                editable=True,# EXTENDED ex) [['id', 'name'], 'profile', ...]
                details=True,# EXTENDED ex) [['id', 'name'], 'profile', ...]
                selectable=None, # TODO 
                create=True, # EXTENDED ex) [['id', 'name'], 'profile', ...]
                csv=True,
                links=None,
                upload = '<default>',
                args=[],
                user_signature = True,
                maxtextlengths={}, # NOT WORK
                maxtextlength=20,
                onvalidation=None,
                oncreate=None,
                onupdate=None, 
                ondelete=None,
                sorter_icons=('[^]','[v]'), # NOT WORK
                ui='ui', # ONLY WORK FOR "ui"
                showbuttontext=True,
                _class="web2py_grid",             
                formname='web2py_grid',
                search_widget='default', # NOT WORK
                extracolumns=None, # CUSTOM (same as in SQLTABLE)
                search_queries={}, # CUSTOM
                showid=True, # CUSTOM
                onpermute=None, # CUSTOM
                virtualtable=None, # CUSTOM
                virtualrecord=None, # CUSTOM
                virtualset=None, # CUSTOM
                hmac_key=None, # CUSTOM
                scope=None, #CUSTOM
                scope_default=None, #CUSTOM
                groupby=None, #CUSTOM
                ):
            
        from gluon.dal import SQLALL
        from plugin_solidform import SOLIDFORM
        from plugin_solidtable import SOLIDTABLE, OrderbySelector
        from plugin_paginator import Paginator, PaginateSelector, PaginateInfo
        gridbutton = self.settings.gridbutton
        recordbutton = self.settings.recordbutton
        
        request, session, T = current.request, current.session, current.T
        
        def __oncreate(form):
            session.flash = T('Created')
        def __onupdate(form):
            session.flash = T('Updated')
        def __ondelete(table, tablename, ret):
            session.flash = T('Deleted')
        def __onpermute(table, tablename, ret):
            session.flash = T('Permuted')
        def redirect_patch():
            onupdate
            
        oncreate = oncreate or __oncreate
        onupdate = onupdate or __onupdate
        ondelete = ondelete or __ondelete
        onpermute = onpermute or __onpermute
        
        if ui == 'ui':
            ui = dict(widget='',                      
                      header='',
                      content='',
                      default='',
                      cornerall='',
                      cornertop='',
                      cornerbottom='',
                      button='',
                      buttontext='',
                      buttonadd='ui-icon-plusthick',
                      buttonback='ui-icon-arrowreturnthick-1-w',
                      buttonexport='',
                      buttondelete='ui-icon-close',
                      buttonedit='ui-icon-pencil',
                      buttontable='',
                      buttonview='ui-icon-zoomin',
                      )
        elif not isinstance(ui,dict):
            raise RuntimeError,'SQLFORM.grid ui argument must be a dictionary'
            
        wenabled = (not user_signature or (session.auth and session.auth.user))
        deletable = wenabled and deletable
        # if search_widget=='default':
            # search_widget = SQLFORM.search_menu
            
        url = self.url_factory(args, user_signature, hmac_key)
        
        db = query._db 
        dbset = db(query)
        tables = [db[tablename] for tablename in db._adapter.tables(dbset.query)]
        if not fields:
            fields = reduce(lambda a,b:a+b,
                            [[field for field in table] for table in tables])
        
        new_fields = []
        for item in fields:
            if isinstance(item,SQLALL):
                new_fields += item.table
            else:
                new_fields.append(item)
        fields = new_fields
        
        main_table = tables[0]
        if not field_id:
            field_id = main_table._id
        
        table = field_id.table
        tablename = table._tablename
        referrer = session.get('_web2py_grid_referrer_'+formname, url())
        
        def __from_process_redirect_patch(func):
            def wrapper(form):
                func(form)
                redirect(referrer)
            return wrapper
        oncreate = __from_process_redirect_patch(oncreate)
        onupdate = __from_process_redirect_patch(onupdate)
            
        def check_authorization():
            if user_signature or hmac_key:
                if not URL.verify(request,user_signature=user_signature, hmac_key=hmac_key):
                    session.flash = T('not authorized')
                    redirect(referrer)

        if upload=='<default>':
            upload = lambda filename: url(args=['download',filename])
            if len(request.args)>1 and request.args[-2]=='download':
                check_authorization()
                stream = response.download(request,db)
                raise HTTP(200,stream,**response.headers)
        
        gridbuttons = [gridbutton('%(buttonback)s' % ui, T('Back'), referrer)]
        
        if create and len(request.args)>1 and request.args[-2]=='new':
            check_authorization()
            table = db[request.args[-1]]
            self.mark_not_empty(virtualtable or table)
            if orderby:
                inverted = (orderby.op == orderby.db._adapter.INVERT)
                field = orderby.first if inverted else orderby
                last = dbset.select(field_id, field, limitby=(0,1), orderby=orderby.first if inverted else ~orderby).first()
                last_value = (last[field] or 0) if last else 0
                table[field.name].default = (-1 if inverted else 1) + last_value
                 
            create_form = SOLIDFORM(virtualtable or table, 
                    fields=create if type(create) in (list, tuple) else None,
                    showid=showid,
                    _class='web2py_form',
                    submit_button=T('Create'),
                    ).process(# next=referrer, for web2py-bug
                              onvalidation=onvalidation,
                              onsuccess=oncreate,                          
                              formname=formname)
            self.unmark_not_empty(table)
            res = DIV(create_form,_class=_class)
            res.create_form = create_form
            res.gridbuttons = gridbuttons
            return res
            
        elif details and len(request.args)>2 and request.args[-3]=='view':
            check_authorization()
            table = db[request.args[-2]]
            record = table(request.args[-1]) or redirect(URL('error'))
            form = SOLIDFORM(virtualtable or table, virtualrecord or record, 
                             fields=details if type(details) in (list, tuple) else
                                        create if type(create) in (list, tuple) else None, 
                             upload=upload,
                             readonly=True,
                             showid=showid,
                             _class='web2py_form')
            res = DIV(form,_class=_class)
            res.record = record # CUSTOM
            res.view_form = form # CUSTOM
            if editable:
                gridbuttons.append(
                    gridbutton('%(buttonedit)s' % ui, T('Edit'), 
                                  url(args=['edit', tablename, record.id]))
                )
            res.gridbuttons = gridbuttons
            return res
            
        elif editable and len(request.args)>2 and request.args[-3]=='edit':
            check_authorization()
            table = db[request.args[-2]]
            record = table(request.args[-1]) or redirect(URL('error'))
            self.mark_not_empty(virtualtable or table)
            edit_form = SOLIDFORM(virtualtable or table, virtualrecord or record,
                                fields=editable if type(editable) in (list, tuple) else
                                            create if type(create) in (list, tuple) else None, 
                                upload=upload,
                                deletable=deletable,
                                showid=showid,
                                delete_label=T('Check to delete:'),
                                submit_button=T('Update'),
                                _class='web2py_form')
            self.unmark_not_empty(table)
            edit_form.process(formname=formname,
                              onvalidation=onvalidation,
                              onsuccess=onupdate,
                              # #next=referrer, for web2py-bug
                              )
            res = DIV(edit_form,_class=_class)
            res.record = record # CUSTOM
            res.edit_form = edit_form
            if details:
                gridbuttons.append(
                    gridbutton('%(buttonview)s' % ui, T('View'), 
                                  url(args=['view', tablename, record.id]))
                )
            res.gridbuttons = gridbuttons
            return res
            
        elif deletable and len(request.args)>2 and request.args[-3]=='delete':
            check_authorization()
            table = db[request.args[-2]]
            ret = db(table.id==request.args[-1]).delete()
            if ondelete:
                ondelete(table, request.args[-1], ret)
            redirect(url())
            
        elif csv and len(request.args)>0 and request.args[-1]=='csv':
            check_authorization()
            return dict()
            
        elif request.vars.records and not isinstance(request.vars.records, list):
            request.vars.records=[request.vars.records]
            
        elif not request.vars.records:
            request.vars.records=[]
           
        session['_web2py_grid_referrer_'+formname] = URL(
                r=request, args=request.args,vars=request.vars,
                user_signature=user_signature, hmac_key=hmac_key)
                
        error = None
        search_form = None
        table_el_id = formname + '_maintable'
        
        columns = columns or [str(f) for f in fields 
                                if f.table==main_table and f.readable and (showid or f.type!='id')]
        
        if searchable:
            field_sep = '___'
            
            if searchable is True:
                _exclude_types = ('upload', 'text') if showid else ('id', 'upload', 'text')
                searchable = [f for f in fields 
                                if f.table==main_table and 
                                   f.type not in _exclude_types and f.readable]
            
            _search_fields = []
            _from_tos = []
            for f in searchable:
                _requires = []
                if f.requires and type(f.requires) not in (list, tuple):
                    if isinstance(f.requires, IS_EMPTY_OR):
                        _requires = [f.requires.other]
                    else:
                        _requires = [f.requires]
                _requires = [r for r in _requires if not isinstance(r, IS_NOT_IN_DB)]
                if _requires:
                    if len(_requires) == 1:
                        _requires = _requires[0]
                    _requires = IS_EMPTY_OR(_requires)
                else:
                    _requires = None
                
                _type = 'string' if f.type=='text' else 'integer' if f.type=='id' else f.type
                
                if (f.type in ('double', 'decimal', 'date', 'datetime') or 
                        (f.type == 'integer' and _requires and 
                         isinstance(_requires.other, (IS_INT_IN_RANGE)))):
                    _from_to = [Field(str(f).replace('.', field_sep) + field_sep + 'from', 
                                      type=_type, requires=_requires, 
                                      label=f.label, widget=f.widget),
                                Field(str(f).replace('.', field_sep) + field_sep + 'to', 
                                      type=_type, requires=_requires, 
                                      label=f.label, widget=f.widget)]
                    _from_tos.append(_from_to)
                    _search_fields += _from_to
                elif hasattr(f, 'table'):
                    _search_fields.append(Field(str(f).replace('.', field_sep), 
                        type=_type, requires=_requires, label=f.label, widget=f.widget))
                else:
                    _search_fields.append(f)
            
            search_form = SQLFORM.factory(
                formstyle='divs', submit_button=T('Search'), 
                _class='search_form',
                *_search_fields)
            
            for _from_to in _from_tos:
                self.inline(search_form, 'no_table', 
                    [f.name for f in _from_to], LABEL(_from_to[0].label), SPAN(' - '))
            
            subquery = self._build_query_by_form(db, search_form, 
                            queries=search_queries,
                            field_sep=field_sep, 
                            formname='search_%s' % formname)
        else:
            subquery = None
            
        if subquery:
            dbset = dbset(subquery)
            
        if scope:
            from plugin_tablescope import TableScope
            scope_el = TableScope(dbset, scope, default=scope_default)
            dbset = scope_el.scoped_dataset
            
        if sortable is True:
            sortable = [~f if f.type in ('id', 'date', 'datetime') else f
                            for f in fields 
                                if f.table==main_table and f.type not in ('text', 'upload')]
        if not sortable:
            sortable = []
        if orderby:
            sortable.insert(0, orderby)
        
        orderby_selector = OrderbySelector(sortable)
        
        current_orderby = orderby_selector.orderby()
        permutable = (orderby and (not subquery) and sortable and current_orderby is sortable[0])
           
        extracolumns = extracolumns or []
        
        if permutable:
            if len(request.args)>2 and request.args[-3] in ('up', 'down'):
                check_authorization()
                table = db[request.args[-2]]
                record = table(request.args[-1]) or redirect(URL('error'))
                inverted = (orderby.op == orderby.db._adapter.INVERT)
                field = orderby.first if inverted else orderby
                 
                current_value = record[field]
                if current_value is None:
                    first = dbset.select(field_id, limitby=(0,1), orderby=orderby).first()
                    current_value = (1 if inverted else -1) + (first.id if first else 0)
                    
                if (request.args[-3] == ('down' if inverted else 'up')):  
                    target = dbset(field<current_value
                        ).select(field_id, field, limitby=(0,1), orderby=orderby if inverted else ~orderby).first()
                elif (request.args[-3] == ('up' if inverted else 'down')):   
                    target = dbset(field>current_value
                        ).select(field_id, field, limitby=(0,1), orderby=orderby.first if inverted else orderby).first()
                else:
                    raise NotImplementedError
                if not target:
                    last = dbset.select(field_id, limitby=(0,1), orderby=orderby.first if orderby.first else ~orderby).first()
                    target_value = (-1 if inverted else 1) + (last.id if last else 0)
                else:
                    target_value = target[field]
                    
                db(table.id==record[field_id]).update(**{field.name:target_value})
                if target:
                    db(table.id==target[field_id]).update(**{field.name:current_value})
                
                if onpermute:
                    onpermute(table, request.args[-2], (record, target))
                redirect(url())
                
            first = dbset.select(field_id, limitby=(0,1), orderby=orderby).first()
            first_id = first.id if first else 0
            last = dbset.select(field_id, limitby=(0,1), orderby=orderby.first if orderby.first else ~orderby).first()
            last_id = last.id if last else 0
            extracolumns.append( 
                {'label':DIV(T('Move'), _style='text-align:center;'), 'width':'150px' if showbuttontext else '65px', 
                'content':lambda row, rc: 
                    DIV(recordbutton('ui-icon-triangle-1-n', T('Up'),
                                url(args=['up', tablename, row[field_id]]), showbuttontext)
                                if row[field_id] != first_id else '',
                          recordbutton('ui-icon-triangle-1-s', T('Down'),
                                url(args=['down', tablename, row[field_id]]), showbuttontext)
                                if row[field_id] != last_id else '',
                    _style='text-align:center;')}
            )
        
        if details or editable or deletable:
            extracolumns.append(
                {'label':'', #'width':'%spx' % (_size + 12), 
                'content':lambda row, rc: 
                     DIV(recordbutton('%(buttonview)s' % ui, T('View'),
                                url(args=['view', tablename, row[field_id]]), showbuttontext)
                                    if details else '',
                         recordbutton('%(buttonedit)s' % ui, T('Edit'),
                                url(args=['edit', tablename, row[field_id]]), showbuttontext)
                                    if editable else '',
                         recordbutton('%(buttondelete)s' % ui, T('Delete'),
                                url(args=['delete', tablename, row[field_id]]), showbuttontext,
                                _onclick="""
if(confirm("%s")){return true;} else {jQuery(this).unbind('click').fadeOut();return false;}""" % 
                                          T('Sure you want to delete them?'),)
                                    if deletable else '',
                         _style='white-space:nowrap;')}
            )
            
        if paginate:
            paginate_selector = PaginateSelector(paginate if type(paginate) in (list, tuple) else [paginate])
            current_paginate = paginate_selector.paginate
            paginator = Paginator(paginate=current_paginate) 
            # TODO for groupby
            paginator.records = virtualset(dbset.query).count() if virtualset else dbset.count()
            paginate_info = PaginateInfo(paginator.page, paginator.paginate, paginator.records)
            limitby = paginator.limitby()
        else:
            limitby = None
            current_paginate = None
            
        # TODO
        # if paginator.records == 0:
            # error = 'Not Found'
        if virtualset:
            records = virtualset(dbset.query).select(left=left, limitby=limitby,
                        orderby=current_orderby, groupby=groupby, *fields)
            records.db = virtualtable._db
        else:
            records = dbset.select(left=left, limitby=limitby,
                        orderby=current_orderby, groupby=groupby, *fields)
        
        table = SOLIDTABLE(records, 
                    columns=columns,
                    headers=headers,
                    orderby=orderby_selector,
                    truncate=maxtextlength, #TODO replace
                    extracolumns=extracolumns, 
                    upload=upload)
        table.attributes['_class'] = 'solidtable'
        table.attributes['_id'] = table_el_id
        
        inner = []
        if scope:    
            inner.append(scope_el)
        if current_paginate:
            inner.append(DIV(paginate_info, _class='pagination_information'))
        inner.append(table)
        if current_paginate and paginator.records > current_paginate:
            inner.append(DIV(paginate_selector, paginator, _class='index_footer'))
        
        res = DIV(_class=_class, *inner)
          
        res.records = records
        res.search_form = search_form
        res.error = error
        res.gridbuttons = []
        if create:
            res.gridbuttons.append(
                gridbutton('%(buttonadd)s' % ui, T('Add'), url(args=['new', tablename]))
            )
            
        return res
        
