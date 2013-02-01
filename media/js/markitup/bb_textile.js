myMarkupSettings = {
    'bb-code': {
        nameSpace: 'bbcode',
        previewParserPath:	'/comment/preview/?markup=bb-code', // path to your BBCode parser
        markupSet: [
            {name:'Bold', key:'B', openWith:'[b]', closeWith:'[/b]', className: 'bold'},
            {name:'Italic', key:'I', openWith:'[i]', closeWith:'[/i]', className: 'italic',},
            {name:'Underline', key:'U', openWith:'[u]', closeWith:'[/u]', className: 'underline'},
            {name:'Stroke through', key:'S', openWith:'[s]', closeWith:'[/s]', className: 'stroke'},
            {separator:'---------------' },
            {name:'Bulleted list', openWith:'[list]\n', closeWith:'\n[/list]', className: 'list-bullet'},
            {name:'Numeric list', openWith:'[list=[![Starting number]!]]\n', closeWith:'\n[/list]', className: 'list-numeric'},
            {name:'List item', openWith:'[*] ', className: 'list-item'},
            {separator:'---------------' },
            {name:'Picture', key:'P', replaceWith:'[img][![Url]!][/img]', className: 'picture'},
            {name:'Link', key:'L', openWith:'[url=[![Url]!]]', closeWith:'[/url]', placeHolder:'Your text to link here...', className: 'link'},
            {separator:'---------------' },
            {name:'Size', key:'S', openWith:'[size=[![Text size]!]]', closeWith:'[/size]', className: 'size',
            dropMenu :[
                {name:'Big', openWith:'[size=200]', closeWith:'[/size]' },
                {name:'Normal', openWith:'[size=100]', closeWith:'[/size]' },
                {name:'Small', openWith:'[size=50]', closeWith:'[/size]' }
            ]},

            {separator:'---------------' },
            {name:'Quotes', openWith:'[quote]', closeWith:'[/quote]', className: 'quote'},
            {name:'Code', openWith:'[code]', closeWith:'[/code]', className: 'code'},
            {separator:'---------------' },
            {name:'Clean', className:"clean", replaceWith:function(markitup) { return markitup.selection.replace(/\[(.*?)\]/g, "") } },
            {name:'Preview', className:"preview", call:'preview' },
            {name:'Markup', className: 'markup', key:'M',
            dropMenu :[
                {name:'BBcode', call: 'reloadMarkItUp("bb-code")'},
                {name:'Textile', call: 'reloadMarkItUp("textile")'}
            ]}
        ]
    }, // end bb-code
    'textile': {
        nameSpace: 'textile',
        previewParserPath:	'/comment/preview/?markup=textile', // path to your Textile parser
        onShiftEnter:		{keepDefault:false, replaceWith:'\n\n'},
        markupSet: [
            {name:'Heading 1', key:'1', openWith:'h1(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h1'},
            {name:'Heading 2', key:'2', openWith:'h2(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h2'},
            {name:'Heading 3', key:'3', openWith:'h3(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h3'},
            {name:'Heading 4', key:'4', openWith:'h4(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h4'},
            {name:'Heading 5', key:'5', openWith:'h5(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h5'},
            {name:'Heading 6', key:'6', openWith:'h6(!(([![Class]!]))!). ', placeHolder:'Your title here...', className: 'h6'},
            {name:'Paragraph', key:'P', openWith:'p(!(([![Class]!]))!). ', className: 'p'},
            {separator:'---------------' },
            {name:'Bold', key:'B', closeWith:'*', openWith:'*', className: 'bold'},
            {name:'Italic', key:'I', closeWith:'_', openWith:'_', className: 'italic'},
            {name:'Underline', key:'U', openWith:'+', closeWith:'+', className: 'underline'},
            {name:'Stroke through', key:'S', closeWith:'-', openWith:'-', className: 'stroke'},
            {separator:'---------------' },
            {name:'Bulleted list', openWith:'(!(* |!|*)!)', className: 'list-bullet'},
            {name:'Numeric list', openWith:'(!(# |!|#)!)', className: 'list-numeric'},
            {separator:'---------------' },
            {name:'Picture', replaceWith:'![![Source:!:http://]!]([![Alternative text]!])!', className: 'picture'},
            {name:'Link', openWith:'"', closeWith:'([![Title]!])":[![Link:!:http://]!]', placeHolder:'Your text to link here...', className: 'link'},
            {separator:'---------------' },
            {name:'Quotes', openWith:'bq(!(([![Class]!]))!). ', className: 'quote'},
            {name:'Code', openWith:'@', closeWith:'@', className: 'code'},
            {separator:'---------------' },
            {name:'Clean', className:"clean", replaceWith:function(markitup) { return false; }, className: 'clean' },
            {name:'Preview', call:'preview', className:'preview', className:' preview'},
            {name:'Markup', key:'M', className: 'markup',
            dropMenu :[
                {name:'BBcode', call: 'reloadMarkItUp("bb-code")'},
                {name:'Textile', call: 'reloadMarkItUp("textile")'}
            ]}

        ]
    } //end textile

}
