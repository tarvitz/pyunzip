//DEPENDS OF JQUERY
function sliding_up(cls,dict1,dict2,interval){
	
	$(cls).hover(
		function(){
			$(cls).animate(dict1,interval);
		},
		function(){
		$(cls).animate(dict2,interval);
		}
	);
}
