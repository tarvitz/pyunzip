// ----------------------------------------------------------------------------
// markItUp!
// ----------------------------------------------------------------------------
// Copyright (C) 2008 Jay Salvat
// http://markitup.jaysalvat.com/
// ----------------------------------------------------------------------------
// BBCode tags example
// http://en.wikipedia.org/wiki/Bbcode
// ----------------------------------------------------------------------------
// Feel free to add more tags
// ----------------------------------------------------------------------------
myBBSettings = {
    nameSpace: 'bbcode',
	previewParserPath:	'', // path to your BBCode parser
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
}
