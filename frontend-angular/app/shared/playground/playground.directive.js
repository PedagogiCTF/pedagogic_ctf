angular.module('myApp')
    .directive('playgroundPopup', ['$rootScope', function() {
        'use strict';
        return {
            'restrict': 'A',
            'scope': {
                dragOptions: '=ngDraggable'
            },
            'replace': false,
            'templateUrl': 'shared/playground/playground-popup.html',
            'link': function($scope) {

                $scope.status = {
                    minimize: false,
                    maximize: false,
                    close: false
                };

                $scope.minimize = function() {
                    $scope.status.maximize = false;
                    $scope.status.minimize = true;
                    $scope.status.close = false;
                };

                $scope.maximize = function() {
                    $scope.status.maximize = true;
                    $scope.status.minimize = false;
                    $scope.status.close = false;
                };

                $scope.restore = function() {
                    $scope.status.maximize = false;
                    $scope.status.minimize = false;
                    $scope.status.close = false;
                };

                $scope.toggle = function() {
                    if ($scope.status.maximize || $scope.status.minimize) {
                        $scope.restore();
                    } else {
                        $scope.maximize();
                    }
                };

                $scope.close = function() {
                    $scope.restore();
                    $scope.status.close = true;
                };

                $scope.$on('playground.popup.maximize', $scope.maximize);
                $scope.$on('playground.popup.minimize', $scope.minimize);
                $scope.$on('playground.popup.restore', $scope.restore);
                $scope.$on('playground.popup.toggle', $scope.toggle);
                $scope.$on('playground.popup.close', $scope.close);
            }
        };
    }]);
