$(function() {

    var rcon = new DebugClient('ws://localhost:32081/{channel}');

    console.log("Loaded");

    $('#logging-terminal').terminal(function(cmd, term) {
        rcon.send(cmd, 'rcon');
    }, {
        prompt: 'rcon> ',
        greetings: false,
        onInit: function(term) {
            rcon.setLoggingTerminal(term);
        }
    });

    $('#repl-terminal').terminal(function(cmd, term) {
        console.log("repl: " + cmd);
        rcon.send(cmd, 'repl');
    }, {
        prompt: 'repl> ',
        greetings: false,
        onInit: function(term) {
            rcon.setReplTerminal(term);
        }
    });

    $('.btn').click(function(evt) {
        evt.preventDefault();
    });

    $('.clear-term').click(function(evt) {
        evt.preventDefault();
        var target = $(this).data('target');
        $(target).terminal().clear();
    })

    var editor = ace.edit("script-editor");
    editor.setTheme('ace/theme/monokai');
    editor.getSession().setMode('ace/mode/python');

    $('.btn-run').click(function(evt) {
        console.log(this);
    });
    $('.btn-clear').click(function(evt) {
        console.log(this);
    });

    rcon.setEditor(editor);
    rcon.run();
});