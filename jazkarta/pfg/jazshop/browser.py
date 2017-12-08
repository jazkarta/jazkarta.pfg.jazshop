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

        user_id = self.request.form.get('user_id', None)
        browser_id = self.request.form.get('browser_id', None)
        if user_id != None or browser_id != None:
            # recreate the cart so that the default thank you template can
            # access it
            self.cart = Cart.from_request(self.request,
                user_id=user_id, browser_id=browser_id)
        return self.index()
