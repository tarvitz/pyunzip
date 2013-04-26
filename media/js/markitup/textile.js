myMarkupSettings = {
    'textile': {
        nameSpace: 'textile',
        previewParserPath:	'/comment/preview/?markup=textile', // path to your Textile parser
        previewAutoRefresh: false,
        onShiftEnter:		{keepDefault:false, replaceWith:'\n\n'},
        markupSet: [
            {name: "Headings", className: 'heading',
            dropMenu: [
                {name:'Heading 1', key:'1', openWith:'h1(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h1'},
                {name:'Heading 2', key:'2', openWith:'h2(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h2'},
                {name:'Heading 3', key:'3', openWith:'h3(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h3'},
                {name:'Heading 4', key:'4', openWith:'h4(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h4'},
                {name:'Heading 5', key:'5', openWith:'h5(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h5'},
                {name:'Heading 6', key:'6', openWith:'h6(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h6'},
            ]},
            {name:'Paragraph', key:'P', openWith:'p(!(([![Class]!]))!). ', className: 'p'},
            {name:'Bold', key:'B', closeWith:'*', openWith:'*', className: 'bold'},
            {name:'Italic', key:'I', closeWith:'_', openWith:'_', className: 'italic'},
            {name:'Underline', key:'U', openWith:'+', closeWith:'+', className: 'underline'},
            {name:'Stroke through', key:'S', closeWith:'-', openWith:'-', className: 'stroke'},
            {separator:'---------------' },
            {name:'Bulleted list', openWith:'(!(* |!|*)!)', className: 'list-bullet'},
            {name:'Numeric list', openWith:'(!(# |!|#)!)', className: 'list-numeric'},
            //{name:'Quotes', openWith:'bq(!(([![Class]!]))!). ', className: 'quote'},
            {name:'Code', openWith:'@', closeWith:'@', className: 'code'},
            {separator:'---------------' },
            /*{name:'Clean', className:"clean", replaceWith:function(markitup) { return false; }, className: 'clean' },*/
            /*{name:'Markup', key:'M', className: 'markup',
            dropMenu :[
                {name:'BBcode', call: 'reloadMarkItUp("bb-code")'},
                {name:'Textile', call: 'reloadMarkItUp("textile")'}
            ]},*/
            {name: "Spoiler", className: 'spoiler-button', openWith:'(spoiler)[', closeWith: ']'},
            {name: "Offtopic", className: 'offtopic-button', openWith:'(off)[', closeWith: ']'},
            {name: "Video", className: 'video', openWith:'(video)[', closeWith: ']'},
            {separator:"---------------"},
            {name:'Link', openWith:'"', closeWith:'[![Title]!]":[![Link:!:http://]!]',
                //placeHolder:'Your text to link here...',
                className: 'link'},

            {name: "Picture", className: 'upload-picture',
            dropMenu: [
                {name:'Picture', replaceWith:'![![Source:!:http://]!]([![Alternative text]!])!', className: 'picture'},
                {
                name:"Upload file", className: 'upload-file',
                beforeInsert: function(h){
                    $("#upload-file").detach().remove();
                    tmpl = $.template('#uploadFileTemplate');
                    blk = $.tmpl(tmpl, {}).insertBefore($(h.textarea));
                    $(blk).find('#id_file').click(); /* invoke click on filefield */

                    csrf = document.cookie.match(/csrftoken=([\w\d]+)/);
                    csrf = (csrf.length) ? csrf[1] : "";
                    textarea = $(h.textarea);

                    $(blk).find('input').html5_upload({
                        url: JS.urls['files:file-upload'],
                        sendBoundary: function(event){
                            return true;
                            // window.FormData || $.browser.mozilla;
                        },
                        extraFields: {
                            'csrfmiddlewaretoken': csrf
                        },
                        fieldName: "file",
                        onStart: function(event, total){
                            //return true;
                            $('#progress-bar').removeClass('hide').addClass('active');
                            result = confirm(JS.locale.upload_file_message);
                            if (!result){
                                $('#progress-bar').addClass('hide').removeClass('active');
                            }
                            return result;
                        },
                        onProgress: function(event, progress, name, number, total) {
                            console.log([progress, number, name, total]);
                        },
                        setName: function(text) {
                            $("#progress_report_name").text(text);
                        },
                        setStatus: function(text) {
                            $("#progress_report_status").text(text);
                        },
                        setProgress: function(val) {
                            $('#progress-bar .bar').css('width', Math.ceil(val*100) + "%");
                        },
                        onFinishOne: function(event, response, name, number, total) {
                            $('#progress-bar').addClass('hide').removeClass('active');
                            json = JSON.parse(response);
                            $('#progress-bar .bar').css('width', "0%");

                            if (json.file && !json.form){
                                noty({
                                    text: JS.locale.download_success,
                                    type: "success",
                                    dismissQueue: true,
                                    timeout: 4000
                                });
                                isImage = (json.mime_type.match(/image/)) ? true : false;
                                klass = (isImage) ? "user image" : "user file";
                                content = (isImage) ?
                                    //"!(__klass__)__url__!\n" :
                                    "\"(__klass__)!(__thmb_klass__)__thumb__!\":__url__" :
                                    "\"(__klass__)__the__link__\":__url__\n";

                                var txt = content.replace('__klass__', klass).replace('__url__', json.file.url);

                                if (txt.match(/__the__link__/)){
                                    link_name = prompt(JS.locale.enter_link_text) || "the link";
                                    txt = txt.replace('__the__link__', link_name);
                                }
                                if (txt.match(/__thumb__/)){
                                    txt = txt.replace('__thumb__', json.thumbnail.url);
                                }
                                if (txt.match(/__thmb_klass__/)){
                                    txt = txt.replace('__thmb_klass__', 'thumbnail inline');
                                }
                                textarea.val(textarea.val() + txt);
                            } else if (json.form){
                                message = '';
                                for (el in json.form.errors){
                                    message += json.form.errors[el].join(", ");
                                }
                                noty({
                                    text: message,
                                    type: "information",
                                    layout: 'center',
                                    dismissQueue: true
                                });
                            }

                        },
                        onError: function(event, name, error) {
                            noty({
                                text: JS.locale.upload_file_error + ": " + name,
                                type: 'error',
                                dismissQueue: true
                            });
                            $('#progress-bar').removeClass('active').addClass('hide');
                        }
                    }); /* end of html5 upload */
                }
            }
            ]},
            {name:'Preview', call:'preview', className:'preview', className:' preview'},
        ]
    } //end textile

}
