/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */
(function (Comment, $, undefined)
{
    // the AJAX objects that handles server communication
    Comment.addRequest;
    Comment.dataRequest;

    Comment.add = function () {
        var addUrl = $("#comments-div form").attr("data-url");
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

        $(".media-list").append(
            $("<li />").attr("class","media"
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
        $("textarea#comment-text").val('');
    }

}( window.Comment = window.Comment || {}, jQuery));


$(document).ready(function() {
    //Appends the text from the box to the commenting feed
    $("button[role='add-comment']").on("click", function (event) {
        Comment.add();
    });
});