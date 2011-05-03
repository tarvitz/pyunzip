/* 
 * Author: blacklibrary.ru
 * Depends on jQuery 1.4 and higher
 * LICENCE: BSD
 *
 */
var mark_read = function(url){
    var state = $.getJSON(url, function(data){
        return data.status;
    });//
    return state;
}
