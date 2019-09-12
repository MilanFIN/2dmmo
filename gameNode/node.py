import tornado.ioloop
import tornado.web
import tornado.websocket
import json
import os
import threading
import time
from websocket import create_connection

from engine.engine import Game


clientSendLock = threading.Lock()

masterSendQueLock = threading.Lock()
masterSendQue = []

alertsLock = threading.Lock()
alerts = []

loggedPlayersLock = threading.Lock()
loggedPlayers = []

reLoggedPlayersLock = threading.Lock()
reloggedPlayers = {}

"""
Pitää vielä handlata tilanne, jossa pelaaja yrittää kirjautua uudelleen ennen timerin umpeutumista
"""
idleClientsLock = threading.Lock()
idleClients = {} # use as [playername: (time, gamestate)]

clientsLock = threading.Lock()
clients = {}
game = Game()


masterAddress = "ws://localhost:3001/ws"
#masterAddress = "wss://asdf.dy.fi:3001/ws"
passphrase = "testipassu1234"
nodeName = "Finland 1"
nodeAddress = "http://localhost:8888"
#nodeAddress = "https://www.asdf.dy.fi:8888"
maxPlayers = 300
logoutTimer = 60





def updateAI(): #called every second independently from player actions, updates ai locations
    #game.moveAndRemoveNpcs()
    game.updateSquareCache()



    with alertsLock:
        #print(alerts[i][0])
        for alert in alerts:
            alert[1].write_message(alert[0])
        alerts.clear()

    with loggedPlayersLock:
        with clientsLock:
            for plr in loggedPlayers:
                destination = plr[1]
                userData = plr[0]
                if (len(clients) < maxPlayers):
                    clients[destination] = userData["name"]
                    game.addExistingPlayer(userData)
                    destination.timer_ = tornado.ioloop.PeriodicCallback(destination.updateClient, 200, jitter=0)
                    destination.timer_.start()
                else:
                    message = {"alert": "Server is full"}
                    destination.write_message(json.dumps(message))

            loggedPlayers.clear()
    with reLoggedPlayersLock:
        with clientsLock:
            for plr in reloggedPlayers:

                if (len(clients) < maxPlayers):
                    destination = reloggedPlayers[plr]
                    clients[destination] = plr
                    destination.timer_ = tornado.ioloop.PeriodicCallback(destination.updateClient, 200, jitter=0)
                    destination.timer_.start()
                else:
                    message = {"alert": "Server is full"}
                    destination.write_message(json.dumps(message))
        reloggedPlayers.clear()



def backUpGameState():

    try:
        ws = create_connection(masterAddress)

        for player in clients.values():
            gamestate = game.getGameState(player)
            #print("sent gamestate for", player)
            name = player
            message = {"action": "update", "passphrase": passphrase, "name": name, "gamestate": gamestate}
            ws.send(json.dumps(message))
    except Exception:
        print("could not connect to login server to backup gamestate")

def sendPlayerCount():
    ws = create_connection(masterAddress)
    with clientsLock:
        count = str(len(clients)) + "/" + str(maxPlayers)
        message = {"action": "serverStatus", "passphrase": passphrase, "nodeName": nodeName, "nodeAddress": nodeAddress, "playerCount": count}
        ws.send(json.dumps(message))



class Root(tornado.web.RequestHandler):
    def get(self):
        self.render("webContent/index.html")

class Static(tornado.web.StaticFileHandler):
    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")


class Controls(tornado.websocket.WebSocketHandler):


    def masterConnection():
        while True:

            with idleClientsLock:
                newIdles = {}
                global idleClients

                for client in idleClients:
                    if (time.time() - idleClients[client] < logoutTimer):
                        newIdles[client] = idleClients[client]
                    else:

                        gamestate = game.getGameState(client)
                        name = client
                        ws = create_connection(masterAddress)
                        message = {"action": "logout", "passphrase": passphrase, "name": name, "gamestate": gamestate}
                        ws.send(json.dumps(message))
                        game.removePlayer(client)

                        #print(client, "logged out")
                idleClients = newIdles


            if (len(masterSendQue) == 0):
                time.sleep(1)
            else:
                message, destination = ("", "")
                #print(message)
                with masterSendQueLock:

                    #print(masterSendQue)


                    message, destination = masterSendQue[0]
                    masterSendQue.pop(0)
                ws = create_connection(masterAddress)
                ws.send(json.dumps(message))
                result =  ws.recv()
                userData = json.loads(result)
                #print(userData)
                ws.close()
                if (userData["result"] == "login"):
                    #print("Received '%s'" % result)
                    with clientsLock:
                        if ("name" in userData):
                            if (userData["name"] not in clients.values()):
                                with loggedPlayersLock:
                                    loggedPlayers.append((userData, destination))

                elif (userData["result"] == "error"):
                    #print("incorrect username and password")
                    if (userData["type"] == "incorrect"):
                        with alertsLock:
                            result = ({"alert": userData["message"]}, destination)
                            alerts.append(result)
                    elif (userData["type"] == "duplicate" and "name" in userData):
                        with idleClientsLock:
                            if (userData["name"] in idleClients):

                                with clientsLock:
                                    if (userData["name"] not in clients.values()):
                                        #print("asd")

                                        with reLoggedPlayersLock:
                                            reloggedPlayers[userData["name"]] = destination
                                        del idleClients[userData["name"]]       
                            else:
                                result = ({"alert": userData["message"]}, destination)
                                alerts.append(result)





                        #destination.write_message({"alert": userData["message"]})


    def check_origin(self, origin):
        return True



    def open(self):
        pass

    def updateClient(self): #called every tick, updates player with content


        with clientsLock:

            game.allowMoving(clients[self])

            xyMap, objectLayer = game.printGameState(clients[self])

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
            tradeTargets = []
            tradeOffer = ""
            tradeItems = {}
            textInfo = ""
            if (infoType == "shop"):
                sellInfo = game.getShopSell(clients[self])
                buyInfo = game.getShopBuy(clients[self])
            elif (infoType == "bank"):
                bankBalance = game.getBankBalance(clients[self])
            elif (infoType == "chooseTradeTarget"):
                tradeTargets = game.getTradeCandidates(clients[self])
            elif (infoType == "tradeOffer"):
                tradeOffer = game.getTradeOffer(clients[self])
            elif (infoType == "tradeOffered"):
                infoType = "textInfo"
                textInfo = game.getTextInfo("tradeOffered")
            elif (infoType == "inTrade"):
                tradeItems = game.getTradeItems(clients[self])
                infoType = "inTrade"


            wear = game.getWear(clients[self])

        try:
            self.write_message({"map": xyMap, "objects": objectLayer, "size": size, "hp": hp, "messages": msgs,
                                "inventory": items, "infoType": infoType, "sellInfo": sellInfo,
                                "buyInfo": buyInfo, "bankBalance": bankBalance, "tradeTargets": tradeTargets,
                                "tradeOffer": tradeOffer, "textInfo": textInfo , "wear": wear, "tradeItems": tradeItems})
        except tornado.websocket.WebSocketClosedError:
            self.on_close


    def on_message(self, message):
        #print(asd.getMap())


        parsed_msg = json.loads(message)


        if (parsed_msg["action"] == "login"):


            #ws = create_connection(masterAddress)
            name = parsed_msg["name"]
            password = parsed_msg["password"]
            passphrase = "testipassu1234"
            message = {"action": "login", "passphrase": "testipassu1234", "name": name, "password": password}

            with masterSendQueLock:
                masterSendQue.append((message, self))



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
        if (parsed_msg["action"] == "act"):
            if (self in clients.keys()):
                game.doAction(clients[self])
        if (parsed_msg["action"] == "attack"):
            if (self in clients.keys()):
                game.attack(clients[self])



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

        if (parsed_msg["action"] == "useItem"):
            if (self in clients.keys()):
                itemToUse = parsed_msg["item"]
                game.useItem(clients[self], itemToUse)

        if (parsed_msg["action"] == "unWear"):
            if (self in clients.keys()):
                game.unWearAll(clients[self])


        if (parsed_msg["action"] == "offerTrade"):
            if (self in clients.keys()):
                opponent = parsed_msg["opponent"]
                game.offerTrade(clients[self], opponent)


        if (parsed_msg["action"] == "acceptTradeOffer"):
            if (self in clients.keys()):
                opponent = parsed_msg["opponent"]
                game.acceptTradeOffer(clients[self], opponent)


        if (parsed_msg["action"] == "declineTradeOffer"):
            if (self in clients.keys()):
                game.declineTradeOffer(clients[self])



        if (parsed_msg["action"] == "acceptTrade"):
            if (self in clients.keys()):
                game.acceptTrade(clients[self])

        if (parsed_msg["action"] == "declineTrade"):
            if (self in clients.keys()):
                game.declineTrade(clients[self])


        if (parsed_msg["action"] == "addTradeItem"):
            if (self in clients.keys()):
                item = parsed_msg["item"]
                game.addTradeItem(clients[self], item)


        if (parsed_msg["action"] == "removeTradeItem"):
            if (self in clients.keys()):
                item = parsed_msg["item"]
                game.removeTradeItem(clients[self], item)



        if (parsed_msg["action"] == "addTradeGold"):
            if (self in clients.keys()):
                amount = parsed_msg["amount"]
                game.addTradeGold(clients[self], amount)


        if (parsed_msg["action"] == "removeTradeGold"):
            if (self in clients.keys()):
                amount = parsed_msg["amount"]
                game.removeTradeGold(clients[self], amount)

        if (parsed_msg["action"] == "getTile"):
            if (self in clients.keys()):
                x = parsed_msg["x"]
                y = parsed_msg["y"]

                game.getTileInfo(clients[self], x, y)










    def on_close(self):

        with clientsLock:
            if (self in clients):

                with idleClientsLock:
                    # playername, logouttime
                    idleClients[clients[self]] =  time.time()


                #moved to different place?
                """
                gamestate = game.getGameState(clients[self])
                name = clients[self]
                ws = create_connection(masterAddress)
                message = {"action": "logout", "passphrase": passphrase, "name": name, "gamestate": gamestate}
                ws.send(json.dumps(message))
                game.removePlayer(clients[self])
                """

                del clients[self]
                self.timer_.stop()



        with loggedPlayersLock:
            for plr in loggedPlayers:
                if (plr[1] == self):
                    loggedPlayers.remove(plr)
                    break

            


            try:
                self.timer_.stop()
            except Exception:
                pass #timer never existed





def make_app():
    return tornado.web.Application([
        (r"/controls", Controls),

        (r"/", Root),
        (r'/(.*)', Static, {'path': './webContent/'}),


    ])

if __name__ == "__main__":
    app = make_app()

    http_server = tornado.httpserver.HTTPServer(app
                                                #,
                                                #ssl_options = {
                                                #    "certfile": os.path.join("certs/domain-crt.txt"),
                                                #    "keyfile": os.path.join("certs/domain-key.txt"),
                                                #}
    )

    http_server.listen(8888)



    #app.listen(8888)
    AITimer_ = tornado.ioloop.PeriodicCallback(updateAI, 1000, jitter=0)
    backUpTimer = tornado.ioloop.PeriodicCallback(backUpGameState, 600000, jitter=0)
    playerCountUpdateTimer = tornado.ioloop.PeriodicCallback(sendPlayerCount, 15000, jitter=0)

    AITimer_.start()
    backUpTimer.start()
    playerCountUpdateTimer.start()

    t1 = threading.Thread(target=Controls.masterConnection, args = ())
    t1.start()

    tornado.ioloop.IOLoop.current().start()
    t1.join()
