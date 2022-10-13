import EntityField from './field.mjs';
import {ReadOnlyPropertyError} from '../../exceptions/model.mjs';


export default class ReadOnlyField extends EntityField{

	constructor(description){
		super(undefined, undefined, description, false);
	}

	proofread(entityName, propertyName, value){
		throw new ReadOnlyPropertyError(entityName, propertyName);
	}

}