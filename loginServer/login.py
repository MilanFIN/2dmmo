#!/usr/bin/python
import tornado.websocket
import tornado.ioloop
import tornado.web
import psycopg2
import json
import time
import os
from argon2 import PasswordHasher



connection = psycopg2.connect(user = "mmo",
                              password = "mmo",
                              host = "127.0.0.1",
                              port = "5432",
                              database = "postgres")
cursor = connection.cursor()

ph = PasswordHasher()

defaultLoadout = {"worldx":0, "worldy":0, "x":10, "y":10, "gold":10, "bankgold":0}
playersOnline = {}
ClientDropTimeout = 1250000 #25 minutes, getting updates every 10



def dropLostClients():
    for player in playersOnline:
        if (time.time() - playersOnline[player] > ClientDropTimeout):
            playersOnline.pop(player, None)


class Root(tornado.web.RequestHandler):
    def get(self):
        self.render("webContent/index.html")



class wshandler(tornado.websocket.WebSocketHandler):

    def open(self):
        pass
    def on_message(self, message):
        parsed_msg = json.loads(message)


        #register request is made by the browser and as such doesn't require authorization
        if (parsed_msg["action"] == "register"):
            if ("name" in parsed_msg and "password" in parsed_msg):

                if (len(parsed_msg["name"]) > 50):
                    self.write_message({"result": "error", "message": "username is too long"})
                    return
                if (len(parsed_msg["password"]) < 8):
                    self.write_message({"result": "error", "message": "password must be atleast 8 characters long"})
                    return




                checkQuery = "SELECT name FROM mmo WHERE name = %s and %s = %s"
                data = (parsed_msg["name"], "s", "s")
                cursor.execute(checkQuery, data)
                existing = cursor.fetchall()

                if (existing != []):
                    self.write_message({"result": "error", "message": "username is taken"})
                else:
                    name = parsed_msg["name"]
                    passwd = parsed_msg["password"]
                    passwd = ph.hash(passwd)


                    gst = defaultLoadout
                    gamestate = json.dumps(gst)
                    query =  "INSERT INTO mmo (name, password, gamestate) VALUES (%s, %s, %s);"

                    data = (name, passwd, gamestate)
                    cursor.execute(query, data)
                    connection.commit()
                    self.write_message({"result": "register", "message": "you registered with the username " + parsed_msg["name"] + " You can now login with that name"})


        #this stuff requires a passphrase as its gameplay critical and is made by the servernode
        if ("passphrase" in parsed_msg):


            if (parsed_msg["passphrase"] == "testipassu1234"):

                #logout, store gamestate and remove player from known online players
                if (parsed_msg["action"] == "logout" and "name" in parsed_msg and "gamestate" in parsed_msg):

                    query = "UPDATE mmo SET gamestate = %s WHERE name = %s";
                    data = (json.dumps(parsed_msg["gamestate"]), parsed_msg["name"])
                    cursor.execute(query, data)
                    connection.commit()

                    if (parsed_msg["name"] in playersOnline):
                        del playersOnline[parsed_msg["name"]]


                    print(json.dumps(parsed_msg["gamestate"]))


                #store gamestate for backup
                if (parsed_msg["action"] == "update" and "name" in parsed_msg and "gamestate" in parsed_msg):
                #query =  "INSERT INTO mmo (name, password, gamestate) VALUES (%s, %s, %s);"

                    query = "UPDATE mmo SET gamestate = %s WHERE name = %s";
                    data = (json.dumps(parsed_msg["gamestate"]), parsed_msg["name"])
                    cursor.execute(query, data)
                    connection.commit()

                    playersOnline[parsed_msg["name"]] = time.time()




                #laod gamestate and add to online players
                elif (parsed_msg["action"] == "login"):
                    name = parsed_msg["name"]


                    passwd = parsed_msg["password"]
                    query = "SELECT name, gamestate, password FROM mmo WHERE name = %s and %s = %s"
                    data = (name, "s", "s")
                    cursor.execute(query, data)
                    userdata = cursor.fetchall()
                    #connection.commit()
                    if (userdata == []):
                        result = {"result": "error", "message": "Wrong username or password."}
                        self.ws_connection.write_message(json.dumps(result))
                    elif (name in playersOnline):
                        result = {"result": "error", "message": "That user is already logged in."}
                        self.ws_connection.write_message(json.dumps(result))
                    else:
                        name = userdata[0][0]
                        gamestate = userdata[0][1]
                        pwhash = userdata[0][2]

                        try:
                            ph.verify(pwhash, passwd)

                            userdata2 = {"result": "login", "name": userdata[0][0], "gamestate":userdata[0][1]}
                            self.ws_connection.write_message(json.dumps(userdata2))
                            playersOnline[name] = time.time()
                        except Exception:
                            result = {"result": "error", "message": "Wrong username or password."}
                            self.ws_connection.write_message(json.dumps(result))

                        #state = json.loads(userdata[0][1])


        #query =  "INSERT INTO mmo (name, password, gamestate) VALUES (%s, %s, %s);"
        #data = ("asd", "testi", json.dumps({"state":"null"}))


def make_app():
    return tornado.web.Application([
        (r"/", Root),
        (r"/ws", wshandler),

        #(r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    http_server = tornado.httpserver.HTTPServer(app,
                                                ssl_options = {
                                                    "certfile": os.path.join("certs/domain-crt.txt"),
                                                    "keyfile": os.path.join("certs/domain-key.txt"),
    })
    http_server.listen(3001)
    DropLostTimer = tornado.ioloop.PeriodicCallback(dropLostClients, 600000, jitter=0)


    DropLostTimer.start()
    tornado.ioloop.IOLoop.current().start()
