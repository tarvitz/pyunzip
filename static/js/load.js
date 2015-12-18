var setTabs = function(src){
    document.cookie = 'mainTab=' + src;
};
var updateTabs = function(){
    kookie = document.cookie.split('; ');
    match = document.cookie.match(/mainTab=(\w+)/);
    tabValue = (match) ? match[1] : -1;
    if (tabValue != -1){
        $('.tab-content').find('.tab-pane').removeClass('active');
        $(".tab-content").find('#' + tabValue).addClass('active');
        $('.nav-tabs').find('li').removeClass('active');
        blk = $('.nav-tabs').find('[href=#' + tabValue + ']');
        blk.parents('li').addClass('active');
    }
};


$("a[rel=twipsy], a[rel=tooltip]").tooltip({live: true, delay: 1200});
$(".control-group").find('.control-label')
 .attr('data-title', 'Обязательное поле')
 .tooltip({live: true, delay: 1000});

$('a[href=#]').click(function(e){ e.preventDefault();});

$('#login-modal .postAjax').click(function(e){
    form = $(this).parents('form');
    $(form).find('ul.errors').detach().remove();
    postFormAjax({
        form: form,
        successMsg: "Успешно авторизован ;)",
        reloadPage: true,
        reloadTimeout: 2000
    });
    return false;
});
$('#login-modal form').submit(function(e){ return false;});
$.each($('a.user.image'), function(idx, img){
    $(img).attr({'rel': 'gal'});
});
$("a.user.image, a[rel=gal]").colorbox({rel: "gal"});

markupSettings = myMarkupSettings['textile'];
markupSettings['previewParserPath'] = markupPreviewURL + '?markup=textile&template=comment';
$('textarea.markitup').markItUp(markupSettings);

//function getCookie(name){
//  var reg = RegExp('(' + name + ')=([\\w\\d\\_\\- ]+)');
//  var out = document.cookie.match(reg);
//  return (out) ? out[2] : '';
//}

// using jQuery
function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
var csrftoken = getCookie('csrftoken');

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

(function(){
  'use strict';

  $.each($('[data-toggle=date-time-picker]'), function(idx, item){
    $(item).datetimepicker({
      language: 'ru'
    });
  });

  $.each($('[data-toggle=select2]'), function(idx, item){
    $(item).select2({
      placeholder: $(self).data('placeholder') || "",
      formatNoMatches: "Не найдено"
    });
  });
  $("[data-toggle=quote]").click(function(e){
    var text = (window.getSelection) ?
        window.getSelection().toString() :
        document.getSelection().toString();
    var user = $(this).parents('.message').data('nickname');
    var quote = '(' + user + ')' + '{' + text + '}';
    text = $('form').find('textarea').val();
    $('form').find('textarea').val(text + '\n' + quote);
  });
})();