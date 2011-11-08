(function($) {
$(function(){
  $('.managed_html_block').hover(function(){
    $(this).children('.managed_html_contents_ctrl').show();
  }, function() {
    $(this).children('.managed_html_contents_ctrl').hide();
  });
  
  $('.managed_html_content').hover(function(){
    //$(this).css('background', 'red');
  }, function() {
    //$(this).css('background', 'transparent');
  });
  
})
})(jQuery);

function managed_html_editing(target, true_or_fase) {
  var el = jQuery('#'+target).parent();
  if (true_or_fase==false) {
    el.find('.managed_html_back_btn').hide();
    el.find('.managed_html_edit_btn').show();
  } else if (true_or_fase==true) {
    el.find('.managed_html_back_btn').show();
    el.find('.managed_html_edit_btn').hide();
  }
}

function managed_html_ajax_page(url, data, target) {
  jQuery('.flash').hide().html(''); 
  managed_html_editing(target, data.action=='edit');
  web2py_ajax_page('post', url, data, target);
}
