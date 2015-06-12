$(function() {
    console.log("Loaded");

    $('#logging-terminal').terminal(function(cmd, term) {
        console.log("rcon: " + cmd);
    }, { prompt: 'rcon> ', greetings: false });

    $('#repl-terminal').terminal(function(cmd, term) {
        console.log("repl: " + cmd);
    }, { prompt: 'repl> ', greetings: false });
});