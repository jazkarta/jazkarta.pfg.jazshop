from zope.interface import directlyProvides
from zope.interface import implements
from zope.schema.interfaces import IVocabularyFactory
from zope.schema.vocabulary import SimpleTerm
from zope.schema.vocabulary import SimpleVocabulary
from Products.ATContentTypes.content import schemata
from Products.Archetypes import atapi
from Products.PloneFormGen.content.fieldsBase import BaseFormField, BaseFieldSchemaStringDefault
from jazkarta.shop.interfaces import IProduct
from .interfaces import IJazShopSelectStringField, IJazShopMultiSelectStringField
from .config import PROJECTNAME


JazShopSelectFieldSchema = BaseFieldSchemaStringDefault.copy() + atapi.Schema((
    atapi.StringField('availableProducts',
        searchable=False,
        required=False,
        widget=atapi.MultiSelectionWidget(),
        vocabulary_factory='jazkarta.pfg.jazshop.available_products',
        enforceVocabulary=True,
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
    product_dict = {product.UID: product.Title for product in products}
    for product in value:
        if product in product_dict:
            selected.append((product, product_dict[product]))
    return selected


class JazShopSelectStringField(BaseFormField):

    implements(IJazShopSelectStringField)

    meta_type = "JazShopSelectStringField"
    schema = JazShopSelectFieldSchema

    def __init__(self, oid, **kwargs):
        BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = atapi.StringField('fg_product_select_field',
            searchable=False,
            required=False,
            widget=atapi.SelectionWidget(),
            vocabulary='_get_selection_vocabulary',
            enforceVocabulary=True,
            )

    def setAvailableProducts(self, value, **kw):
        """ set vocabulary """
        self.fgField.vocabulary = get_selected_products(self, value)


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

    meta_type = "JazShopMultiSelectStringField"
    schema = JazShopMultiSelectFieldSchema

    def __init__(self, oid, **kwargs):
        BaseFormField.__init__(self, oid, **kwargs)

        self.fgField = atapi.StringField('fg_multi_product_select_field',
            searchable=False,
            required=False,
            widget=atapi.MultiSelectionWidget(),
            vocabulary='_get_selection_vocabulary',
            enforceVocabulary=True,
            )

    def setAvailableProducts(self, value, **kw):
        """ set vocabulary """
        self.fgField.vocabulary = get_selected_products(self, value)


atapi.registerType(JazShopSelectStringField, PROJECTNAME)
atapi.registerType(JazShopMultiSelectStringField, PROJECTNAME)
