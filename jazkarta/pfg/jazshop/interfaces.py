from zope.interface import Interface


class IJazShopSelectStringField(Interface):
    """Product Selection Field"""


class IJazShopMultiSelectStringField(Interface):
    """Multiple Product Selection Field"""


class IJazShopArbitraryPriceStringField(Interface):
    """Arbitrary Price String Field"""


class IJazShopCheckoutAdapter(Interface):
    """Add items to cart and checkout"""
