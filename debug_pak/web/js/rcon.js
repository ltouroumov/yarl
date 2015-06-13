(function(window, undefined) {

    function DebugClient(address) {
        this.address = address;
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

    DebugClient.prototype.run = function() {
        this.loggingTerminal.echo("[[b;#00BF00;]Connecting to server ...]");
        this.socket = new WebSocket(this.address);
        this.socket.onopen = this.onSocketOpen.bind(this);
        this.socket.onclose = this.onSocketClose.bind(this);
        this.socket.onmessage = this.onSocketMessage.bind(this);
        this.socket.onerror = this.onSocketError.bind(this);
    };

    DebugClient.prototype.onSocketOpen = function(event) {
        this.loggingTerminal.echo("[[b;#00BF00;]Connected]");
        console.log(event);
    };

    DebugClient.prototype.onSocketClose = function(event) {
        this.loggingTerminal.echo("[[b;#BE0000;]Server Closed]");
        console.log(event);
    };

    DebugClient.prototype.onSocketError = function(event) {
        this.loggingTerminal.echo("[[b;#BE0000;]Socket Error]");
        console.log(event);
    };

    DebugClient.prototype.onSocketMessage = function(event) {
        var json = JSON.parse(event.data);

        switch (json.packet_type) {
            case 'rcon':
                this.loggingTerminal.echo(json.payload);
                break;
            case 'repl':
                this.replTerminal.echo(json.payload);
                break;
            default:
                this.loggingTerminal.echo("[[b;red;]Unhandled packet type] " + json.packet_type);
                break;
        }

        console.log(event);
    };

    DebugClient.prototype.send = function(message, channel) {
        var data = JSON.stringify({ 'channel': channel, 'message': message });
        this.socket.send(data);
    };

    window.DebugClient = DebugClient;
})(window, undefined);