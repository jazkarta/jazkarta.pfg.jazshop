from zope.interface import implementer
from Products.Archetypes import atapi
from Products.ATContentTypes.content.schemata import finalizeATCTSchema
from Products.PloneFormGen.content.actionAdapter import FormActionAdapter
from Products.PloneFormGen.content.actionAdapter import FormAdapterSchema
from Products.PloneFormGen.interfaces import IPloneFormGenActionAdapter
from jazkarta.shop.cart import Cart
from Products.statusmessages.interfaces import IStatusMessage
from .config import PROJECTNAME
from .interfaces import IJazShopCheckoutAdapter


JAZSHOP_FIELDS = ['JazShopSelectStringField',
                  'JazShopMultiSelectStringField']

JazShopCheckoutAdapterSchema = FormAdapterSchema.copy()
finalizeATCTSchema(JazShopCheckoutAdapterSchema)


@implementer(IPloneFormGenActionAdapter, IJazShopCheckoutAdapter)
class JazShopCheckoutAdapter(FormActionAdapter):
    meta_type = 'JazShopCheckoutAdapter'
    schema = JazShopCheckoutAdapterSchema

    def onSuccess(self, fields, REQUEST=None):
        cart = Cart.from_request(REQUEST)
        products = []
        for field in fields:
            if field.portal_type in JAZSHOP_FIELDS:
                value = REQUEST.form.get(field.id)
                if not value:
                    continue
                if isinstance(value, list):
                    products.extend(value)
                else:
                    products.append(value)
            if field.portal_type == 'JazShopArbitraryPriceStringField':
                price = REQUEST.form.get(field.id)
                if not price or not field.availableProducts:
                    continue
                product_uid = field.availableProducts[0]
                cart.add_product(product_uid)
                for item in cart._items.values():
                    if item['uid'] == product_uid:
                        item['price'] = price
        for uid in products:
            cart.add_product(uid)
        # store reference to this form
        cart.data['pfg_form_uid'] = self.aq_parent.UID()
        cart.save()


def add_checkout_redirect_after_creation(adapter, event):
    redirect_to = 'redirect_to:string:${portal_url}/checkout'
    success_override = adapter.aq_parent.getThanksPageOverride()
    if success_override:
        message = """By default, this adapter redirects the user to
            the Jazkarta Shop checkout after a successful submission.
            However, this form already has an active override. The
            checkout override was not added. Please see the documentation
            for information on how to set it manually."""
        messages = IStatusMessage(event.object.REQUEST)
        messages.add(message)
    else:
        adapter.aq_parent.setThanksPageOverride(redirect_to)

atapi.registerType(JazShopCheckoutAdapter, PROJECTNAME)
