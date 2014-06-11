// -------------------------------------------------------------------
// markItUp!
// -------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// -------------------------------------------------------------------
// Textile tags example
// http://en.wikipedia.org/wiki/Textile_(markup_language)
// http://www.textism.com/
// -------------------------------------------------------------------
// Feel free to add more tags
// -------------------------------------------------------------------
myTextileSettings = {
    nameSpace: 'textile',
	previewParserPath:	'', // path to your Textile parser
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
}
