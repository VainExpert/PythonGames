
    def trainBot(self):

        """
        Trains a NN+MCTS-Bot of set Strength
        *Don't show Training and Optimization but show Progressbar*
        """

        eps, sims, strengthName = self.strength
        Trainer = GameTraining(strengthName, eps, sims, self.gcls, self.NN)

        self.Logger.subtitle("Train {} Bot".format(strengthName))
        self.Logger.log("info", "Creating examples.")
        if strengthName == "cust":
            Trainer.customExamples()

        elif strengthName == "best":
            Trainer.solvedExamples()

        else:
            Trainer.createExamples()

        self.Logger.log("info", "Training.")
        Trainer.trainNN()
        self.NN.save_checkpoint(folder="{}/models".format(self.gamename), filename="{}.pth.tar".format(strengthName))

        self.Logger.log("info", "Testing.")
        optimize = Trainer.testNN()

        while optimize:
            self.Logger.log("info", "Optimizing.")
            Trainer.optimizeNN()

            self.Logger.log("info", "Testing.")
            optimize = Trainer.testNN()

        self.playVBotMenu()
