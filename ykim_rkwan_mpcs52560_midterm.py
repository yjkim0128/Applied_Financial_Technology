from datetime import timedelta, datetime

PYPL = Symbol.Create("PYPL", SecurityType.Equity, Market.USA)
SQ = Symbol.Create("SQ", SecurityType.Equity, Market.USA)

UL = Symbol.Create("UL", SecurityType.Equity, Market.USA)
PG = Symbol.Create("PG", SecurityType.Equity, Market.USA)

SPY = Symbol.Create("SPY", SecurityType.Equity, Market.USA)


class SMAPairsTrading(QCAlgorithm):
    def Initialize(self):
        self.SetStartDate(2018, 3, 1)
        self.SetEndDate(2018, 4, 1)
        self.SetCash(1000000)

        self.AddUniverseSelection(ManualUniverseSelectionModel([PYPL, SQ, UL, PG, SPY]))

        self.UniverseSettings.Resolution = Resolution.Hour
        self.UniverseSettings.DataNormalizationMode = DataNormalizationMode.Raw

        self.SetAlpha(CompositeAlphaModel(PairsAlpha_PYPL_SQ(), PairsAlpha_UL_PG()))

        self.SetPortfolioConstruction(EqualWeightingPortfolioConstructionModel())
        self.SetExecution(ImmediateExecutionModel())

    def OnEndOfDay(self, symbol):
        self.Log(
            "Taking a position of "
            + str(self.Portfolio[symbol].Quantity)
            + " units of symbol "
            + str(symbol)
        )


class PairsAlpha_PYPL_SQ(AlphaModel):
    def __init__(self):
        self.pair = []
        self.spreadMean = SimpleMovingAverage(500)
        self.spreadStd = StandardDeviation(500)
        self.period = timedelta(hours=2)

    def Update(self, algorithm, data):
        spread = self.pair[1].Price - self.pair[0].Price

        self.spreadMean.Update(algorithm.Time, spread)
        self.spreadStd.Update(algorithm.Time, spread)

        upperthreshold = self.spreadMean.Current.Value + self.spreadStd.Current.Value
        lowerthreshold = self.spreadMean.Current.Value - self.spreadStd.Current.Value

        if spread > upperthreshold:
            return Insight.Group(
                [
                    Insight.Price(
                        self.pair[0].Symbol, self.period, InsightDirection.Up
                    ),
                    Insight.Price(
                        self.pair[1].Symbol, self.period, InsightDirection.Down
                    ),
                    Insight.Price(
                        self.pair[2].Symbol, self.period, InsightDirection.Down
                    ),
                ]
            )
        elif spread < lowerthreshold:
            return Insight.Group(
                [
                    Insight.Price(
                        self.pair[0].Symbol, self.period, InsightDirection.Down
                    ),
                    Insight.Price(
                        self.pair[1].Symbol, self.period, InsightDirection.Up
                    ),
                    Insight.Price(
                        self.pair[2].Symbol, self.period, InsightDirection.Down
                    ),
                ]
            )
        return [Insight.Price(self.pair[2].Symbol, self.period, InsightDirection.Up)]

    def OnSecuritiesChanged(self, algorithm, changes):
        self.pair = [x for x in changes.AddedSecurities if x.Symbol in {PYPL, SQ}] + [
            x for x in changes.AddedSecurities if x.Symbol == SPY
        ]
        history = algorithm.History([x.Symbol for x in self.pair], 500)
        history = history.close.unstack(level=0)

        for tuple in history.itertuples():
            self.spreadMean.Update(tuple[0], tuple[2] - tuple[1])
            self.spreadStd.Update(tuple[0], tuple[2] - tuple[1])


class PairsAlpha_UL_PG(AlphaModel):
    def __init__(self):
        self.pair = []
        self.spreadMean = SimpleMovingAverage(500)
        self.spreadStd = StandardDeviation(500)
        self.period = timedelta(hours=2)

    def Update(self, algorithm, data):
        spread = self.pair[1].Price - self.pair[0].Price

        self.spreadMean.Update(algorithm.Time, spread)
        self.spreadStd.Update(algorithm.Time, spread)

        upperthreshold = self.spreadMean.Current.Value + self.spreadStd.Current.Value
        lowerthreshold = self.spreadMean.Current.Value - self.spreadStd.Current.Value

        if spread > upperthreshold:
            return Insight.Group(
                [
                    Insight.Price(
                        self.pair[0].Symbol, self.period, InsightDirection.Up
                    ),
                    Insight.Price(
                        self.pair[1].Symbol, self.period, InsightDirection.Down
                    ),
                    Insight.Price(
                        self.pair[2].Symbol, self.period, InsightDirection.Down
                    ),
                ]
            )
        elif spread < lowerthreshold:
            return Insight.Group(
                [
                    Insight.Price(
                        self.pair[0].Symbol, self.period, InsightDirection.Down
                    ),
                    Insight.Price(
                        self.pair[1].Symbol, self.period, InsightDirection.Up
                    ),
                    Insight.Price(
                        self.pair[2].Symbol, self.period, InsightDirection.Down
                    ),
                ]
            )
        return [Insight.Price(self.pair[2].Symbol, self.period, InsightDirection.Up)]

    def OnSecuritiesChanged(self, algorithm, changes):
        self.pair = [x for x in changes.AddedSecurities if x.Symbol in {UL, PG}] + [
            x for x in changes.AddedSecurities if x.Symbol == SPY
        ]
        history = algorithm.History([x.Symbol for x in self.pair], 500)
        history = history.close.unstack(level=0)

        for tuple in history.itertuples():
            self.spreadMean.Update(tuple[0], tuple[2] - tuple[1])
            self.spreadStd.Update(tuple[0], tuple[2] - tuple[1])
