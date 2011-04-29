$(document).ready(function(){ });
	_id_ = -1;
	function perform_update(field, val,id){
			var data = {};
			data[field] = val;
			url = "/comment/"+id+"/update/";
			var args = {type: "POST", url:url, data:data, complete:done};
			$.ajax(args);
			_id_ = id;
		};
	var done = function(res,status){
		 //ADD SOME Eye-candy effects ;)
			if (status == "success") {
				//alert("success");
				$.getJSON("/comment/"+_id_+"/get/", recive_comment); //getting the formatted view of the comment form db
			}
			else {
				//alert("failed"+res.responseText);
				switch(res.responseText){
					case("timeout"):{ 	
						alert("Промежуток между правками коментариев не должен превышать 15 секунд! Подождите немного.");
						break;
						}
					default: {
						alert("Неизвестная ошибка:"+res.responseText);
						break;
					}//default
				}//switch
			}//else
			return status
		
	}
	 function flip_to_textarea(id){
		var the_text = $("#text_"+id);
		$.getJSON("/comment/"+id+"/get/raw/",get_raw_comment);
	}
	
	function recieve_formatted_comment(id){
		var txt = $("#text_"+id).val();
		perform_update("comment",txt,id); //writes the changes
		//$.getJSON("/comment/"+id+"/get/", recive_comment); //getting the formatted view of the comment form db
	}
	
	var recive_comment = function(data){
		jQuery.each(data, function(){
				var text_area = $("#text_"+this.pk);
				var the_text = $('<div id="text_'+this.pk+'">'+this.fields.comment+'</div>');
				//alert(this.fields.comment);
				text_area.replaceWith(the_text);
				$("input[id=button_"+this.pk+"]").remove();
			})
	}

	function textarea_to_text(id){
		//alert("O_O");
		var text_area = $('#text_'+id);
		var the_text = $('<div id="text_'+id+'">'+text_area.val()+'</div>');
		text_area.replaceWith(the_text);
		perform_update("comment",text_area.val(),id);
		$("input[id=button_"+id+"]").remove();
	}
	var get_raw_comment = function get_raw_comment(data){
		jQuery.each(data, function(){
			var form = '<form><textarea class="quick_edit" id="text_'+this.pk+'">\
'+this.fields.comment+'</textarea>\
<input type="button" id="button_'+this.pk+'" value="Обновить"\
onClick="recieve_formatted_comment('+this.pk+')">\
</form>'; //\
			var text_area = $(form);
			the_text = $("#text_"+this.pk);
			the_text.replaceWith(text_area);
		});
	}
//	});

function insertQuoteUser(user){
    t = document.getElementById('id_comment');
    if (window.getSelection){
        quote_text = window.getSelection().toString();
    }
    else if (document.getSelection){
        quote_text = document.getSelection().toString();
    }
    if (quote_text){
        text = "("+user+"){"+quote_text+"}";
        if (t.value) t.value += "\n" + text;
        else t.value += text;
    }
}
