//Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.

/**
 * Select-all script to use a single checkbox to select or deselect every checkbox
 * within the sepcified list. To use this feature you must add a role="select-all"
 * to the checkbox you want to be considered the select all checkbox. Then you have
 * add a data-target attribute equal to the id attribute of the list of checkboxes.
 */

$(document).ready(function() {
   $("body").on("click", "[role='select-all']", function (event)  
    {  
        var target = $(this).attr("data-target");
        $("#" + target + " input[type='checkbox']").prop("checked", $(this).prop("checked"));
    });

    if ($('.checkbox-inputs:checked').length == $('.checkbox-inputs').length){
        $('#fields-select-all').prop("checked", true);
    }
});