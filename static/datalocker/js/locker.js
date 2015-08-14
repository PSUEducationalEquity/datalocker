/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */
(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;
    Locker.addRequest;
    Locker.deleteRequest;

    /**
     *  Javascript to add users to existing lockers; Archive, Unarchive, &
     *  Delete functionality handled here as well. JS code to activate
     *  locker and users modals are located at the bottom of this file.
     *
    */


    /* Add a user to the selected locker */
    Locker.add = function () {
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
            if ($("#no-users-message").length){
                $("#no-users-message").remove();
            }
            $("#existing-users").append(Locker._build_user_list_entry(response));
            $("#email").val("");
            $("#email").focus();
            Locker.addRequest = null;
        });

        // callback handler: failure
        Locker.addRequest.fail(function (jqXHR, errorThrown) {
            if (errorThrown != "abort") {
                console.error("Locker.add in Locker.js AJAX error");
            }
            Locker.addRequest = null;
        });
    }

    /* Adds the ability to archive a locker */
    Locker.archive = function(id) {
        archiveUrl = $("#archive-locker").attr("data-url");
        $.ajax({
            url: archiveUrl.replace("/0/", "/" + id +"/"),
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find(
                    "input[name='csrfmiddlewaretoken']").val()
            },
            // callback handler: success
            success: function(data) {
                $("#locker-list tr[data-id='" + id + "']").addClass('list-lockers is-archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                    'Unarchive');
            },
            // callback handler: failure
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Locker.archive in Locker.js AJAX error: "
                    + textStatus,
                    errorThrown
                );
            }
        });
    }

    /* Adds the ability to unarchive a locker */
    Locker.unarchive = function(id) {
        unarchiveUrl = $("#unarchive-locker").attr("data-url");
        $.ajax({
            url: unarchiveUrl.replace("/0/", "/" + id +"/"),
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find(
                    "input[name='csrfmiddlewaretoken']").val()
            },
            // callback handler: success
            success: function(data) {
                $('#locker-list tr[data-id=' + id + "]").removeClass('list-lockers is-archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                    'Archive');
            },
            // callback handler: failure
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(
                    "Locker.archive in Locker.js AJAX error: "
                    + textStatus,
                    errorThrown
                );
            }
        });
    }

    /* Adds the ability to delete user from a locker */
    Locker.delete = function (user_id) {
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
        // callback handler: success
        Locker.deleteRequest.done(function (response, textStatus, jqXHR) {
            $("#existing-users li[data-id='" + response.user_id + "']").remove();
            Locker.no_user_message();
          Locker.deleteRequest = null;
        });

        // callback handler: failure
        Locker.deleteRequest.fail(function (jqXHR, errorThrown) {
            if (errorThrown != "abort") {
               console.error("Locker.delete in Locker.js AJAX error");
            }
            Locker.deleteRequest = null;
        });
    }


    /**
     * Builds a list of a single entry of a user that was submitted
     *
     * @return     void
     * @author     Hunter Yohn  <hay110@psu.edu>
     */

    Locker._build_user_list_entry = function (user) {
        return  $("<li />").attr("data-id", user.id).append(
            $("<div />").addClass("existing-users-list").html(
                user.first_name + " " + user.last_name + " "
            )).append(
                $("<a />").attr("href", "#").attr(
                    "title",
                    "Stop sharing access to this locker with " + user.first_name + " " + user.last_name
                ).append(
                    $("<span />").addClass(
                        "glyphicon glyphicon-remove pull-right remove-users"
                    )
                )
            );
    }

    /**
     * Builds a list off all of the user list entries
     *
     * @return     void
     * @author     Hunter Yohn  <hay110@psu.edu>
     */

    Locker.build_user_list = function (users) {
        var locker_id = $("#dialog-edit-users").attr("data-locker-id");
        var url = $("#existing-users").attr("data-url").replace(
            "/0/", "/" + locker_id +"/");


        // submit the request (if none are pending)
        if  (!Locker.dataRequest && url) {
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
                        $users_list.append(Locker._build_user_list_entry(user));
                });
                Locker.no_user_message();
                Locker.dataRequest = null;
            });

            // callback handler: failure
            Locker.dataRequest.fail(function (jqXHR, textStatus, errorThrown) {
                if  (errorThrown != "abort") {
                    console.error(
                        "Locker.build_user_list in locker.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Locker.dataRequest = null;
            });
        }

        Locker.no_user_message = function () {
            if ($("#existing-users li").length == 0){
                $("#existing-users").append(
                    $("<li />").attr('id','no-users-message'
                        ).append(
                            "There are no users for this locker")
                        );
            }
        }
    }
}( window.Locker = window.Locker || {}, jQuery));


$(document).ready(function () {

    //opens the users modal dialog
    $("button[role='edit-users']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        $("#dialog-edit-users").attr("data-locker-id", id);
        var url = $("#dialog-edit-users").find("form").attr("data-url");
        $("#dialog-edit-users").find("form").attr(
            "action", url.replace("/0/","/"+ id +"/"));
        Locker.build_user_list();
        var name = $(this).closest("tr").attr("data-name");
        $("#dialog-edit-users-title").html('Share access to ' + name);
        $("#dialog-edit-users").modal('show');
    });

    //opens the edit lockers modal dialog
    $("button[role='edit-locker']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        $("#dialog-edit-locker").attr("data-locker-id", id);
        var url = $("#dialog-edit-locker").find("form").attr("data-url");
        $("#dialog-edit-locker").find("form").attr(
            "action", url.replace("/0/","/"+ id +"/"));
        var name = $(this).closest("tr").attr("data-name");
        $("#edit-locker").val(name);
        var settings = jQuery.parseJSON($(this).closest("tr").attr("data-settings"));
        console.log(settings);
        $("#dialog-edit-locker input[name='enable-workflow']").prop('checked', settings['workflow|enabled']);
        $("#dialog-edit-locker input[name='users-can-view-workflow']").prop('checked', settings['workflow|users-can-view']);
        $("#dialog-edit-locker input[name='users-can-edit-workflow']").prop('checked', settings['workflow|users-can-edit']);
        $("#dialog-edit-locker textarea[name='workflow-states-textarea']").val(
            settings['workflow|states'].join("\n")
        );
        $("#dialog-edit-locker").modal('show');
    });

    //handles the 'add' button for the edit users dialog
    $("#dialog-edit-users form").on("submit", function (event) {
        event.preventDefault();
        Locker.add();
    });

    //handles the 'delete' button for the edit users dialog
    $("#dialog-edit-users form ul").on("click","a", function (event) {
        event.preventDefault();
        var user_id = $(this).closest("li").attr("data-id");
        Locker.delete(user_id);
    });

    $("[role='archive-locker']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        if ($(this).html() == "Archive") {
            Locker.archive(id);
            $(this).removeClass('btn-danger');
            $(this).addClass('btn-success');
        } else {
            Locker.unarchive(id);
            $(this).addClass('btn-danger');
            $(this).removeClass('btn-success');
        }
    });
    $(".button-archived-showhide").click(function() {
      if ($(this).html() == "Show Archived Lockers") {
            $('.is-archived').show();
            $(this).addClass('button-archived-showhide is-active');
            $(this).html('Hide Archived Lockers');
            document.cookie="show/hide=show";
        } else {
            $('.is-archived').hide();
            $(this).removeClass('button-archived-showhide is-active');
            $(this).html('Show Archived Lockers');
            document.cookie="show/hide=hide"
        }
    });


    var showHide = getCookie("show/hide");
    if (showHide == "show") {
        $('.is-archived').show();
        $(".button-archived-showhide").addClass('button-archived-showhide is-active');
        $(".button-archived-showhide").html('Hide Archived Lockers');
    }
    else {
        $('.is-archived').hide();
        $(".button-archived-showhide").removeClass('button-archived-showhide is-active');
        $(".button-archived-showhide").html('Show Archived Lockers');
    }

    // Taken from w3 schools to retireve a cookie value
    function getCookie(cname) {
        var name = cname + "=";
        var ca = document.cookie.split(';');
        for(var i=0; i<ca.length; i++) {
            var c = ca[i];
            while (c.charAt(0)==' ') c = c.substring(1);
            if (c.indexOf(name) == 0) return c.substring(name.length,c.length);
        }
        return "";
    }

    // Enables tablesorter JS on the tablesorter tables
    $('.tablesorter').tablesorter();
});