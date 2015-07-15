(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;   
    Locker.addRequest;


    /**
     * Adds a new tag to the student via AJAX
     *
     * @return      void
     * @access      private
     * @author      Paul Rentschler <par117@psu.edu>
     * @since       21 March 2014
     */
Locker.add = function ()
{
    // submit the request
    var email = $("#email").val();
    var addUrl = $("#dialog-edit-users form").attr("action");           
    Locker.addRequest = $.ajax({
        url: addUrl,
        type: "post",
        data: {
            email: email,
            csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
              }
    });

    // callback handler: success
    Locker.addRequest.done(function (response, textStatus, jqXHR) {        
            $("#email").val("");
            $("#existing-users").append(Locker._build_list_entry(response));    
          Locker.addRequest = null;       
    });
    // callback handler: failure
    Locker.addRequest.fail(function (jqXHR, textStatus, errorThrown) {
        if (errorThrown != "abort") {
            if (jqXHR.status == 400 || jqXHR.status == 404) {
                Locker.errorHandler(jqXHR, 'adding');

            } else {
                console.error(
                    "Locker.add in Locker.js AJAX error: "
                        + textStatus,
                    errorThrown
                );
            }
        }
        Locker.addRequest = null;
    });
}

// Locker.delete = function ()
// {
//     // submit the request
//     var email = $("#email").val();
//     var deleteUrl = $("#tag-list").attr("data-url")           
//     Locker.deleteRequest = $.ajax({
//         url: deleteUrl,
//         type: "post",      
//         data: {
//             id: 'id',
//             csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
//         }
//     });

//     // callback handler: success
//     Locker.deleteRequest.done(function (response, textStatus, jqXHR) {
//         if (response.result) {
//             $("#email").val("");
//             Locker.update();
//         } else if (typeof(response) == "object") {
//             // this was a group add
//             $("#email").val("");
//             Locker.buildList(response);
//         }
//         Locker.deleteRequest = null;
//     });

//     // callback handler: failure
//     Locker.deleteRequest.fail(function (jqXHR, textStatus, errorThrown) {
//         if (errorThrown != "abort") {
//             if (jqXHR.status == 400 || jqXHR.status == 404) {
//                 Locker.errorHandler(jqXHR, 'adding');

//             } else {
//                 console.error(
//                     "Locker.add in Locker.js AJAX error: "
//                         + textStatus,
//                     errorThrown
//                 );
//             }
//         }
//         Locker.deleteRequest = null;
//     });
// }


Locker._build_list_entry = function (user)
{
 
    return $("<li />").attr("data-id", user.id).append( 
            $("<span />").html(user.first_name + " " + user.last_name)
        )    

 
}



  
     
Locker.buildList = function (users){

    var $users_list = $("#existing-users");

    // clear the list
    $tagList.children().remove();

    // build the list of Locker
    $.each(data, function (index, entry) {
        var $item = $("<a />").attr("href", "#").text(entry.name);
        if (entry.description != "") {
            $item.attr("title", entry.description);
        }
        if (entry.active) {
            $item.addClass("active");
        }
        if (!entry.user) {
            $item.append(
                $("<i />").addClass(
                    "global-indicator fo-icon-globe"
                ).attr("title", "Global tag").append(
                    $("<span />").addClass("sr-only").text("Global tag")
                )
            );
        }       
        
    });
}    
   

}( window.Locker = window.Locker || {}, jQuery));



$(document).ready(function (){
    //Opens the users modal dialog
    $("button[role='edit-users']").on("click", function (event){        
        event.preventDefault();
        var id= $(this).closest("tr").attr("data-id");
        var url = $("#dialog-edit-users").find("form").attr("data-url");
        $("#dialog-edit-users").find("form").attr("action", url.replace("/0/","/"+ id +"/"));
        $("#dialog-edit-users").modal('show');
    });

    //Opens the edit lockers modal dialog
    $("button[role='edit-locker']").on("click", function (event){
        $("#dialog-edit-locker").modal('show');
    });

    //Calls the add function 
    $("#dialog-edit-users form").on("submit", function (event){         
        event.preventDefault();
        Locker.add();
    });
 

});
