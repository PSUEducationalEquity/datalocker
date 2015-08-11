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
            $("<li />").attr("data-id", comment.id
                ).addClass("media comment"
                ).append(
                    $("<div />").addClass("media-left"
                    ).append(
                        $("<img />").addClass("media-object"
                ))).append(
                    $("<div />").addClass("media-body"
                        ).html(comment.comment
                    ).append(
                        $("<div />").addClass("single-comment-options pull-right"
                        ).append($("<button />").html("Reply"
                            ).attr("data-id", comment.id
                            ).attr("role", "reply"
                            ).addClass("btn btn-link"))
                )).append(
                    $("<textarea />").addClass("comment-reply"
                        ).attr("id", comment.id
                        ).attr("data-id", comment.id)));
    }

    Comment.build_comment_feed = function (comments) {
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
                var $comments_list = $("#comment-list");
                // build the list of Comment
                $.each(response.comments, function (index, comment) {
                        $comments_list.append(Comment._build_comment_feed_entry(comment));
                });
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
    Comment.build_comment_feed();

    //Appends the text from the box to the commenting feed
    $("button[role='add-comment']").on("click", function (event) {
        if ($("#comment-text").val() != '') {
            Comment.add();
        }
    });

    $("#comment-list").on("click", "button[role='reply']", function (event) {
        var id = $(this).attr("data-id");
        $("textarea#" + id).show();
    });
});