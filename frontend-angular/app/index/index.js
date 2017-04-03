'use strict';

angular.module('myApp')

.config(['$routeProvider', function($routeProvider) {
    $routeProvider.when('/', {
        templateUrl: 'index/index.html',
        controller: 'IndexCtrl'
    });
}])

.controller('IndexCtrl', function($cookies, $sce, $scope, $http, $location, $anchorScroll, ModalService, Users, Challenges) {

    $scope.init = function() {

        $.fn.extend({
            qcss: function(css) {
                return $(this).queue(function(next) {
                    $(this).css(css);
                    next();
                });
            }
        });

        $scope.executeButtonText = "Execute";
        $scope.correctButtonText = "Try to exploit my patched code";
        $scope.interpretButtonText = "Run";

        $scope.isShownHash = {};
        $scope.requestExecute = {};
        $scope.requestValidate = {};
        $scope.challengeResults = {};
        $scope.requestCorrect = {};
        $scope.requestInterpret = {};
        $scope.validatedChallenges = [];
        $scope.challenge = {};
        $scope.language = {};
        $scope.user = $cookies.getObject('user') || {};
        $scope.challengeMode = "execute";
        $scope.interpretOutput = "";

        $scope.getAllChallenges();
        $scope.getUserValidatedChallenges();
    };

    $scope.showChallenge = function(challengeId, challIndex) {
        $scope.isShownHash = {};
        $scope.aceLoaded = {};
        $scope.editors = {};
        Challenges.get({
            id: challengeId
        }).$promise.then(
            function(response) {
                $scope.challenge = response;
                $scope.challenge.challenge_id = challengeId;

                var challenge = $scope.challenge;
                $scope.challenges[challIndex].languages = challenge.languages;
                $scope.aceLoaded[challengeId] = {};
                $scope.editors[challengeId] = {};
                for (var i = 0; i < challenge.languages.length; ++i) {
                    var language = challenge.languages[i];
                    $scope.requestCorrect[challengeId][language.extension] = {
                        "content_script": language.file_content
                    };
                    $scope.requestInterpret[challengeId][language.extension] = {
                        "content_script": getInterpreterShibang(language.extension)
                    };
                    $scope.aceLoaded[challengeId][language.extension] = (function(challId, ext) {
                        return function(_editor) {
                            $scope.editors[challId][ext] = _editor;
                            $scope.editors[challId][ext].renderer.updateFull();
                        };
                    })(challengeId, language.extension);
                }
                $scope.language = challenge.languages[0];
            },
            function(err) {
                $.snackbar({
                    content: "An error occured while processing request : " + err.data,
                    timeout: 3000
                });
            }
        );
    };

    $scope.execute = function(challengeId, language) {

        $http.defaults.headers.common['X-CTF-AUTH'] = $scope.user.token;
        var title = "";
        var message = "";

        var previousButtonText = $scope.executeButtonText;
        $scope.executeButtonText = "Processing";
       
        $scope.requestExecute[challengeId].language = language;

        Challenges.execute({
            id: challengeId
        }, $scope.requestExecute[challengeId]).$promise.then(
            function(response) {
                var output = response;
                $anchorScroll("output_" + challengeId);
                $("#output_" + challengeId, function() {
                    $("#output_" + challengeId).html(output.message); // To generate XSS !!
                })
                $("#output_" + challengeId).delay(750).qcss({
                    backgroundColor: '#FFFF70'
                }).delay(750).qcss({
                    backgroundColor: 'white'
                }).delay(750);
                $scope.executeButtonText = previousButtonText;
            },
            function(err) {
                title = "Execution error";
                message = err.data.message;
                $scope.executeButtonText = previousButtonText;
                showModal(title, message);
            }
        );
    };

    $scope.validate = function(challengeId) {

        $http.defaults.headers.common['X-CTF-AUTH'] = $scope.user.token;
        var title = "";
        var message = "";

        Challenges.validate({
            id: challengeId
        }, $scope.requestValidate[challengeId]).$promise.then(
            function(response) {
                title = "Success";
                message = response.message;
            },
            function(err) {
                title = "Correction error";
                message = err.data.message;
            }
        )["finally"](function() {
            showModal(title, message);
        });
    };

    $scope.correct = function(challengeId, extension, language) {

        $http.defaults.headers.common['X-CTF-AUTH'] = $scope.user.token;
        var title = "";
        var message = "";
        var previousButtonText = $scope.correctButtonText;

        $scope.correctButtonText = "Checking";
        $scope.requestCorrect[challengeId][extension].language = language;
        Challenges.correct({
            id: challengeId
        }, $scope.requestCorrect[challengeId][extension]).$promise.then(
            function(response) {
                title = "Success";
                message = response.message;
            },
            function(err) {
                title = "Correction error";
                message = err.data.message;
            }
        )["finally"](function() {
            $scope.correctButtonText = previousButtonText;
            showModal(title, message);
        });
    };

    $scope.interpret = function(challengeId, extension, language) {

        $http.defaults.headers.common['X-CTF-AUTH'] = $scope.user.token;
        var title = "";
        var message = "";
        var previousButtonText = $scope.interpretButtonText;
        $scope.interpretButtonText = "Processing";

        $scope.requestInterpret[challengeId][extension].language = language;
        Challenges.interpret({
            id: challengeId
        }, $scope.requestInterpret[challengeId][extension]).$promise.then(
            function(response) {
                var output = response;
                $scope.interpretOutput = output.message;
                $scope.interpretButtonText = previousButtonText;
            },
            function(err) {
                title = "Execution error";
                message = err.data.message;
                $scope.executeButtonText = previousButtonText;
                showModal(title, message);
            }
        );
    };

    $scope.reset = function(challengeId) {
        $scope.requestExecute = {};
        $scope.requestValidate = {};
        $scope.execute(challengeId);
    };

    $scope.isChallengeValidated = function(challenge) {
        return $scope.validatedChallenges.indexOf(challenge.name) != -1;
    };

    $scope.isChallengeSelected = function(challenge) {
        return challenge.challenge_id == $scope.challenge.challenge_id;
    };

    $scope.isLanguageSelected = function(language) {
        return language == $scope.language;
    };

    $scope.areLanguageAndChallengeSelected = function(language, challenge) {
        return $scope.isChallengeSelected(challenge) && $scope.isLanguageSelected(language);
    };

    $scope.selectLanguage = function(language) {
        $scope.language = language;
    };

    $scope.selectChallengeMode = function(mode) {
        $scope.challengeMode = mode;
    };

    $scope.getAllChallenges = function() {
        Challenges.getAll().$promise.then(
            function(response) {
                $scope.challenges = response;
                for (var i = 0; i < $scope.challenges.length; ++i) {
                    $scope.requestExecute[$scope.challenges[i].challenge_id] = {};
                    $scope.requestCorrect[$scope.challenges[i].challenge_id] = {};
                    $scope.requestInterpret[$scope.challenges[i].challenge_id] = {};
                }
                $scope.showChallenge($scope.challenges[0].challenge_id, 0);
                $(".search-details-form").hide();
            },
            function(err) {
                $.snackbar({
                    content: "An error occured while processing request : " + err.data,
                    timeout: 3000
                });
            }
        );
    };

    $scope.getUserValidatedChallenges = function() {
        $http.defaults.headers.common['X-CTF-AUTH'] = $scope.user.token;
        Users.me().$promise.then(
            function(response) {
                var userId = response.ID;
                Users.getValidatedChallenges({
                    id: userId
                }).$promise.then(
                    function(response) {
                        var validated = response;
                        for (var i = 0; i < validated.length; i++) {
                            if (validated[i].is_exploited && validated[i].is_corrected) {
                                $scope.validatedChallenges.push(validated[i].name);
                            }
                        }
                    },
                    function(err) {}
                );
            },
            function(err) {}
        );
    };

    function getInterpreterShibang(extension) {
        var shibang = "";
        switch (extension) {
            case ".py":
                shibang = "#!/usr/bin/python3\n\n";
                break;
            case ".pl":
                shibang = "#!/usr/bin/env perl\n\n";
                break;
            case ".go":
                shibang = "package main\n\n";
                break;
            default:
                shibang = "";
        };
        return shibang
    };

    function showModal(title, message) {
        ModalService.showModal({
            templateUrl: "partials/modal.html",
            controller: function() {
                this.title = title;
                this.message = message;
            },
            controllerAs: "modal"
        }).then(function(modal) {
            modal.element.modal();
        });
    };
});
