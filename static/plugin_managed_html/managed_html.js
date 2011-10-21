(function($) {
$(function(){
  $('.managed_html_content').hover(function(){
    $(this).children('.managed_html_tabs').show();
  }, function() {
    $(this).children('.managed_html_tabs').hide();
  });
})


})(jQuery);