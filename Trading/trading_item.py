class User:
    def __init__(self, segment: str):
        self.segment = segment

    def __str__(self):
        return self.segment


class TradingItem:
    def __init__(self, brand: str, model: str, color: str, material: str, condition: int, owner: User):
        self.brand = brand
        self.model = model
        self.color = color
        self.material = material
        self.condition = condition
        self.income = 0  # income the platform can have from this item
        self.cost = 0  # how much the platform has already paid for the item
        self.possession = 'user'  # who is current owner of the item
        self.price = None
        self.t = 0  # current item lifetime
        self.lifetime = None  # expected lifetime
        self.owner = owner  # defines a user segment the owner belongs to

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
    user = User('trader')
    item = TradingItem('Chanel', 'Classic Flap', 'black', 'lamb skin', 'new with tags', user)
    print(item)

