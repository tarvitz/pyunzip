(function(){
  function format(state) {
    return state.text;
  }

  $.each($('[data-toggle=select2]'), function(idx, element){
    var self = this;
    $(element).select2({
      minimumInputLength: $(self).data('minimum-input-length') || 0,
      placeholder: $(self).data('placeholder') || "",
      formatNoMatches: "Не найдено"
      //formatResult: format,
      //formatSelection: format
    })
  });
})();