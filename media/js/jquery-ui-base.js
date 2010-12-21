var m_user_autocomplete = function(obj,url){
$(obj).keyup(function(event){
	    url2 = url + $(obj).val();
    	    $(obj).autocomplete({
		source: url2,
		minLength: 3,
    	});//autocomplete
  });
}
