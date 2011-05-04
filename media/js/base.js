function show_hide(blockid){
	mode = document.getElementById(blockid).style.display;
		if (mode == 'none'){
            document.getElementById(blockid).style.display = 'block';
		}else{
            document.getElementById(blockid).style.display = 'none';
		}
}


function do_hide(obj){
			o = document.getElementsByClassName(obj);
			for (var i=0;i<o.length;i++){
				//alert(o[i].className);
				if (o[i].style.display == 'none'){
					o[i].style.display = 'block';
					data = 'block';
					var args = {type: "POST", url:'/settings/store/display_'+o[i].className+'/'+data+'/', data:data, complete:done};
			        $.ajax(args);
				}else{
					o[i].style.display = 'none';
					data = 'none';
					var args = {type: "POST", url:'/settings/store/display_'+o[i].className+'/'+data+'/', data:data, complete:done};
			        $.ajax(args);

				}
			}
}
var done = function(res,status){
	if (status == 'success'){
	}else{
	}
}
function go_to(loc){
    //document.location = loc;
    alert(this);
}

