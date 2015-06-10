
var showMore = function(key) {
  $("#entry-" + key + " > .bib-entry-more").toggle();
};

$(document).ready(function() {

  // list.js
  var pubList = new List('zth-pubs', {
    valueNames: ['bib-entry-summary']
  });

});
