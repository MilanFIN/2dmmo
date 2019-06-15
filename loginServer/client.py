from websocket import create_connection
import json





ws = create_connection("ws://localhost:3001/ws")
print("Sending 'Hello, World'...")
name = "asd"
gamestate = {"worldx":0, "worldy":1}
message2 = {"passphrase":"testipassu1234", "action":"update", "name":name, "gamestate": gamestate}
message = {"passphrase":"testipassu1234", "action":"login", "name":name, "password":"testi"}

ws.send(json.dumps(message))
print("Sent")
print("Reeiving...")
result =  ws.recv()
print("Received '%s'" % result)
ws.close()
