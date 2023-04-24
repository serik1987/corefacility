import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as CloseIcon} from 'corefacility-base/shared-view/icons/close.svg';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';


/**
 * 	Closes current application
 */
export default class CloseAppTool extends BaseTool{

	/**
	 * 	@param {String} 		redirectUri 			URI of the parent application to go to.
	 */
	constructor(redirectUri){
		super();
		this._redirectUri = redirectUri;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Close the application");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <CloseIcon/>;
	}

	/**
	 * 	Triggers when the user selects a tool
	 * 	@param {FunctionalMapDrawer} drawer a parent drawer this tool belongs to
	 * 	@return {boolean} true will cancel selection, false will do nothing
	 */
	selectTool(drawer){
		window.postMessage({method: 'redirect', info: this._redirectUri}, window.location.origin);
		return true;
	}

}