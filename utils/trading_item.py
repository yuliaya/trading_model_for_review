import numpy
from utils.market_state import Market

class User:
    '''
    Evaluated behavior segment of a user
    '''
    def __init__(self, market: Market):
        if market.segmentation:
            segments = list(market.segments.keys())
            segments_p = [market.segments[s]['p'] for s in segments]
            self.segment = numpy.random.choice(segments, p=segments_p)
        else:
            segments = list(market.segments.keys())
            self.segment = segments[0]
        self.max_reduce = numpy.random.uniform(low=0.9 - market.segments[self.segment]['reduce_math_exp'],
                                               high=1.1 - market.segments[self.segment]['reduce_math_exp'])
        self.days_abandoned = None

    def __str__(self):
        return self.segment


class TradingItem:
    '''
    A single product on the market and its features.
    Has 3 types of features:
    1. objective characteristics (color, size etc),
    2. predicted features (expected lifetime, expected price etc),
    3. state features (possession, owner etc)
    '''

    def __init__(self,
                 market: Market,
                 time_created_period: int,
                 brand: str = 'Chanel',
                 color: str = 'black',
                 size: str = 'Medium',
                 material: str = 'lamb skin',
                 condition: str = 'new with tags'
                 ):
        self.brand = brand
        self.color = color
        self.size = size
        self.material = material
        self.condition = condition
        self.income = 0  # current income the platform got from this item
        self.cost = 0  # how much the platform has already paid for the item
        self.possession = 'user'  # who is current owner of the item
        self.time_created_period = time_created_period  # an epoch when the item was created
        self.cur_time_period = time_created_period  # current epoch for the item
        self.lifetime_prob = None  # expected probability to be sold during the first 30 days
        self.lifetime_prob_real = None  # correct probability after considering error
        self.price = None
        self.retail_price = None  # retail price of median retail of a similar
        self.owner = User(market)  # defines a user segment the owner belongs to
        self.state = True  # defines if item is live in the system or already left


    def __str__(self):
        output = 'Item created at %s epoch. \n' % self.time_created_period + \
        '%s bag.\nSize: %s. Color: %s. Meterial: %s. Condition: %s.\nOwner: a user from %s segment.\n' \
        % (self.brand, self.size, self.color, self.material, self.condition, self.owner) + \
        'Prob to leave in 30 days: %s\n' % self.lifetime_prob_real+ \
        'Price: %d.\n' % self.price + 'Belongs to: %s \n\n' %self.possession
        return(output)


if __name__ == "__main__":
    item = TradingItem(time_created_period=0)
    print(item)

