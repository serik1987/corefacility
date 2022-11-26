import {translate as t} from '../../utils.mjs';
import ModuleTreeItem from '../../model/tree/module-tree-item.mjs';
import Module from '../../model/entity/module.mjs';

import CoreWindow from '../base/CoreWindow.jsx';
import CoreWindowHeader from '../base/CoreWindowHeader.jsx';
import TreeView from '../base/TreeView.jsx';
import Scrollable from '../base/Scrollable.jsx';
import styles from './SettingsWindow.module.css';


/** Defines the application settings
 * 
 * 	State
 * 	@param {boolean} error404 		Whether the entity was not found here...
 */
class _SettingsWindow extends CoreWindow{

	constructor(props){
		super(props);
		this._moduleTree = new ModuleTreeItem(window.application.model);
		this.handleInputChange = this.handleInputChange.bind(this);

		this.state = {
			...this.state,
			module: window.application.model,
		}
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Application Settings");
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		console.log("The reload button will NOT reload the module tree! (Just reloading current module settings...");
	}

	/** Triggers when the user selectes a given module (or, probably, entry point)
	 */
	handleInputChange(event){
		if (event.value instanceof Module){
			this.setState({module: event.value});
		}
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
					<div className={styles.base_container}>
						<Scrollable cssSuffix={` ${styles.tree_container}`}>
							<TreeView
								tree={this._moduleTree}
								value={this.state.module}
								onInputChange={this.handleInputChange}
							/>
						</Scrollable>
						<div className={styles.options_container}>
							Layouting options container...
						</div>
					</div>
			</CoreWindowHeader>
		);
	}

}


export default function SettingsWindow(props){

	return <_SettingsWindow/>

}
