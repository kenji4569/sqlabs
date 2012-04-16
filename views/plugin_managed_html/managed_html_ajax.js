jQuery.extend(jQuery.easing,
{
  easeInQuart: function (x, t, b, c, d) {
    return c*(t/=d)*t*t*t + b;
  },
});
	
(function($) {$(function(){
  
  managed_html_init_blocks();
  
  // ---------------------------------------------------------------------------
  // top-bar
  // ---------------------------------------------------------------------------
  var preview_url = "{{=preview_url}}";
  var live_url = "{{=live_url}}";
  
  var height = 40;
  var padding = parseInt($('body').css('padding-top'));
  $('body').css('padding-top', (padding+height) + 'px');
  var topbar = $('<div class="managed_html_topbar" data-dropdown="dropdown" style="height:'+height+'px;"></div>');
  var inner = $('<div class="managed_html_container_fluid"></div>');
  var brand = $('<a class="managed_html_brand" href="{{=home_url}}">{{=home_label}}</a>');
  var nav = $('<ul></ul>');
  {{if edit_url:}}
    nav.append($('<li><a href="{{=edit_url}}">Edit</a></li>'));
  {{else:}}
    nav.append($('<li class="active"><a href="#">Edit</a></li>'));
  {{pass}}
  {{if preview_url:}}
    nav.append($('<li><a href="{{=preview_url}}">Preview</a></li>'));
  {{else:}}
    nav.append($('<li class="active"><a href="#">Preview</a></li>'));
  {{pass}}
  {{if show_page_grid:}}
    nav.append($('<li><a href="#" onclick="managed_html_show_page_grid('+"'True'"+');">+ Page</a></li>'));
  {{pass}}
  
  nav.append($(
  '<li class="dropdown"><a href="#" class="dropdown-toggle" style="color:skyblue;">Device</a>' + 
  '<ul class="dropdown-menu">' + 
    {{for device in devices:}}
    '<li><a href="{{=device['url']}}">{{=device['label']}}</a></li>' +
    {{pass}}
  '</ul></li>'
  ));
  {{ if current_device and 'view_width' in current_device:}}
    $('#main').css('width','{{=current_device['view_width']}}px');
    var reference_view = $('<div id="managed_reference_view"></div>').css('left', '{{=int(current_device['view_width']) + 40}}px');
    var reference_view_content = $('<div id="managed_reference_view_content">');
    reference_view.append(reference_view_content);
    $('body').prepend(reference_view);
    managed_html_web2py_ajax_page('post', '{{=reference_url}}', {'_action':'reference'}, 'managed_reference_view_content');
  {{pass}}
  var secondary_nav = $('<ul class="managed_html_secondary_nav"></ul>');
  secondary_nav.append($('<li><a target="_blank" href="'+live_url+'" style="color:pink;">Check Live Site</a></li>'));
  
  inner.append(brand);
  inner.append(nav);
  inner.append(secondary_nav);
  topbar.append(inner);
  
  $('body').prepend(topbar).load(function() {
    $('body').dropdown( '[data-dropdown] a.menu, [data-dropdown] .dropdown-toggle' );
  });
  
  // ---------------------------------------------------------------------------
  // link management TODO refactoring
  // ---------------------------------------------------------------------------
  $('a').not('.managed_html_topbar a').each(function() {
    var el = $(this);
    var href = el.attr('href');
  if (href == undefined) { return; }
    if (href.slice(0, 4) == 'http') {
      el.click(function(){ managed_html_show_page_grid(href); return false;})
    }
  });
  
})})(jQuery);

function managed_html_init_blocks() {

  // ---------------------------------------------------------------------------
  // block events
  // ---------------------------------------------------------------------------
  jQuery('.managed_html_content_block').hover(function(e){
    managed_html_show_content_ctrl(jQuery(this));
  }, function(e) {
    jQuery(this).children('.managed_html_content_ctrl').hide();
  });
  
  jQuery('.managed_html_collection_anchor, .managed_html_collection_anchor_pending, .managed_html_collection_ctrl').hover(function(){
    managed_html_show_collection_ctrl(jQuery(this).closest('.managed_html_collection_block'));
  }, function() {
    jQuery(this).closest('.managed_html_collection_block').children('.managed_html_collection_ctrl').hide();
  });
  
}

// for top bar new button
function managed_html_show_page_grid(__placeholder__) {
  {{=XML(show_page_grid.replace('__placeholder__', '"+__placeholder__+"'))}}
}

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
         
         // === For elrte editor widget TODO merge plugin ===
         var iframe = form.find('iframe');
         var source_active = form.find('.tabsbar .source').hasClass('active');
         if (!source_active && iframe.length>0) {
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
  if (target.slice(0, 21) == 'managed_html_content_') {
    managed_html_editing(target, data._action=='edit' || data._action=='revert');
  }
  managed_html_web2py_ajax_page('post', action, data, target);
}

// ---------------------------------------------------------------------------
// for content_block action control
// ---------------------------------------------------------------------------

function managed_html_show_content_ctrl(block_el) {
  var _inner_el = block_el.find('.managed_html_content_inner');
  var target_el = _inner_el.children(':first');
  if (target_el.length == 0) {
    var _target_el = block_el.find('.managed_html_content').children('form').find('.el-rte');
    if (_target_el.length > 0) {
      target_el = _target_el;
    } else {
      target_el = _inner_el;
    }
  }
  if (target_el.length == 0) {
    target_el = _inner_el;
  }
  
  var pos = target_el.position();

  var margin = {top: (parseInt(target_el.css('margin-top'), 10) || 0),
                left: (parseInt(target_el.css('margin-left'), 10) || 0)}
  pos.top = pos.top - 38 + margin.top;
  pos.left = pos.left + margin.left;
  block_el.children('.managed_html_content_ctrl').css(pos).show();
}

function managed_html_show_collection_ctrl(block_el) {
  var _inner_el = block_el.find('.managed_html_collection_inner');
  var target_el = _inner_el.children(':first');
  if (target_el.length == 0) {
    target_el = _inner_el;
  }
  var pos = target_el.position();
  var margin = {top: (parseInt(target_el.css('margin-top'), 10) || 0),
                left: (parseInt(target_el.css('margin-left'), 10) || 0)}
  pos.top = pos.top + target_el.height() + margin.top -1; //- 38
  pos.left = pos.left + margin.left;
  block_el.children('.managed_html_collection_ctrl').css(pos).show();
}

function managed_html_editing(target, true_or_fase) {
  var el = jQuery('#'+target);
  var ctrl_el = el.parent();
  if (true_or_fase==false) {
    ctrl_el.find('.managed_html_back_btn').hide();
    ctrl_el.find('.managed_html_submit_btn').hide();
    ctrl_el.find('.managed_html_history_btn').hide();
    
    ctrl_el.find('.managed_html_edit_btn').show();
    ctrl_el.find('.managed_html_delete_btn').show();
    ctrl_el.find('.managed_html_move_btn').show();
    
    ctrl_el.find('.managed_html_content_ctrl').hide();
  } else if (true_or_fase==true) {
    ctrl_el.find('.managed_html_back_btn').show();
    ctrl_el.find('.managed_html_submit_btn').show();
    ctrl_el.find('.managed_html_history_btn').show();
    
    ctrl_el.find('.managed_html_edit_btn').hide();
    ctrl_el.find('.managed_html_delete_btn').hide();
    ctrl_el.find('.managed_html_move_btn').hide();
    
    ctrl_el.find('.managed_html_publish_now_btn').hide();
  }
}

function managed_html_published(target, true_or_fase) {
  var el = jQuery('#'+target);
  var ctrl_el = el.children('.managed_html_content_ctrl');
  if (true_or_fase==false) {
    el.addClass('managed_html_content_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').show();
  } else if (true_or_fase==true) {
    el.removeClass('managed_html_content_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').hide();
  }
}

function managed_html_collection_published(target, true_or_fase) {
  var el = jQuery('#'+target);
  var ctrl_el = el.children('.managed_html_collection_ctrl');
  if (true_or_fase==false) {
    el.addClass('managed_html_collection_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').show();
  } else if (true_or_fase==true) {
    el.removeClass('managed_html_collection_block_pending');
    ctrl_el.find('.managed_html_publish_now_btn').hide();
  }
}


function managed_html_move(name, keyword, url, confirm_message) {
    var el = jQuery("#managed_html_collection_block_" + name);
    var blocks = el.find(".managed_html_content_block"); // TODO for nested blocks..
    blocks.each(function(){
      var this_block = jQuery(this);
      var this_id = this_block.attr("id");
      this_block.find(".managed_html_content_ctrl").draggable({
        opacity:0.5, cursor:"move", 
        handle:".managed_html_move_btn",
        snap: false, 
        helper: 'clone',
        zIndex: '5000',
        revert: "invalid" ,
        appendTo: 'body',
        cursor: 'move',
        start: function(event, ui){
            blocks.not("#"+this_id).each(function(){
              var target_block = jQuery(this);
              var _inner_el = target_block.find('.managed_html_content_inner');
              var target_el = _inner_el.children(':first');
              if (target_el.length == 0) {
                target_el = _inner_el;
              }
              var pos = target_el.position();
              var margin = {top: (parseInt(target_el.css('margin-top'), 10) || 0),
                            left: (parseInt(target_el.css('margin-left'), 10) || 0)}
              pos.top = pos.top + margin.top;
              pos.left = pos.left + margin.left;
              
              target_block.prepend(jQuery('<div class="managed_html_droppable_target ui-icon-arrowthickstop-1-s"></div>'));
              target_block.children(".managed_html_droppable_target")
                .css(pos)
                .droppable({
                  accept: ".managed_html_content_ctrl",
                  activeClass: "managed_html_movable_hover",
                  hoverClass: "managed_html_movable_active",
                  tolerance: "pointer",
                  drop: function(e, ui) {
                    
                      var from_el = ui.draggable;
                      var to_el = jQuery(this);
                      from_el.fadeOut()
                      to_el.fadeOut()
                      data = {
                          "from" : this_id.slice(27),
                          "to" : to_el.parent().attr("id").slice(27),
                          "_action": "move"
                      }
                      data[keyword] = name;
                      managed_html_ajax_page(url, data, "managed_html_collection_" + name)
                  },
              });
            });
        },
        stop: function(event, ui){
            blocks.not("#"+this_id).each(function(){
              jQuery(this).children(".managed_html_droppable_target").remove();
            });
        }});
    });
}


// ---------------------------------------------------------------------------
// for movable blocks # ! Deprecated
// ---------------------------------------------------------------------------

function managed_html_movable(name, indices, keyword, url, confirm_message) {
  function _get_index(_el) {return parseInt(_el.attr('id').split('_').slice(-1)[0]);}
  function _movable(el) {
    el.draggable({
        opacity:0.5, cursor:"move", revert: 'invalid', snap: false, 
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
                     
              jQuery('.managed_html_block').unbind('hover').hover(function(){
                managed_html_show_content_ctrl(jQuery(this));
                //jQuery(this).children('.managed_html_content_ctrl').show();
              }, function() {
                jQuery(this).children('.managed_html_content_ctrl').hide();
              });
              jQuery('.managed_html_block a').unbind("click").click(function(e) {e.preventDefault();});
              
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

var current_view_width = '0'
function toggle_side_view(url, show_side_view, view_width){
  
  //var reference_view = $('<div id="managed_reference_view"></div>');
  //var reference_view_content = $('<div id="managed_reference_view_content">');

  view_width = parseInt(view_width) + 30;
  var side_view = jQuery("#managed_side_view").css('width', view_width + 'px');
  
  if(show_side_view == 'True' && side_view.is(":hidden")){
    
    side_view.animate({"width":"toggle"},"fast", "easeInQuart")
    jQuery('#base').animate({"padding-left":"+=" + view_width + 'px'}, "easeInQuart")
  
  }else if(show_side_view == 'True'){
    
    jQuery('#managed_side_view_content').children().remove();
    var current = parseInt(current_view_width);
    var next = parseInt(view_width);
    if(next < current){
      jQuery('#base').animate({"padding-left":"-="+(current-next)+"px"}, "easeInQuart")
    }else{
      jQuery('#base').animate({"padding-left":"+="+(next-current)+"px"}, "easeInQuart")
    }
  
  }else if(show_side_view == 'False' && !side_view.is(":hidden")){
    
    jQuery('#managed_side_view_content').children().remove();
    side_view.animate({"width":"toggle"},"fast", "easeInQuart")
    jQuery('#base').animate({"padding-left":"-=" + current_view_width + 'px'}, "easeInQuart")
    jQuery('[id^=tmp_managed_html_]').each(function(){
      jQuery(this).attr('id', jQuery(this).attr('id').replace('tmp_', ''));
    });
    jQuery('[class^=tmp_managed_html_]').each(function(){
      jQuery(this).attr('class', jQuery(this).attr('class').replace('tmp_', ''));
    });
    jQuery('[tmp_onclick^=managed_html_ajax_page]').each(function(){
      jQuery(this).attr('onclick', jQuery(this).attr('tmp_onclick')).removeAttr('tmp_onclick')
    })
    managed_html_init_blocks();
  }
  current_view_width = view_width

  if(show_side_view == 'True'){
    jQuery('[onclick^=managed_html_ajax_page]').each(function(){
      jQuery(this).attr('tmp_onclick', jQuery(this).attr('onclick')).removeAttr('onclick');
    })
    jQuery('[id^=managed_html_]').each(function(){
      jQuery(this).attr('id', 'tmp_'+jQuery(this).attr('id'));
    });
    jQuery('[class^=managed_html_]').each(function(){
      if(!(jQuery(this).hasClass('managed_html_topbar') ||
          jQuery(this).hasClass('managed_html_container_fluid') ||
          jQuery(this).hasClass('managed_html_brand') ||
          jQuery(this).hasClass('managed_html_secondary_nav') ||
          jQuery(this).hasClass('managed_html_content_anchor') ||
          jQuery(this).hasClass('managed_html_content_ctrl') ||
          jQuery(this).hasClass('managed_html_collection_ctrl'))
      ){
        jQuery(this).attr('class', 'tmp_'+jQuery(this).attr('class'));
      }
    });
    
    jQuery('.managed_html_content_block').unbind("mouseenter").unbind("mouseleave");
    managed_html_web2py_ajax_page('post', url, {}, 'managed_reference_view_content');
  }
}

function reference_end(event){
  var reference_id = jQuery(this).attr('id').replace('tmp_managed_html_content_block_', '');
  jQuery('[id^=tmp_managed_html_content_block_]').unbind('click', reference_end);
  managed_html_web2py_ajax_page('get', event.data.url, 
                                {'reference_id':reference_id, 
                                 '_managed_html':event.data.content_id, 
                                 'content_id':event.data.content_id, 
                                 '_action':'reference'}, 
                                'managed_html_collection_' + event.data.content_id);
}

function reference_start(content_id, url){
  jQuery('[id^=tmp_managed_html_content_block_]').click({content_id:content_id, url:url}, reference_end);
}
