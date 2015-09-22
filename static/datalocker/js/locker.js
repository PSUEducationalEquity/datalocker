/* Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */

(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;
    Locker.addRequest;
    Locker.deleteRequest;


    /* Adds the ability to archive a locker */
    Locker.archive = function(id) {
        archiveUrl = $("#locker-list").attr("data-archive-url");
        $.ajax({
            url: archiveUrl.replace("/0/", "/" + id +"/"),
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-sharing").find(
                    "input[name='csrfmiddlewaretoken']").val()
            },
            // callback handler: success
            success: function(data) {
                $("#locker-list tr[data-id='" + id + "']").addClass('is-archived');
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
                csrfmiddlewaretoken: $("#dialog-sharing").find(
                    "input[name='csrfmiddlewaretoken']").val()
            },
            // callback handler: success
            success: function(data) {
                $('#locker-list tr[data-id=' + id + "]").removeClass('is-archived');
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



    /**
     * Builds a single entry for the list of existing users
     *
     * @param   user object  an object representing the user to build the list
     *                       entry for
     * @return  a string containing the HTML to display a single user in the
     *          existing users list
     * @author  Hunter Yohn <hay110@psu.edu>
     */
    Locker._build_user_list_entry = function (user)
    {
        return  $("<li />").attr("data-id", user.id).append(
            $("<div />").html(user.first_name + " " + user.last_name)).append(
                $("<a />").attr("href", "#").attr(
                    "title",
                    "Stop sharing access to this locker with "
                        + user.first_name + " " + user.last_name
                ).append(
                    $("<span />").addClass(
                        "glyphicon glyphicon-remove pull-right"
                    )
                )
            );
    }



    /**
     * Builds a list of users who have access to this locker
     *
     * @param   users array  an array of users who currently have access to
     *          the locker
     * @return  void
     * @author  Hunter Yohn <hay110@psu.edu>
     */
    Locker.build_user_list = function (users)
    {
        var locker_id = $("#dialog-sharing").attr("data-locker-id");
        var url = $("#dialog-sharing .list-existing-users").attr("data-url");

        // submit the request (if none are pending)
        if  (!Locker.dataRequest && url) {
            Locker.dataRequest = $.ajax({
                url: url.replace("/0/", "/" + locker_id + "/"),
                type: "get",
                cache: false,
                success: function(response, textStatus, jqXHR)
                {
                    var $users_list = $("#dialog-sharing .list-existing-users");
                    $users_list.children(":not(.no-entries)").remove();
                    $.each(response.users, function (index, user) {
                        $users_list.append(Locker._build_user_list_entry(user));
                    });
                    Locker.no_user_message();
                    Locker.dataRequest = null;
                },
                error: function(jqXHR, textStatus, errorThrown)
                {
                    if  (errorThrown != "abort") {
                        console.error(
                            "Locker.build_user_list in locker.js AJAX error: "
                                + textStatus,
                            errorThrown
                        );
                    }
                    Locker.dataRequest = null;
                }
            });
        }
    }



    /**
     * Shows/hides the "no users have access" message
     *
     * @return  void
     */
    Locker.no_user_message = function ()
    {
        var $users_list = $("#existing-users");
        if ($users_list.children("li:not(.no-entries)").length == 0){
            $users_list.children(".no-entries").show();
        } else {
            $users_list.children(".no-entries").hide();
        }
    }



    Locker.show_hide_archived = function (state) {
        if (state == 'show') {
            $("table").addClass("js-show-archived");
        } else if (state == 'hide') {
            $("table").removeClass("js-show-archived");
        }
        document.cookie="show/hide=" + state;
    }



    /**
     * Add a user to the current locker
     *
     * @param   integer user_id  an integer indicating the user id to add
     * @return  void
     */
    Locker.user_add = function () {
        var url = $("#dialog-sharing form").attr("action");
        var csrf_token = $("#dialog-sharing").find("input[name='csrfmiddlewaretoken']").val();
        Locker.addRequest = $.ajax({
            url: url,
            type: "post",
            data: {
                email: $("#email").val(),
                csrfmiddlewaretoken: csrf_token,
            },
            success: function(response, textStatus, jqXHR)
            {
                $("#existing-users").append(
                    Locker._build_user_list_entry(response.user)
                );
                Locker.no_user_message();
                Locker.addRequest = null;
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                if (jqXHR.status == 404) {
                    UserMessage.add(
                        "<strong>Oops!</strong> the user you specified "
                        + "does not exist.",
                        "danger",
                        5,
                        "dialog-sharing"
                    );
                } else if (errorThrown != "abort") {
                    console.error(
                        "Locker.add_user in locker.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Locker.addRequest = null;
            }
        });
    }



    /**
     * Delete a user from the current locker
     *
     * @param   integer user_id  an integer indicating the user id to remove
     * @return  void
     */
    Locker.user_delete = function (user_id)
    {
        var url =  $("#dialog-sharing .list-existing-users").attr("data-delete-url");
        var locker_id = $("#dialog-sharing").attr("data-locker-id");
        var csrf_token = $("#dialog-sharing").find("input[name='csrfmiddlewaretoken']").val();
        Locker.deleteRequest = $.ajax({
            url: url.replace("/0/", "/" + locker_id +"/"),
            type: "post",
            data: {
                id : user_id,
                csrfmiddlewaretoken: csrf_token,
            },
            success: function(response, textStatus, jqXHR)
            {
                $("#existing-users li[data-id='" + response.user_id + "']").remove();
                Locker.no_user_message();
                Locker.deleteRequest = null;
            },
            error: function(jqXHR, textStatus, errorThrown)
            {
                if (errorThrown != "abort") {
                    console.error(
                        "Locker.build_user_list in locker.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Locker.deleteRequest = null;
            }
        });
    }
}( window.Locker = window.Locker || {}, jQuery));




/**
 * Get a specific value from a cookie
 *
 * Base code adapted from the example here:
 * http://www.w3schools.com/js/js_cookies.asp
 *
 * @param   cookie string  a string containing the name of the cookie to retrieve
 * @return  a string containing the cookie value requested
 */
function getCookieValue(key)
{
    var name = key + "=";
    var pairs = document.cookie.split(';');
    for (var i=0; i < pairs.length; i++) {
        var entry = pairs[i];
        while (entry.charAt(0)==' ') entry = entry.substring(1);
        if (entry.indexOf(name) == 0) {
            return entry.substring(name.length, entry.length);
        }
    }
    return 'false';
}




/**
 * Convert a string to a boolean
 *
 * @param   value string  a string containing either "true" or "false"
 * @return  a boolean based on the string contents provided
 */
function toBool(value)
{
    value = value.toLowerCase();
    if (value == 'false' || value == 'no') {
        return false;
    }
    return true;
}


$(document).ready(function () {
    // enable table sorting
    $('table.tablesorter').tablesorter();


    // Show/hide archived lockers
    $("[name='archived-lockers-toggle']").on("change", function (event)
    {
        if ($(this).prop("checked")) {
            $("body").addClass("js-show-archived");
        } else {
            $("body").removeClass("js-show-archived");
        }
        document.cookie="show-archived-toggle=" + $(this).prop("checked");
    });
    $("[name='archived-lockers-toggle']").prop(
        "checked",
        toBool(getCookieValue("show-archived-toggle"))
    ).change();


    // Handle the archive locker buttons
    $("[role='archive-locker']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Locker.archive(id);
    });


    // Handle the unarchive locker buttons
    $("[role='unarchive-locker']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Locker.unarchive(id);
    });




    // Activate the Sharing dialog
    $("button[role='sharing']").on("click", function (event)
    {
        event.preventDefault();
        var locker_id = $(this).closest("tr").attr("data-id");
        $("#dialog-sharing").attr("data-locker-id", locker_id);
        var url = $("#dialog-sharing").find("form").attr("data-url");
        $("#dialog-sharing").find("form").attr(
            "action",
            url.replace("/0/","/"+ locker_id + "/")
        );
        var name = $(this).closest("tr").attr("data-name");

        Locker.build_user_list();
        $("#dialog-sharing-title").html('Share access to ' + name);
        $("#dialog-sharing .typeahead").typeahead('val', '');

        $("#dialog-sharing").modal('show');
    });

    // Sharing dialog: Add user button
    $("#dialog-sharing form").on("submit", function (event)
    {
        event.preventDefault();
        Locker.user_add();
        $(".typeahead").typeahead('val', '');
    });

    // Sharing dialog: Delete user buttons
    $("#dialog-sharing .list-existing-users").on("click", "a", function (event)
    {
        event.preventDefault();
        var user_id = $(this).closest("li").attr("data-id");
        Locker.user_delete(user_id);
    });




    /**
     * Auto-complete functionality
     *
     * Using http://typeahead.js
     * Configures the auto-complete engine with a list of all the system users
     */
    var users_engine = new Bloodhound({
        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('email'),
        queryTokenizer: Bloodhound.tokenizers.whitespace,
        prefetch: {
            url: $("#locker-list").attr("data-users-url"),
            cache: false,
            transform: function (response) {
                return response.users;
            }
        }
    });
    $(".typeahead").typeahead({
        hint: false,
        minLength: 1,
        highlight: true,
    }, {
        displayKey: 'email',
        name: 'users',
        source: users_engine,
        templates: {
            suggestion: function (user) {
                return '<p>' + user.email + ' &nbsp; <em>' + user.first_name
                    + ' ' + user.last_name + '</em></p>';
            }
        }
    }).on("typeahead:open", function () {
        var $menu = $(this).closest(".twitter-typeahead").find(".tt-menu");
        $menu.width($(this).width());
    });
    $(".twitter-typeahead").attr("style", "position: relative;");




    // Activate the Edit Locker dialog
    $("[role='edit-locker']").on("click", function (event)
    {
        event.preventDefault();
        var locker_id = $(this).closest("tr").attr("data-id");
        $("#dialog-edit-locker").attr("data-locker-id", locker_id);
        var url = $("#dialog-edit-locker").find("form").attr("data-url");
        $("#dialog-edit-locker").find("form").attr(
            "action",
            url.replace("/0/","/"+ locker_id +"/")
        );

        // set the name and clear the owner field
        $("#locker-name").val($(this).closest("tr").attr("data-name"));
        $("#dialog-edit-locker .typeahead").typeahead('val', '');

        // load the feature options
        var settings = jQuery.parseJSON($(this).closest("tr").attr("data-settings"));

        // set the new submissions option
        $("input[name='shared-users']").prop(
            'checked',
            settings['submission-notifications|notify-shared-users']
        );

        // set the workflow options
        $("input[name='workflow-users-can-edit']").prop(
            'checked',
            settings['workflow|users-can-edit']
        );
        workflow_states = [];
        if (settings['workflow|states']) {
            workflow_states = settings['workflow|states'];
        }
        $("textarea[name='workflow-states']").val(
            workflow_states.join("\n")
        );
        $("input[name='workflow-enable']").prop(
            'checked',
            settings['workflow|enabled']
        ).change();

        // set the discussion options
        $("input[name='discussion-users-have-access']").prop(
            'checked',
            settings['discussion|users-have-access']
        );
        $("input[name='discussion-enable']").prop(
            'checked',
            settings['discussion|enabled']
        ).change();

        // show the dialog
        $("#dialog-edit-locker").modal('show');
    });

    // Show/hide the various locker options
    $(".locker-option").on("change", function ()
    {
        $sub_options = $("[role='" + $(this).attr("data-target") + "']");
        if ($(this).prop("checked")) {
            $sub_options.slideDown();
        } else {
            $sub_options.slideUp();
        }
    });

    // disable the submit/cancel buttons when the edit locker form is submitted
    $("#dialog-edit-locker form").on("submit", function (event) {
        $("#dialog-edit-locker .modal-footer input").prop("disabled", true);
        $("#dialog-edit-locker button.close").prop("disabled", true);
    });
});