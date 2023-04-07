import {wait, id} from 'corefacility-base/utils';

import client from '../HttpClient';
import FieldManager, {ManagedField} from './FieldManager';


/** Deals with certain files, provide their upload and delete
 * 
 * 	Options:
 * 		@param {function} path 	The API path to the file resource. Should be a function
 * 								that accepts the entity object and returns an API path
 * 								relatively to /api/<version>
 */
export class FileManager extends FieldManager{

	constructor(entity, propertyName, defaultValue, options){
		super(entity, propertyName, defaultValue);
		this._path = `/api/${window.SETTINGS.client_version}/${options.path(entity)}`;
		this._uploadingFile = null;
	}

	/** Returns the file URL if the file has been uploaded or the file's object
	 * 	if the file has already been uploaded.
	 */
	get value(){
		return this._uploadingFile || this._internalValue;
	}

	/** Uploads the file to the external server
	 * 	@param {File} file the File object
	 */
	async upload(file){
		this._uploadingFile = file;
		try{
			let hiddenFields = this._saveHiddenFields();
			let result = await client.upload(this._path, file);
			this._internalValue = result[this._propertyName];
			this._entity._entityFields = result;
			this._restoreHiddenFields(hiddenFields);
		} catch (error){
			throw error;
		} finally {
			this._uploadingFile = null;
		}
	}

	/** Deletes the file from the external server.
	 * 	@return {undefined}
	 * 
	 */
	async delete(){
		let hiddenFields = this._saveHiddenFields();
		let result = await client.request(this._path, "DELETE", null);
		this._uploadingFile = null;
		this._internalValue = result[this._propertyName];
		this._entity._entityFields = result;
		this._restoreHiddenFields(hiddenFields);
	}

	/** A short string representation of the file
	 */
	toString(){
		return this.value && this.value.toString();
	}

	/**
	 * 	Saves values of the hidden fields before upload/delete the file, since they will be removed.
	 * 	@return {object} 				Saved hidden fields; to be used as argument to the _restoreHiddenFields method.
	 */
	_saveHiddenFields(){
		let hiddenFields = {};
		for (let field in this._entity._entityFields){
			if (field.startsWith('_')){
				hiddenFields[field] = this._entity._entityFields[field];
			}
		}
		return hiddenFields;
	}

	/**
	 * 	Restores values from the hidden fields after upload/delete the value.
	 * 	@param {object} fields 			Result of the _saveHiddenFields method.
	 */
	_restoreHiddenFields(fields){
		this._entity._entityFields = {...this._entity._entityFields, ...fields};
	}

}


/** The field which value must be a valid file stored
 * 	on the client or server side.
 * 
 * 	Refer to FileManager for details.
 */
export default class FileField extends ManagedField{

	/** Creates new field
	  * 		@param {function} path 	The API path to the file resource. Should be a function
 	  * 								that accepts the entity object and returns an API path
      * 								relatively to /api/<version>
	 */
	constructor(path){
		super(FileManager, {path: path});
	}

}