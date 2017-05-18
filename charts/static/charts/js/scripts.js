'use strict';

(function($){

  function datasource(rootClass){
    var json = null;
    $.ajax({
      'async': false,
      'global': false,
      'url': "../static/charts/js/" + rootClass + ".json",
      'dataType': "json",
      'success': function (data) {
        json = data;
      }
    });
    return json;
  }; 

  function get_department(rootClass){
    var data = datasource(rootClass)
    var dep = data.department
    return dep
  }

  function initOrgchart(rootClass) {
    $('#chart-container').orgchart({
      'chartClass': rootClass,
      //'data' : datasource[0], 
      'data' : datasource(rootClass),
      'nodeContent': 'title',
      'pan': true,
      'zoom': true,
      'createNode': function($node, data) {
        if ($node.is('.drill-down')) {
          var assoClass = data.className.match(/asso-\w+/)[0];
          var drillDownIcon = $('<i>', {
            'class': 'fa fa-arrow-circle-down drill-icon down',
            'click': function() {
              
              
              $('#chart-container').find('.orgchart:visible').addClass('hidden');
              if (!$('#chart-container').find('.orgchart.' + assoClass).length) {
                initOrgchart(assoClass);
              } else {
                $('#chart-container').find('.orgchart.' + assoClass).removeClass('hidden');
                $('#chart-title').html("<p>" + get_department(assoClass) + "</p>");
              }
            }
          });
          $node.append(drillDownIcon);
        } else if ($node.is('.drill-up')) {
          var assoClass = data.className.match(/asso-\w+/)[0];
          var upClass = data.className.match(/up-\w+/)[0].replace("up","asso");
          var drillUpIcon = $('<i>', {
            'class': 'fa fa-arrow-circle-up drill-icon up',
            'click': function() {
              $('#chart-container').find('.orgchart:visible').addClass('hidden');
              if (!$('#chart-container').find('.orgchart.' + upClass).length) {
                initOrgchart(upClass);
              } else {
               $('#chart-container').find('.orgchart.' + upClass).removeClass('hidden');
               $('#chart-title').html("<p>" + get_department(upClass) + "</p>");
              }
            }
          });
          $node.append(drillUpIcon);
        }
      }
    });
    $('#chart-title').html("<p>" + get_department(rootClass) + "</p>");
  }

  $(function() {

    initOrgchart('asso-it');

  });

})(jQuery);