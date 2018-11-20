$(document).ready(function() {
    $('[data-toggle="tooltip"]').tooltip()

    if (is_favorited){
        $("#btn_favorited").toggleClass("btn-primary btn-outline-primary");
    }

    if (current_vote == 1){
        $("#btn_vote_up").toggleClass("btn-primary btn-outline-primary");
    }
    else if(current_vote == -1){
        $("#btn_vote_down").toggleClass("btn-primary btn-outline-primary");
    }

    $("#btn_favorited").click(function(){
        $("#btn_favorited").toggleClass("btn-primary btn-outline-primary");
        is_favorited = !is_favorited;
        
        $.get(favorite_url, function(data, status){
            var fav_count = parseInt($("#favorite_count").text(), 10);

            if (is_favorited === true){
                fav_count += 1;
            }
            else{
                fav_count -= 1;
            }

            $("#favorite_count").text(fav_count);
        });
    });

    function getScore(){
        return parseInt($("#score_count").text(), 10);
    }

    function setScore(value){
        $("#score_count").text(value);
    }

    function switchButton(button_name, value){
        if (value == true){
            $(button_name).addClass('btn-outline-primary').removeClass('btn-primary');
        }
        else if (value == false){
            $(button_name).addClass('btn-primary').removeClass('btn-outline-primary');
        }
    }

    $("#btn_vote_up").click(function(){            
        $.get(vote_url + "?point=1", function(data, status){
            var value = data['value'];
            var current_points = data['current_points'];
            setScore(current_points);

            if (value === 1){
                switchButton("#btn_vote_up", true);
                switchButton("#btn_vote_down", false);
            }
            else {
                switchButton("#btn_vote_up", false);
                switchButton("#btn_vote_down", false);
            }
        });
    });

    $("#btn_vote_down").click(function(){            
        $.get(vote_url + "?point=-1", function(data, status){
            var value = data['value'];
            var current_points = data['current_points'];
            setScore(current_points);

            if (value === -1){
                switchButton("#btn_vote_up", false);
                switchButton("#btn_vote_down", true);
            }
            else {
                switchButton("#btn_vote_up", false);
                switchButton("#btn_vote_down", false);
            }
        });
    });
    
    var $root = $('html, body');

    $( "#show_edit_form" ).click(function() {
        $("#show_comments").removeClass("btn-primary").addClass("btn-outline-primary");
        $("#show_edit_form").toggleClass("btn-primary btn-outline-primary");
        $( "#edit" ).toggle();
        $( "#comment-section" ).hide();

        if ($('#edit').is(':visible')){
            $root.animate({
                scrollTop: $("#edit").offset().top},
                'slow'
            );
        }
    });

    $( "#show_comments" ).click(function() {
        $("#show_edit_form").removeClass("btn-primary").addClass("btn-outline-primary");
        $("#show_comments").toggleClass("btn-primary btn-outline-primary");
        $( "#edit" ).hide();
        $( "#comment-section" ).toggle();

        if ($('#comment-section').is(':visible')){
                $root.animate({
                scrollTop: $("#comment-section").offset().top},
                'slow'
            );
        }
    });
});