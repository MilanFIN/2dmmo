#!/usr/bin/python
import tornado.websocket
import tornado.ioloop
import tornado.web
import psycopg2
import json
import time


connection = psycopg2.connect(user = "mmo",
                              password = "mmo",
                              host = "127.0.0.1",
                              port = "5432",
                              database = "postgres")
cursor = connection.cursor()

defaultLoadout = {"worldx":0, "worldy":0, "x":10, "y":10, "gold":10, "bankgold":0}
playersOnline = {}


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

                checkQuery = "SELECT name FROM mmo WHERE name = %s and %s = %s"
                data = (parsed_msg["name"], "s", "s")
                cursor.execute(checkQuery, data)
                existing = cursor.fetchall()

                if (existing != []):
                    self.write_message({"result": "error", "message": "username is taken"})
                else:
                    name = parsed_msg["name"]
                    passwd = parsed_msg["password"]
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

                    if (name in playersOnline):
                        result = {"result": "error", "message": "already logged in"}
                        self.ws_connection.write_message(json.dumps(result))
                    else:
                        passwd = parsed_msg["password"]
                        query = "SELECT name, gamestate FROM mmo WHERE name = %s and password = %s"
                        data = (name, passwd)
                        cursor.execute(query, data)
                        userdata = cursor.fetchall()
                        #connection.commit()
                        if (userdata == []):
                            result = {"result": "error", "message": "wrong username or password"}
                            self.ws_connection.write_message(json.dumps(result))
                        else:
                            userdata2 = {"result": "login", "name": userdata[0][0], "gamestate":userdata[0][1]}
                            self.ws_connection.write_message(json.dumps(userdata2))
                            playersOnline[name] = time.time()
                            #state = json.loads(userdata[0][1])

            else:
                result = {"result": "error", "messasge": "not authorized"}
                self.ws_connection.write_message(json.dumps(result))



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
    app.listen(3001)
    tornado.ioloop.IOLoop.current().start()
