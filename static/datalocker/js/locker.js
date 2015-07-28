// Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.
(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;
    Locker.addRequest;
    Locker.deleteRequest;

    /**
     *  Builds a list of users,also archives/unarchives lockers
     *      
    */



    Locker.add = function ()
       {   // submit the request
            var email = $("#email").val();
            var addUrl = $("#dialog-edit-users form").attr("action");
            Locker.addRequest = $.ajax({
                url: addUrl,
                type: "post",
                data: {
                    email: email,
                    csrfmiddlewaretoken: $("#dialog-edit-users").find(
                        "input[name='csrfmiddlewaretoken']").val()
                    }
            });
    // callback handler: success
            Locker.addRequest.done(function (response, textStatus, jqXHR) {
                    $("#email").val("");
                    $("#existing-users").append(Locker._build_list_entry(response));
                    $("email").focus();
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

    Locker.archive = function(id)
        {
            $.ajax({
                url: '/datalocker/' + id + '/archive',
                type: 'POST',
                data: {
                    id: id,
                    csrfmiddlewaretoken: $("#dialog-edit-users").find(
                        "input[name='csrfmiddlewaretoken']").val()
                },
                success: function(data){
                    $("#locker-list tr[data-id='" + id + "']").addClass('archived');
                    $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                        'Unarchive Locker');
                }
            });
        }

    Locker.unarchive = function(id) {
        $.ajax({
            url: '/datalocker/' + id + '/unarchive',
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find(
                    "input[name='csrfmiddlewaretoken']").val()
            },
            success: function(data){
                $('#locker-list tr[data-id=' + id + "]").removeClass('archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                    'Archive Locker');
                }
            });
        }

    Locker.delete = function (user_id)
        {
            // submit the request
            var deleteUrl =  $("#existing-users").attr("data-delete-url");
            var locker_id = $("#dialog-edit-users").attr("data-locker-id");

            Locker.deleteRequest = $.ajax({
                url: deleteUrl.replace("/0/", "/" + locker_id +"/"),
                type: "post",
                data: {
                    id : user_id,
                    csrfmiddlewaretoken: $("#dialog-edit-users").find(
                        "input[name='csrfmiddlewaretoken']").val()
                      }
            });

            Locker.deleteRequest.done(function (response, textStatus, jqXHR) {
             $("#existing-users li[data-id='" + response.user_id + "']").remove();
              Locker.deleteRequest = null;
            });
            // callback handler: failure
            Locker.deleteRequest.fail(function (jqXHR, textStatus, errorThrown) {
                if (errorThrown != "abort") {
                    if (jqXHR.status == 400 || jqXHR.status == 404) {
                        Locker.errorHandler(jqXHR, 'deleting');

                    } else {
                        console.error(
                            "Locker.delete in Locker.js AJAX error: "
                                + textStatus,
                        errorThrown
                        );
                    }
                }
                Locker.deleteRequest = null;
            });
        }


Locker._build_list_entry = function (user)
{
    return $("<li />").attr("data-id", user.id).append(
            $("<span />").html(user.first_name + " " + user.last_name + " ")
        ).append(
            $("<a />").html("<span class='glyphicon glyphicon-remove'>" ).attr("href", "#")
        );
}


Locker.buildList = function (users){

     // get the url to use
    var locker_id = $("#dialog-edit-users").attr("data-locker-id");
    var url = $("#existing-users").attr("data-url").replace(
        "/0/", "/" + locker_id +"/");

    // submit the request (if none are pending)
    if (!Locker.dataRequest && url) {
        Locker.dataRequest = $.ajax({
            url: url,
            type: "get",
            cache: false
        });

        // callback handler: success
        Locker.dataRequest.done(function (response, textStatus, jqXHR) {
            var $users_list = $("#existing-users");
            // clear the list
            $users_list.children().remove();
            // build the list of Locker
            $.each(response.users, function (index, user) {
                $users_list.append(Locker._build_list_entry(user));
            });
            Locker.dataRequest = null;
        });

        // callback handler: failure
        Locker.dataRequest.fail(function (jqXHR, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                console.error(
                    "Locker.dataRequest in locker.js AJAX error: "
                        + textStatus,
                    errorThrown
                );
            }
            Locker.dataRequest = null;
        });
    }    
} 
}( window.Locker = window.Locker || {}, jQuery));


$(document).ready(function (){
    //Opens the users modal dialog
    $("button[role='edit-users']").on("click", function (event){
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        $("#dialog-edit-users").attr("data-locker-id", id);
        var url = $("#dialog-edit-users").find("form").attr("data-url");
        $("#dialog-edit-users").find("form").attr(
            "action", url.replace("/0/","/"+ id +"/"));
        Locker.buildList();
        $("#dialog-edit-users").modal('show');
    });

    //Opens the edit lockers modal dialog
    $("button[role='edit-locker']").on("click", function (event){
        var id = $(this).closest("tr").attr("data-id");
        $("#dialog-edit-locker").attr("data-locker-id", id);
        var url = $("#dialog-edit-locker").find("form").attr("data-url");
        $("#dialog-edit-locker").find("form").attr(
            "action", url.replace("/0/","/"+ id +"/"));
        $("#dialog-edit-locker").modal('show');
    });

    //Calls the add function
    $("#dialog-edit-users form").on("submit", function (event){
        event.preventDefault();
        Locker.add();
    });

    $("#dialog-edit-users form ul").on("click","a", function (event){
        event.preventDefault();      
        var user_id =$(this).closest("li").attr("data-id");
        Locker.delete(user_id);
    });

    $("[role='archive-locker']").on("click", function (event){
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        if ($(this).html() == "Archive Locker"){
            Locker.archive(id);
        }
        else {
            Locker.unarchive(id);
        }
    }); 
    $("#show-hide-archived").click(function() {
      $('.archived').toggle();
      if ($(this).html() == "Show Archived Lockers"){
            $(this).addClass('active');
            $(this).html('Hide Archived Lockers');
        }
        else {
            $(this).removeClass('active');
            $(this).html('Show Archived Lockers');
        }
    });
});