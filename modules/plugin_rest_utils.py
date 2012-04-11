## --------------
from gluon import *
from gluon.contenttype import contenttype
import os, sys, traceback

## --------------------------------------------------------------------------------
ORIGINAL_DAL = DAL

class DAL(ORIGINAL_DAL):

    def parse_as_rest(self, patterns,args,vars,queries=None,nested_select=True,custom_select=None):
        """
    EXAMPLE:
    
    db.define_table('person',Field('name'),Field('info'))
    db.define_table('pet',Field('owner',db.person),Field('name'),Field('info'))
    
    @request.restful()
    def index():
    def GET(*args,**vars):
        patterns = [
            "/friends[person]",
            "/{friend.name.startswith}",
            "/{friend.name}/:field",
            "/{friend.name}/pets[pet.owner]",
            "/{friend.name}/pet[pet.owner]/{pet.name}",
            "/{friend.name}/pet[pet.owner]/{pet.name}/:field"
            ]
        parser = db.parse_as_rest(patterns,args,vars)
        if parser.status == 200:
            return dict(content=parser.response)
        else:
            raise HTTP(parser.status,parser.error)
    def POST(table_name,**vars):
        if table_name == 'person':
            return db.person.validate_and_insert(**vars)
        elif table_name == 'pet':
            return db.pet.validate_and_insert(**vars)
        else:
            raise HTTP(400)
    return locals()
        """
        import re
        from gluon.dal import Row
        db = self
        re1 = re.compile('^{[^\.]+\.[^\.]+(\.(lt|gt|le|ge|eq|ne|contains|startswith|year|month|day|hour|minute|second))?(\.not)?}$')
        re2 = re.compile('^.+\[.+\]$')
    
        def auto_table(table,base='',depth=0):
            patterns = []
            for field in db[table].fields:
                if base:
                    tag = '%s/%s' % (base,field.replace('_','-'))
                else:
                    tag = '/%s/%s' % (table.replace('_','-'),field.replace('_','-'))
                f = db[table][field]
                if not f.readable: continue
                if f.type=='id' or 'slug' in field or f.type.startswith('reference'):
                    tag += '/{%s.%s}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                elif f.type.startswith('boolean'):
                    tag += '/{%s.%s}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                elif f.type.startswith('double') or f.type.startswith('integer'):
                    tag += '/{%s.%s.ge}/{%s.%s.lt}' % (table,field,table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                elif f.type.startswith('list:'):
                    tag += '/{%s.%s.contains}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                elif f.type in ('date','datetime'):
                    tag+= '/{%s.%s.year}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                    tag+='/{%s.%s.month}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                    tag+='/{%s.%s.day}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                if f.type in ('datetime','time'):
                    tag+= '/{%s.%s.hour}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                    tag+='/{%s.%s.minute}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                    tag+='/{%s.%s.second}' % (table,field)
                    patterns.append(tag)
                    patterns.append(tag+'/:field')
                if depth>0:
                    for rtable,rfield in db[table]._referenced_by:
                        tag+='/%s[%s.%s]' % (rtable,rtable,rfield)
                        patterns.append(tag)
                        patterns += auto_table(rtable,base=tag,depth=depth-1)
            return patterns
    
        if patterns=='auto':
            patterns=[]
            for table in db.tables:
                if not table.startswith('auth_'):
                    patterns.append('/%s[%s]' % (table,table))
                    patterns += auto_table(table,base='',depth=1)
        else:
            i = 0
            while i<len(patterns):
                pattern = patterns[i]
                tokens = pattern.split('/')
                if tokens[-1].startswith(':auto') and re2.match(tokens[-1]):
                    new_patterns = auto_table(tokens[-1][tokens[-1].find('[')+1:-1],
                                              '/'.join(tokens[:-1]))
                    patterns = patterns[:i]+new_patterns+patterns[i+1:]
                    i += len(new_patterns)
                else:
                    i += 1
        if '/'.join(args) == 'patterns':
            return Row({'status':200,'pattern':'list',
                        'error':None,'response':patterns})
        for pattern in patterns:
            otable=table=None
            if not isinstance(queries,dict):
                dbset=db(queries)
            i=0
            tags = pattern[1:].split('/')
            if len(tags)!=len(args):
                continue
            for tag in tags:
                if re1.match(tag):
                    # print 're1:'+tag
                    tokens = tag[1:-1].split('.')
                    table, field = tokens[0], tokens[1]
                    if not otable or table == otable:
                        if len(tokens)==2 or tokens[2]=='eq':
                            query = db[table][field]==args[i]
                        elif tokens[2]=='ne':
                            query = db[table][field]!=args[i]
                        elif tokens[2]=='lt':
                            query = db[table][field]<args[i]
                        elif tokens[2]=='gt':
                            query = db[table][field]>args[i]
                        elif tokens[2]=='ge':
                            query = db[table][field]>=args[i]
                        elif tokens[2]=='le':
                            query = db[table][field]<=args[i]
                        elif tokens[2]=='year':
                            query = db[table][field].year()==args[i]
                        elif tokens[2]=='month':
                            query = db[table][field].month()==args[i]
                        elif tokens[2]=='day':
                            query = db[table][field].day()==args[i]
                        elif tokens[2]=='hour':
                            query = db[table][field].hour()==args[i]
                        elif tokens[2]=='minute':
                            query = db[table][field].minutes()==args[i]
                        elif tokens[2]=='second':
                            query = db[table][field].seconds()==args[i]
                        elif tokens[2]=='startswith':
                            query = db[table][field].startswith(args[i])
                        elif tokens[2]=='contains':
                            query = db[table][field].contains(args[i])
                        else:
                            raise RuntimeError, "invalid pattern: %s" % pattern
                        if len(tokens)==4 and tokens[3]=='not':
                            query = ~query
                        elif len(tokens)>=4:
                            raise RuntimeError, "invalid pattern: %s" % pattern
                        if not otable and isinstance(queries,dict):
                            dbset = db(queries[table])
                        dbset=dbset(query)
                    else:
                        raise RuntimeError, "missing relation in pattern: %s" % pattern
                elif re2.match(tag) and args[i]==tag[:tag.find('[')]:
                    ref = tag[tag.find('[')+1:-1]
                    if '.' in ref and otable:
                        table,field = ref.split('.')
                        # print table,field
                        if nested_select:
                            try:
                                dbset=db(db[table][field].belongs(dbset._select(db[otable]._id)))
                            except ValueError:
                                return Row({'status':400,'pattern':pattern,
                                            'error':'invalid path','response':None})
                        else:
                            items = [item.id for item in dbset.select(db[otable]._id)]
                            dbset=db(db[table][field].belongs(items))
                    else:
                        table = ref
                        if not otable and isinstance(queries,dict):
                            dbset = db(queries[table])
                        dbset=dbset(db[table])
                elif tag==':field' and table:
                    # # print 're3:'+tag
                    field = args[i]
                    if not field in db[table]: break
                    try:
                        item =  dbset.select(db[table][field],limitby=(0,1)).first()
                    except ValueError:
                        return Row({'status':400,'pattern':pattern,
                                    'error':'invalid path','response':None})
                    if not item:
                        return Row({'status':404,'pattern':pattern,
                                    'error':'record not found','response':None})
                    else:
                        return Row({'status':200,'response':item[field],
                                    'pattern':pattern})
                elif tag != args[i]:
                    break
                otable = table
                i += 1
                if i==len(tags) and table:
                    ofields = vars.get('order',db[table]._id.name).split('|')
                    try:
                        orderby = [db[table][f] if not f.startswith('~') else ~db[table][f[1:]] for f in ofields]
                    except KeyError:
                        return Row({'status':400,'error':'invalid orderby','response':None})
                    fields = [field for field in db[table] if field.readable]
                    count = dbset.count()
                    try:
                        offset = int(vars.get('offset',None) or 0)
                        limits = (offset,int(vars.get('limit',None) or 1000)+offset)
                    except ValueError:
                        Row({'status':400,'error':'invalid limits','response':None})
                    if count > limits[1]-limits[0]:
                        Row({'status':400,'error':'too many records','response':None})
                    try:
                        if custom_select:
                            response = custom_select(dbset, limitby=limits,orderby=orderby,*fields)
                        else:
                            response = dbset.select(limitby=limits,orderby=orderby,*fields)
                    except ValueError:
                        return Row({'status':400,'pattern':pattern,
                                    'error':'invalid path','response':None})
                    return Row({'status':200,'response':response,'pattern':pattern})
        return Row({'status':400,'error':'no matching pattern','response':None})
    

## --------------------------------------------------------------------------------
def restful():
    from gluon import current
    self = current.request
    def wrapper(action,self=self):
        def f(_action=action,_self=self,*a,**b):
            self.is_restful = True
            method = _self.env.request_method or 'GET'
            if len(_self.args) and '.' in _self.args[-1]:
                _self.args[-1],_self.extension = _self.args[-1].rsplit('.',1)
                current.response.headers['Content-Type'] = \
                    contenttype(_self.extension.lower())
            if not method in ['GET','POST','DELETE','PUT']:
                raise HTTP(400,"invalid method")
            rest_action = _action().get(method,None)
            if not rest_action:
                raise HTTP(400,"method not supported")
            try:
                return rest_action(*_self.args,**_self.vars)
            except TypeError, e:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                if len(traceback.extract_tb(exc_traceback))==1:
                    raise HTTP(400,"invalid arguments")
                else:
                    raise e
        f.__doc__ = action.__doc__
        f.__name__ = action.__name__
        return f
    return wrapper


## --------------------------------------------------------------------------------
from functools import wraps
def progressive_enhance():
    def wrapper(action):
        if '_template' in current.request.vars:
            from pybars import Compiler
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file = open(base_dir + current.request.vars['_template'], 'r')
            source = ''
            try:
                source = unicode(file.read(), 'utf-8')
                del current.request.vars['_template']
            finally:
                file.close()

            _template = Compiler().compile(source)
            @wraps(action)
            def f(*a, **b):
                content = action(*a, **b)
                return XML(_template(content['content']).__unicode__())
            return f
        else:
            return action
    return wrapper

