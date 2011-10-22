(function($) {
$(function(){
  $('.managed_html_contents').hover(function(){
    $(this).children('.managed_html_contents_ctrl').show();
  }, function() {
    $(this).children('.managed_html_contents_ctrl').hide();
  });
})
})(jQuery);
