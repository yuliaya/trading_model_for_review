class Market:
    '''
    Defines current market state: Epoch, distribution of user features, distribution of product features etc
    '''
    def __init__(self,
                 lifetime_period: int = 300,
                 platform_interest: float=0.2):
        self.epoch = 0
        self.life_period = lifetime_period  # number of epochs
        self.platform_interest = platform_interest  # commission for trading
