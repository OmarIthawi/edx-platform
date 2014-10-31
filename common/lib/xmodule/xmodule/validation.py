from xblock.validation import Validation, ValidationMessageTypes


class StudioValidationMessagesTypes (ValidationMessageTypes):
    NOT_CONFIGURED = "not-configured"


class StudioValidation(Validation):

    MESSAGE_TYPES = StudioValidationMessagesTypes()

    @classmethod
    def copy(cls, validation):
        studio_validation = cls(validation.xblock_id)
        studio_validation.messages = validation.messages
        return studio_validation

    @classmethod
    def create_message(
            cls, message_type, message_text, action_label=None, action_class=None, action_runtime_event=None
    ):
        message = super(StudioValidation, cls).create_message(message_type, message_text)
        assert isinstance(message_text, unicode), "Message text must be unicode."
        if action_label:
            if not isinstance(action_label, unicode):
                raise TypeError("Action label must be unicode.")
            message["action_label"] = action_label
        if action_class:
            if not isinstance(action_class, basestring):
                raise TypeError("Action class must be a string.")
            message["action_class"] = action_class
        if action_runtime_event:
            if not isinstance(action_runtime_event, basestring):
                raise TypeError("Action runtime event must be a string.")
            message["action_runtime_event"] = action_runtime_event
        return message

    def __init__(self, xblock_id):
        super(StudioValidation, self).__init__(xblock_id)
        self.summary = None

    def add(self, message_type, message_text, action_label=None, action_class=None, action_runtime_event=None):
        self.messages.append(
            self.create_message(message_type, message_text, action_label, action_class, action_runtime_event)
        )

    def set_summary(self, message_type, message_text, action_label=None, action_class=None, action_runtime_event=None):
        self.summary = self.create_message(message_type, message_text, action_label, action_class, action_runtime_event)

    @property
    def is_empty(self):
        return super(StudioValidation, self).is_empty and not self.summary

    def to_json(self):
        """
        Convert to a json-serializable representation.
        """
        serialized = super(StudioValidation, self).to_json()
        if self.summary:
            serialized["summary"] = self.summary
        return serialized
