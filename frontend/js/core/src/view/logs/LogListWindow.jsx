import {translate as t} from '../../utils.mjs';

import CoreWindow from '../base/CoreWindow.jsx';
import LogListLoader from './LogListLoader.jsx';


/** Deals with log lists.
 */
export default class LogListWindow extends CoreWindow{

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Logs");
	}

	/** Renders the area on the top of the Web browser window;
	 *  between the logo and the controls
	 *  @abstract
	 * 	@return {React.js component}
	 */
	renderControls(){
		return null;
	}

	/** Renders the rest part of the window; below the window header
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return <LogListLoader ref={this.setReloadCallback}/>
	}

}