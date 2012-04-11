
function Pagination(name, load_url, limit, vars) {
  this.name = name;
  this.load_url = load_url;
  this.limit = limit;
  this.request_vars = vars;
}

Pagination.prototype = {
  name: undefined,
  num_entries: undefined,
  limit: undefined,

  load_url: undefined,
  request_vars: {},

  $results: undefined,
  $paginator: undefined,

  page_request_func: function(vars, page_index){},

  pageselectCallback: function(page_index, jq){
    this.$paginator[0].classList.add('loading');
    this.page_request_func(this.request_vars, page_index);
    var self = this;
    $.ajax({
      url: this.load_url,
      data: this.request_vars,
      cache: false,
      success: function(html){
	self.$results[0].innerHTML = html;
	self.$paginator[0].classList.remove('loading');
      }
    });
  },

  get_total_count_func: function($results){
    return $(".total_count", $results).text();
  },

  run: function(){
    this.$paginator = $("#Pagination_"+this.name);
    this.$paginator[0].classList.add('loading');
    this.$results = $("#results_"+this.name);
    if( this.request_vars['offset'] == undefined && this.request_vars['page'] ){
      this.page_request_func(this.request_vars, this.request_vars['page'] );
    }

    var self = this;
    $.ajax({
      url: self.load_url,
      data: self.request_vars,
      cache: false,
      success: function(html){
        self.$results[0].innerHTML = html;

        self.num_entries = self.get_total_count_func(self.$results);
        if( self.num_entries==undefined ) return false;
        if( self.num_entries <= self.limit ) return ;

	var offset = self.request_vars['offset']/self.limit;
	if( !offset ) offset = 0;

        self.$paginator[0].classList.remove('loading');
        self.$paginator.pagination(self.num_entries, {
  	                         num_edge_entries: 2,
             	                 num_display_entries: 8,
                              	 callback: function(idx,jq){self.pageselectCallback(idx,jq)},
                              	 items_per_page:self.limit,
				 current_page: offset
                              	 });

      }
    });

  }
}

