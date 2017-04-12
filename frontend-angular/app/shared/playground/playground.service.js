angular.module('myApp')
.service('PlaygroundService',
         ['$rootScope', '$compile', function ($rootScope, $compile) {
    'use strict';

    var self = this,
        actions = ['minimize', 'maximize', 'restore', 'close'],
        isLoaded = false;

    angular.forEach(actions, function (action) {
        self[action] = function (id) {
            $rootScope.$broadcast('playground.popup.' + action, id);
        };
    });

    this.toggle = function () {
        if ($('[playground-popup] .draggable').hasClass('close')) {
            self.restore();
        } else {
            self.close();
        }
    };

    this.init = function () {
        $compile('<div playground-popup></div>')($rootScope, function(el) {
            $('body').append(el);
            isLoaded = true;
        });
    };

    this.isLoaded = function () {
        return isLoaded;
    };

}]);
