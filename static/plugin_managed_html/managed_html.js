(function($) {
$(function(){
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
})
})(jQuery);

function managed_html_editing(target, true_or_fase) {
  var el = jQuery('#'+target).parent();
  if (true_or_fase==false) {
    el.find('.managed_html_back_btn').hide();
    el.find('.managed_html_submit_btn').hide();
    el.find('.managed_html_main_comment').hide();
    
    el.find('.managed_html_edit_btn').show();
    
    el.find('.managed_html_contents_ctrl').hide();
  } else if (true_or_fase==true) {
    el.find('.managed_html_back_btn').show();
    el.find('.managed_html_submit_btn').show();
    el.find('.managed_html_main_comment').show();
    
    el.find('.managed_html_edit_btn').hide();
  }
}

function managed_html_ajax_page(url, data, target) {
  jQuery('.flash').hide().html(''); 
  managed_html_editing(target, data._action=='edit');
  web2py_ajax_page('post', url, data, target);
}

function managed_html_movable(name, indices, keyword, url) {
  function _get_index(_el) {return parseInt(_el.attr('id').split('_').slice(-1)[0]);}
  function _movable(el) {
    el.draggable({opacity:0.5, cursor:"move", revert: 'invalid'})
      .droppable({
        accept: ".managed_html_name_" + name,
        activeClass: "managed_html_movable_hover",
        hoverClass: "managed_html_movable_active",
        drop: function(e, ui) {
          var from_el = ui.draggable;
          var to_el = jQuery(this);
          if (!confirm('Sure you want to move them?')) {
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
          jQuery.post(url, data,
            function (r) {
              var arg_from = indices.indexOf(from);
              var arg_to = indices.indexOf(to);
              indices[arg_from] = to;
              indices[arg_to] = from;
              from_el.css({left:'0px', top:'0px'});
              var from_parent = from_el.parent();
              var to_parent = to_el.parent();
              var from_html = from_parent.html();
              var to_html = to_parent.html();
              from_parent.html(to_html);
              to_parent.html(from_html);
              _movable(from_parent.children(".managed_html_name_" + name));
              _movable(to_parent.children(".managed_html_name_" + name));
              from_parent.children(".managed_html_name_" + name);
              to_parent.children(".managed_html_name_" + name);
            }
          ).error(function(r){ 
              alert('Error occured');
              from_el.css({left:'0px', top:'0px'});
          });
        }
      }); 
    }
    _movable(jQuery(".managed_html_name_" + name));
}