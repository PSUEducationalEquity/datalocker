/* Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */

/**
 * Handle the discussion functionality for a submission
 */
(function (Discussion, $, undefined) {
    // the AJAX objects that handle the server communication
    Discussion.addRequest;
    Discussion.dataRequest;


    /**
     * Adds a comment or reply to the discussion
     *
     * @return  void
     */
    Discussion.add = function () {
        Comment.addRequest = $.ajax({
            url: $(".panel-discussion form").attr("action"),
            type: "post",
            data: {
                comment: $("textarea#comment-text").val(),
                csrfmiddlewaretoken: $(".panel-discussion form").find(
                    "input[name='csrfmiddlewaretoken']"
                ).val(),
            }
        }).done(function(response, textStatus, jqXHR) {
            var $discussion_tree = $(".panel-discussion .discussion-tree")
            if (response.parent_comment) {
                $discussion_tree.find(
                    "li[data-id='" + response.parent_comment + "'] .discussion-replies"
                ).prepend(Discussion._build_entry(response));
            } else {
                $discussion_tree.prepend(Discussion._build_entry(response));
            }
            $(".panel-discussion form textarea").val("");
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                console.error(
                    "Discussion.display in commenting.js AJAX error: "
                        + textStatus,
                    errorThrown
                );
            }
        }).always(function(jqXHR, textStatus, errorThrown) {
            $(".panel-discussion form input[type='submit']").prop("disabled", false);
            $(".panel-discussion form textarea").prop("disabled", false);
            Comment.addRequest = null;
        });
    }


    /**
     * Build a comment entry for the discussion tree
     *
     * Example Entry:
     *  <li class="media">
     *    <div class="media-left">
     *      <span class="media-object user-icon user-color-azure">PR</span>
     *    </div>
     *    <div class="media-body">
     *      <h4 class="media-heading">Paul Rentschler</h4>
     *      <p class="discussion-timestamp text-muted">10 minutes ago</p>
     *      <p class="discussion-comment">
     *        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
     *      </p>
     *      <div class="discussion-actions">
     *        <a href="#" role="discussion-reply">Reply</a>
     *        &#149;
     *        <a href="#" role="discussion-edit">Edit</a>
     *      </div>
     *    </div>
     *    <ul class="discussion-replies"></ul>
     *  </li>
     *
     * @param   object comment  an object that represents a comment
     * @return  object  an object that contains the HTML to display a comment
     */
    Discussion._build_entry = function (comment)
    {
        var $template = $('<li class="media" />').html(
            '<div class="media-left">' +
            '  <span class="media-object user-icon"></span>' +
            '</div>' +
            '<div class="media-body">' +
            '  <h4 class="media-heading"></h4>' +
            '  <p class="discussion-timestamp text-muted"></p>' +
            '  <p class="discussion-comment"></p>' +
            '  <div class="discussion-actions">' +
            '    <a href="#" role="discussion-reply">Reply</a>' +
            '    <span class="action-separator">&#149;</span>' +
            '    <a href="#" role="discussion-edit">Edit</a>' +
            '  </div>' +
            '</div>' +
            '<ul class="discussion-replies"></ul>'
        );

        var $entry = $template;
        $entry.attr("data-id", comment.id);
        $entry.find(".user-icon").addClass(comment.user.color).html(
            comment.user.first_name[0].toUpperCase()
            + comment.user.last_name[0].toUpperCase()
        );
        $entry.find("h4.media-heading").html(
            comment.user.first_name + " " + comment.user.last_name
        );
        $entry.find(".discussion-timestamp").attr(
            "data-timestamp",
            comment.timestamp
        ).html(moment(comment.timestamp).fromNow());
        $entry.find(".discussion-comment").html(comment.comment);
        if (!comment.is_editable) {
            $entry.find("[role='discussion-edit']").remove();
            $entry.find(".action-separator").remove();
        }
        if (comment.parent_comment) {
            $entry.find(".discussion-replies").remove();
        }
        return $entry;
    }


    /**
     * Display the discussion tree on the page
     *
     * @param
     * @return  void
     */
    Discussion.display = function ()
    {
        var url = $(".panel-discussion").attr("data-url");
        // submit the request (if none are pending)
        if  (!Discussion.dataRequest && url) {
            Discussion.dataRequest = $.ajax({
                url: url,
                type: "get",
                cache: false
            }).done(function(response, textStatus, jqXHR) {
                var $discussion_tree = $(".panel-discussion .discussion-tree");
                $discussion_tree.children("li").remove();
                $.each(response.discussion, function (index, comment) {
                    if (comment.parent_comment) {
                        $discussion_tree.find(
                            "li[data-id='" + comment.parent_comment + "'] .discussion-replies"
                        ).append(Discussion._build_entry(comment))
                    } else {
                        $discussion_tree.append(Discussion._build_entry(comment));
                    }
                });
                Discussion.dataRequest = null;
            }).fail(function(jqXHR, textStatus, errorThrown) {
                if  (errorThrown != "abort") {
                    console.error(
                        "Discussion.display in commenting.js AJAX error: "
                            + textStatus,
                        errorThrown
                    );
                }
                Discussion.dataRequest = null;
            });
        }
    }

}(window.Discussion = window.Discussion || {}, jQuery))






/*
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
        }).done(function(response, textStatus, jqXHR) {
            $("#comment-list").append(Comment._build_comment_feed_entry(response));
            $("textarea#comment-text").val('');
            Comment.addRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
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
        }).done(function(response, textStatus, jqXHR) {
            $("#comment-list").append(Comment._build_comment_feed_entry(response));
            $("#comment-list li[data-id='" + id + "'] textarea").val('');
            $("#comment-list li[data-id='" + id + "'] div.comment-reply-entry").addClass("hide");
            $("#comment-list li[data-id='" + id + "'] button[role='comment-reply']").show();

            Comment.addRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                console.error("Comment.add in commenting.js AJAX error");
            }
            Comment.addRequest = null;
        });
    }

    Comment.edit = function (id) {
        var addUrl = $("#comment-form").attr("action");
        addUrl += "Edit";
        var comment = $("#comment-list li[data-id='" + id + "'] textarea.edit").val();
        Comment.addRequest = $.ajax({
            url: addUrl,
            type: "post",
            data: {
                comment: comment,
                id: id,
                csrfmiddlewaretoken: $("#comments-div").find(
                    "input[name='csrfmiddlewaretoken']").val()
                }
        }).done(function(response, textStatus, jqXHR) {
            $("#comment-list li[data-id='" + id + "'] textarea").val('');
            $("#comment-list li[data-id='" + id + "'] div.comment-reply-entry").addClass("hide");
            $("#comment-list li[data-id='" + id + "'] button[role='comment-reply']").show();
            $("#comment-list li[data-id='" + id + "'] button[role='comment-edit']").show();

            Comment.addRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                console.error("Comment.add in commenting.js AJAX error");
            }
            Comment.addRequest = null;
        });
    }

    Comment._build_comment_feed_entry = function (comment) {
        var user = comment.user;
        var username = user.replace(/[0-9]+/g, '');
        var initials = username.substring(1,0) + username.slice(-1);
        var $icon = $("<div />").addClass("media-left").append(
                        $("<span />").addClass("media-object " + comment.color).html(
                            initials.toUpperCase())
                    );
        var $body = $("<div />").addClass("media-body").append(
            $("<span />").addClass("comment").html(comment.comment));
        if ($("#current-username").html() == user) {
            $body.append(
                    $("<button />").html("Edit").addClass(
                        "btn btn-link btn-xs"
                    ).attr("role", "comment-edit")
                ).append(
                    $("<button />").html("Reply").addClass(
                        "btn btn-link btn-xs hide"
                    ).attr("role", "submit-edit"));
            }
        if (comment.parent_comment == null){
            $body.append(
                $("<button />").html("Reply").addClass(
                        "btn btn-link btn-xs"
                    ).attr("role", "comment-reply")).append(
                $("<div />").addClass("comment-actions"
            ).append(
                $("<ul />").addClass("media-list")
            ).append(
                $("<div />").addClass("comment-reply-entry hide").append(
                    $("<textarea />").attr("name", "comment-reply").addClass(
                        "comment-reply-textarea")
                ).append(
                    $("<button />").html("Reply").addClass(
                        "btn btn-link btn-xs"
                    ).attr("role", "comment-add")
                ))
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
            }).done(function(response, textStatus, jqXHR) {
                var $comments_list = $("#comment-list");
                // build the list of Comment
                $.each(response.comments, function (index, comment) {
                    $comments_list.append(Comment._build_comment_feed_entry(comment));
                    });
                $.each(response.replies, function (index, reply) {
                    $comments_list.append(Comment._build_comment_feed_entry(reply));
                    });
                Comment.dataRequest = null;
            }).fail(function(jqXHR, textStatus, errorThrown) {
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
*/

$(document).ready(function() {
    Discussion.display();

    // Handle adding a new comment
    $(".panel-discussion form").on("submit", function (event) {
        event.preventDefault();
        var $textarea = $(this).find("textarea");
        if ($textarea.val() != "") {
            $(this).find("input[type='submit']").prop("disabled", true);
            $textarea.prop("disabled", true);
            Discussion.add();
        }
    });

    // Shift-enter in TextArea should submit the form
    $(".panel-discussion textarea").on("keypress", function (event) {
        if (event.keyCode == 13 && event.shiftKey) {
            event.preventDefault();
            $(this).closest("form").submit();
        }
    });




/*
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

    $("#comment-list").on("click", "button[role='comment-edit']", function (event) {
        var id = $(this).closest("li").attr("data-id");
        var text = $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body span.comment").html();
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("button[role='comment-reply']").hide();
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body span.comment").first().replaceWith("<textarea class='edit' />");
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body textarea").val(text);
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("button[role='submit-edit']").removeClass("hide");
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("button[role='submit-edit']").show();
        $(this).hide();

    });

    $("#comment-list").on("click", "button[role='submit-edit']", function (event) {
        var id = $(this).closest("li").attr("data-id");
        var html = $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body textarea").val();
        if ($("#comment-list").find("li[data-id='" + id + "']").find("div.media-body textarea.edit").val() != '') {
            Comment.edit(id);
        }
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body textarea").first().replaceWith("<span class='comment' />");
        $("#comment-list").find("li[data-id='" + id + "']"
            ).find("div.media-body span").first().html(html);
        $("#comment-list li[data-id='" + id + "'] button[role='comment-reply']").show();
        $("#comment-list li[data-id='" + id + "'] button[role='comment-edit']").show();
        $(this).hide();
    });
*/
});
