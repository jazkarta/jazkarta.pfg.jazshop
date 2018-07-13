import csv
from collections import OrderedDict
from DateTime import DateTime
from StringIO import StringIO
from zope.browserpage import ViewPageTemplateFile
from Products.Five import BrowserView
from jazkarta.shop.api import get_order_from_id
from jazkarta.shop.browser.controlpanel import DateMixin, _fetch_orders
from jazkarta.shop.utils import resolve_uid
from jazkarta.shop import storage
from plone.uuid.interfaces import IUUID


class JazShopPFGCallback(BrowserView):
    """ Redirect to form's thank-you page, if available. """
    index = ViewPageTemplateFile('thanks.pt')

    def __call__(self):
        order_id = self.request.form.get('order_id')
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

        self.cart_items = []
        self.cart_data = []
        self.amount = 0
        self.ship_method = None
        self.ship_charge = None
        self.taxes = None
        if order_id:
            # get cart data from stored order
            data = get_order_from_id(order_id)
            self.cart_items = data['items'].items()
            for order_item in self.cart_items:
                href = resolve_uid(order_item[1]['uid']).absolute_url()
                self.cart_data.append({'href': href,
                                       'quantity': order_item[1]['quantity'],
                                       'price': order_item[1]['price'],
                                       'name': order_item[1]['name']})
                self.amount += order_item[1]['quantity']*order_item[1]['price']

            if 'ship_charge' in data:
                self.amount += data['ship_charge']
                self.ship_charge = data['ship_charge']

            if 'taxes' in data:
                for tax_entry in data['taxes']:
                    self.amount += tax_entry['tax']
                self.taxes = data['taxes']

            if 'ship_method' in data:
                self.ship_method = data['ship_method']

        return self.index()


class JazShopPFGOrders(BrowserView, DateMixin):
    """ Redirect to form's thank-you page, if available. """
    index = ViewPageTemplateFile('orders.pt')
    orders_exist = False

    def __call__(self):

        csv_content = None
        orders = _fetch_orders(storage.get_storage(), key=(), csv=True)
        pfg_form = self.context.aq_parent
        form_uid = IUUID(pfg_form)
        # filter orders to those with generated by this form
        orders = [o for o in orders if form_uid in o.get('pfg_forms', {})]
        # sort by date
        orders.sort(key=lambda o: o.get('date_sort', ''), reverse=True)
        orders_csv = StringIO()

        if len(orders) > 0:
            self.orders_exist = True
            self.most_recent_order_date = orders[0]['date']
            self.first_order_date = orders[len(orders)-1]['date']

            # default in case date selection integrity check fails
            # this could happen if end date < start date
            self.end_index = 0
            self.start_index = len(orders)-1

            if self.request.form.get('export_csv') is None:
                return self.index()

            selected_start = self.startDate()
            selected_end = self.endDate()

            if self.check_date_integrity():
                filtered_orders = []
                for order in orders:
                    if order['datetime'].date() > selected_end:
                        continue
                    if order['datetime'].date() < selected_start:
                        break
                    filtered_orders.append(order)
                orders = filtered_orders

        field_map = OrderedDict()
        for field in pfg_form._getFieldObjects():
            field_map[field.getId()] = field.fgField.widget.label

        if orders and len(orders) > 0:
            writer = csv.DictWriter(
                orders_csv,
                fieldnames=(['date', 'ship_to', 'total'] +
                            list(field_map.keys())),
                restval='',
                extrasaction='ignore',
                dialect='excel',
                quoting=csv.QUOTE_ALL
            )
            # Column titles
            ldict = {
                'date': "Date",
                'ship_first_name': 'Shipping First Name',
                'ship_last_name': 'Shipping Last Name',
                'ship_street': 'Shipping Street',
                'ship_city': 'Shipping City',
                'ship_state': 'Shipping State',
                'ship_postal_code': 'Shipping Postal Code',
                'ship_country': 'Shipping Country',
            }
            ldict.update(field_map)
            writer.writerow(ldict)

            for order in orders:
                address = order.get('address', {})
                ldict = {
                    'date': order['date'],
                    'ship_first_name': address.get('first_name'),
                    'ship_last_name': address.get('last_name'),
                    'ship_street': address.get('street'),
                    'ship_city': address.get('city'),
                    'ship_state': address.get('state'),
                    'ship_postal_code': address.get('postal_code'),
                    'ship_country': address.get('country'),
                }
                ldict.update(order['pfg_forms'][form_uid])
                writer.writerow(ldict)

            csv_content = orders_csv.getvalue()
            orders_csv.close()

            # filename generation with date range included
            end = self.to_datetime(orders[0]['date'],
                                   '%Y-%m-%d %I:%M %p')
            start = self.to_datetime(orders[len(orders)-1]['date'],
                                     '%Y-%m-%d %I:%M %p')
            end_str = end.strftime(u'%m%d%Y')
            start_str = start.strftime(u'%m%d%Y')
            if start_str == end_str:
                nice_filename = '%s_%s_%s' % (self.context.getId(),
                                              'form_orders', start_str)
            else:
                nice_filename = '%s_%s_%s_%s' % (
                    self.context.getId(), 'form_orders', start_str, end_str
                )

            self.request.response.setHeader("Content-Disposition",
                                            "attachment; filename=%s.csv" %
                                            nice_filename)
            self.request.response.setHeader("Content-Type", "text/csv")
            self.request.response.setHeader("Content-Length", len(csv_content))
            self.request.response.setHeader('Last-Modified',
                                            DateTime.rfc822(DateTime()))
            self.request.response.setHeader("Cache-Control", "no-store")
            self.request.response.setHeader("Pragma", "no-cache")
            self.request.response.write(csv_content)

        return csv_content
