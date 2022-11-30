import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';


/** This is the base class for all widgets that have to be filled
 *  by the data that shall be loaded asynchronously from the external
 *  source.
 * 
 *  Such data are represented as entities or entity lists.
 * 
 * The component doesn't have any props or state.
 */
export default class Loader extends React.Component{

	/** Reloads the data. This method runs automatically when the componentDidMount.
	 * 	Also, you can invoke it using the imperative React principle
	 * 	@return {undefined}
	 */
	reload(){
		throw new NotImplementedError("reload");
	}

	componentDidMount(){
		this.reload();
	}

	render(){
		throw new NotImplementedError("render");
		return null;
	}

}