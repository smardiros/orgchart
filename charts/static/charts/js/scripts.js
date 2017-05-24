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
              $( ":contains('" + get_department(assoClass) + "')" ).addClass("active mx-auto");
              $( ":not(:contains('" + get_department(assoClass) + "'))" ).removeClass("active mx-auto");
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
              $( ":contains('" + get_department(upClass) + "')" ).addClass("active mx-auto");
              $( ":not(:contains('" + get_department(upClass) + "'))" ).removeClass("active mx-auto");
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
    savebutton.setAttribute('class', 'btn btn-success');
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
        data: {
          'data':window[rootClass],
          'department':rootClass
        },
        success: function() {
          $('#save-button').append('<div class="alert alert-success alert-dismissable fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a> <strong>Success!</strong> Chart changes saved.</div>')
        },
        error: function(XMLHttpRequest, textStatus, errorThrown) { 
            $('#save-button').append('<div class="alert alert-danger alert-dismissable fade in"><a href="#" class="close" data-dismiss="alert" aria-label="close">&times;</a> <strong>Save Failed</strong>' + " Error: " + errorThrown +'</div>')
        }
      });
    };

    document.getElementById('save-button').replaceChild(savebutton, document.getElementById('save-button').childNodes[0]);



    window.curr_department = rootClass;
  }

  $(function() {
    var x = window['department'];

    if(typeof (x) !== 'undefined'){
      var y = window[x];
      if (typeof y !== 'undefined'){
       initOrgchart(window['department'])
      } else {
        initOrgchart('it');
      }
    } else {
      initOrgchart('it');
    }

    

  });

})(jQuery);