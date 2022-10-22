import {NotImplementedError} from '../../exceptions/model.mjs';
import * as React from 'react';


/** This is the base class for all corefacility windows
 *  Corefacility windows are such components that can define
 *  the title of the Web Browser tab
 *  
 *  The class requires no props.
 */
export default class Window extends React.Component{

	constructor(props){
		super(props);
		this._setBrowserTitle();
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		throw new NotImplementedError("browserTitle");
	}

	/** Sets the browser title from the 'browserTitle' property */
	_setBrowserTitle(){
		if (this.browserTitle){
			document.head.getElementsByTagName("title")[0].innerText = this.browserTitle;
		}
	}

	shouldComponentUpdate(props, state){
		this._setBrowserTitle();
		return true;
	}

	/** Renders the window.
	 *  @abstract
	 */
	render(){
		throw new NotImplementedError("render");
		return null;
	}

}