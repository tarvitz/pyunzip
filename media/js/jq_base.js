$(document).ready(function(){
    $('.message .msg_headline .transparency:even').addClass('tr_navy');
        $('.spoiler_block a').click(function(){
            $(this).parent().children('.spoiler').toggle(500, function(){
            p = $(this).parent();
            if (p.children('.spoiler').css('display') != 'none'){
                p.attr('class', p.attr('class') + ' spoiler_show');
                p.children('.marker').html('[-]');
            }else{
                p.attr('class', 'spoiler_block');
                p.children('.marker').html('[+]');
            }
            });
        });
});//document ready

	function perform_update(field, val,id,url){
			var data = {};
			data[field] = val;
			if (url == '' )url = "/comment/"+id+"/update/";
			var args = {type: "POST", url:url, data:data, complete:done};
			$.ajax(args);
		};
	var done = function(res, status){
		 //ADD SOME Eye-candy effects ;)
			if (status == "success") {
				//alert("success");
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
		
	}
	 function flip_to_textarea(obj,id,url){
		if (obj != ''){
			var the_text = $(obj+"_"+id);
		}else var the_text = $("#text_"+id);
		//var the_text = $();
		if (url == '') url = "/comment/"+id+"/get/raw/";
		//$.getJSON(url,get_raw_content);
		$.getJSON(url,function(data){

			jQuery.each(data,function(){
			var form = '<form><textarea class="quick_edit" id="textarea_'+this.pk+'">\
			'+this.fields.description+'</textarea>\
			<br><input type="button" id="button_'+this.pk+'" value="Обновить"\
			onClick="recieve_formatted_content(\''+obj+'\','+this.pk+',\''+url+'\');">\
			</form>'; //\	
			var text_area = $(form);
			the_text.replaceWith(text_area);

			});//jquery.each
	
		});
	}
	
	function recieve_formatted_content(obj,id,url){
		var txt = $('#textarea_'+id).val();
		var new_url = url
		perform_update('text',txt,id,new_url.replace('/get','/update'));
		//TODO: IS STOPPED HERE!!!	
		$.getJSON(url.replace('/get','/get/formatted'),function(data){
			//alert("O_O");
			jQuery.each(data,function(){
				var text_area = $("#textarea_"+id);
				var the_text = $("<div class='msg_text' id='"+obj.replace("#",'')+"_"+this.pk+"'>"+this.fields.description+"<br clear='all'></div>");
				text_area.replaceWith(the_text);
				$("input[id=button_"+this.pk+"]").remove();
			});//jquery
		});
		//$.getJSON("/comment/"+id+"/get/", recive_content); //getting the formatted view of the comment form db
	}
	
	var recive_content = function(data){
		jQuery.each(data, function(){
				var text_area = $("#text_"+this.pk);
				var the_text = $('<div id="text_'+this.pk+'">'+this.fields.comment+'</div>');
				//alert(this.fields.comment);
				text_area.replaceWith(the_text);
				$("input[id=button_"+this.pk+"]").remove();
			})
	}

	function textarea_to_text(obj,id){
		//alert("O_O");
		if (obj == ''){ obj = "#text"; }
		var text_area = $(obj+"_"+id);
		var the_text = $('<div id="text_'+id+'">'+text_area.val()+'</div>');
		text_area.replaceWith(the_text);
		//perform_update("comment",text_area.val(),id);
		$("input[id=button_"+id+"]").remove();
	}

	var get_raw_content = function get_raw_content(data){
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
 
var postAjax = function(params){
    url = params.url;
    data = params.data;

    $.ajax(url, {
        dataType: params.dataType || 'json',
        data: data,
        type: "POST",
        crossDomain: params.crossDomain || false,
        success: function(response, state, jqXHR){
            if (params.success) params.success(response, state);
        },
        error: function(response, state, jqXHR){
            if (params.failure) params.failure(response, state);
        },
        beforeSend: function(xhrResponse, settings){
            xhrResponse.setRequestHeader('X-Force-XHttpResponse', 'on');
        },
    });
}

var updateFormErrors = function(form, errors){
    $('ul.errors').detach().remove();
    for (el in errors){
        
        blk = $(form).find("#id_" + el);
        ul = $("<ul class='errors'></ul>");
        for (i=0; i < errors[el].length; i++){
            li = $("<li>" + errors[el][i] + "</li>");
            li.appendTo(ul);
        }
        ul.insertBefore(blk);
		blk.addClass('errors');
    }
}

var postFormAjax = function(p){
    form = p.form;
    data = p.data || form.serialize();

    postAjax({
        url: p.url || form.attr('action'),
        data: data,
        success: function(response, code){
            var _form = (typeof response.form == 'undefined') ? {} : response.form;
            if (_form.errors){
                updateFormErrors(form, _form.errors);
            }
            else {
                // do something
                var message = noty({
                    text: p.successMsg || "Сохранено ;)",
                    type: "success",
                    dismissQueue: true,
                    timeout: (typeof p.notyTimeout == 'undefined') ? 2000 : p.notyTimeout
                });
                if (p.reloadPage || false ){
                    setTimeout(function(){
                        document.location.reload();
                    }, p.reloadTimeout || 2500);
                }
                if (p.success) p.success(response);
            }
        },
        failure: function(response, code){
            noty({
                text: p.failreMsg || "Что-то пошло не так",
                type: "error",
                dismissQueue: true
            });
        }
    }); //end postAjax
}

