define([
    'jquery',
    'underscore',
    'js/common_helpers/template_helpers',
    'js/common_helpers/ajax_helpers',
    'js/student_account/models/PasswordResetModel',
    'js/student_account/views/PasswordResetView',
    'js/student_account/views/FormView'
], function($, _, TemplateHelpers, AjaxHelpers, PasswordResetModel, PasswordResetView, FormView) {
        describe('Password Reset View', function() {
            'use strict';

            var requests = null,
                view = null,
                EMAIL = 'xsy@edx.org',
                FORM_DESCRIPTION = {
                    'method': 'post',
                    'submit_url': '/account/password',
                    'fields': [{
                        'name': 'email',
                        'label': 'Email',
                        'defaultValue': '',
                        'type': 'text',
                        'required': true,
                        'placeholder': 'xsy@edx.org',
                        'instructions': 'Enter your email here.',
                        'restrictions': {}
                    }]
                };

            var model = new PasswordResetModel({
                url: FORM_DESCRIPTION.submit_url
            });

            var ajaxSpyAndInitialize = function(that) {
                // Spy on AJAX requests
                requests = AjaxHelpers.requests(that);

                view = new PasswordResetView({
                    fields: FORM_DESCRIPTION.fields,
                    model: model
                });

                // Simulate a response from the server containing
                // a form description
                // AjaxHelpers.respondWithJson(requests, FORM_DESCRIPTION);
            };

            // var ajaxAssertAndRespond = function(url, requestIndex) {
            //     // Verify that the client contacts the server
            //     AjaxHelpers.expectJsonRequest(requests, 'GET', url, null, requestIndex);

            //     // Simulate a response from the server containing
            //     // a form description
            //     AjaxHelpers.respondWithJson(requests, FORM_DESCRIPTION);
            // };

            var submitEmail = function(validationSuccess) {
                // Simulate manual entry of an email address
                $('#password-reset-email').val(EMAIL);

                // Create a fake click event
                var clickEvent = $.Event('click');

                // If validationSuccess isn't passed, we avoid
                // spying on `view.validate` twice
                if (typeof validationSuccess !== 'undefined') {
                    // Force validation to return as expected
                    spyOn(view, 'validate').andReturn({
                        isValid: validationSuccess,
                        message: 'We\'re all good.'
                    });
                }

                // Submit the email address
                view.submitForm(clickEvent);
            };

            beforeEach(function() {
                setFixtures('<div id="password-reset-wrapper"></div>');
                TemplateHelpers.installTemplate('templates/student_account/password_reset');
                TemplateHelpers.installTemplate('templates/student_account/form_field');
            });

            it('allows the user to request a new password', function() {
                ajaxSpyAndInitialize(this);

                submitEmail(true);

                // Verify that the client contacts the server
                AjaxHelpers.expectRequest(
                    requests, 'POST', '/account/password', $.param({
                        email: EMAIL,
                        url: FORM_DESCRIPTION.submit_url
                    })
                );

                // Respond with status code 200
                AjaxHelpers.respondWithJson(requests, {});

                expect($('.js-reset-success')).not.toHaveClass('hidden');
            });

            it('validates the email field', function() {
                ajaxSpyAndInitialize(this);

                submitEmail(true);
                expect(view.validate).toHaveBeenCalled()
                expect(view.$errors).toHaveClass('hidden');
            });

            it('displays password reset validation errors', function() {
                ajaxSpyAndInitialize(this);

                submitEmail(false);
                expect(view.$errors).not.toHaveClass('hidden');
            });

            it('displays an error if the server cannot be contacted', function() {
                ajaxSpyAndInitialize(this);

                submitEmail(true);

                // Simulate an error from the LMS servers
                AjaxHelpers.respondWithError(requests);

                // Expect that an error is displayed
                expect($('#submission-error')).not.toHaveClass('hidden');

                // If we try again and succeed, the error should go away
                submitEmail();
                
                // This time, respond with status code 200
                AjaxHelpers.respondWithJson(requests, {});
                
                // Expect that the error is hidden
                expect($('#submission-error')).toHaveClass('hidden');
            });
        });
    }
);
