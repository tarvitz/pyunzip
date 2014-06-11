(function(){
  $.each($('[data-toggle=select2]'), function(idx, element){
    var self = this;
    $(element).select2({
      placeholder: $(self).data('placeholder') || "",
      formatNoMatches: "Не найдено"
    })
  });
})();