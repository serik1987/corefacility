from .entity_field import EntityField
from .read_only_field import ReadOnlyField


class BooleanField(EntityField):
	"""
	Represents the boolean field
	"""

	def __init__(self, default=None, description: str = None):
		"""
		Initializes the EntityField. After being initialized the EntityField shall be added inside the
		'_public_field_description' dictionary inside the Entity object

		:param default: Entity default value. Such value will be assigned to 'creating' entity by default
		:param description: The entity string description used for logging and debugging
		"""
		super().__init__(bool, default=default, description=description)

	def proofread(self, value):
		"""
		Proofreads the entity value. The method is called when the entity gets the field value to the user.
		Such value passes to the user itself who in turn proofreads such value

		:param value: the value stored in the entity as defined by one of the entity providers
		:return: the value given to the user
		"""
		return bool(value)


class BooleanReadOnlyField(ReadOnlyField):
	"""
	Represents a boolean read-only field
	"""

	def proofread(self, value):
		"""
		Proofreads the entity value. The method is called when the entity gets the field value to the user.
		Such value passes to the user itself who in turn proofreads such value

		:param value: the value stored in the entity as defined by one of the entity providers
		:return: the value given to the user
		"""
		return bool(value)	
