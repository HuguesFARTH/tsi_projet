class TimerDebug:
    def __init__(self,main):
        self.main = main
        self.single = {}
        self.dics = {}
        self.nano_dics = {}
        self.traite = {}
        self.call = {}
        self.nano_traite = {}
        self.single_traite = {}

    def reset(self):
        if len(self.dics) > 0:
            print("Attention il y a un oublie de fermeture de timer pour le TimerDebug")
        self.dics.clear()
        self.traite.clear()
        self.single.clear()
        self.single_traite.clear()
        self.nano_dics.clear()
        self.nano_traite.clear()

    def start(self,name):
        # print(str(" | " * len(self.dics)), "+", name)
        if not name in self.dics:
            self.dics[name] = self.main.msTime()

    def end(self):
        last = list(self.dics.items())[-1]
        if last[0] in self.traite:
            self.traite[last[0]] += self.main.msTime()-last[1]
            self.call[last[0]] += 1
        else:
            self.traite[last[0]] = self.main.msTime()-last[1]
            self.call[last[0]] = 1
        # print(str(" | " * (len(self.dics)-1)), "-", last[0])
        self.dics.pop(last[0])

    def startNano(self,name):
        if not name in self.nano_dics:
            self.nano_dics[name] = self.main.nanoTime()

    def endNano(self):
        last = list(self.nano_dics.items())[-1]
        if last[0] in self.nano_traite:
            self.nano_traite[last[0]] += self.main.nanoTime()-last[1]
        else:
            self.nano_traite[last[0]] = self.main.nanoTime()-last[1]
        self.nano_dics.pop(last[0])

    def startSingle(self,name):
        if not name in self.single:
            self.single[name] = self.main.nanoTime()

    def endSingle(self,name):
        if name in self.single:
            last = self.single[name]
            self.single_traite[name] = self.main.nanoTime()-last
            del self.single[name]

    def print(self, ticks, frames):
        print(ticks," ticks, ",frames," fps")
        print("Nbr entitiées: ",len(self.main.entities))
        print("-----TimerDebug-----")
        for k,v in self.traite.items():
            print("  -",k,":",v," ms","call:",round(self.call[k]/(ticks if not ticks == 0 else 1),2),"/tick")
        # print("--Nano--")
        # for k,v in self.nano_traite.items():
            # print("  -",k,":",v," ns")
        # print("--Single--")
        # for k,v in self.single_traite.items():
            # print("  -",k,":",v," ns")
        print("--------------------")
