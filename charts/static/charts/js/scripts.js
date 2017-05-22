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
    var data = JSON.parse(window[rootClass])
    var dep = data.department
    return dep
  }

  function initOrgchart(rootClass) {
    $('#chart-container').orgchart({
      'chartClass': rootClass,
      //'data' : datasource[0], 
      'data' : JSON.parse(window[rootClass]),//datasource(rootClass),
      'nodeContent': 'title',
      'draggable': true,
      'pan': true,
      'zoom': true,
      'createNode': function($node, data) {
        if ($node.is('.drill-down')) {
          var assoClass = data.className.match(/asso-\w+/)[0].replace("asso-","");
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
          var assoClass = data.className.match(/asso-\w+/)[0].replace("asso-","");
          var upClass = data.className.match(/up-\w+/)[0].replace("up-","");
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
        if ($node.is('.picture')) {
          var url = data.picture;
        }
      }
    });
    $('#chart-title').html("<p>" + get_department(rootClass) + "</p>");
    var savebutton = document.createElement('button');
    savebutton.setAttribute('class', 'button')
    savebutton.innerHTML = 'Save';
    var csrftoken = jQuery("[name=csrfmiddlewaretoken]").val();
    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
      return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }
    $.ajaxSetup({
      beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
      }
    });
    savebutton.onclick = function(){
      $.ajax({
        type: "POST",
        url: "/charts/update/",
        data: {'data':window[rootClass]}
      });
    };
    // where do we want to have the button to appear?
    // you can append it to another element just by doing something like
    // document.getElementById('foobutton').appendChild(button);
    document.getElementById('save-button').appendChild(savebutton)
  }

  $(function() {

    initOrgchart('it');

  });

})(jQuery);