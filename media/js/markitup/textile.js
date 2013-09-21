debug = console.log.bind(console);
var uploadFile = function(h){
    $("#upload-file").detach().remove();
    tmpl = (isOpera) ? $.template('#uploadFileOperaTemplate') : $.template('#uploadFileTemplate');
    blk = $.tmpl(tmpl, {}).insertBefore($(h.textarea));
    // opera can not invoke file dialog, sad
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
            if (isOpera) $('#file-uploader').removeClass('hide');
            result = confirm(JS.locale.upload_file_message);
            if (!result){
                $('#progress-bar').addClass('hide').removeClass('active');
                if (isOpera) $('#file-uploader').addClass('hide');
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
            if (isOpera) $('#file-uploader').addClass('hide');
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
            if (isOpera) $('#file-uploader').addClass('hide');
        }
    }); /* end of html5 upload */
    }


myMarkupSettings = {
    'textile': {
        nameSpace: 'textile',
        previewParserPath:	'/comment/preview/?markup=textile', // path to your Textile parser
        previewAutoRefresh: false,
        onShiftEnter:		{keepDefault:false, replaceWith:'\n\n'},
        markupSet: [
            {
            name: "", className: 'heading',
            dropMenu: [
                {name:'Heading 1', key:'1', openWith:'h1(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h1'},
                {name:'Heading 2', key:'2', openWith:'h2(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h2'},
                {name:'Heading 3', key:'3', openWith:'h3(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h3'},
                {name:'Heading 4', key:'4', openWith:'h4(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h4'},
                {name:'Heading 5', key:'5', openWith:'h5(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h5'},
                {name:'Heading 6', key:'6', openWith:'h6(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h6'}
            ]},
            {name:'', key:'P', openWith:'p(!(([![Class]!]))!). ', className: 'p', dataTitle: "new paragraph"},
            {name:'', key:'B', closeWith:'*', openWith:'*', className: 'bold', dataTitle: "bold text"},
            {name:'', key:'I', closeWith:'_', openWith:'_', className: 'italic', dataTitle: "italic text"},
            {name:'', key:'U', openWith:'+', closeWith:'+', className: 'underline', dataTitle: "underline text"},
            {name:'', key:'S', closeWith:'-', openWith:'-', className: 'stroke', dataTitle: "strike through text"},
            {separator:'', className: 'divider' },
            {name:'', openWith:'(!(* |!|*)!)', className: 'list-bullet', dataTitle: "bullet list"},
            {name:'', openWith:'(!(# |!|#)!)', className: 'list-numeric', dataTitle: "numeric list"},
            //{name:'Quotes', openWith:'bq(!(([![Class]!]))!). ', className: 'quote'},
            {name:'', openWith:'@', closeWith:'@', className: 'code', dataTitle: "code"},
            {separator:'', className: 'divider' },
            /*{name:'Clean', className:"clean", replaceWith:function(markitup) { return false; }, className: 'clean' },*/
            /*{name:'Markup', key:'M', className: 'markup',
            dropMenu :[
                {name:'BBcode', call: 'reloadMarkItUp("bb-code")'},
                {name:'Textile', call: 'reloadMarkItUp("textile")'}
            ]},*/
            {name: "", className: 'spoiler-button', openWith:'(spoiler)[', closeWith: ']', dataTitle: "spoiler"},
            {name: "", className: 'offtopic-button', openWith:'(off)[', closeWith: ']', dataTitle: "offtopic"},
            {name: "", className: 'video', openWith:'(video)[', closeWith: ']', dataTitle: "video"},
            {separator:"", className: 'divider'},
            {name:'', openWith:'"', closeWith:'[![Title]!]":[![Link:!:http://]!]',
                //placeHolder:'Your text to link here...',
                className: 'link', dataTitle: "link"},

            {name: "", className: 'upload-picture',
            dropMenu: [
                {name:'Picture', replaceWith:'![![Source:!:http://]!]([![Alternative text]!])!', className: 'picture'},
                {
                name:"Upload file", className: 'upload-file',
                beforeInsert: uploadFile
                }
            ]},
            {name:'', call:'preview', className:'preview', className:' preview', dataTitle: "preview"}
        ]
    } //end textile

}