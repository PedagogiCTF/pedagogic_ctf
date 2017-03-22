'use strict';

angular.module('myApp').factory("Challenges", function($resource, URLS) {
    return $resource(
        [URLS.API, "challenge/:id"].join("/"), {
            id: "@id"
        }, {
            getAll: {
                method: "GET",
                url: [URLS.API, "challenge"].join("/"),
                isArray: true
            },
            get: {
                method: "GET",
                url: [URLS.API, "challenge/:id"].join("/"),
                isArray: false
            },
            execute: {
                method: "POST",
                url: [URLS.API, "challenge/:id/execute"].join("/"),
            },
            validate: {
                method: "POST",
                url: [URLS.API, "challenge/:id/validate"].join("/"),
            },
            correct: {
                method: "POST",
                url: [URLS.API, "challenge/:id/correct"].join("/"),
            },
        });
});
