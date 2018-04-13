from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from AccessControl import ClassSecurityInfo
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.CMFCore.permissions import View
from Products.PloneFormGen.content.fieldsBase import BaseFormField, BaseFieldSchemaStringDefault
from jazkarta.shop.interfaces import IProduct
from .interfaces import IJazShopSelectStringField, IJazShopMultiSelectStringField
from .interfaces import IJazShopArbitraryPriceStringField
from .config import PROJECTNAME


JazShopSelectFieldSchema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
    atapi.StringField('availableProducts',
        searchable=False,
        required=False,
        widget=atapi.MultiSelectionWidget(),
        vocabulary_factory='jazkarta.pfg.jazshop.available_products',
        enforceVocabulary=False,
    ),
))

schemata.finalizeATCTSchema(JazShopSelectFieldSchema, moveDiscussion=False)


def get_available_products_vocab(context):
    terms = []
    products = context.portal_catalog(
        object_provides=IProduct.__identifier__,
        sort_on='sortable_title',
        sort_order='ascending')
    for product in products:
        terms.append(SimpleTerm(
            value=product.UID,
            token=product.UID,
            title=product.Title,
        ))
    return SimpleVocabulary(terms)
directlyProvides(get_available_products_vocab, IVocabularyFactory)


def get_selected_products(context, value):
    selected = []
    products = context.portal_catalog(
        object_provides=IProduct.__identifier__,
        sort_on='sortable_title',
        sort_order='ascending')
    product_dict = {product.UID: ("{}|{}".format(product.Title, product.UID), "$" + str(product.getObject().price) + ' - ' + product.Title) for product in products}
    for product in value:
        if product in product_dict:
            selected.append(product_dict[product])
    selected = sorted(selected, key=lambda(x): float(x[1].split()[0][1:]))
    if context.portal_type == 'JazShopSelectStringField' and context.fgDefault:
        selected.insert(0, ('{}|0'.format(context.fgDefault), context.fgDefault))
    return selected


class JazShopSelectStringField(BaseFormField):

    implements(IJazShopSelectStringField)

    security  = ClassSecurityInfo()

    meta_type = "JazShopSelectStringField"
    schema = JazShopSelectFieldSchema

    def __init__(self, oid, **kwargs):
        BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = atapi.StringField('fg_product_select_field',
            searchable=False,
            required=False,
            widget=atapi.SelectionWidget(),
            vocabulary='_get_selection_vocabulary',
            enforceVocabulary=False,
            write_permission=View,
            )

    def setAvailableProducts(self, value, **kw):
        """ set vocabulary """
        self.fgField.vocabulary = get_selected_products(self, value)

    def htmlValue(self, REQUEST):
        """ return product title instead of uid """
        value = REQUEST.form.get(self.__name__, 'No Input')
        return value.split('|')[0]

JazShopMultiSelectFieldSchema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
    atapi.StringField('availableProducts',
        searchable=False,
        required=True,
        widget=atapi.MultiSelectionWidget(),
        vocabulary_factory='jazkarta.pfg.jazshop.available_products',
    ),
))

schemata.finalizeATCTSchema(JazShopMultiSelectFieldSchema, moveDiscussion=False)


class JazShopMultiSelectStringField(BaseFormField):

    implements(IJazShopMultiSelectStringField)

    security  = ClassSecurityInfo()

    meta_type = "JazShopMultiSelectStringField"
    schema = JazShopMultiSelectFieldSchema

    def __init__(self, oid, **kwargs):
        BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = atapi.StringField('fg_multi_product_select_field',
            searchable=False,
            required=False,
            widget=atapi.MultiSelectionWidget(),
            vocabulary='_get_selection_vocabulary',
            enforceVocabulary=False,
            write_permission=View,
            )

    def setAvailableProducts(self, value, **kw):
        """ set vocabulary """
        self.fgField.vocabulary = get_selected_products(self, value)

    def htmlValue(self, REQUEST):
        """ return product title instead of uid """
        value = REQUEST.form.get(self.__name__, 'No Input')
        if type(value) != type([]):
            value = [value]
        value = ', '.join([v.split('|')[0] for v in value])
        return value


JazShopArbitraryPriceFieldSchema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
    atapi.StringField('availableProducts',
        searchable=False,
        required=True,
        widget=atapi.MultiSelectionWidget(),
        vocabulary_factory='jazkarta.pfg.jazshop.available_products',
    ),
))

schemata.finalizeATCTSchema(JazShopArbitraryPriceFieldSchema, moveDiscussion=False)


class JazShopArbitraryPriceStringField(BaseFormField):

    implements(IJazShopArbitraryPriceStringField)

    security  = ClassSecurityInfo()

    meta_type = "JazShopArbitraryPriceStringField"
    schema = JazShopArbitraryPriceFieldSchema

    def __init__(self, oid, **kwargs):
        BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = atapi.StringField('fg_product_price_field',
            searchable=False,
            required=False,
            write_permission=View,
            )


atapi.registerType(JazShopSelectStringField, PROJECTNAME)
atapi.registerType(JazShopMultiSelectStringField, PROJECTNAME)
atapi.registerType(JazShopArbitraryPriceStringField, PROJECTNAME)
