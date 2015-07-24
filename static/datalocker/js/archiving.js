//Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.

/**
 * archiving script is used to simulate a post on a button click on the Locker
 * listing table on the index.html page. The button with the id="archive-button"
 * is the button run by the top onClick function. The button with the id="unarchive-button"
 * is the button run by the second onClick function.
 */
(function (Locker, $, undefined)
{

    Locker.archive = function(id){
        $.ajax({
            url: '/datalocker/' + id + '/archive',
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
            },
            success: function(data){
                $("#locker-list tr[data-id='" + id + "']").addClass('archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html('Unarchive Locker');
            }
        });
    }

    Locker.unarchive = function(id) {
        $.ajax({
            url: '/datalocker/' + id + '/unarchive',
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
            },
            success: function(data){
                $('#locker-list tr[data-id=' + id + "]").removeClass('archived');
                $("#locker-list tr[data-id='" + id + "'] button[role='archive-locker']").html('Archive Locker');
            }
        });
    }
}( window.Locker = window.Locker || {}, jQuery));

$(document).ready(function(){
    $("[role='archive-locker']").on("click", function (event){
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        if ($(this).html() == "Archive Locker"){
            Locker.archive(id);
        }
        else {
            Locker.unarchive(id);
        }
    });
    $("#show-hide-archived").click(function() {
      $('.archived').toggle();
      if ($(this).html() == "Show Archived Lockers"){
            $(this).addClass('active');
            $(this).html('Hide Archived Lockers');
        }
        else {
            $(this).removeClass('active');
            $(this).html('Show Archived Lockers');
        }
    });
});