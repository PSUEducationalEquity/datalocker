/**
 * Select-all script to use a single checkbox to select or deselect every checkbox
 * within the sepcified list. To use this feature you must add a role="select-all"
 * to the checkbox you want to be considered the select all checkbox. Then you have
 * add a data-target attribute equal to the id attribute of the list of checkboxes.
 *
 */
$(document).ready(function() {
    $("[role='select-all']").on("click", function (event) {  //on click
        var target = $(this).attr("data-target");
        $("#" + target + " input[type='checkbox']").prop("checked", $(this).prop("checked"));
    });
});