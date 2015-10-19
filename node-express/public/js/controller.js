var chatApp = angular.module('app', []);

chatApp.config(function($locationProvider){
    $locationProvider.html5Mode({
    enabled: true,
    requireBase: false
  });
});

chatApp.controller('Ctrl', function($scope, $http){

    $scope.value ="It works!";

    $scope.init = function(token){

        $scope.value = "Token succesfully retrieved";
        $scope.token = {
            token_type: 'Bearer',
            access_token: token
            };

    };

    $scope.logout = function(){
        CONNECT_AUTH.logout();
    };

    $scope.get_user = function() {
        $http.get(CONNECT_AUTH.config().fc_endpoints.userinfo,
            {headers: {'Authorization': $scope.token.token_type + ' ' + $scope.token.access_token}})
            .success(function(data){
                $scope.user = data;
            })
            .error(function(err){
                console.log(err);
            })
    };

    $scope.get_groups = function() {
        $http.get(CONNECT_AUTH.config().fc_endpoints.groups,
            {headers: {'Authorization': $scope.token.token_type + ' ' + $scope.token.access_token}})
            .success(function(data){
                $scope.groups = data;
            })
            .error(function(err){
                console.log(err);
            })
    };

    $scope.get_group_members = function(group) {

        $http.get(CONNECT_AUTH.config().fc_endpoints.groups + '/' + group.id + '/members',
            {headers: {'Authorization': $scope.token.token_type + ' ' + $scope.token.access_token}})
            .success(function(data){
                group.members = data;
            })
            .error(function(err){
                console.log(err);
                group.members =  [];
            });
    };

    $scope.get_chatting = function(group) {
        $http.get(CONNECT_AUTH.config().api_endpoints.feide_chat)
            .success(function(data){
                group.chat = data;
            })
            .error(function(err){
                console.log(err);
                group.chat =  ":(";
            });
    };


});