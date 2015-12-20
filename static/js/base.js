var xhr = function(params){
  var url = params.url;
  var data = params.data || {};
  var type = params.type || "GET";

  $.ajax(url, {
    dataType: params.dataType || "json",
    data: data,
    type: type,
    crossDomain: params.crossDomain || false,
    success: function(response, state){
      if (params.success) params.success(response, state);
    },
    error: function(response, state){
      if (params.failure) params.failure(response, state);
    },
    beforeSend: function(xhrResponse){
      xhrResponse.setRequestHeader('X-Force-XHttpResponse', 'on');
    }
  });
};

var postAjax = function(params){
  params.type = 'POST';
  xhr(params);
};

var updateFormErrors = function(form, errors){
  $('ul.errors').detach().remove();
  for (var el in errors){

    var blk = $(form).find("#id_" + el);
    var ul = $("<ul class='errors'></ul>");
    for (var i = 0; i < errors[el].length; i++){
      var li = $("<li>" + errors[el][i] + "</li>");
      li.appendTo(ul);
    }
    ul.insertBefore(blk);
    blk.addClass('errors');
  }
};

var postFormAjax = function(p){
  var form = p.form;
  var data = p.data || form.serialize();

  postAjax({
    url: p.url || form.attr('action'),
    data: data,
    success: function(response){
      var _form = (typeof response.form == 'undefined') ? {} : response.form;
      if (_form.errors){
        updateFormErrors(form, _form.errors);
        $(form).find("input, select").removeAttr('disabled');
      }
      else {
        // do something
        noty({
          text: p.successMsg || "Сохранено ;)",
          type: "success",
          dismissQueue: true,
          timeout: (typeof p.notyTimeout == 'undefined') ? 2000 : p.notyTimeout
        });
        if (p.reloadPage || false ){
          setTimeout(function(){
            document.location.reload();
          }, p.reloadTimeout || 2500);
        }
        if (p.success) p.success(response);
      }
    },
    failure: function(){
      noty({
        text: p.failreMsg || "Что-то пошло не так",
        type: "error",
        dismissQueue: true
      });
    }
  }); //end postAjax
};

function isInstance(x, Obj){
  return Object.prototype.toString.call(x) === Object.prototype.toString.call(Obj);
}

function parseJSONFormFields(data, form){
  $.each(data, function(index, value){
    if (isInstance(value, [])){
      $.each(value, function(idx, val){
        if (!isInstance(value, [])){
          container = "#id_" + index + ' option[value=' + val + ']';
          $(form).find(container).attr({selected: true});
        }
      });//each value given array
    } else {
      if ($(form).find('#id_' + index).is('select')){
        $(form).find('#id_' + index).find('option[value='+value+']').attr({selected: true});
      } else {
        form.find('#id_' + index).attr({value: value});
      }// if given
    } // if isarray
  });// each
}
