# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *
from gluon.storage import Storage

class CommentBox(object):
    
    def __init__(self, db):
        self.db = db
        
        settings = self.settings = Storage()
        
        settings.oncomment = None
        
        settings.select_fields = []
        settings.select_attributes = {}
        settings.content = lambda row: row
        
        settings.table_comment_name = 'comment'
        settings.table_comment = None
        
    def define_tables(self, table_target_name, table_user_name, 
                      migrate=True, fake_migrate=False):
        db, settings = self.db, self.settings
        
        if not settings.table_comment_name in db.tables:
            settings.table_comment = db.define_table(
                settings.table_comment_name,
                Field('target', 'reference %s' % table_target_name),
                Field('user', 'reference %s' % table_user_name),
                Field('body', 'text'),
                Field('created_on', 'datetime', default=current.request.now),
                migrate=migrate, fake_migrate=fake_migrate)
                
    def add_comment(self, user_id, target_id, body):
        db, settings, table = self.db, self.settings, self.settings.table_comment
        table.insert(target=target_id,
                     user=user_id,
                     body=body)
        if settings.oncomment:
            settings.oncomment(target_id, user_id, current.request.now)
            
    def remove_comment(self, user_id, comment_id):
        db, table = self.db, self.settings.table_comment
        
        if db(table.id==comment_id)(table.user==user_id).count():
            db(table.id==comment_id).delete()
        else:
            raise ValueError
            
    def comments(self, target_id):
        db, table = self.db, self.settings.table_comment
        return db(table.target==target_id)
        
    def element(self, user_id, target_id):  
        settings = self.settings
        _id = 'plugin_comment_box__%s__%s' % (user_id, target_id)
            
        records = self.comments(target_id).select(
            *settings.select_fields, **settings.select_attributes
        )
        comment_els = []
        for record in records:
            comment_els.append(LI(settings.content(record)))
        text_el = TEXTAREA('', _rows=1, _class='plugin_comment_box_comment')
        
        return DIV(UL(*comment_els), text_el, _id=_id)
    
    def process(self):
        import uuid
        
        form = FORM(INPUT(_type='hidden', _name='form_id'),
                    INPUT(_type='hidden', _name='target_id'),
                    INPUT(_type='hidden', _name='user_id'),
                    INPUT(_type='hidden', _name='body'))
        if form.accepts(current.request.vars, current.session):
            user_id, target_id = form.vars.user_id, form.vars.target_id
            self.add_comment(user_id, target_id, form.vars.body)
            current.response.js = """
jQuery('#%(form_id)s').find('input[name=_formkey]').val('%(formkey)s');
""" % dict(form_id=form.vars.form_id, formkey=form.formkey)
            raise HTTP(200, self.element(user_id, target_id))
        
        _form_id = str(uuid.uuid4())
        form.attributes['_id'] = _form_id
        
        script = SCRIPT("""
(function($) {
$(function(){
    $('.plugin_comment_box_comment').live('keypress', function(e){
        if (e.keyCode==13){
            $('.flash').hide().html('');
            var form = $('#%(form_id)s'),
                text = $(this),
                el_id = text.parent().attr('id');
                body = text.val(),
                ids = el_id.split('__'),
                user_id = ids[1],
                target_id = ids[2];
            form.children('input[name=form_id]').attr('value', '%(form_id)s');
            form.children('input[name=user_id]').attr('value', user_id);
            form.children('input[name=target_id]').attr('value', target_id);
            form.children('input[name=body]').attr('value', body);
            web2py_ajax_page('post', '', form.serialize(), el_id);
            return false;
        }
    });
});})(jQuery);""" % dict(form_id=_form_id))
        form.components.append(script)
            
        return form