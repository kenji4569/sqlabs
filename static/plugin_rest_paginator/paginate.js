

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

  get_total_count_func: function(){
    this.$results = $("#results_"+this.name);
    this.num_entries = $(".total_count", this.$results).text();
  },

  run: function(){
    this.get_total_count_func();
    if( this.num_entries==undefined ) return false;
    var self = this;

    if( this.num_entries <= this.limit ) return ;

    this.$paginator = $("#Pagination_"+this.name);
    return this.$paginator.pagination(this.num_entries, {
  	                                num_edge_entries: 2,
        	        	        num_display_entries: 8,
                              	        callback: function(idx,jq){self.pageselectCallback(idx,jq)},
                              	        items_per_page:this.limit
                              	      });
  }
}

