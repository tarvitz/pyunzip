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
