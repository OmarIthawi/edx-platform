"""
Test xblock/validation.py
"""

import unittest
from xblock.test.tools import assert_raises

from xmodule.validation import StudioValidationMessagesTypes, StudioValidation
from xblock.validation import Validation


class StudioValidationMessageTypesTest(unittest.TestCase):
    """
    Tests for `StudioValidationMessageTypes`
    """

    def test_contains(self):
        """
        Verify the `contains` method returns `True` for warning, error, and not-configured types.
        """
        self.assertTrue(StudioValidationMessagesTypes.contains(StudioValidationMessagesTypes.WARNING))
        self.assertTrue(StudioValidationMessagesTypes.contains(StudioValidationMessagesTypes.ERROR))
        self.assertTrue(StudioValidationMessagesTypes.contains(StudioValidationMessagesTypes.NOT_CONFIGURED))


class StudioValidationTest(unittest.TestCase):
    """
    Tests for `StudioValidation` class.
    """
    def test_copy(self):
        validation = Validation("id")
        validation.add(Validation.MESSAGE_TYPES.ERROR, u"Error message")

        studio_validation = StudioValidation.copy(validation)
        self.assertIsInstance(studio_validation, StudioValidation)
        self.assertFalse(studio_validation)
        self.assertEqual(1, len(studio_validation.messages))
        expected = {
            "type": "error",
            "text": u"Error message"
        }
        self.assertEqual(expected, studio_validation.messages[0])
        self.assertIsNone(studio_validation.summary)

    def test_create_message(self):
        """
        Test that `create_message` creates the expected structure.
        """
        expected = {
            "type": "warning",
            "text": u"Warning message"
        }
        self.assertEqual(
            expected,
            StudioValidation.create_message(Validation.MESSAGE_TYPES.WARNING, u"Warning message")
        )

        expected = {
            "type": "warning",
            "text": u"Warning message",
            "action_label": u"Action label",
            "action_runtime_event": "create groups"
        }
        self.assertEqual(
            expected,
            StudioValidation.create_message(
                Validation.MESSAGE_TYPES.WARNING,
                u"Warning message",
                action_label=u"Action label",
                action_runtime_event="create groups"
            )
        )

        expected = {
            "type": "warning",
            "text": u"Warning message",
            "action_label": u"Action label",
            "action_class": "edit-button"
        }
        self.assertEqual(
            expected,
            StudioValidation.create_message(
                Validation.MESSAGE_TYPES.WARNING,
                u"Warning message",
                action_label=u"Action label",
                action_class="edit-button"
            )
        )

    def test_create_message_errors(self):
        """
        Test that `create_message` throws expected errors.
        """
        with assert_raises(TypeError):
            StudioValidation.create_message("info", u"Unknown type info", action_label="not unicode")

        with assert_raises(TypeError):
            StudioValidation.create_message(Validation.MESSAGE_TYPES.WARNING, action_class=0)

        with assert_raises(TypeError):
            StudioValidation.create_message(Validation.MESSAGE_TYPES.WARNING, action_runtime_event=0)

    def test_is_empty(self):
        """
        Test that `is_empty` return True iff there are no messages and no summary.
        Also test the "bool" property of `Validation`.
        """
        validation = StudioValidation("id")
        self.assertTrue(validation.is_empty)
        self.assertTrue(validation)

        validation.add(Validation.MESSAGE_TYPES.ERROR, u"Error message")
        self.assertFalse(validation.is_empty)
        self.assertFalse(validation)

        validation_with_summary = StudioValidation("id")
        validation_with_summary.set_summary(StudioValidation.MESSAGE_TYPES.NOT_CONFIGURED, u"Summary message")
        self.assertFalse(validation.is_empty)
        self.assertFalse(validation)

    def test_add_operator(self):
        """
        Test the behavior of the addition operator (+) with `Validation` and `StudioValidation` instances.
        """
        validation_1 = Validation("id")
        validation_1.add(Validation.MESSAGE_TYPES.ERROR, u"Error message")

        validation_2 = StudioValidation("id")
        validation_2.add(StudioValidation.MESSAGE_TYPES.NOT_CONFIGURED, u"Not configured")
        validation_2.set_summary(StudioValidation.MESSAGE_TYPES.WARNING, u"Summary message")

        validation = validation_1 + validation_2

        # TODO: need to figure this out
        # self.assertIsInstance(validation, StudioValidation)
        self.assertEqual(2, len(validation.messages))
        self.assertEqual(
            StudioValidation.create_message(Validation.MESSAGE_TYPES.ERROR, u"Error message"), validation.messages[0]
        )
        self.assertEqual(
            StudioValidation.create_message(
                StudioValidation.MESSAGE_TYPES.NOT_CONFIGURED, u"Not configured"
            ), validation.messages[1]
        )
        # TODO: need to figure this out
        # self.assertEqual(
        #     StudioValidation.create_message(
        #         StudioValidation.MESSAGE_TYPES.WARNING, u"Summary message"
        #     ), validation.summary
        # )

    def test_to_json(self):
        """
        Test the ability to serialize a `StudioValidation` instance.
        """
        validation = StudioValidation("id")
        expected = {
            "xblock_id": "id",
            "messages": [],
            "is_empty": True
        }
        self.assertEqual(expected, validation.to_json())

        validation.add(
            StudioValidation.MESSAGE_TYPES.ERROR,
            u"Error message",
            action_label=u"Action label",
            action_class="edit-button"
        )
        validation.add(
            StudioValidation.MESSAGE_TYPES.NOT_CONFIGURED,
            u"Not configured message",
            action_label=u"Action label",
            action_runtime_event="make groups"
        )
        validation.set_summary(
            StudioValidation.MESSAGE_TYPES.WARNING,
            u"Summary message",
            action_label=u"Summary label",
            action_runtime_event="fix everything")

        expected = {
            "xblock_id": "id",
            "messages": [
                {"type": "error", "text": u"Error message", "action_label": u"Action label", "action_class": "edit-button"},
                {"type": "not-configured", "text": u"Not configured message", "action_label": u"Action label", "action_runtime_event": "make groups"}
            ],
            "summary": {"type": "warning", "text": u"Summary message", "action_label": u"Summary label", "action_runtime_event": "fix everything"},
            "is_empty": False
        }
        self.assertEqual(expected, validation.to_json())
