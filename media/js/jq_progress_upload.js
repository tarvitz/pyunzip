function gen_uuid(){
var uuid = String(Math.random(100)).replace('.','x');
return uuid;
}

$("#upload_form").submit(function(){
    //cleanse
    $('.form_errors').remove();
    if ($("upload_form").attr("submited")) return false;

    var tid = 0;
    var freq = 1000;
    var uuid = gen_uuid();
    var progress_url = progress_url_global;
    //var action = $('#upload_form').attr("action");
    var action = action_field + '?X-Progress-ID=' + uuid;
    $("#upload_form").attr("action",action);
    if (isFireFox || isChrome || isOpera){
    var progress_bar = "<div class='progressbar'><div class='transparency tr_navy'></div><div class='reflects_up'></div><div class='reflects_left'></div><div class='reflects_right'></div><span class='progress_info'>uploading </span><span id='upload_status' class='progress_values'>0%</span><br /><span class='progress_info'>uploaded </span><span id='upload_state' class='progress_values'>0 kb</span><br /><span class='progress_info'>size </span><span id='upload_size' class='progress_values'>0 kb</span><br /></div>";
    }else{
     var progress_bar = "<div class='progressbar'><div class='transparency tr_navy'></div><div class='reflects_up'></div><div class='reflects_left'></div><div class='reflects_right'></div><span class='progress_info'>uploading file </span><br /></div>";
    }
    $(this).fadeOut(1000,function(){
        $("#upload_progress").html(progress_bar).fadeIn(1000); 
    });
    //$("#upload_progress").html("<div class='progress-container'><span class='progress-info'>uploading 0%</span></div class='progress-bar'></div></div>").show();

    function update_progress_info(){
        $('#upload_progress').fadeIn(1000);
        $.getJSON(progress_url, {"X-Progress-ID": uuid}, function(data, status){
            if (data){
                //var width = $('.progress-container').width();
                //var progress_width = width * 1; //progress; // what the fuck is it?
                //$('.progress-bar').css('width', progress_width);
                //$('.progress-info').html('uploading' + parseInt(data.progress) + "%");
                if (isFireFox || isChrome || isOpera){
                    $("#upload_status").html(parseInt(data.progress) + "%");
                    $("#upload_size").html(Math.round(data.length/1024) + " kb");
                    $("#upload_state").html(Math.round(data.uploaded/1024) +" kb");
                }
                //$("#upload_speed").html(parseInt(data.progress) + "kb");
                /*if (!data.filename){ $("#upload_fname").hide(); } else {
                $("#upload_fname").html(data.filename); }*/
            }
        tid = window.setTimeout(update_progress_info,freq);
        if (data){
            if (data.complete){
                window.clearTimeout(tid);
                if (data.error == ''){
                    $("#upload_progress").html("<div class='new'>Upload Complete</div>").fadeOut(7000);
                    $("#upload_form").fadeIn(1000);
                } else {
                    if (data.errors){
                    /* $('#upload_progress').html('<p class="error">'+ data.error+'</p>'); <-- ugly :) */
                    $("#upload_progress").html("<div class='error'>Устраните нижеследующие ошибки</div>");
                    $('#upload_form').fadeIn(1000);
                    /*marking some errors*/
                    jQuery.each(data.errors,function(index,value){
                        var err_id = "#id_"+index+"_error";
                        //settings
                        if (!$(err_id).length)
                            $("<div class='error form_errors' id='id_"+index+"_error'> *"+value+"</div>").insertBefore("#id_"+index);
                        //cleansing

                    });
                    } //if errors
                    else {
                        $("#upload_progress").html("<div class='error'>"+data.error+"</div>");
                        $("#upload_form").fadeIn(1000);
                    }
                }
            }
        }
    });
  };
  tid = window.setTimeout(update_progress_info, freq);
  $('#upload_form').attr('submitted',true);
  return true;
});
