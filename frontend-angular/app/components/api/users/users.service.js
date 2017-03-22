'use strict';

angular.module('myApp').factory("Users", function($resource, URLS) {
    return $resource(
        [URLS.API, "user/:id"].join("/"), {
            id: "@id"
        }, {
            getAll: {
                method: "GET",
                url: [URLS.API, "user"].join("/"),
                isArray: true
            },
            me: {
                method: "GET",
                url: [URLS.API, "user/me"].join("/"),
                isArray: false
            },
            get: {
                method: "GET",
                url: [URLS.API, "user/:id"].join("/"),
                isArray: false
            },
            getValidatedChallenges: {
                method: "GET",
                url: [URLS.API, "user/:id/validatedChallenges"].join("/"),
                isArray: true
            },
        });
});
