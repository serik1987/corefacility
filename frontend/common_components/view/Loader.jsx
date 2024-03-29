import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import {NotFoundError} from 'corefacility-base/exceptions/network';


/** This is the base class for all widgets that have to be filled
 *  by the data that shall be loaded asynchronously from the external
 *  source.
 * 
 *  Such data are represented as entities or entity lists.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback} 		on404 				Triggers when no requested resource was found.
 * 
 * The component doesn't have any state.
 */
export default class Loader extends React.Component{

	/** Reloads the data. This method runs automatically when the componentDidMount.
	 * 	Also, you can invoke it using the imperative React principle
	 * 	@return {undefined}
	 */
	reload(){
		throw new NotImplementedError("reload");
	}

	/**
	 *  Tries to find an entity with a particular ID. If such entity doesn't exist, calls
	 *  the value of the 'on404' prop if applicable.
	 * 	@async
	 * 	@param {function} callback this function will be invoked to retrieve the entity
	 */
	async getEntityOr404(callback){
		let entity = null;

		try{
    		entity = await callback();
    	} catch (error){
    		if (error instanceof NotFoundError){
    			this.process404();
    			return null;
    		} else {
    			throw error;
    		}
    	}

    	return entity;
	}

	/**
	 * 	Processes the error 404 (the requested resource was not found).
	 */
	process404(){
		if (this.props.on404){
    		this.props.on404();
    	}
	}

	componentDidMount(){
		this.reload();
	}

	render(){
		throw new NotImplementedError("render");
		return null;
	}

}