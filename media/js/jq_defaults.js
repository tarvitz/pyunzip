$.fn.popover.defaults = $.extend({} , $.fn.tooltip.defaults, {
    placement: 'right'
    , trigger: 'click'
    , content: ''
    , template: '<div class="popover"><div class="transparency tr_black"></div><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"></div></div></div>'
})
