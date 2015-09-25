/* Copyright 2015 The Pennsylvania State University. Office of the Vice Provost for Educational Equity. All Rights Reserved. */

/**
 * Provides a framework for displaying user messages on a page
 */
(function (UserMessage, $, undefined)
{
    /**
     * Add a user message to the page/dialog
     *
     * If an appropriate container (ul element with the `messages` class)
     * cannot be found, an attempt to create it will be made.
     *
     * @access public
     * @param  string  message    a string containing the message to display
     * @param  string  type       a string indicating the type of message.  Use
     *                            the standard Bootstrap types here:
     *                              success, info, warning, danger
     * @param  integer dismiss    an integer indicating the number of seconds
     *                            to wait before closing the message. If blank
     *                            or not specified, the message will not be
     *                            dismissable. Use -1 to enable the user to
     *                            dismiss the message but not automatically
     *                            close it.
     * @param  string  dialog_id  a string indicating the element ID of the
     *                            dialog to display the message within. If blank
     *                            or not specified, the message will be added
     *                            to the page.
     * @return void
     */
    UserMessage.add = function (message, type, dismiss, dialog_id)
    {
        var $holder = UserMessage._find_message_holder(dialog_id);
        if ($holder) {
            dismiss = parseInt(dismiss);
            var dismissable = (dismiss) ? true : false;
            var $alert = UserMessage._build_alert(message, type, dismissable);
            if ($alert) {
                $($holder).append($alert);
                if (dismiss > 0) {
                    window.setTimeout(function () {
                        $alert.slideUp(
                            400,
                            function () {
                                $alert.alert("close");
                            }
                        )
                    }, dismiss * 1000);
                }
            }
        }
    }


    /**
     * Creates the HTML alert entry
     *
     * @access private
     * @param  string  message      a string containing the message to display
     * @param  string  type         a string indicating the type of message.
     *                              Use the standard Bootstrap types here:
     *                                success, info, warning, danger
     * @param  integer dismissable  a boolean indicating whether or not the
     *                              alert should be able to be dismissed by
     *                              the user
     * @return object  an object containing the HTML to render the alert
     */
    UserMessage._build_alert = function (message, type, dismissable)
    {
        var $alert = $("<li />").addClass("alert").attr("role", "alert");
        type = type.toLowerCase();
        if (['success', 'info', 'warning', 'danger'].indexOf(type) !== -1) {
            $alert.addClass("alert-" + type);
        } else {
            return null;
        }
        if (dismissable) {
            $alert.addClass("alert-dismissable");
            $alert.append(
                $("<button />").addClass("close").attr(
                    "type",
                    "button"
                ).attr(
                    "data-dismiss",
                    "alert"
                ).attr(
                    "aria-label",
                    "CLose"
                ).append(
                    $("<span />").attr("aria-hidden", "true").html("&times;")
                )
            );
        }
        $alert.append(message);
        return $alert;
    }


    /**
     * Find the ul.messages element that holds the user messages
     *
     * If an appropriate container cannot be found, an attempt to create it
     * is made.
     *
     * @access private
     * @param  string  dialog_id  a string indicating the element ID of the
     *                            dialog to display the message within. If blank
     *                            or not specified, the message will be added
     *                            to the page.
     * @return object  an object that should contain the user messages or null
     */
    UserMessage._find_message_holder = function (dialog_id)
    {
        var $new_holder = $("<ul />").addClass("messages list-unstyled");
        if (typeof dialog_id !== "undefined" && dialog_id != "") {
            // dialog message
            var $dialog = $("[role='dialog']#" + dialog_id);
            if ($dialog.length) {
                $holder = $dialog.find("ul.messages, ol.messages");
                if ($holder.length) {
                    return $holder[0];
                } else {
                    var $body = $dialog.find(".modal-body");
                    if ($body.length) {
                        $body.prepend($new_holder);
                        return $new_holder;
                    }
                }
            }
        } else {
            // page message
            $holder = $("body ul.messages, body ol.messages");
            if ($holder.length) {
                return $holder[0];
            } else {
                if ($("header").length) {
                    $body = $("header").next();
                } else {
                    $body = $("body");
                }
                var $container = $body.find(".container, .container-fluid");
                if ($container.length) {
                    $container = $container[0];
                } else {
                    var $page_title = $body.find("h1");
                    if ($page_title.length) {
                        var $container = $("<div />").addClass("container-fluid");
                        $container.insertAfter($page_title[0]);
                    }
                }
                if ($container !== "undefined") {
                    $container.prepend($new_holder);
                    return $new_holder;
                }
            }
        }
        return null;
    }

}( window.UserMessage = window.UserMessage || {}, jQuery));
