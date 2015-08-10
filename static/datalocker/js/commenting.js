/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */
(function (Comment, $, undefined)
{
    // the AJAX objects that handles server communication
    Comment.addRequest;
    Comment.dataRequest;

    Comment.add = function () {
        var addUrl = $("#comment-form").attr("action");
        var comment = $("textarea#comment-text").val();
        Comment.addRequest = $.ajax({
            url: addUrl,
            type: "post",
            data: {
                comment: comment,
                csrfmiddlewaretoken: $("#comments-div").find(
                    "input[name='csrfmiddlewaretoken']").val()
                }
        });

        // Callback handler: success
        Comment.addRequest.done(function (response, textStatus, jqXHR) {
            if ($("#comment-list").length){
                $(".comment").remove();
            }
            $("#comment-list").append(Comment._build_comment_feed_entry(response));
            $("textarea#comment-text").val('');
            Comment.addRequest = null;
        });

        // Callback handler: failure
        Comment.addRequest.fail(function (jqXHR, errorThrown) {
            if (errorThrown != "abort") {
                console.error("Comment.add in commenting.js AJAX error");
            }
            Comment.addRequest = null;
        });
    }

    Comment._build_comment_feed_entry = function (comment) {
        return $(".media-list").append(
            $("<li />").attr("class","media comment"
                ).append(
                    $("<div />").attr("class", "media-left"
                    ).append(
                        $("<img />").attr("class","media-object"
                )).append(
                    $("<div />").attr("class", "media-body"
                        ).append(comment
                    ).append(
                        $("<div />").attr("class","single-comment-options pull-right"
                        ).append($("<a />").attr("href","#").html("Reply"))))));
    }

    Comment.build_comment_feed = function (comment) {
        var url = $("#comment-form").attr("data-url");
        // submit the request (if none are pending)
        if  (!Comment.dataRequest && url) {
            Comment.dataRequest = $.ajax({
                url: url,
                type: "get",
                cache: false
            });

            // callback handler: success
            Comment.dataRequest.done(function (response, textStatus, jqXHR) {
                var $comment_list = $("#comment-list");
                // clear the list
                //$comment_list.children().remove();
                // build the list of Comment
                $.each(response.comment, function (index, comment) {
                        $comment_list.append(Comment._build_comment_feed_entry(comment));
                });
                Comment.no_user_message();
                Comment.dataRequest = null;
            });

            // callback handler: failure
            Comment.dataRequest.fail(function (jqXHR, textStatus, errorThrown) {
                if  (errorThrown != "abort") {
                    console.error(
                        "Comment.build_comment_feed in commenting.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Comment.dataRequest = null;
            });
        }
    }

}( window.Comment = window.Comment || {}, jQuery));


$(document).ready(function() {
    //Appends the text from the box to the commenting feed
    $("button[role='add-comment']").on("click", function (event) {
        Comment.add();
    });
    url = $("#comment-form").attr("data-url");
    $("#comment-form").attr(
            "action", url);
    Comment.build_comment_feed();
});