/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */


    /**
     * Delete's and Undelete's submissions
     *
     * @return     void
     * @author     Hunter Yohn  <hay110@psu.edu>
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
            url: '/datalocker/'+locker_id+'/submissions/' + id + '/delete_submission',
            type: "post",
            data:{
                id: id,
                csrfmiddlewaretoken: $("#delete_undelete_form").find(
                   "input[name='csrfmiddlewaretoken']").val()
                },
            success: function(data) {
                // deletes the submission and adds the class "deleted"
                $("#submission-list tr[data-id='" + id +"']").addClass('deleted submission-deleted');
                $("#submission-list tr[data-id='" + id +"'] button[role='delete-submission']").html(
                    'Undelete');
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
            url: '/datalocker/'+locker_id+'/submissions/' + id + '/undelete_submission',
            type: "post",
            data:{
                id : id,
                csrfmiddlewaretoken: $("#delete_undelete_form").find(
                    "input[name='csrfmiddlewaretoken']").val()
                },
            success: function(data) {
                // undeletes the submission and removes the class "deleted"
                $("#submission-list tr[data-id='"+id +"']").removeClass('deleted');
                $("#submission-list tr[data-id='"+id +"'] button[role='delete-submission']").html(
                    'Delete');
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

    }( window.Submission = window.Submission || {}, jQuery));


$(document).ready(function()
{
    $("#submission-list").on("click","button[role='delete-submission']", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        var locker_id = $(this).closest("table").attr("data-locker-id");
        if ($(this).html() == "Delete") {
            Submission.delete(locker_id, id);
            $(this).html('Undelete');
            $(this).removeClass("btn-danger").addClass("btn-success");
        } else {
            Submission.undelete(locker_id, id);
            $(this).removeClass("deleted")
            $(this).removeClass("btn-success").addClass("btn-danger");
            $(this).html('Delete');
        }
    });
    $(".onoffswitch").on("click", function (event) {
        $("button[role='delete-submission']").toggle();
        $(".deleted").toggle();

    });


});