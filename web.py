import tornado.ioloop
import tornado.web
import tornado.websocket
import json
from engine.engine import Game





clients = {}
game = Game()



def updateAI(): #called every second independently from player actions, updates ai locations
    #game.moveAndRemoveNpcs()
    game.updateSquareCache()

class Root(tornado.web.RequestHandler):
    def get(self):
        self.render("webContent/index.html")

class Controls(tornado.websocket.WebSocketHandler):


    def open(self):
        pass

    def updateClient(self): #called every tick, updates player with content
        game.allowMoving(clients[self])

        xyMap = game.printGameState(clients[self])

        hp = game.getPlayerHp(clients[self])

        size = game.getSize()

        msgs = game.getMessages(clients[self])
        game.clearMessages(clients[self])

        items = game.getItems(clients[self])

        infoType = "none"
        infoType = game.getActionStatus(clients[self])

        sellInfo = ""
        buyInfo = ""
        bankBalance = ""
        if (infoType == "shop"):
            sellInfo = game.getShopSell(clients[self])
            buyInfo = game.getShopBuy(clients[self])
        elif (infoType == "bank"):
            bankBalance = game.getBankBalance(clients[self])

        wear = game.getWear(clients[self])


        self.write_message({"map": xyMap, "size": size, "hp": hp, "messages": msgs, "inventory": items, "infoType": infoType, "sellInfo": sellInfo, "buyInfo": buyInfo, "bankBalance": bankBalance, "wear": wear })
        # self.write_message(json.dumps(xyMap))


    def on_message(self, message):
        #print(asd.getMap())
        parsed_msg = json.loads(message)
        if (parsed_msg["action"] == "register"):

            if (parsed_msg["name"] not in clients.values()):
                clients[self] = parsed_msg["name"]
                #print(clients)
                game.addPlayer(parsed_msg["name"])
                #print(parsed_msg["name"] + " registered")
                self.timer_ = tornado.ioloop.PeriodicCallback(self.updateClient, 200, jitter=0)

                self.timer_.start()
            else:
                self.write_message({"alert": "Name is already taken."})


        if (parsed_msg["action"] == "moveRight"):
            if (self in clients.keys()):
                game.movePlayerRight(clients[self])
        if (parsed_msg["action"] == "moveLeft"):
            if (self in clients.keys()):
                game.movePlayerLeft(clients[self])
        if (parsed_msg["action"] == "moveUp"):
            if (self in clients.keys()):
                game.movePlayerUp(clients[self])
        if (parsed_msg["action"] == "moveDown"):
            if (self in clients.keys()):
                game.movePlayerDown(clients[self])
        if (parsed_msg["action"] == "newMessage"):
            try:
                newMessage = parsed_msg["msg"]
                game.addMessageToNeighbors(clients[self], newMessage)
            except Exception:
                pass
        if (parsed_msg["action"] == "doAction"):
            if (self in clients.keys()):
                game.doAction(clients[self])


        if (parsed_msg["action"] == "changeBalance"):
            if (self in clients.keys()):
                change = parsed_msg["amount"]
                game.changeBankBalance(clients[self], change)


        if (parsed_msg["action"] == "sellItem"):
            if (self in clients.keys()):
                itemToSell = parsed_msg["item"]
                game.sellItem(clients[self], itemToSell)

        if (parsed_msg["action"] == "buyItem"):
            if (self in clients.keys()):
                itemToBuy = parsed_msg["item"]
                game.buyItem(clients[self], itemToBuy)

        if (parsed_msg["action"] == "wearItem"):
            if (self in clients.keys()):
                itemToWear = parsed_msg["item"]
                game.wearItem(clients[self], itemToWear)

        if (parsed_msg["action"] == "unWear"):
            if (self in clients.keys()):
                game.unWearAll(clients[self])






    def on_close(self):
        try:
            game.removePlayer(clients[self])
        except Exception:
            pass

        try:
            del clients[self]
            print("Player left")
        except KeyError:
            print("Player left, but nobody cares as they never registered")

        try:
            self.timer_.stop()
        except Exception:
            pass #timer never existed



def make_app():
    return tornado.web.Application([
        (r"/controls", Controls),

        (r"/", Root),
        (r'/(.*)', tornado.web.StaticFileHandler, {'path': './webContent/'}),


    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    AITimer_ = tornado.ioloop.PeriodicCallback(updateAI, 1000, jitter=0)
    AITimer_.start()

    tornado.ioloop.IOLoop.current().start()
