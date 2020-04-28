class User:
    '''
    Evaluated behavior segment of a user
    '''
    def __init__(self, segment: str = 'trader'):
        self.segment = segment
        self.min_price = None
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
                 time_created_period: int,
                 brand: str = 'Chanel',
                 color: str = 'black',
                 size: str = 'Medium',
                 material: str = 'lamb skin',
                 condition: str = 'new with tags',
                 owner=User(),
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
        #self.max_price = None  # maximum price so that the item can be sold in the next 30 days
        self.owner = owner  # defines a user segment the owner belongs to
        self.state = True  # defines if item is live in the system or already left
        #self.cur_state = 'start'  # a stage of item life

    def __str__(self):
        output = \
        '%s bag.\nSize: %s. Color: %s. Meterial: %s. Condition: %s.\nOwner: a user from %s segment.\n' \
        % (self.brand, self.size, self.color, self.material, self.condition, self.owner) + \
        (('Prob to leave in 30 days: %d\n' % self.lifetime_prob) if self.lifetime_prob else '')+ \
        (('Retail price: %d.\n' % self.retail_price) if self.retail_price else '') + \
        (('Max price: %d.\n' % self.max_price) if self.max_price else '') + \
        'Belongs to: %s\nCurrent state: %s' %(self.possession, self.cur_state)

        return(output)


if __name__ == "__main__":
    item = TradingItem(time_created_period=0)
    print(item)

