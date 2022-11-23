import {translate as t} from '../../utils.mjs';
import ModuleTreeItem from '../../model/tree/module-tree-item.mjs';
import Hyperlink from '../base/Hyperlink.jsx';

import CoreWindow from '../base/CoreWindow.jsx';
import CoreWindowHeader from '../base/CoreWindowHeader.jsx';


/** Defines the application settings
 * 
 * 	State
 * 	@param {boolean} error404 		Whether the entity was not found here...
 */
class _SettingsWindow extends CoreWindow{

	constructor(props){
		super(props);
		this.resetModuleTree();
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Application Settings");
	}

	/** Removes all nodes from the module tree except the root node.
	 */
	resetModuleTree(){
		this._moduleTree = new ModuleTreeItem(window.application.model);
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		this.resetModuleTree();
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
		console.log("Tree rendering...");

		return (
			<CoreWindowHeader
				isLoading={false}
				isError={false}
				error={null}
				header={t("Application Settings")}
				>
					<Hyperlink onClick={event => this.loadNodes()}>Load nodes</Hyperlink>
					{" "}
					<Hyperlink onClick={event => this.printNodes()}>Print nodes</Hyperlink>
			</CoreWindowHeader>
		);
	}

	loadNodes(branch = null){
		let isRootNode = false;
		if (branch === null){
			branch = this._moduleTree;
			isRootNode = true;
		}
		let promise = null;
		if (branch.childrenState === ModuleTreeItem.ChildrenState.ready){
			for (let childBranch of branch.children){
				promise = this.loadNodes(childBranch);
				if (promise){
					break;
				}
			}
		} else {
			promise = branch.loadChildren();
		}
		if (isRootNode){
			this.printNodes();
		}
		return promise;
	}

	printNodes(){
		console.log(this._moduleTree.toString());
	}

}


export default function SettingsWindow(props){

	return <_SettingsWindow/>

}
