$(document).ready(function(){        
    $("#edit_about").click(function(){
        if ($("#about-data").css('display') === "none")
        {
            $("#about-data").show();
            $("#about-edit").hide();
        }
        else
        {
            $("#about-data").hide();
            $("#about-edit").show();
        }
    }); 
});