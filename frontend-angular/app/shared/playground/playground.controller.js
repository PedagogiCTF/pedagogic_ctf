'use strict';

angular.module('myApp').controller('PlaygroundCtrl', function($rootScope, $scope, Challenges) {

    function init() {

        $scope.dragOptions = {
            handle: '#headerPopup, #contentPopup',
            cancel: '#output, #ace'
        };

        $scope.selectedLanguage = "PERL";
        $scope.languages = ["PERL", "PYTHON", "GOLANG"];
        $scope.snippets = {};

        for (var i = 0; i < $scope.languages.length; i++) {
            var lang = $scope.languages[i];
            $scope.snippets[lang] = getInterpreterShibang(lang);
        }

        $scope.interpretOutput = "";
        $scope.interpretButtonText = "Run";
    }

    function getInterpreterShibang(language) {
        var shibang = "";
        switch (language) {
            case "PYTHON":
                shibang = "#!/usr/bin/python3\n\n";
                break;
            case "PERL":
                shibang = "#!/usr/bin/env perl\n\n";
                break;
            case "GOLANG":
                shibang = "package main\n\n";
                break;
            default:
                shibang = "";
        };
        return shibang
    };

    $scope.isLanguageSelected = function(language) {
        return language == $scope.selectedLanguage;
    };

    $scope.selectLanguage = function(language) {
        $scope.selectedLanguage = language;
    };

    $scope.interpret = function() {

        var title = "";
        var message = "";
        $scope.interpretButtonText = "Processing";

        var payload = {
            "content_script": $scope.snippets[$scope.selectedLanguage],
            "language": $scope.selectedLanguage,
        }
        Challenges.playground(payload).$promise.then(
            function(response) {
                $scope.interpretButtonText = "Run";
                var output = response;
                $scope.interpretOutput = output.message;
            },
            function(err) {
                $scope.interpretButtonText = "Run";
                message = "Execution error\n\n" + err.data.message;
                $scope.interpretOutput = output.message;
            }
        );
    };

    init();

});
