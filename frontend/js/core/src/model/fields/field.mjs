export default class EntityField{

	constructor(defaultValue, valueType, description){
		this._defaultValue = defaultValue;
		this._valueType = valueType;
		this._description = description;
	}

	get default(){
		return this._defaultValue;
	}

	get description(){
		return this._description;
	}

	correct(internalValue){
		return internalValue;
	}

	proofread(value){
		if (typeof value !== this._valueType){
			throw new TypeError("Bad type of the property value");
		}
		return value;
	}

}