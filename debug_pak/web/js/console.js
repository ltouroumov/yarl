$(function() {

    function reloadLibrary() {
        var library = $('#file-library');
        library.empty();
        var pattern = /\.py$/;
        for (var n = 0; n < localStorage.length; ++n) {
            var key = localStorage.key(n);
            if (pattern.test(key)) {
                console.log(key);
                library.append('<option>' + key + '</option>');
            }
        }
    }

    var rcon = new DebugClient('ws://localhost:32081/{channel}');

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
        rcon.send({'repl': false, 'code': cmd}, 'repl');
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
    });

    var editor = ace.edit("script-editor");
    editor.setTheme('ace/theme/monokai');
    editor.getSession().setMode('ace/mode/python');

    $('.btn-run').click(function(evt) {
        var text = editor.getSession().getDocument().getValue();
        rcon.send({'repl': false, 'code': text}, 'repl');
    });
    $('.btn-clear').click(function(evt) {
        editor.getSession().getDocument().setValue("");
    });
    $('.btn-file-save').click(function (evt) {
        var text = editor.getSession().getDocument().getValue();
        var name = prompt("File name");
        if (!name)
            name = $('#file-library').val();
        localStorage.setItem(name, text);
        reloadLibrary();
    });
    $('.btn-file-load').click(function (evt) {
        var name = $('#file-library').val();
        var text = localStorage.getItem(name);
        editor.getSession().getDocument().setValue(text);
    });
    $('.btn-file-del').click(function (evt) {
        var name = $('#file-library').val();
        localStorage.removeItem(name);
        reloadLibrary();
    });


    reloadLibrary();

    rcon.setEditor(editor);
    rcon.run();

    console.log("Loaded");
});