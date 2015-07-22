$(document).ready(function(){
    $('#archive-button').click(function(){
        var id = $(this).closest("tr").attr("data-id");
        $.ajax({
            url: '/datalocker/' + id + '/archive',
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
            }
        });
    });
    $('#unarchive-button').click(function(){
        var id = $(this).closest("tr").attr("data-id");
        $.ajax({
            url: '/datalocker/' + id + '/unarchive',
            type: 'POST',
            data: {
                id: id,
                csrfmiddlewaretoken: $("#dialog-edit-users").find("input[name='csrfmiddlewaretoken']").val()
            }
        });
    });
});