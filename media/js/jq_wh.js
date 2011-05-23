$(document).ready(function(){
    var side = document.getElementById('id_side');
    var army = document.getElementById('id_army');
    var updateArmy = function(callback){
        army_id = side.options[side.selectedIndex].value;
        url = _xhr_get_armies + army_id;
        $.getJSON(url, function(data){
            army.options.length = 1; // cleanse
            var i = 1;
            $.each(data, function(key, val){
               army.options[i] = new Option(this.fields['name'], this.pk, false, false);
               i++;
            });
        });
    }
    $('#id_side').change(function(){
        updateArmy();
    });
    var setDefaults = function(){
        for (var i = 0; i<side.options.length; i++){
            if (side.options[i].value == _user_army_side_id)
                side.selectedIndex = i;
        }
        /*cleanse useless data*/
        army.options.length = 1;
        var i = 1;
        xhr_url = _xhr_get_armies + side.options[side.selectedIndex].value;
        $.getJSON(xhr_url, function(data){
            $.each(data, function(key, val){
                army.options[i] = new Option(this.fields['name'], this.pk, false,
                    _user_army_id == this.pk ? true: false);
                i++;
            });
        });
    };
    if (_user_army_id)
        setDefaults();
    else
        updateArmy();
});
