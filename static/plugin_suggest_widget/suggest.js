/*
 *	jquery.suggest 1.1 - 2007-08-06
 *	Uses code and techniques from following libraries:
 *	1. http://www.dyve.net/jquery/?autocomplete
 *	2. http://dev.jquery.com/browser/trunk/plugins/interface/iautocompleter.js
 *	All the new stuff written by Peter Vulgaris (www.vulgarisoip.com)	
 *	Feel free to do whatever you want with this file
 */
(function($) {
$.suggest = function(input, options) {
  var $input = $(input).attr("autocomplete", "off");
  var timeout = false;		// hold timeout ID for suggestion results to appear
  var preval = "";			// last recorded length of $input.val()
  var cache = [];				// cache MRU list
  var cacheSize = 0;			// size of cache in chars (bytes?)
  var $results;
  if (options.resultsId!=null) {
    $results = $('#'+options.resultsId);
    $results.addClass(options.resultsClass);
  } else {
    $results = $(document.createElement("ul"));
    $results.addClass(options.resultsClass).appendTo('body');
  }
  
  // resetPosition();
  // $(window)
    // .load(resetPosition)		// just in case user is changing size of page while loading
    // .resize(resetPosition);

  $input.blur(function() {
    setTimeout(function() { $results.hide() }, 200);
  });

  $input.keydown(processKey);
  $input.focus(suggest);

  // function resetPosition() {
    // requires jquery.dimension plugin
    // var offset = $input.offset();
    // $results.css({
        // top: (offset.offsetHeight) + 'px',
        // left: (offset.offsetLeft) + 'px'
    // });
  // }
  function processKey(e) {
    preval = $input.val();
    // handling up/down/escape requires results to be visible
    // handling enter/tab requires that AND a result to be selected
    if ((/27$|38$|40$/.test(e.keyCode) && $results.is(':visible')) ||
        (/^13$|^9$/.test(e.keyCode) && getCurrentResult())) {
      switch(e.keyCode) {
        case 38: // up
          prevResult();
          break;
        case 40: // down
          nextResult();
          break;
        case 9:  // tab
        case 13: // return
              // for JAP by hotcake
          selectCurrentResult();
          break;
        case 27: //	escape
          $results.hide();
          break;
      }
      if (e.preventDefault) e.preventDefault();
      if (e.stopPropagation) e.stopPropagation();
      e.cancelBubble = true;
      e.returnValue = false;
    } else {
      if($('.suggest_over').length==1 && e.keyCode==13) {
          return;
      }
      clearTimeout(timeout);
      timeout = setTimeout(suggest,options.delay);
    }
  }
  function suggest() {
    $input.trigger($input.attr('id') + '__unselected');
    if (options.name != null) {
      $('input[name='+options.name+']').val('');
    }
  
    var q = $.trim($input.val());
    if (q.length >= options.minchars) {
      if ($input.val() != preval) {
        preval = $input.val();
        cached = checkCache(q);
        if (cached) {
          displayItems(cached['html']);
          nextResult()
        } else {
          var query = {}
          query[options.keyword] = q;
          jQuery.ajax({type: "POST", url: options.source, data: query, 
            success: function(html) {
              $results.hide();
              displayItems(html);
              addToCache(q, html, html.length);
              nextResult()
            }});
        }
      }
    } else {
      $results.hide();
    }
  }
  function checkCache(q) {
    for (var i = 0; i < cache.length; i++)
      if (cache[i]['q'] == q) {
        cache.unshift(cache.splice(i, 1)[0]);
        return cache[0];
      }
    return false;
  }
  function addToCache(q, html, size) {
    while (cache.length && (cacheSize + size > options.maxCacheSize)) {
      var cached = cache.pop();
      cacheSize -= cached['size'];
    }
    cache.push({
      q: q,
      size: size,
      html: html });
    cacheSize += size;
  }
  function displayItems(html) {
    if(html=='') {
      $input.addClass(options.noMatchClass);
      $input.removeClass(options.matchClass);
      $input.removeClass(options.selectedClass); 
    } else {
      $input.addClass(options.matchClass);
      $input.removeClass(options.noMatchClass);
      $input.removeClass(options.selectedClass); 
    }
    if (!html) return;
    if (!html.length) {
      $results.hide();
      return;
    }
    $results.html(html).show();
    
    $results
      .find('li')
      .mouseover(function() {
        $results.find('li').removeClass(options.selectClass);
        $(this).addClass(options.selectClass);
      })
      .click(function(e) {
        e.preventDefault(); 
        e.stopPropagation();
        selectCurrentResult();
      });
  }
  function getCurrentResult() {
    var $currentResult = $results.find('li.' + options.selectClass);
    
    if (!$currentResult.length)
      $currentResult = false;
    return $currentResult;
  }
  function selectCurrentResult() {
    $currentResult = getCurrentResult();
    if ($currentResult) {
      
      $input.addClass(options.selectedClass);  
      $input.removeClass(options.matchClass);
      $input.removeClass(options.noMatchClass);  
      
      var val = $currentResult.children('b').text();
      $input.val(val);
      if (options.name != null) {
        val = $currentResult.children('span').text();
        $('input[name='+options.name+']').val(val);
      }
      $input.trigger($input.attr('id') + '__selected', [val]);
      
      $results.hide();
      if (options.onSelect) options.onSelect($currentResult.text());
    }
  }
  function nextResult() {
    $currentResult = getCurrentResult();
    if ($currentResult)
      $currentResult
        .removeClass(options.selectClass)
        .next()
          .addClass(options.selectClass);
    else
      $results.find('li').slice(0,1).addClass(options.selectClass);
  }
  function prevResult() {
    $currentResult = getCurrentResult();
    if ($currentResult)
      $currentResult
        .removeClass(options.selectClass)
        .prev()
            .addClass(options.selectClass);
    else
      $results.find('li').slice(-1).addClass(options.selectClass);
  }
}
$.fn.suggest = function(source, options) {
  if (!source) return;
  options = options || {};
  options.source = source;
  options.delay = options.delay || 100;
  options.resultsClass = options.resultsClass || 'suggest_results';
  options.selectClass = options.selectClass || 'suggest_over';
  options.selectedClass = options.selectedClass || 'suggest_selected';
  options.matchClass = options.matchClass || 'suggest_match';
  options.noMatchClass = options.noMatchClass || 'suggest_no_match';
  options.minchars = options.minchars || 2;
  options.delimiter = options.delimiter || '\n';
  options.onSelect = options.onSelect || false;
  options.maxCacheSize = options.maxCacheSize || 65536;
  options.keyword = options.keyword || 'q';
  options.name = options.name || null;
  options.resultsId = options.resultsId || null;

  this.each(function() {
      new $.suggest(this, options);
  });

  return this;
};})(jQuery);