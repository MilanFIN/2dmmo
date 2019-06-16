#!/usr/bin/python
import tornado.websocket
import tornado.ioloop
import tornado.web
import psycopg2
import json



connection = psycopg2.connect(user = "mmo",
                              password = "mmo",
                              host = "127.0.0.1",
                              port = "5432",
                              database = "postgres")
cursor = connection.cursor()



class Root(tornado.web.RequestHandler):
    def get(self):
        self.render("webContent/index.html")
    def post(self):
        name = self.get_argument('username')
        passwd = self.get_argument('password')
        gst = {"worldx":0, "worldy":0, "x":0, "y":0, "gold":10, "bankGold":0}
        gamestate = json.dumps(gst)
        query =  "INSERT INTO mmo (name, password, gamestate) VALUES (%s, %s, %s);"

        data = (name, passwd, gamestate)
        cursor.execute(query, data)
        connection.commit()
        self.render("webContent/registered.html")


class wshandler(tornado.websocket.WebSocketHandler):

    def open(self):
        pass
    def on_message(self, message):
        parsed_msg = json.loads(message)

        if (parsed_msg["passphrase"] == "testipassu1234"):
            if (parsed_msg["action"] == "update"):
            #query =  "INSERT INTO mmo (name, password, gamestate) VALUES (%s, %s, %s);"

                query = "UPDATE mmo SET gamestate = %s WHERE name = %s";
                data = (json.dumps(parsed_msg["gamestate"]), parsed_msg["name"])
                cursor.execute(query, data)
                connection.commit()


            if (parsed_msg["action"] == "login"):
                name = parsed_msg["name"]
                passwd = parsed_msg["password"]

                query = "SELECT name, gamestate FROM mmo WHERE name = %s and password = %s";
                data = (name, passwd)
                cursor.execute(query, data)
                userdata = cursor.fetchall()
                #connection.commit()
                if (userdata == []):
                    result = {"result": "error"}
                    self.ws_connection.write_message(json.dumps(result))
                else:
                    userdata2 = {"result": "login", "name": userdata[0][0], "gamestate":userdata[0][1]}
                    self.ws_connection.write_message(json.dumps(userdata2))
        else:
            result = {"result": "error"}
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
