
/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */


  /**
   * Changes the workflow state for the submisison
   *
   * @return     void
   * @author     Hunter Yohn  <hay110@psu.edu>
  */


(function (Submission, $, undefined)
{
    // the AJAX objects that handles server communication
    Submission.workflowRequest;


    Submission.changeWorkflowState = function () {
        var changeWorkflowStateUrl = $("#dialog-edit-users form").attr("action");
        Submission.workflowRequest = $.ajax({
            url: changeWorkflowStateUrl,
            type: "post",
            data: {
                email: email,
                csrfmiddlewaretoken: $("#dialog-edit-locker").find(
                    "input[name='csrfmiddlewaretoken']").val()
                }
        });

        // callback handler: success
        Submission.workflowRequest.done(function (response, textStatus, jqXHR) {

            Submission.workflowRequest = null;
        });

        // callback handler: failure
        Submission.workflowRequest.fail(function (jqXHR, errorThrown) {
            if (errorThrown != "abort") {
                console.error("Locker.add in Locker.js AJAX error");
            }
            Submission.workflowRequest = null;
        });
    }
}( window.Locker = window.Locker || {}, jQuery));

$(document).ready(function () {

    $('#discussion-options').hide();
    $('select[id=states]').change( function(){
        var newText = $('option:selected',this).text();
          $('.state-status').text(" "+ newText);
        }
    );
    $('#enable-workflow').change(function(){
        if (this.checked) {
            $('#locker-options').show();
        } else {
            $('#locker-options').hide();
        }
    });
    $('#enable-discussion').change(function(){
        if (this.checked) {
            $('#discussion-options').show();
        } else {
            $('#discussion-options').hide();
        }
    });
    (function() {
        var boxes = document.querySelectorAll("input[type='checkbox']");
        for (var i = 0; i < boxes.length; i++) {
            var box = boxes[i];
            if (box.hasAttribute("store")) {
                setupBox(box);
            }
    }

    function setupBox(box) {
        var storageId = box.getAttribute("store");
        var oldVal    = localStorage.getItem(storageId);
        console.log(oldVal);
        box.checked = oldVal === "true" ? true : false;

        box.addEventListener("change", function() {
            localStorage.setItem(storageId, this.checked);
        });
    }
})();
});