/*! Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */
(function (Comment, $, undefined)
{
    // the AJAX objects that handles server communication
    Comment.addRequest;
    Comment.dataRequest;

}( window.Comment = window.Comment || {}, jQuery));


$(document).ready(function() {
    //Appends the text from the box to the commenting feed
    $("button[role='add-comment']").on("click", function (event) {
        var comment = $("textarea#comment-text").val();
        $("#comment-feed-list").append(
                $("<li />").attr("class","comment-li"
                ).append(
                    $("<span />").attr("class","user-image"
                        )
                ).append(
                    $("<div />").attr("class","single-comment-text"
                        ).append(comment
                ).append(
                    $("<div />").attr("class","single-comment-options pull-right"
                        ).append($("<a />").attr("href","#").html("Reply")))));
        $("textarea#comment-text").val('');
    });
});