'use strict';

// Declare app level module which depends on views, and components
angular.module('myApp', [
    'ngResource',
    'ngRoute',
    'angularModalService',
    'ui.ace',
    'myApp.style',
    'myApp.scoreboard',
    'myApp.register',
    'myApp.login',
    'myApp.logout',
    'myApp.profile',
]).config(['$locationProvider', '$routeProvider', function($locationProvider, $routeProvider) {
    $locationProvider.hashPrefix('!');

    $routeProvider.otherwise({
        redirectTo: '/'
    });
}]);
