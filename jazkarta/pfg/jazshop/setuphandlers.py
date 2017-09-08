import config
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import safe_hasattr
from Products.Archetypes.public import listTypes


def importVarious(context):
    """
    Final jazkarta.pfg.jazshop import steps.
    """

    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('pfgjazshop-various.txt') is None:
        return

    site = context.getSite()

    #######################
    # Both PloneFormGen and the target field provider are going to have
    # to be installed first. So, let's check.

    portal_skins = getToolByName(site, 'portal_skins')
    assert safe_hasattr(portal_skins, 'PloneFormGen'), "PloneFormGen must be installed prior to installing this product."

    #######################
    # Here's the code specific to making this visible to PloneFormGen

    classes = listTypes(config.PROJECTNAME)
    myTypes = [item['name'] for item in classes]
    portal_types = getToolByName(site, 'portal_types')
    for typeName in ('FormFolder', 'FieldsetFolder'):
        ptType = portal_types.getTypeInfo(typeName)
        ffact = list(ptType.allowed_content_types)
        ffact += myTypes
        ptType.manage_changeProperties(allowed_content_types=ffact)
