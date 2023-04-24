import BaseTool from './BaseTool';


/**
 * 	The tool provides change of the application route.
 */
export default class RedirectionTool extends BaseTool{

	/**
	 * 	@param {String} 		toolName 				Tool name to be used for the tooltip
	 * 	@param {React.Component} icon 					An svg image to be used as an icon
	 * 	@param {String} 		uri 					Redirection uri for the client-side routing
	 */
	constructor(toolName, icon, uri){
		super();
		this._toolName = toolName;
		this._icon = icon;
		this._uri = uri;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return this._toolName;
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return this._icon;
	}

	/**
	 * 	Triggers when the user selects a given tool
	 * 	@param {FunctionalMapDrawer} drawer 			a drawer component this tool belongs to.
	 * 	@return {boolean} 								true because this tool is not toggleable
	 */
	selectTool(drawer){
		drawer.setState({redirect: this._uri});
		return true;
	}

}