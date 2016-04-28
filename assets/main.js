(function() {

  var hostname = location.host;
  var ws = new WebSocket("ws://" + hostname + "/ws");

  ws.onopen = function() {
    // WebSocketオープン時の挙動を書く
    ws.send(JSON.stringify({command: "state_check"}));
  };

  ws.onmessage = function (evt) {
    // WebSocketでメッセージを受け取った時の処理をまとめて
    try {
      var messageData = JSON.parse(evt.data);
      parseMessage(messageData);
    } catch(e) {
      alert('受け取ったメッセージの形式が不正です [message]:' + messageData['message']);
    }
  };

  $('#arrival_alert').on('click', function() {
    ws.send(JSON.stringify({command: "arrival_alert"}));
    buttonDisable($('#arrival_alert'));
    buttonEnable($('#alert_reset'));
  });

  $('#alert_reset').on('click', function() {
    ws.send(JSON.stringify({command: "alert_reset"}));
    buttonDisable($('#alert_reset'));
    buttonEnable($('#arrival_alert'));
  });

  function parseMessage(messageData) {
    // WebSocketで受け取ったJSONメッセージの処理
    message = messageData['message']
    if (message == 'robot_connected') {
       $('#robot_connection').text('ロボットが監視中')
    }
    if (message == 'robot_disconnected') {
      $('#robot_connection').text('誰も見ていません')
    }
  }

  function buttonEnable(button) {
    button.prop("disabled", false);
    button.prop("className", "button");
  }

  function buttonDisable(button) {
    button.prop("disabled", true);
    button.prop("className", "button-disable");
  }

  function printJSON() {
    $('#json-data').val(JSON.stringify(json, null, '  '));
  }

  function updateJSON(data) {
      json = data;
      printJSON();
  }

  function showPath(path) {
    $('#path').text(path);
  }

})();
