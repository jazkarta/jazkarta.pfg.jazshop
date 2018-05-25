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

    def _get_item_details(self, pfg_form, REQUEST):
        details = '<p></p><h2>{}</h2><dl>'.format(pfg_form.title)
        form_fields = {}
        fields = pfg_form._getFieldObjects()
        for field in fields:
            label = field.fgField.widget.label
            value = field.htmlValue(REQUEST)
            form_fields[field.id] = value
            details += '<dt>{}</dt><dd>{}</dd>'.format(label, value)
        details += '</dl><p></p>'
        return form_fields, details

    def onSuccess(self, fields, REQUEST=None):
        item_prepend = None
        if getattr(self, 'formIdExpression', None):
            try:
                item_prepend = self.formIdExpression.format(**REQUEST.form)
            except (KeyError, ValueError):
                pass
        cart = Cart.from_request(REQUEST)
        products = []
        pfg_products = []
        arbitrary = []
        if 'pfg_products' not in cart.data:
            cart.data['pfg_products'] = {}
        if 'pfg_details' not in cart.data:
            cart.data['pfg_details'] = {}
        if 'pfg_forms' not in cart.data:
            cart.data['pfg_forms'] = {}
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
            if uid != '0':
                cart.add_product(uid)
                pfg_products.append(uid)
        if item_prepend is not None:
            for item in cart._items.values():
                if (item['uid'] in (products + arbitrary) and
                        not item['name'].startswith(item_prepend)):
                    item['name'] = item_prepend + item['name']
        # store form fields and reference to this form
        pfg_form = self.aq_parent
        pfg_form_uid = self.aq_parent.UID()
        cart.data['pfg_products'][pfg_form_uid] = pfg_products
        fields, details = self._get_item_details(pfg_form, REQUEST)
        cart.data['pfg_forms'][pfg_form_uid] = fields
        cart.data['pfg_details'][pfg_form_uid] = details
        order_details = ''
        cart_products = [i.uid for i in cart.items]
        for form_uid in cart.data['pfg_forms'].keys():
            form_products = cart.data['pfg_products'][pfg_form_uid]
            in_cart = True
            for p in form_products:
                if p not in cart_products:
                    in_cart = False
            if in_cart:
                order_details += cart.data['pfg_details'][pfg_form_uid]
        cart.data['order_details'] = order_details
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
