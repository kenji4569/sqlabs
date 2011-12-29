(function($) {$(function(){
  // ---------------------------------------------------------------------------
  // block events
  // ---------------------------------------------------------------------------
  $('.managed_html_block').hover(function(){
    $(this).children('.managed_html_contents_ctrl').show();
  }, function() {
    $(this).children('.managed_html_contents_ctrl').hide();
  });
  
  $('.managed_html_content').hover(function(){
    $(this).addClass('managed_html_editing');
  }, function() {
    $(this).removeClass('managed_html_editing');
  });
  
  // ---------------------------------------------------------------------------
  // top-bar
  // ---------------------------------------------------------------------------
  var home_url = $("meta[name=managed_html_home_url]").attr("content");
  var home_label = $("meta[name=managed_html_home_label]").attr("content");
  var edit_url = $("meta[name=managed_html_edit_url]").attr("content");
  var preview_url = $("meta[name=managed_html_preview_url]").attr("content");
  var live_url = $("meta[name=managed_html_live_url]").attr("content");
  
  var height = 40;
  var padding = parseInt($('body').css('padding-top'));
  $('body').css('padding-top', (padding+height) + 'px');
  var topbar = $('<div class="managed_html_topbar" style="height:'+height+'px;"></div>');
  var inner = $('<div class="managed_html_container_fluid"></div>');
  var brand = $('<a class="managed_html_brand" href="'+home_url+'">'+home_label+'</a>');
  var nav = $('<ul></ul>');
  if (edit_url!=null) {
    nav.append($('<li><a href="'+edit_url+'">Edit</a></li>'));
  } else {
      nav.append($('<li class="active"><a href="#">Edit</a></li>'));
  }
  if (preview_url!=null) {
    nav.append($('<li><a href="'+preview_url+'">Preview</a></li>'));
  } else {
      nav.append($('<li class="active"><a href="#">Preview</a></li>'));
  }
  
  var secondary_nav = $('<ul class="managed_html_secondary_nav"></ul>');
  secondary_nav.append($('<li><a target="_blank" href="'+live_url+'" style="color:pink;">Check Live Site</a></li>'));
  
  inner.append(brand);
  inner.append(nav);
  inner.append(secondary_nav);
  topbar.append(inner);
  $('body').prepend(topbar);
})})(jQuery);


// ---------------------------------------------------------------------------
// custom ajax functions
// ---------------------------------------------------------------------------

function managed_html_web2py_trap_form(action,target) {
  function params2json(d) {
    if (d.constructor != Array) {return d;}
    var data={};
    for(var i=0;i<d.length;i++) {
        if (typeof data[d[i].name] != 'undefined') {
            if (data[d[i].name].constructor!= Array) { data[d[i].name]=[data[d[i].name],d[i].value ];
            } else {  data[d[i].name].push(d[i].value);  }
        } else { data[d[i].name]=d[i].value; }
    }
    return data;
  };
  jQuery('#'+target+' form').each(function(i){
      var form=jQuery(this);
      if(!form.hasClass('no_trap'))
        form.submit(function(obj){
         var data = params2json(form.serializeArray());
         
         // === For elrte editor widget ===
         var iframe = form.find('iframe');
         if (iframe.length>0) {
            var key = iframe.next().attr('name');
            var value = form.find('iframe:first').contents().find('body').html();
            data[key] = value;
         }
         
         jQuery('.flash').hide().html('');
         managed_html_web2py_ajax_page('post',action,data,target);
         return false;
      });
   });
}
function managed_html_web2py_ajax_page(method,action,data,target) {
  jQuery.ajax({'type':method,'url':action,'data':data,
    'beforeSend':function(xhr) {
      jQuery('#'+target).managed_html_spinner();
      xhr.setRequestHeader('web2py-component-location',document.location);
      xhr.setRequestHeader('web2py-component-element',target);
    },
    'complete':function(xhr,text){
      jQuery('#'+target).managed_html_spinner('remove');
      jQuery('.managed_html_spinner').hide(); // TODO
      var html=xhr.responseText;
      var content=xhr.getResponseHeader('web2py-component-content'); 
      var command=xhr.getResponseHeader('web2py-component-command'); 
      var flash=xhr.getResponseHeader('web2py-component-flash');
      var t = jQuery('#'+target);
      if(content=='prepend') t.prepend(html); 
      else if(content=='append') t.append(html);
      else if(content!='hide') t.html(html); 
      managed_html_web2py_trap_form(action,target);
      web2py_trap_link(target);
      web2py_ajax_init();  
      if(command) eval(command);
      if(flash) jQuery('.flash').html(flash).slideDown();
      }
    });
}
function managed_html_ajax_page(action, data, target) {
  jQuery('.flash').hide().html(''); 
  managed_html_editing(target, data._action=='edit');
  managed_html_web2py_ajax_page('post', action, data, target);
}

// ---------------------------------------------------------------------------
// for block action control
// ---------------------------------------------------------------------------

function managed_html_editing(target, true_or_fase) {
  var el = jQuery('#'+target);
  var ctrl_el = el.parent();
  if (true_or_fase==false) {
    ctrl_el.find('.managed_html_back_btn').hide();
    ctrl_el.find('.managed_html_submit_btn').hide();
    ctrl_el.find('.managed_html_main_comment').hide();
    
    ctrl_el.find('.managed_html_edit_btn').show();
    
    ctrl_el.find('.managed_html_contents_ctrl').hide();
  } else if (true_or_fase==true) {
    ctrl_el.find('.managed_html_back_btn').show();
    ctrl_el.find('.managed_html_submit_btn').show();
    ctrl_el.find('.managed_html_main_comment').show();
    
    ctrl_el.find('.managed_html_edit_btn').hide();
    
    ctrl_el.find('.managed_html_publish_now_btn').hide();
  }
}

function managed_html_published(target, true_or_fase) {
  var el = jQuery('#'+target);
  var ctrl_el = el.parent();
  if (true_or_fase==false) {
    el.addClass('managed_html_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').show();
  } else if (true_or_fase==true) {
    el.removeClass('managed_html_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').hide();
  }
}

// ---------------------------------------------------------------------------
// for movable blocks
// ---------------------------------------------------------------------------

function managed_html_movable(name, indices, keyword, url, confirm_message) {
  function _get_index(_el) {return parseInt(_el.attr('id').split('_').slice(-1)[0]);}
  function _movable(el) {
    el.draggable({
        opacity:0.5, cursor:"move", revert: 'invalid', snap: true, 
        start: function(event, ui){jQuery(event.target).css('background', 'pink');},
        stop: function(event, ui){
            jQuery(event.target).css('background', 'transparent');
        }})
      .droppable({
        accept: ".managed_html_name_" + name,
        activeClass: "managed_html_movable_hover",
        hoverClass: "managed_html_movable_active",
        drop: function(e, ui) {
          var from_el = ui.draggable;
          var to_el = jQuery(this);
          var from_parent = from_el.parent();
          var to_parent = to_el.parent();
          if (!confirm(confirm_message)) {
            from_el.css({left:'0px', top:'0px'});
            return;
          }
          from = _get_index(from_el);
          to = _get_index(to_el);
          data = {
              "indices" : indices,
              "from" : from,
              "to" : to,
              "_action": "permute"
          }
          data[keyword] = name;
          jQuery.ajax({type: 'POST', url: url, data: data,
            success: function (r) {
              var arg_from = indices.indexOf(from);
              var arg_to = indices.indexOf(to);
              indices[arg_from] = to;
              indices[arg_to] = from;
              from_el.css({left:'0px', top:'0px'});
              var from_html = from_parent.html();
              var to_html = to_parent.html();
              from_parent.html(to_html);
              to_parent.html(from_html);
              _movable(from_parent.children(".managed_html_name_" + name));
              _movable(to_parent.children(".managed_html_name_" + name));
              from_parent.children(".managed_html_name_" + name);
              to_parent.children(".managed_html_name_" + name);
                     
              $('.managed_html_block').unbind('hover').hover(function(){
                $(this).children('.managed_html_contents_ctrl').show();
              }, function() {
                $(this).children('.managed_html_contents_ctrl').hide();
              });
              $('.managed_html_content').unbind('hover').hover(function(){
                $(this).addClass('managed_html_editing');
              }, function() {
                $(this).removeClass('managed_html_editing');
              });
              $('.managed_html_block a').unbind("click").click(function(e) {e.preventDefault();});
              
            },
            error: function(r){ 
              from_el.css({left:'0px', top:'0px'});
            },
            beforeSend:function(xhr) {
              to_parent.managed_html_spinner();
              xhr.setRequestHeader('web2py-component-location',document.location);
              xhr.setRequestHeader('web2py-component-element',el.attr('id'));
              jQuery('.flash').hide().html('');},
            complete: function(xhr, text) {
              to_parent.managed_html_spinner('remove');
              var flash=xhr.getResponseHeader('web2py-component-flash');
              if(flash) jQuery('.flash').html(flash).slideDown();
            }
          });
        }
      }); 
    }
    _movable(jQuery(".managed_html_name_" + name));
}

/*
    Original by jquery.spinner.js
    
    Spinner provides a simple approach for adding and removing a preloader
    for your web applications. Usage is as simple as calling $('elem').spinner() and
    subsequently $('elem').spinner.remove(). You may create your own preloader
    at http://www.ajaxload.info. Please note that if you use a custom preloader,
    you must pass in the new height and width as options.
    
    Copyright (C) 2010 Corey Ballou
    Website: http://www.jqueryin.com
    Documentation: http://www.jqueryin.com/projects/spinner-jquery-preloader-plugin/

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */
(function($) {
    $.fn.managed_html_spinner = function(options) {
        var opts = $.extend({}, $.fn.managed_html_spinner.defaults, options);

        return this.each(function() {
            var l=0, t=0, w=0, h=0, shim=0, $s;
            var $this = $(this);
            
            // removal handling
            if (options == 'remove' || options == 'close') {
                var $s = $this.data('spinner');
                var o = $this.data('opts');
                if (typeof $s != 'undefined') {
                    $s.remove();
                    $this.removeData('spinner').removeData('opts');
                    if (o.hide) $this.css('visibility', 'visible');
                    o.onFinish.call(this);
                    return;
                }
            }
            
            // retrieve element positioning
            var pos = $this.offset();
            w = $this.outerWidth();
            h = $this.outerHeight();
            
            // calculate vertical centering
            if (h > opts.height) shim = Math.round((h - opts.height)/ 2);
            else if (h < opts.height) shim = 0 - Math.round((opts.height - h) / 2);
            t = pos.top + shim + 'px';
            
            // calculate horizontal positioning
            if (opts.position == 'right') {
                l = pos.left + w + 10 + 'px';
            } else if (opts.position == 'left') {
                l = pos.left - opts.width - 10 + 'px';
            } else {
                l = pos.left + Math.round(.5 * w) - Math.round(.5 * opts.width) + 'px';
            }
            
            // call start callback
            opts.onStart.call(this);
            
            // hide element?
            if (opts.hide) $this.css('visibility', 'hidden');
            
            // create the spinner and attach
            $s = $('<div class="managed_html_spinner" style="left: ' + l +'; top: ' + t + '; width: ' + opts.width + 'px; height: ' + opts.height + 'px; z-index: ' + opts.zIndex + ';"></div>').appendTo('body');
            
            // removal handling
            $this.data('spinner', $s).data('opts', opts);
        });
    };
    
    // default spinner options
    $.fn.managed_html_spinner.defaults = {
        position    : 'left'       // left, right, center
        , height    : 16            // height of spinner img
        , width     : 16            // width of spinner img
        , zIndex    : 1001          // z-index of spinner
        , hide      : false         // whether to hide the elem
        , onStart   : function(){ } // start callback
        , onFinish  : function(){ } // end callback
    };
})(jQuery);