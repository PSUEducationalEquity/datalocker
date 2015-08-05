/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */

/**
 * Select-all script uses a single checkbox to select or deselect every checkbox
 * within the sepcified list. To use this feature you must add a role="select-all"
 * to the checkbox. Add a data-target="checkboxlist id's"
 */

$(document).ready(function() {
    $("body").on("click", "[role='select-all']", function (event)
    {
        var target = $(this).attr("data-target");
        $("#" + target + " input[type='checkbox']").prop(
        	"checked", $(this).prop("checked"));
    });

    $("[role='select-all']").each(function () {
        var $target = $("#" + $(this).attr("data-target"));
        var checked_count = $target.find("input[type='checkbox']:checked").length;
        var checkbox_count = $target.find("input[type='checkbox']").length;
        console.log($(this));
        console.log($target);
        console.log(checked_count);
        console.log(checkbox_count);
        if (checkbox_count == checked_count) {
            $(this).prop("checked", true);
        }
    });
});