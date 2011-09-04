function reload_image(obj){
	img = document.getElementById(obj);
	syntax = document.getElementById('id_syntax');
	if (syntax.value)	img.src = '/media/tinymk/'+syntax.value+'.png';
    else img.src = '/media/tinymk/markdown.png';
}
function filter_syntax(){
	syntax = document.getElementById('id_syntax');
	hidden_syntax = document.getElementById('id_hidden_syntax');
	syntax_img = document.getElementById('id_syntax_change');
	if (hidden_syntax){
			hidden_syntax.value = syntax.value;
	}	
    if (syntax.value)
        syntax_img.src = '/media/tinymk/'+syntax.value+'.png';
    else
        syntax_img.src = '/media/tinymk/markdown.png';
}

function change_syntax(obj){
		img_obj = document.getElementById(obj);
		syntax_object = document.getElementById('id_hidden_syntax');
	    syntax_main = document.getElementById('id_syntax');
		if (syntax_main){
			if (syntax_object.value == 'bb-code') syntax_main.value = 'textile';
			else syntax_main.value = 'bb-code';
		 }//if syntax_main

		//alert(syntax_object.value);
		if (syntax_object.value == '') syntax_object.value = 'textile';

		if (syntax_object.value == 'bb-code'){
			syntax_object.value = 'textile';
			img_obj.src = '/media/tinymk/markdown.png';
			img_obj.title = 'Textile syntax is active';
		}
		else {
			syntax_object.value = 'bb-code';
			img_obj.src = '/media/tinymk/bb-code.png';
			img_obj.title = 'BB-code syntax is active';
		}
}

/* deprecated */
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
					insertBlockTag(block, {start: "[b]", end: "[/b]"});
                                        //textarea_object.value += '[b][/b]';
					break;
				 };
				case 'italic':{
					insertBlockTag(block, {start: "[i]", end: "[/i]"});
                                        //textarea_object.value += '[i][/i]';
					break;
				};
				case 'underline':{	
					insertBlockTag(block, {start: "[u]", end: "[/u]"});
                    //textarea_object.value += '[u][/u]';
					break;
				};
				case 'quote':{
					textarea_object.value += '(User){userquote}';
					break;
				};
                case 'spoiler':{
                    textarea_object.value += "(spoiler)[ spoiler text here :) ]";
                    break;
                };
                case 'offtopic':{
                    textarea_object.value += "(off)[ offtopic text here :) ]";
                    break;
                };
				default:{
					break;	
				}
			}
		}else{ //markdown by default
		switch (obj){
			case 'bold': {
					
					insertBlockTag(block, {start: "**", end: "**"});
                                        //textarea_object.value += '** **';
					break;
			};
			case 'italic':{
				
				insertBlockTag(block, {start: "__", end: "__"});
                                //textarea_object.value += '* *';
				break;
			};
			case 'underline':{
				insertBlockTag(block, {start: "+", end: "+"});
                                //textarea_object.value += '_ _'
				break;
			};
			case 'quote':{
				textarea_object.value += '(User){userquote}';
				break;
			};
            case 'spoiler':{
                textarea_object.value += "(spoiler)[ spoiler text here :) ]";
                break;
            };
            case 'offtopic':{
                textarea_object.value += "(off)[ offtopic text here :) ]";
                break;
            };
			default: {
				//alert('unknown');
			};
		 } //switch
		}//endif
	}


function insertQuote(){
    t = document.getElementById('id_comment');
    if (window.getSelection){
        quote_text = window.getSelection().toString();
    }
    else if (document.getSelection){
        quote_text = document.getSelection().toString();
    }
    if (quote_text)
        t.value += "\n(User){"+quote_text+"}";
}

function insertBlockTag(element, pattern){
    t = document.getElementById(element);
    sel_start = t.selectionStart;
    sel_end = t.selectionEnd;
    text = t.value;
    
    s_text = text.substr(0,sel_start);
    e_text = text.substr(sel_end, text.length);
    tg_text = text.substr(sel_start, sel_end - sel_start);

    var new_text =  String(s_text + pattern.start + tg_text + pattern.end + e_text);
    t.value = new_text;

}

