from zope.interface import Interface


class IJazShopSelectStringField(Interface):
    """Product Selection Field"""


class IJazShopMultiSelectStringField(Interface):
    """Multiple Product Selection Field"""


class IJazShopCheckoutAdapter(Interface):
    """Add items to cart and checkout"""
