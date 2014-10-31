define(["backbone", "gettext"], function (Backbone, gettext) {
    /**
     * Model for validation messages shown on components in Studio.
     */
    var ValidationMessages = Backbone.Model.extend({
        defaults: {
            summary: {},
            detailed_messages: [],
            show_summary_only: false,
            is_root: false
        },

        getSummaryMessage: function () {
            var summaryMessage;
            if ("text" in this.get("summary")) {
                summaryMessage = this.get("summary");
            }
            else {
                summaryMessage = {"text" : gettext("This component has validation issues.")};
            }

            if (!("type" in summaryMessage) || summaryMessage.type === null) {
                summaryMessage.type = this.getSummaryType();
            }
            return summaryMessage;
        },

        getSummaryType: function () {
            var detailedMessages = this.get("messages");
            // Possible types are "error", "warning", and "not-configured". "not-configured" is treated as a warning.
            for (var i = 0; i < detailedMessages.length; i++) {
                if (detailedMessages[i].type === "error") {
                    return "error";
                }
            }
            return "warning";
        },

        getDisplayName: function (messageType) {
            if (messageType === "warning") {
                // Translators: This message will be added to the front of messages of type warning,
                // e.g. "Warning: this component has not been configured yet".
                return gettext("Warning");
            }
            else if (messageType === "error") {
                // Translators: This message will be added to the front of messages of type error,
                // e.g. "Error: required field is missing".
                return gettext("Error");
            }
            else {
                return null;
            }
        },

        getDetailedMessages: function () {
            if (this.get("show_summary_only")) {
                return [];
            }
            return this.get("messages");
        },

        getAdditionalClasses: function () {
            if (this.get("is_root") && this.getSummaryMessage().type === "not-configured" &&
                this.getDetailedMessages().length === 0) {
                return "no-container-content";
            }
            return "";
        }

    });
    return ValidationMessages;
});

