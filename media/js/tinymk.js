function reload_image(obj){
	img = document.getElementById(obj);
	syntax = document.getElementById('id_syntax');
	if (syntax)	img.src = '/media/tinymk/'+syntax.value+'.png';
}
function filter_syntax(){
	syntax = document.getElementById('id_syntax');
	hidden_syntax = document.getElementById('id_hidden_syntax');
	syntax_img = document.getElementById('id_syntax_change');
	if (hidden_syntax){
			hidden_syntax.value = syntax.value;
	}
	syntax_img.src = '/media/tinymk/'+syntax.value+'.png';
}

function change_syntax(obj){
		img_obj = document.getElementById(obj);
		syntax_object = document.getElementById('id_hidden_syntax');
	    syntax_main = document.getElementById('id_syntax');
		if (syntax_main){
			if (syntax_object.value == 'bb-code') syntax_main.value = 'markdown';
			else syntax_main.value = 'bb-code';
		 }//if syntax_main

		//alert(syntax_object.value);
		if (syntax_object.value == '') syntax_object.value = 'markdown';

		if (syntax_object.value == 'bb-code'){
			syntax_object.value = 'markdown';
			img_obj.src = '/media/tinymk/markdown.png';
			img_obj.title = 'Markdown syntax is active';
		}
		else {
			syntax_object.value = 'bb-code';
			img_obj.src = '/media/tinymk/bb-code.png';
			img_obj.title = 'BB-code syntax is active';
		}
}

function paste_code(obj,block){
		textarea_object = document.getElementById(block);
		//alert(textarea_object);
		var syntax_object;
		greater_syntax_object = document.getElementById('id_syntax');
		lesser_syntax_object = document.getElementById('id_hidden_syntax');
		//greater_syntax_object has higher priority so we choose it as default
		if (greater_syntax_object) syntax_object = greater_syntax_object;
		else {
			if (lesser_syntax_object) syntax_object = lesser_syntax_object;
		}
		if (syntax_object.value == 'bb-code'){
			switch (obj){
				case 'bold':{
					textarea_object.value += '[b][/b]';
					break;
				 };
				case 'italic':{
					textarea_object.value += '[i][/i]';
					break;
				};
				case 'underline':{
					textarea_object.value += '[u][/u]';
					break;
				};
				case 'quote':{
					textarea_object.value += '(User){userquote}';
					break;
				}
				default:{
					break;	
				}
			}
		}else{ //markdown by default
		switch (obj){
			case 'bold': {
					textarea_object.value += '** **';
					break;
			};
			case 'italic':{
				textarea_object.value += '* *';
				break;
			};
			case 'underline':{
				textarea_object.value += '_ _'
				break;
			};
			case 'quote':{
				textarea_object.value += '(User){userquote}';
				break;
			};
			default: {
				//alert('unknown');
			};
		 } //switch
		}//endif
	}

