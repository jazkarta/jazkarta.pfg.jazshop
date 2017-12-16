from decimal import Decimal
from zope.browserpage import ViewPageTemplateFile
from Products.Five import BrowserView
from jazkarta.shop.api import get_order_from_id
from jazkarta.shop.utils import resolve_uid
from jazkarta.shop.cart import Cart


class JazShopPFGCallback(BrowserView):
    """ Redirect to form's thank-you page, if available. """
    index = ViewPageTemplateFile('thanks.pt')

    def __call__(self):
        order_id = self.request.form.get('order_id')
        if order_id is not None:
            data = get_order_from_id(order_id)
            form_uid = data.get('pfg_form_uid')
            form = resolve_uid(form_uid)
        if order_id and form:
            try:
                thanks_page = form.restrictedTraverse('thank-you')
            except AttributeError:
                thanks_page = None
            if thanks_page:
                self.request.response.redirect(thanks_page.absolute_url())

        error = self.request.form.get('error', None)
        self.error = None
        mail_not_sent = self.request.form.get('mail_not_sent', None)
        self.mail_not_sent = None
        if error != None:
            error.replace("_", " ") # decode error message
            self.error = error
        if mail_not_sent != None:
            mail_not_sent.replace("_", " ") # decode error message
            self.mail_not_sent = mail_not_sent

        # get cart data from stored order
        data = get_order_from_id(order_id)
        self.cart_items = data['items'].items()
        self.cart_data = []
        self.amount = 0
        for order_item in self.cart_items:
            href = resolve_uid(order_item[1]['uid']).absolute_url()
            self.cart_data.append({'href': href,
                                   'quantity': order_item[1]['quantity'],
                                   'price': order_item[1]['price'],
                                   'name': order_item[1]['name']})
            self.amount += order_item[1]['quantity']*order_item[1]['price']

        self.amount += data['ship_charge']
        for tax_entry in data['taxes']:
            self.amount += tax_entry['tax']

        self.taxes = data['taxes']
        self.ship_method = data['ship_method']
        self.ship_charge = data['ship_charge']

        return self.index()
