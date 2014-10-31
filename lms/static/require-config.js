;(function (require) {
    require.config({
        // NOTE: baseUrl has been previously set in the 4 OVA templates in lms/static/templates:
        // imageannotation.html, notes.html, textannotation.html, videoannotation.html
        waitSeconds: 60,
        paths: {
          // Files needed for OVA
          "annotator": "js/vendor/ova/annotator-full",
          "annotator-harvardx": "js/vendor/ova/annotator-full-firebase-auth",
          "video.dev": "js/vendor/ova/video.dev",
          "vjs.youtube": 'js/vendor/ova/vjs.youtube',
          "rangeslider": 'js/vendor/ova/rangeslider',
          "share-annotator": 'js/vendor/ova/share-annotator',
          "richText-annotator": 'js/vendor/ova/richText-annotator',
          "reply-annotator": 'js/vendor/ova/reply-annotator',
          "grouping-annotator": 'js/vendor/ova/grouping-annotator',
          "tags-annotator": 'js/vendor/ova/tags-annotator',
          "diacritic-annotator": 'js/vendor/ova/diacritic-annotator',
          "flagging-annotator": 'js/vendor/ova/flagging-annotator',
          "jquery-Watch": 'js/vendor/ova/jquery-Watch',
          "openseadragon": 'js/vendor/ova/openseadragon',
          "osda": 'js/vendor/ova/OpenSeaDragonAnnotation',
          "ova": 'js/vendor/ova/ova',
          "catch": 'js/vendor/ova/catch/js/catch',
          "handlebars": 'js/vendor/ova/catch/js/handlebars-1.1.2',
          // end of OVA files
        },
        shim: {
          // The following are all needed for OVA
          "video.dev": {
            exports:"videojs"
          },
          "vjs.youtube": {
            deps: ["video.dev"]
          },
          "rangeslider": {
            deps: ["video.dev"]
          },
          "annotator": {
            exports: "Annotator"
          },
          "annotator-harvardx":{
            deps: ["annotator"]
          },
          "share-annotator": {
            deps: ["annotator"]
          },
          "richText-annotator": {
            deps: ["annotator", "tinymce"]
          },
          "reply-annotator": {
            deps: ["annotator"]
          },
          "tags-annotator": {
            deps: ["annotator"]
          },
          "diacritic-annotator": {
            deps: ["annotator"]
          },
          "flagging-annotator": {
            deps: ["annotator"]
          },
          "grouping-annotator": {
            deps: ["annotator"]
          },
          "ova":{
            exports: "ova",
            deps: ["annotator", "annotator-harvardx", "video.dev", "vjs.youtube", "rangeslider", "share-annotator", "richText-annotator", "reply-annotator", "tags-annotator", "flagging-annotator", "grouping-annotator", "diacritic-annotator", "jquery-Watch", "catch", "handlebars", "URI"]
          },
          "osda":{
            exports: "osda",
            deps: ["annotator", "annotator-harvardx", "video.dev", "vjs.youtube", "rangeslider", "share-annotator", "richText-annotator", "reply-annotator", "tags-annotator", "flagging-annotator", "grouping-annotator", "diacritic-annotator", "openseadragon", "jquery-Watch", "catch", "handlebars", "URI"]
          },
          // End of OVA
        }
    });
}).call(this, require || RequireJS.require);