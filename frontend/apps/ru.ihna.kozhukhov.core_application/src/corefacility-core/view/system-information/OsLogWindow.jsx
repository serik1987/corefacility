import {translate as t} from 'corefacility-base/utils';

import CoreWindow from '../base/CoreWindow';
import CoreWindowHeader from '../base/CoreWindowHeader';
import OsLogLoader from './OsLogLoader';


/**
 * 	A window where the user can watch the operating system logs
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class OsLogWindow extends CoreWindow{

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Operating system logs");
	}

	/** Renders the area on the top of the Web browser window;
	 *  between the logo and the controls
	 * 	@return {React.js component}
	 */
	renderControls(){
		return null;
	}

	/** Renders the rest part of the window; below the window header
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<OsLogLoader
				ref={this.setReloadCallback}
			/>
		);
	}

}