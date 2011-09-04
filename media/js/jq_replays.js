var version = document.getElementById('id_version');
var game = document.getElementById('id_game'); 
$(document).ready(function(){
    var updateVersion = function(){
    url = _xhr_request + game.options[game.selectedIndex].value;
    game_name = game.options[game.selectedIndex].text;
    $.getJSON(url, function(data){
        version.options.length = 1;
        var i = 1;
        $.each(data, function(key, val){
            version.options[i] = new Option(game_name + ": " + this.fields['name'] + ' ' + this.fields['patch'], this.pk, false, false);
            i++;
        });//each
     });//json
    }//update Game

    $('#id_game').change(function(){
        updateVersion();
    });
});
