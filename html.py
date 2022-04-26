html = """\
    <html>
  <head>
    <title>ESP Web Server</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <link rel="icon" href="data:," />
    <style>
      html {
        font-family: Helvetica;
        display: inline-block;
        margin: 0px auto;
        text-align: center;
        background-color: #918F8F;
      }
      h1 {
        color: #0f3376;
        padding: 2vh;
      }
      p {
        font-size: 1.5rem;
      }
      table {
        width: 30%;
      }
      td input {
        width: 100%;
      }
      .button {
        display: inline-block;
        background-color: #e7bd3b;
        border: none;
        border-radius: 4px;
        color: white;
        padding: 8px 20px;
        text-decoration: none;
        font-size: 15px;
        margin: 2px;
        cursor: pointer;
      }
      .button2 {
        background-color: #4286f4;
      }
      .button.rm {
        color: black;
        background-color: red;
        padding: 2px 15px;
      }
      .center {
          margin-left: auto;
          margin-right: auto;
      }
    </style>
  </head>
  <body>
    <h1>ESP Web Server</h1>
    <p>MQTT state: <strong>Connected</strong></p>
      <table class="center">
        <tr>
          <th>Raw Address</th>
          <th>Friendly name</th>
          <th>Alive</th>
        </tr><form method="post" action="">"""