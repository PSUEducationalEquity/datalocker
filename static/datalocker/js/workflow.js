/**
 * Handle manipulating the workflow state of a submission
 *
 * @return     void
 */
(function (Workflow, $, undefined)
{
    // the AJAX objects that handles server communication
    Workflow.request;


    /**
     * Change the workflow state
     *
     * @param   string value  a string containing the value to change the
     *                        workflow state to
     * @return  void
     */
    Workflow.change = function (value)
    {
        var csrf_token = $(".panel-workflow form").find(
            "input[name='csrfmiddlewaretoken']"
        ).val();
        if (!Workflow.request) {
            Workflow.request = $.ajax({
                url: $(".panel-workflow form").attr("action"),
                type: "post",
                data: {
                    'workflow-state': value,
                    'csrfmiddlewaretoken': csrf_token,
                }
            }).done(function(response, textStatus, jqXHR) {
                $(".js-workflow-current-state").html(response.state);
                Workflow.request = null;

            }).fail(function(jqXHR, textStatus, errorThrown) {
                if (jqXHR.status == 400) {
                    UserMessage.add(jqXHR.responseText, "danger", 5);
                } else if (jqXHR.status == 404) {
                    UserMessage.add(
                        "<strong>Oops!</strong> the workflow state for this "
                        + "submission could not be updated.",
                        "danger",
                        7
                    );
                } else if (errorThrown != "abort") {
                    console.error(
                        "Workflow.change in workflow.js AJAX error: "
                        + textStatus,
                        errorThrown
                    );
                }
                Workflow.request = null;
            });
        }
    }

}( window.Workflow = window.Workflow || {}, jQuery));


$(document).ready(function ()
{
    // handle a change to the workflow state
    $(".panel-workflow select#workflow-state").on("change", function () {
        Workflow.change($(this).val());
        $(this).val("0");
    });

    // prevent a form submission as it's not necessary
    $(".panel-workflow form").on("submit", function (event) {
        event.preventDefault();
    });
});
