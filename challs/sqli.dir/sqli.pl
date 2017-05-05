#! /usr/bin/env perl

use strict;
use warnings;
use DBI;
use Mojolicious;
use Mojo::Log;
use Mojo::URL;
use Mojo::UserAgent;

my $driver = "SQLite";
my $dsn = "DBI:$driver:dbname=/tmp/sqli.db";
my $dbh = DBI->connect($dsn, undef, undef, { AutoCommit => 1 }) or exit;

my $app = Mojolicious->new;
$app = $app->log(Mojo::Log->new(path => '/dev/null'));


sub getUser {
    #
    #    Get account details for user
    #
    my $username = shift;
    my $password = shift;
    my $sth = $dbh->prepare("SELECT username FROM users WHERE username='$username' AND password='$password'");
    $sth->execute;
    $sth->bind_columns(\my($user));
    $sth->fetch;

    return $user;
}

######################   API   ##############################

$app->routes->post('/login' => sub {
    #
    #    Get secret page
    #
    my $c = shift;
    my $username = $c->param('username');
    my $password = $c->param('password');
    
    my $user = eval {getUser($username, $password)};
    if(!$user) {
        return $c->render(
            status => 401,
            template => 'unauthorized',
            text => "Invalid username/password"
        );
    }

    open my $fh, '<', 'secret' or die "error opening secret file";
    my $secret = do { local $/; <$fh> };
        
    return $c->render(
        status => 200,
        text => "You are logged in. The secret is $secret"
    );
});

####################     Main   #############################

sub main {

    my $username = $ARGV[0];
    my $password = $ARGV[1];
    
    my $url = Mojo::URL->new('/login');
    my $ua = Mojo::UserAgent->new();
    $ua->server->app($app);
    my $response = $ua->post($url => form => {username => $username, password => $password});
    print $response->res->content->asset->{'content'};
    $dbh->disconnect();
}

main();
1;

__DATA__

@@ unauthorized.html.ep
% layout 'default';
<h1>Unauthorized</h1>
<p><%= $content %></p>

@@ layouts/default.html.ep
<!DOCTYPE html>
<html>
  <head><title>MyApp</title></head>
  <body><%= content %></body>
</html>
