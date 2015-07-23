(function (Submission, $, undefined)
{
    // the AJAX objects that handles server communication
    Submission.dataRequest;   
    Submission.addRequest;
    Submission.deleteRequest;    

    /**
     * Delete's and Undelete's submissions     
     */



Submission.delete = function ()
{
    // submit the request
    var id = $("tr").attr("data-id");
    var deleteUrl = $("#delete_undelete_form").attr("data-url");           
    Submission.addRequest = $.ajax({
        url: deleteUrl,
        type: "post",
        data: {
            id: id,
            csrfmiddlewaretoken: $("#delete_undelete_form").find("input[name='csrfmiddlewaretoken']").val()
              },
        success: function(data){
            $("#submission-list tr[data-id'"id +"']").addClass('delete');
            $("#submission-list tr[data-id'"+id +"'] button[role='delete']").html('Undelete');      

        }
    });      
}


Submission.undelete = function ()
{
    // submit the request
    var undeleteUrl =  $("#existing-users").attr("data-delete-url");
    var id = $("tr").attr("data-id");

    Submission.undeleteRequest = $.ajax({
        url: undeleteUrl.replace("/0/", "/" + Submission_id +"/"),
        type: "post",      
        data: {
            id : id,
            csrfmiddlewaretoken: $("#delete_undelete_form").find("input[name='csrfmiddlewaretoken']").val()
              },
        success: function(data){
            $("#submission-list tr[data-id'"+id +"']").removeClass('delete');
            $("#submission-list tr[data-id'"+id +"'] button[role='delete']").html('Delete');      

        }     
    });    
}
}( window.Submission = window.Submission || {}, jQuery));


$(document).ready(function (){   
    $('#delete').click(function(){
    $("[role='delete']").on("click", function (event){
        event.preventDefault();        
        Submission.delete(id);
        if ($(this).html() == "Delete"){
            Submission.delete(id);
        }
        else {
            Submission.undelete(id);
        }
     });
    $('#unarchive-button').click(function(){
        event.preventDefault();
        Submission.unarchive(id);
});
    $(".onoffswitch-checkbox").on("click", function (event) {       
      $("#delete").toggle();
    });
  

});
