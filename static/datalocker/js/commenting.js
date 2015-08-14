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
    Comment.addReply = function (id) {
        var addUrl = $("#comment-form").attr("action");
        addUrl += "Reply";
        var comment = $("#comment-list li[data-id='" + id + "'] textarea").val();
        Comment.addRequest = $.ajax({
            url: addUrl,
            type: "post",
            data: {
                comment: comment,
                parent_comment: id,
                csrfmiddlewaretoken: $("#comments-div").find(
                    "input[name='csrfmiddlewaretoken']").val()
                }
        });

        // Callback handler: success
        Comment.addRequest.done(function (response, textStatus, jqXHR) {
            $("#comment-list").append(Comment._build_comment_feed_entry(response));
            $("#comment-list li[data-id='" + id + "'] textarea").val('');
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
        var user = comment.user;
        var username = user.replace(/[0-9]+/g, '');
        var $icon = $("<div />").addClass("media-left").append(
                        $("<span />").addClass("media-object brown").html(
                            username)
                    );
        var $body = $("<div />").addClass("media-body").html(comment.comment);
        if (comment.parent_comment == null){
            $body.append(
                $("<div />").addClass("comment-actions").append(
                    $("<button />").html("Reply").addClass(
                        "btn btn-link btn-xs"
                    ).attr("role", "comment-reply")
                )
            ).append(
                $("<ul />").addClass("media-list")
            ).append(
                $("<div />").addClass("comment-reply-entry hide").append(
                    $("<textarea />").attr("name", "comment-reply")
                ).append(
                    $("<button />").html("Add").addClass(
                        "btn btn-link btn-xs"
                    ).attr("role", "comment-add")
                )
            );
        }

        var $entry = $("<li />").attr("data-id", comment.id).addClass(
            "media comment"
        ).append($icon).append($body);

        var $parent = $("#comment-list");
        if (comment.parent_comment > 0){
            $parent = $("#comment-list li[data-id='" + comment.parent_comment + "'] ul");
        }
        $parent.append($entry);
    }

    Comment.build_comment_feed = function (comments, replies) {
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
                $.each(response.replies, function (index, reply) {
                    $comments_list.append(Comment._build_comment_feed_entry(reply));
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

    $("#comment-list").on("click", "button[role='comment-reply']", function (event) {
        var id = $(this).closest("li").attr("data-id");
        $(this).closest("li").find(".comment-reply-entry").removeClass("hide");
        $(this).closest("li").find(".comment-reply-entry textarea").focus();
        $(this).hide();
    });

    $("#comment-list").on("click", "button[role='comment-add']", function (event) {
        var id = $(this).closest("li").attr("data-id");
        var $textarea = $(this).closest("li").find(".comment-reply-entry textarea");
        if ($textarea.val() != '') {
            Comment.addReply(id);
        }
    });
});