from decimal import Decimal
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

JazShopCheckoutAdapterSchema = FormAdapterSchema.copy() + atapi.Schema((
    atapi.StringField('formIdExpression',
        required=False,
        default='',
        description="""Expression containing one or more field names to be
                       prepended to order data on Jazkarta Shop orders page.
                       Field names must be enclosed in brackets.
                       Example: {last_name}, {first_name}: """,
    ),
))

finalizeATCTSchema(JazShopCheckoutAdapterSchema)


@implementer(IPloneFormGenActionAdapter, IJazShopCheckoutAdapter)
class JazShopCheckoutAdapter(FormActionAdapter):
    meta_type = 'JazShopCheckoutAdapter'
    schema = JazShopCheckoutAdapterSchema

    def onSuccess(self, fields, REQUEST=None):
        item_prepend = None
        if getattr(self, 'formIdExpression', None):
            try:
                item_prepend = self.formIdExpression.format(**REQUEST.form)
            except (KeyError, ValueError):
                pass
        cart = Cart.from_request(REQUEST)
        products = []
        arbitrary = []
        for field in fields:
            if field.portal_type in JAZSHOP_FIELDS:
                value = REQUEST.form.get(field.id)
                if not value:
                    continue
                if isinstance(value, list):
                    value = map(lambda x: x.split('|')[-1], value)
                    products.extend(value)
                else:
                    value = value.split('|')[-1]
                    products.append(value)
            if field.portal_type == 'JazShopArbitraryPriceStringField':
                price = REQUEST.form.get(field.id)
                if not price or not field.availableProducts:
                    continue
                product_value = field.availableProducts[0]
                product_uid = product_value.split('|')[-1]
                cart.add_product(product_uid)
                arbitrary.append(product_uid)
                for item in cart._items.values():
                    if item['uid'] == product_uid:
                        price = price.replace('$', '')
                        item['price'] = Decimal(price)
        for uid in products:
            cart.add_product(uid)
        if item_prepend is not None:
            for item in cart._items.values():
                if (item['uid'] in (products + arbitrary) and
                        not item['name'].startswith(item_prepend)):
                    item['name'] = item_prepend + item['name']
        # store form fields and reference to this form
        if 'order_details' not in cart.data:
            cart.data['order_details'] = ''
        details = '<p></p><h3>{}</h3><dl>'.format(self.aq_parent.title)
        form_fields = {}
        fields = self.aq_parent._getFieldObjects()
        for field in fields:
            if field.id in REQUEST.form:
                form_fields[field.id] = REQUEST.form.get(field.id)
                label = field.fgField.widget.label
                value = field.htmlValue(REQUEST)
                details += '<dt>{}</dt><dd>{}</dd>'.format(label, value)
        details += '</dl><p></p>'
        cart.data['order_details'] += details
        if 'pfg_forms' not in cart.data:
            cart.data['pfg_forms'] = {}
        pfg_form_uid = self.aq_parent.UID()
        cart.data['pfg_forms'][pfg_form_uid] = form_fields
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
