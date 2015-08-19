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
        archiveUrl = $("#locker-list").attr("data-archive-url");
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
                $("#locker-list tr[data-id='" + id + "']").addClass('is-archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                    "Unarchive");
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
        unarchiveUrl = $("#locker-list").attr("data-unarchive-url");
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
                $('#locker-list tr[data-id=' + id + "]").removeClass('is-archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html(
                    "Archive");
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



    // Locker.show_hide_archived = function (state) {
    //     if (state == 'show') {
    //         $("table").addClass("js-show-archived");
    //         $("button[name='show-hide-lockers']").addClass(
    //             'is-active'
    //         ).html(
    //             'Hide Archived Lockers'
    //         );
    //     } else if (state == 'hide') {
    //         $("table").removeClass("js-show-archived");
    //         $("button[name='show-hide-lockers']").removeClass(
    //             'is-active'
    //         ).html(
    //             'Show Archived Lockers'
    //         );
    //     }
    //     document.cookie="show/hide=" + state;
    // }
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

    $("#locker-list").on("click","button[role='archive-locker']", function (event) {
        event.preventDefault();
        var showing = $("table").hasClass("js-show-archived");
        var id = $(this).closest("tr").attr("data-id");
        if ($(this).html() == "Archive") {
            Locker.archive(id);
            $(this).html("Unarchive");
            $(this).removeClass("btn-danger").addClass("btn-success");
        } else {
            Locker.unarchive(id);
            var showing = $("table").removeClass("js-show-archived");
            $(this).removeClass("btn-success").addClass("btn-danger");
            $(this).html("Archive");
        }
    });

    $(".hide-show-archived-lockers-checkbox").on("click", function (event) {
        $("button[role='archive-locker']").show();
        $(".is-archived").toggle();

    });

    // var showHide = getCookie("show/hide");
    // Locker.show_hide_archived(showHide);

    // Taken from w3 schools to retrieve a cookie value
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