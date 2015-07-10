(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;   
    Locker.addRequest;


    /**
     * Adds a new tag to the student via AJAX
     *
     * @return      void
     * @access      private
     * @author      Paul Rentschler <par117@psu.edu>
     * @since       21 March 2014
     */
Locker.add = function ()
{
    // submit the request
    var email = $("#email").val();
    var addUrl = $("#tag-list").attr("data-url")           
    Locker.addRequest = $.ajax({
        url: addUrl,
        type: "post",
        data: {
            email: 'email'
            //crsf: 
              }
    });

    // callback handler: success
    Locker.addRequest.done(function (response, textStatus, jqXHR) {
        if (response.result) {
            $("#email").val("");
            Locker.update();
        } else if (typeof(response) == "object") {
            // this was a group add
            $("#email").val("");
            Locker.buildList(response);
        }
        Locker.addRequest = null;
    });

    // callback handler: failure
    Locker.addRequest.fail(function (jqXHR, textStatus, errorThrown) {
        if (errorThrown != "abort") {
            if (jqXHR.status == 400 || jqXHR.status == 404) {
                Locker.errorHandler(jqXHR, 'adding');

            } else {
                console.error(
                    "Locker.add in Locker.js AJAX error: "
                        + textStatus,
                    errorThrown
                );
            }
        }
        Locker.addRequest = null;
    });
}

Locker.delete = function ()
{
    // submit the request
    var email = $("#email").val();
    var deleteUrl = $("#tag-list").attr("data-url")           
    Locker.deleteRequest = $.ajax({
        url: deleteUrl,
        type: "post",      
        data: {
            id: 'id'
          //  CSRF: 
        }
    });

    // callback handler: success
    Locker.deleteRequest.done(function (response, textStatus, jqXHR) {
        if (response.result) {
            $("#email").val("");
            Locker.update();
        } else if (typeof(response) == "object") {
            // this was a group add
            $("#email").val("");
            Locker.buildList(response);
        }
        Locker.deleteRequest = null;
    });

    // callback handler: failure
    Locker.deleteRequest.fail(function (jqXHR, textStatus, errorThrown) {
        if (errorThrown != "abort") {
            if (jqXHR.status == 400 || jqXHR.status == 404) {
                Locker.errorHandler(jqXHR, 'adding');

            } else {
                console.error(
                    "Locker.add in Locker.js AJAX error: "
                        + textStatus,
                    errorThrown
                );
            }
        }
        Locker.deleteRequest = null;
    });
}



//     Locker._build_list = function (data)
// $.each(json, function(key, value){
//    $("ul").append('<li>'+value+'</div>');





  
     
Locker.buildList = function (data)
{
    var count = 0;
    var $tagList = $("#tag-list");

    // clear the list
    $tagList.children().remove();

    // build the list of Locker
    $.each(data, function (index, entry) {
        var $item = $("<a />").attr("href", "#").text(entry.name);
        if (entry.description != "") {
            $item.attr("title", entry.description);
        }
        if (entry.active) {
            $item.addClass("active");
        }
        if (!entry.user) {
            $item.append(
                $("<i />").addClass(
                    "global-indicator fo-icon-globe"
                ).attr("title", "Global tag").append(
                    $("<span />").addClass("sr-only").text("Global tag")
                )
            );
        }
        $item.append(
            $("<i />").addClass(
                "pull-right active-indicator fo-icon-ok"
            ).append(
                $("<span />").addClass("sr-only").text("Selected")
            )
        );
        $tagList.append(
            $("<li />").attr("data-id", entry.id).append(
                $item
            )
        );
    });
}    
   
Locker.update = function ()
    {
        // get the url to use
        var url = $("#tag-list").attr("data-url") + "/list";
        if ($("#tag-list").length === 0) {
            url = false;
        }

        // submit the request (if none are pending)
        if (!Locker.dataRequest && url) {
            Locker.dataRequest = $.ajax({
                url: url,
                type: "get",
                cache: false
            });

            // callback handler: success
            Locker.dataRequest.done(function (response, textStatus, jqXHR) {
                Locker.buildList(response);
                Locker.dataRequest = null;
            });

            // callback handler: failure
            Locker.dataRequest.fail(function (jqXHR, textStatus, errorThrown) {
                if (errorThrown != "abort") {
                    console.error(
                        "Locker.dataRequest in tagging.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Locker.dataRequest = null;
            });
        }
    }
}( window.Locker = window.Locker || {}, jQuery));



$(document).ready(function (){
    //Opens the users modal dialog
    $("button[role='edit-users']").on("click", function (event){
        $("#dialog-edit-users").modal('show');
    });


     //Opens the edit lockers modal dialog
    $("button[role='edit-locker']").on("click", function (event){
        $("#dialog-edit-locker").modal('show');
    });



});
