function change_star(obj,id,img_str_full,img_str_null){
	for (i=1;i<id+1;i++){
		img_obj = document.getElementById(obj+'_'+i);
		img_obj.src = img_str_full;

	}
	for (i=id+1;i<6;i++){
		img_obj = document.getElementById(obj+'_'+i);
		img_obj.src = img_str_null;

	}
}

function stars_back(obj,id,str_stars,path){
					stars = String(str_stars).split(',');
					for (i=0;i<stars.length;i++){
						obj_img = document.getElementById(obj+'_'+(i+1));
						img_str = path+stars[i]+'.png';
						obj_img.src = img_str;
					}
				}
