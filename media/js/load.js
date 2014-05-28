
var setTabs = function(src){
    document.cookie = 'mainTab=' + src;
}
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
}


$("a[rel=twipsy], a[rel=tooltip]").tooltip({live: true, delay: 1200});
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

(function(){
  $('[data-toggle=date-time-picker]').datetimepicker({
    language: 'ru',
    pick12HourFormat: false
  });
})();