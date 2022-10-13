export default class EntityField{

	constructor(defaultValue, valueType, description, required){
		this._defaultValue = defaultValue;
		this._valueType = valueType;
		this._description = description;
		this._required = required;
	}

	get default(){
		return this._defaultValue;
	}

	get description(){
		return this._description;
	}

	get required(){
		return this._required;
	}

	correct(internalValue){
		return internalValue;
	}

	proofread(entityName, propertyName, value){
		if (typeof value !== this._valueType){
			throw new TypeError("Bad type of the property value");
		}
		return value;
	}

}