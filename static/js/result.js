function f1(){
    var centrifuge = new Centrifuge();
    centrifuge.configure({
        url: "{{ CENTRIFUGE_WEBSOCKET }}",
        project: "{{ CENTRIFUGE_PROJECT_ID }}",
        user: "",
        timestamp: "1",
        token: "1",
        debug: true
    })
    centrifuge.connect();
    centrifuge.on('connect', function() {
        // now your client connected
        var subscription = centrifuge.subscribe("{{ data_channel }}", function(message) {
            // called when message received from this channel
            console.log(message)

            var items = [];
            $.each( message.data, function( key, val ) {

                var test = val;
                if(test=="failed")
                    alert(test);
                else {
                    items.push( "<id='" + key + "'>" + val + "" );
                    if(key=="Data")
                        document.getElementById("mytext").value = test;
                    else if(key=="Data2")
                        document.getElementById("mytext2").value = test;
                    else if(key=="Data3")
                        document.getElementById("mytext3").value = test;
                    else
                        document.getElementById("mytext4").value = test;
                }
            });

            $( "</>", {
                              "class": "my-new-list",
                              html: items.join( "" )
                            }).appendTo( "body" );
        });
    });
}

