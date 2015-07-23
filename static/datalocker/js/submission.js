(function (Submission, $, undefined)
{
    // the AJAX objects that handles server communication
    Submission.dataRequest;   
    Submission.addRequest;
    Submission.deleteRequest;    

    /**
     * Delete's and Undelete's submissions     
     */



Submission.delete = function (locker_id, id)
{
    // submit the request
   
    
    Submission.addRequest = $.ajax({
        url: '/datalocker/'+locker_id+'/submissions/' + id + '/delete_submission',
        type: "post",
        data: {
            id: id,
            csrfmiddlewaretoken: $("#delete_undelete_form").find("input[name='csrfmiddlewaretoken']").val()
              },
        success: function(data){
            $("#submission-list tr[data-id='" + id +"']").addClass('deleted');
            $("#submission-list tr[data-id='" + id +"'] button[role='delete']").html('Undelete');      

        }
    });      
}


Submission.undelete = function (locker_id, id)
{
    // submit the request   

    Submission.undeleteRequest = $.ajax({
        url: '/datalocker/'+locker_id+'/submissions/' + id + '/undelete_submission',
        type: "post",      
        data: {
            id : id,
            csrfmiddlewaretoken: $("#delete_undelete_form").find("input[name='csrfmiddlewaretoken']").val()
              },
        success: function(data){
            $("#submission-list tr[data-id='"+id +"']").removeClass('deleted');
            $("#submission-list tr[data-id='"+id +"'] button[role='delete']").html('Delete');      

        }     
    });    
}
}( window.Submission = window.Submission || {}, jQuery));


$(document).ready(function (){   
   
    $("[role='delete']").on("click", function (event){
        event.preventDefault();        
        var id = $(this).closest("tr").attr("data-id");
        var locker_id = $(this).closest("tr").attr("locker-id");       
        if ($(this).html() == "Delete"){
            Submission.delete(locker_id, id );
            $(this).html('Undelete');
        }
        else {
            Submission.undelete(locker_id, id);  
             $(this).html('Delete');          
        }
     });

    $(".onoffswitch-checkbox").on("click", function (event) {       
        var id = $(this).closest("tr").attr("data-id");
      $(".delete-button").toggle();
      $(".deleted").toggle();
    });
});
