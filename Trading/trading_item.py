class User:
    '''
    Evaluated behavior segment of a user
    '''
    def __init__(self, segment: str):
        self.segment = segment
        self.selling_decision = True
        self.min_price = 50.

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

    def __init__(self, brand: str = 'Chanel',
                 model: str = 'Classic Flap',
                 color: str = 'black',
                 material: str = 'lamb skin',
                 condition: str = 'new with tags',
                 owner=User('trader'),
                 time: int=0):
        self.brand = brand
        self.model = model
        self.color = color
        self.material = material
        self.condition = condition
        self.income = 0  # current income the platform got from this item
        self.cost = 0  # how much the platform has already paid for the item
        self.possession = 'user'  # who is current owner of the item
        self.t = time  # current item lifetime
        self.lifetime = None  # expected lifetime
        self.price_predicted = None  # predicted product price with the ending of expected lifetime - demand
        self.price_supply = None  # current supply price
        self.price_real = None  # current evaluated price of an item considering market objectives and product features
        self.price_transactional = None  # the platform defines which price to suggest
        self.owner = owner  # defines a user segment the owner belongs to
        self.state = True  # defines if item is live in the system of already left
        self.cur_state = 'start'  # a stage of item life period

    def __str__(self):
        output = \
        '%s %s bag.\nColor: %s. Meterial: %s. Condition: %s.\nOwner: a user from %s segment.\n' \
        %(self.brand, self.model, self.color, self.material, self.condition, self.owner) + \
        ('Live on platform for %i days out of expected %i days.\n' %(self.t, self.lifetime) if self.lifetime else
        'Live on platform for %i days.\n' %(self.t)) + \
        ('Current bag price: %d.' %self.price if self.price else '') + \
        'Belongs to: %s' %self.possession

        return(output)


if __name__ == "__main__":
    item = TradingItem()
    print(item)

