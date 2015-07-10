(function (Locker, $, undefined)
{
    // the AJAX objects that handles server communication
    Locker.dataRequest;
    Locker.toggleRequest;
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
            type: "get",
            cache: flase
            data: {
                email: 'email'
                CSRF: 
            }
        });

        // callback handler: success
        Locker.addRequest.done(function (response, textStatus, jqXHR) {
            if (response.result) {
                $("#add-tag-name").val("");
                Locker.update();
            } else if (typeof(response) == "object") {
                // this was a group add
                $("#add-tag-name").val("");
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





    Locker._build_list = function (data)




    /**
     * Creates the tag entries in the list of Locker
     *
     * @param       object data  an object containing a JSON list of Locker
     * @return      void
     * @access      private
     * @author      Paul Rentschler <par117@psu.edu>
     * @since       18 April 2014
     */
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



    /**
     * Handles errors from the server-side
     *
     * @param       object jqXHR  an object containing the AJAX response
     * @return      void
     * @access      private
     * @author      Paul Rentschler <par117@psu.edu>
     * @since       17 September 2014
     */
    Locker.errorHandler = function (jqXHR, action)
    {
        var msg = "<strong>Oops!</strong> An error occurred while "
            + action + " the tag.";
        if (jqXHR.responseJSON.msg) {
            msg += " " + jqXHR.responseJSON.msg;
        }
        userMessage.add(msg, 'danger', true, 10);
        $(window).scrollTop(0);
    }

$(document).ready(function ()
{
    
    // add a tag when pressing enter in the input field
     $("[role='edit-users']").on("click", function (event) {  //on click      
        $('#modalUsers').modal('show');

})