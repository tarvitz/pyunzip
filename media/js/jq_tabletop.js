var get_roster = function(url, id){
	r = $("#"+id+" span.roster");
	a = $("#"+id+" a");
	if (r.is(":empty")){
	$.getJSON(url, function(data){
		jQuery.each(data, function(){	
			r.toggle();
			r.html(this.fields['roster']);
			r.toggle(1000);
			a.text('[-]').attr('alt','[-]').attr('title', '[-]');
		});
	});
	}else{
	 if (a.text() == '[-]'){
	 	r.toggle(2000);
		a.text('[+]').attr('alt','[+]').attr('title', '[+]');
	 }else{
		r.toggle(2000);
		a.text('[-]').attr('alt','[-]').attr('title', '[-]');
	 }
	}// if is blank
}

var _updateRevision = function(){
    url = _xhr_get_codex_revisions + codex.options[codex.selectedIndex].value;
    $.getJSON(url, function(data){
        revlist = data.revlist;
        revision.value = revlist[revlist.length-1];
        p = $('<span class="info">Available revisions: '+ data.revisions +'</span>');
        _parent = $("#"+revision.id).parent();
        if (_parent.children("span.info").length){
            _parent.children("span.info").text("Available revisions: " + data.revisions);
        }else{
            $(p).insertBefore("#"+revision.id);
        }
    });
}

var getRevision = function(d){
    $.getJSON(d.url, function(json){
        if (d.success) d.success(json);
    });
}