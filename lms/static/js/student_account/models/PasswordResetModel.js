var edx = edx || {};

(function($, Backbone) {
    'use strict';

    edx.student = edx.student || {};
    edx.student.account = edx.student.account || {};

    edx.student.account.PasswordResetModel = Backbone.Model.extend({

        defaults: {
            email: ''
        },

        urlRoot: '',

        initialize: function( obj ) {
            this.urlRoot = obj.url;
        },

        sync: function(method, model) {
            var headers = {
                'X-CSRFToken': $.cookie('csrftoken')
            };

            // Only expects an email address.
            $.ajax({
                url: model.urlRoot,
                type: 'POST',
                // Should this be model.get('email')? The URL doesn't need to be in this data
                data: model.attributes,
                headers: headers
            })
            .done(function() {
                model.trigger('success');
            })
            .fail( function( error ) {
                model.trigger( 'error', error );
            });
        }
    });
})(jQuery, Backbone);
