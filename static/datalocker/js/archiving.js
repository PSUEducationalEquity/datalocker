//Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved.

/**
 * archiving script is used to simulate a post on a button click on the Locker
 * listing table on the index.html page. The button with the id="archive-button"
 * is the button run by the top onClick function. The button with the id="unarchive-button"
 * is the button run by the second onClick function.
 */
Locker.archive = function(id){
    $.ajax({
        url: '/datalocker/' + id + '/archive',
        type: 'POST',
        data: {
            id: id,
            csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
        },
        success: function(data){
            $('#locker-list tr[data-id=' + id + "]").remove();
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
            $('#locker-list tr[data-id=' + id + "]").remove();
        }
    });
}

$(document).ready(function(){
    $('#archive-button').click(function(){
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Locker.archive(id);

    });
    $('#unarchive-button').click(function(){
        event.preventDefault();
        var id = $(this).closest("tr").attr("data-id");
        Locker.unarchive(id);
    });
});