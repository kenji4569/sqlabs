# -*- coding: utf-8 -*-
# This plugins is licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php
# Authors: Kenji Hosoda <hosoda@s-cubism.jp>
from gluon import *


class lazy_options_widget(SQLFORM.widgets.options):

    def __init__(self, on_key, off_key, where,
                 trigger=None, default='---',
                 keyword='_lazy_options_%(fieldname)s', orderby=None,
                 user_signature=False, hmac_key=None,
                 field=None):
        self.on_key, self.off_key, self.where = (
            on_key, off_key, where
        )
        self.trigger, self.default, self.keyword, self.orderby = (
            trigger, default, keyword, orderby,
        )
        self.user_signature, self.hmac_key = user_signature, hmac_key
        
        if field:
            self.process_now(field)
        
    def _get_select_el(self, trigger, value=None):
        if trigger:
            self._require.orderby = self.orderby or self._require.orderby
            self._require.dbset = self._require.dbset(self.where(trigger))
            options = self._require.options()
            opts = [OPTION(v, _value=k) for (k, v) in options]
            return SELECT(_id='%s__aux' % self._el_id, value=value,
                          _onchange='jQuery("#%s").val(jQuery(this).val());' % self._hidden_el_id,
                          *opts)
        else:
            return self.default
            
    def _pre_process(self, field):
        self._keyword = self.keyword % dict(fieldname=field.name)
        self._el_id = '%s_%s' % (field._tablename, field.name)
        self._disp_el_id = '%s__display' % self._el_id
        self._hidden_el_id = '%s__hidden' % self._el_id

        requires = field.requires
        
        if isinstance(requires, IS_EMPTY_OR):
            requires = requires.other
        if not isinstance(requires, (list, tuple)):
            requires = [requires]
        if requires:
            if hasattr(requires[0], 'options'):
                self._require = requires[0]
            else:
                raise SyntaxError('widget cannot determine options of %s' % field)
        else:
            self._require = []
        
    def process_now(self, field):
        if not hasattr(self, '_keyword'):
            self._pre_process(field)
        
        if self._keyword in current.request.vars:
            if self.user_signature:
                if not URL.verify(current.request, user_signature=self.user_signature, hmac_key=self.hmac_key):
                    raise HTTP(400)
                    
            trigger = current.request.vars[self._keyword]
            raise HTTP(200, self._get_select_el(trigger))
        return self
        
    def __call__(self, field, value, **attributes):
        self._pre_process(field)
        
        request = current.request
        if hasattr(request, 'application'):
            self.url = URL(r=request, args=request.args,
                           user_signature=self.user_signature, hmac_key=self.hmac_key)
            self.process_now(field)
        else:
            self.url = request
        
        script_el = SCRIPT("""
jQuery(document).ready(function() {
    jQuery("body").bind("%(on_key)s", function(e, val) {
        jQuery("#%(disp_el_id)s").html("%(default)s");
        jQuery("#%(hidden_el_id)s").val("");
        var query = {}
        query["%(keyword)s"] = val;
        jQuery.ajax({type: "POST", url: "%(url)s", data: query,
            success: function(html) {
              jQuery("#%(disp_el_id)s").html(html);
        }});
        
    });
    jQuery("body").bind("%(off_key)s", function(e) {
        jQuery("#%(disp_el_id)s").html("%(default)s");
        jQuery("#%(hidden_el_id)s").val("");
    });
});""" % dict(on_key=self.on_key,
              off_key=self.off_key,
              disp_el_id=self._disp_el_id,
              hidden_el_id=self._hidden_el_id,
              default=self.default,
              keyword=self._keyword,
              url=self.url))
        
        select_el = self._get_select_el(self.trigger, value) if self.trigger else None
        
        el = DIV(script_el,
                 SPAN(select_el or self.default, _id=self._disp_el_id),
                 INPUT(_value=value, _type='hidden',
                       _name=field.name, _id=self._hidden_el_id,
                       requires=field.requires),
                 _id=self._el_id)
        return el
