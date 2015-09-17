/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */

/**
 * Interactions related to submissions
 */


/**
 * Submission related actions
 */
(function (Submission, $, undefined)
{
    // the AJAX objects that handles server communication
    Submission.deleteRequest;
    Submission.undeleteRequest;




    /**
     * Delete's submissions, untill they are purged or undeleted   \
     *
     * @param      integer locker_id   an integer indicating the locker_id
     *                                 where the submission is located
     * @param      integer id          an integer indicating the submission id
     *                                 that will be deleted
     *
     * @return     void
     * @author     Hunter Yohn  <hay110@psu.edu>
     */
    Submission.delete = function (locker_id, id)
    {
        deleteUrl = $("#delete-submission").attr("data-url");
        // submits the request to delete the submission
        Submission.deleteRequest = $.ajax({
            url: "/datalocker/"+locker_id+"/submissions/" + id + "/delete_submission",
            type: "post",
            data:{
                id: id,
                csrfmiddlewaretoken: $("#delete_undelete_form").find(
                   "input[name='csrfmiddlewaretoken']").val()
                },
            success: function(data, response) {
                // deletes the submission and adds the class "deleted"
                $("#submission-list tr[data-id='" + id +"']").addClass("deleted submission-deleted");
                $("#submission-list tr[data-id='" + id +"'] button[role='delete-submission']").html(
                    "Undelete");
                var $label = $("#submission-list tr[data-id='" + id +"'] td span.label")
                $label.attr("data-timestamp", data.oldest_date);
                $label.html(Submission.build_timestamp_warning($label));
                console.log(data);


                Submission.deleteRequest = null;
                },
            error: function(jqXHR, textStatus, errorThrown) {
                    console.error(
                        "Submission.delete in Submission.js AJAX error: "
                    );
                }
            });
        Submission.deleteRequest = null;
    }


    /**
     * Undelete's submissions
     *
     * @param      integer locker_id   an integer indicating the locker_id
     *                                 where the submission is located
     * @param      integer id          an integer indicating the submission id
     *                                 that will be undeleted
     *
     * @return     void
     * @author     Hunter Yohn  <hay110@psu.edu>
     */
    Submission.undelete = function (locker_id, id)
    {
        undeleteUrl = $("button[role='delete-submission']").attr("data-url");
        // submits the request to undelete the submission
        Submission.undeleteRequest = $.ajax({
            url: "/datalocker/"+locker_id+"/submissions/" + id + "/undelete_submission",
            type: "post",
            data:{
                id : id,
                csrfmiddlewaretoken: $("#delete_undelete_form").find(
                    "input[name='csrfmiddlewaretoken']").val()
                },
            success: function(data) {
                // undeletes the submission and removes the class "deleted"
                $("#submission-list tr[data-id='"+id +"']").removeClass("deleted");
                $("#submission-list tr[data-id='"+id +"'] button[role='delete-submission']").html(
                    "Delete");
                // $("#submission-list tr[data-id='" + id +"'] td[name='date']").find("span:first").attr("data-timestamp", deleted_timestamp);
                 Submission.undeleteRequest = null;
                },
            error: function(jqXHR) {
                    console.error(
                        "Submission.undelete in Submission.js AJAX error: "
                    );
                }
            });
        Submission.undeleteRequest = null;
    }



    /**
     * Updates the deleted submission warning message
     *
     * Looks at the associated timestamp and converts it into the number of
     * days remaining
     *
     * @param  id  integer  an integer that references the submission id of
     *                      the entry to update
     * @return void
     */
    Submission.update_purge_warning = function (id)
    {
        console.log(id);
        var $element = $("tr[data-id='" + id + "']");
        console.log($element);
        var deleted_timestamp = $element.attr("data-deleted-timestamp");
        console.log(deleted_timestamp);
        $element.find("span.label").text(
            "Will be removed "
            + moment(deleted_timestamp).fromNow() + "."
        );
    }

}( window.Submission = window.Submission || {}, jQuery));



$(document).ready(function(id)
{
    // enable table sorting
    $('#submission-list').tablesorter();


    // handle the `select fields to display` button
    $("button[role='filter-results']").on("click", function (event)
    {
        $("#dialog-filter-results").modal('show');
    });


    /**
     * Enable/disable maintenance mode
     *
     * Shows/hides the deleted submissions and shows/hides the delete/undelete
     * buttons.
     */
    $("[name='maintenance-mode-toggle']").on("change", function (event)
    {
        if ($("[name='maintenance-mode-toggle']").prop("checked")) {
            $("body").addClass("js-show-deleted");
        } else {
            $("body").removeClass("js-show-deleted");
        }

        $("#submission-list tr.is-deleted").each(function() {
            Submission.update_purge_warning($(this).attr("data-id"));
        });
    });
    $("[name='maintenance-mode-toggle']").change();


    //changes the html and css of the button when clicked to 'delete' or 'undelete'
    // $("#submission-list").on("click","button[role='delete-submission']", function (event) {
    //     event.preventDefault();
    //     var id = $(this).closest("tr").attr("data-id");
    //     var locker_id = $(this).closest("table").attr("data-locker-id");
    //     if ($(this).html() == "Delete") {
    //         Submission.delete(locker_id, id);
    //         $(this).html("Undelete");
    //         $(this).removeClass("btn-danger").addClass("btn-success");
    //     } else {
    //         Submission.undelete(locker_id, id);
    //         $(this).removeClass("deleted");
    //         $("#submission-list tr[data-id='" + id +"'] td span.label").attr("data-timestamp","");
    //         $(this).removeClass("btn-success").addClass("btn-danger");
    //         $(this).html("Delete");
    //     }
    // });


});