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

function managed_html_ajax_page(url, data, target) {
  jQuery('.flash').hide().html(''); 
  web2py_ajax_page('post', url, data, target);
}
