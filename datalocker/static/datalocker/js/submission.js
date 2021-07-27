/**
 * Submission related actions
 */
(function (Submission, $, undefined)
{
    // the AJAX objects that handles server communication
    Submission.deleteRequest;
    Submission.undeleteRequest;



    /**
     * Mark a submission as deleted
     *
     * @param   integer id  an integer indicating the submission id to delete
     * @return  void
     */
    Submission.delete = function (id)
    {
        var delete_url = $("#submission-list").attr("data-delete-url");
        Submission.deleteRequest = $.ajax({
            url: delete_url.replace("/0/", "/" + id + "/"),
            type: "post",
            data: {
                id: id,
                csrfmiddlewaretoken: $("#submission-list").attr("data-csrf-token")
            },
        }).done(function(response, textStatus, jqXHR) {
            $("#submission-list tr[data-id='" + response.id +"']").attr(
                "data-purge-timestamp",
                response.purge_timestamp
            ).addClass("is-deleted");
            Submission.update_purge_warning(response.id);
            Submission.deleteRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.error(
                "Submission.delete in Submission.js AJAX error:",
                errorThrown,
                jqXHR.responseText
            );
            Submission.deleteRequest = null;
        });
    }



    /**
     * Mark a submission as undeleted
     *
     * @param   integer id  an integer indicating the submission id to undelete
     * @return  void
     */
    Submission.undelete = function (id)
    {
        var delete_url = $("#submission-list").attr("data-undelete-url");
        Submission.undeleteRequest = $.ajax({
            url: delete_url.replace("/0/", "/" + id + "/"),
            type: "post",
            data: {
                id: id,
                csrfmiddlewaretoken: $("#submission-list").attr("data-csrf-token")
            },
        }).done(function(response, textStatus, jqXHR) {
            $("#submission-list tr[data-id='" + response.id +"']").attr(
                "data-purge-timestamp",
                ""
            ).removeClass("is-deleted");
            Submission.undeleteRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
            console.error(
                "Submission.undelete in Submission.js AJAX error:",
                errorThrown,
                jqXHR.responseText
            );
            Submission.undeleteRequest = null;
        });
    }



    /**
     * Updates the deleted submission warning message
     *
     * Looks at the associated timestamp and converts it into the number of
     * days remaining
     *
     * @param   integer id  an integer indicating the submission id to update
     * @return  void
     */
    Submission.update_purge_warning = function (id)
    {
        var $element = $("tr[data-id='" + id + "']");
        var purge_timestamp = $element.attr("data-purge-timestamp");
        $element.find("span.label").text(
            "Will be removed "
            + moment(purge_timestamp).fromNow() + "."
        );
    }

}( window.Submission = window.Submission || {}, jQuery));



$(document).ready(function(id)
{
    // enable table sorting
    //$('#submission-list').tablesorter();


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
            $("body").toggleClass("js-show-deleted", true);
        } else {
            $("body").toggleClass("js-show-deleted", false);
        }

        $("#submission-list tr.is-deleted").each(function() {
            Submission.update_purge_warning($(this).attr("data-id"));
        });
    });
    $("[name='maintenance-mode-toggle']").change();


    // Handle the delete submission buttons
    $("[role='delete-submission']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Submission.delete(id);
    });


    // Handle the undelete submission buttons
    $("[role='undelete-submission']").on("click", function (event) {
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Submission.undelete(id);
    });
});
