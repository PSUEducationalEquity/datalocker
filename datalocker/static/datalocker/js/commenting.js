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
     * @access  public
     * @param   string  comment    a string containing the comment text
     * @param   integer parent_id  an integer indicating the parent id for this
     *                             comment (optional)
     * @return  void
     */
    Discussion.add = function (comment, parent_id)
    {
        var form_data = {
            comment: comment,
            csrfmiddlewaretoken: $(".panel-discussion form:first").find(
                "input[name='csrfmiddlewaretoken']"
            ).val(),
        }
        if (typeof parent_id !== "undefined" && parent_id != "") {
            form_data['parent'] = parseInt(parent_id);
        }
        Comment.addRequest = $.ajax({
            url: $(".panel-discussion form:first").attr("action"),
            type: "post",
            data: form_data,
        }).done(function(response, textStatus, jqXHR) {
            var $discussion_tree = $(".panel-discussion .discussion-tree")
            if (response.parent) {
                var $parent = $discussion_tree.find(
                    "li[data-id='" + response.parent + "']"
                );
                $parent.find(".discussion-replies").prepend(
                    Discussion._build_entry(response)
                );
                $("#discussion-reply-active-form").remove();
                $("html, body").animate({
                    scrollTop: $parent.offset().top
                }, 1000);
            } else {
                $discussion_tree.prepend(Discussion._build_entry(response));
                $(".panel-discussion form:first textarea").val("");
            }
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if (errorThrown != "abort") {
                console.error(
                    "Discussion.add in commenting.js AJAX error:",
                    errorThrown,
                    jqXHR.responseText
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
     * @access  private
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
            '  <div class="discussion-actions hidden-print">' +
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
        $entry.find(".discussion-comment").html(
            comment.comment.replace(/\n/g, "<br>")
        );
        if (!comment.editable) {
            $entry.find("[role='discussion-edit']").remove();
            $entry.find(".action-separator").remove();
        }
        if (comment.parent) {
            $entry.find(".discussion-replies").remove();
        }
        return $entry;
    }


    /**
     * Closes/removes the edit comment UI
     *
     * @access  public
     * @param   object comment  an object that represents the comment being edited
     * @return  void
     */
    Discussion.close_edit_ui = function (comment)
    {
        $(comment).find("form").remove()
        $(comment).find(".discussion-comment, .discussion-actions").show();
    }


    /**
     * Display the discussion tree on the page
     *
     * @access  public
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
                $discussion_tree.attr(
                    "data-editing-time",
                    response.editing_time_value + "|" + response.editing_time_units
                );
                $discussion_tree.children("li").remove();
                $.each(response.discussion, function (index, comment) {
                    var $comment_parent = $discussion_tree;
                    if (comment.parent) {
                        $comment_parent = $discussion_tree.find(
                            "li[data-id='" + comment.parent + "'] .discussion-replies"
                        );
                    }
                    $comment_parent.append(Discussion._build_entry(comment));
                });
                Discussion.dataRequest = null;
            }).fail(function(jqXHR, textStatus, errorThrown) {
                if  (errorThrown != "abort") {
                    console.error(
                        "Discussion.display in commenting.js AJAX error:",
                        errorThrown,
                        jqXHR.responseText
                    );
                }
                Discussion.dataRequest = null;
            });
        }
    }


    /**
     * Edit a comment
     *
     * @access  public
     * @param   integer comment_id  an integer indicating which comment to edit
     * @return  void
     */
    Discussion.edit = function (comment_id)
    {
        var $comment = $(".discussion-tree li[data-id='" + comment_id + "']");
        var $form = $comment.find("form");
        Comment.addRequest = $.ajax({
            url: $form.attr("action"),
            type: "post",
            data: {
                comment: $form.find("textarea").val(),
                id: comment_id,
                csrfmiddlewaretoken: $form.find(
                    "input[name='csrfmiddlewaretoken']"
                ).val(),
            }
        }).done(function(response, textStatus, jqXHR) {
            var $comment = $(".discussion-tree li[data-id='" + response.id + "']");
            $comment.find(".discussion-comment").html(
                response.comment.replace(/\n/g, "<br>")
            );
            Discussion.close_edit_ui($comment);
            Comment.addRequest = null;
        }).fail(function(jqXHR, textStatus, errorThrown) {
            if  (errorThrown != "abort") {
                console.error(
                    "Discussion.edit in commenting.js AJAX error:",
                    errorThrown,
                    jqXHR.responseText
                );
            }
            Comment.addRequest = null;
        });

    }


    /**
     * Update the times and editability of the discussion comments
     *
     * @access  public
     * @return  void
     */
    Discussion.update = function ()
    {
        var editing_time = $(".discussion-tree").attr('data-editing-time').split("|");
        var oldest_timestamp = moment().subtract(editing_time[0], editing_time[1]);
        $(".discussion-tree .discussion-timestamp").each(function (index, entry) {
            var timestamp = moment($(entry).attr("data-timestamp"));
            $(entry).html(timestamp.fromNow());
            if (timestamp < oldest_timestamp) {
                var $actions = $(entry).closest("li").find(
                    ".discussion-actions:first"
                );
                $actions.find("[role='discussion-edit']").remove();
                $actions.find(".action-separator").remove();
            }
        });
    }

}(window.Discussion = window.Discussion || {}, jQuery))


$(document).ready(function() {
    Discussion.display();


    // Update discussion timestamps and editablity every minute
    setInterval(function () { Discussion.update(); }, 60000);


    // Handle adding a new comment
    $(".panel-discussion").on("submit", "form", function (event) {
        event.preventDefault();
        var $textarea = $(this).find("textarea");
        if ($textarea.val() != "") {
            // disable the UI
            $(this).find("input[type='submit']").prop("disabled", true);
            $(this).find("input[type='button']").prop("disabled", true);
            $textarea.prop("disabled", true);

            // are we updating or adding?
            if ($(this).find("input[type='submit']").val() == "Update") {
                // update the existing comment
                Discussion.edit($(this).closest("li[data-id]").attr("data-id"));
            } else {
                // determine if there is a parent
                var $replies_container = $(this).closest(".discussion-replies");
                if ($replies_container.length) {
                    var $parent = $replies_container.closest("li[data-id]");
                } else {
                    var $parent = $(this).closest("li[data-id]");
                }

                // add the comment to the discussion
                Discussion.add($textarea.val(), $parent.attr("data-id"));
            }
        }
    });

    // Shift-enter in TextArea should submit the form
    $(".panel-discussion").on("keypress", "textarea", function (event) {
        if (event.keyCode == 13 && event.shiftKey) {
            event.preventDefault();
            $(this).closest("form").submit();
        }
    });

    // Esc in TextArea should remove it
    $(".panel-discussion").on("keypress", "textarea", function (event) {
        if (event.keyCode == 27) {
            event.preventDefault();
            if ($(this).closest(".discussion-replies").length) {
                $(this).closest("li").remove();
            } else {
                var $cancel_btn = $(this).closest("li").find(
                    "form input[type='button']"
                );
                if ($cancel_btn.length) {
                    $cancel_btn.click();
                }
            }
        }
    })


    // Handle editing a comment
    $(".panel-discussion").on("click", "[role='discussion-edit']", function (event) {
        event.preventDefault();
        var $comment = $(this).closest("li");
        var $form = $(".panel-discussion form:first").clone();
        $form.attr("action", $form.attr("data-edit-url"));
        $form.find("input[type='submit']").attr("value", "Update").after(
            $("<input />").addClass(
                "btn btn-default btn-sm pull-right"
            ).attr("type", "button").attr("value", "Cancel")
        );
        $form.find("textarea").val(
            $comment.find(".discussion-comment:first").html().replace(/<br>/g, "\n")
        );
        $comment.find(".media-body:first").append($form);
        $comment.find(".discussion-comment:first, .discussion-actions:first").hide();
        $form.find("textarea").focus();
    });

    // Handle canceling the editting UI
    $(".panel-discussion").on("click", "form input[type='button']", function (event) {
        event.preventDefault();
        Discussion.close_edit_ui($(this).closest("li"));
    });


    // Handle repling to a comment
    $(".panel-discussion").on("click", "[role='discussion-reply']", function (event) {
        event.preventDefault();

        // remove all but the main form
        if ($(".panel-discussion form").length > 1) {
            $(".panel-discussion form").each(function (index, form) {
                if (index > 0) {
                    if ($(form).parent("li").length) {
                        $(form).parent("li").remove();
                    }
                }
            });
        }

        // clone the main form and prepare it for use creating a reply
        var $form = $(".panel-discussion form:first").clone();
        $form.find("textarea").attr(
            "placeholder",
            "Say something in response to the above comment"
        );
        var $wrapper = $("<li />").attr(
            "id",
            "discussion-reply-active-form"
        ).addClass("media").append($form)

        // find the appropriate container for the reply UI
        var $container = $(this).closest("li").find(".discussion-replies");
        if ($container.length) {
            $container.prepend($wrapper);
        } else {
            $(this).closest("li").after($wrapper);
        }
        $form.find("textarea").focus();
    });
});
