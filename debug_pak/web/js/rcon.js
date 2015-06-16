(function(window, undefined) {

    function DebugClient(address) {
        this.address = address;
        this.sockets = {};
    }

    DebugClient.prototype.setLoggingTerminal = function(term) {
        this.loggingTerminal = term;
    };

    DebugClient.prototype.setReplTerminal = function(term) {
        this.replTerminal = term;
    };

    DebugClient.prototype.setEditor = function(editor) {
        this.editor = editor;
    };

    DebugClient.prototype.connect = function(channel) {
        var socket = new WebSocket(this.address.replace("{channel}", channel));
        socket.onopen = this.onSocketOpen.bind(this);
        socket.onclose = this.onSocketClose.bind(this);
        socket.onmessage = this.onSocketMessage.bind(this);
        socket.onerror = this.onSocketError.bind(this);
        return socket;
    };

    DebugClient.prototype.run = function() {
        this.loggingTerminal.echo("[[b;#00BF00;]Connecting to server ...]");

        this.sockets['log'] = this.connect("log");
        this.sockets['rcon'] = this.connect("rcon");
        this.sockets['repl'] = this.connect("repl");
    };

    DebugClient.prototype.onSocketOpen = function(event) {
        //this.loggingTerminal.echo("[[b;#00BF00;]Connected to " + event.currentTarget.url + "]");
        console.log(event);
    };

    DebugClient.prototype.onSocketClose = function(event) {
        this.loggingTerminal.echo("[[b;#BE0000;]Connection to " + event.currentTarget.url + " Closed]");
        console.log(event);
    };

    DebugClient.prototype.onSocketError = function(event) {
        this.loggingTerminal.echo("[[b;#BE0000;]Socket Error]");
        console.log(event);
    };

    DebugClient.prototype.onSocketMessage = function(event) {
        console.log(event);
        var json = JSON.parse(event.data);
        console.log(json);

        switch (json.packet_type) {
            case 'log':
                json.payload.forEach(function(item) {
                    this.loggingTerminal.echo(item);
                }.bind(this));
                break;
            case 'rcon':
                this.loggingTerminal.echo(json.payload);
                break;
            case 'repl':
                this.replTerminal.echo(json.payload);
                break;
            default:
                this.loggingTerminal.echo("[[b;red;]Unhandled packet type " + json.packet_type + "]");
                break;
        }
    };

    DebugClient.prototype.send = function(message, channel) {
        var data = JSON.stringify({ 'channel': channel, 'message': message });
        this.sockets[channel].send(data);
    };

    window.DebugClient = DebugClient;
})(window, undefined);