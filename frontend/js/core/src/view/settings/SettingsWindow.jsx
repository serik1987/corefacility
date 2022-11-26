import {translate as t} from '../../utils.mjs';
import EntityState from '../../model/entity/entity-state.mjs';
import ModuleTreeItem from '../../model/tree/module-tree-item.mjs';
import Module from '../../model/entity/module.mjs';

import CoreWindow from '../base/CoreWindow.jsx';
import CoreWindowHeader from '../base/CoreWindowHeader.jsx';
import TreeView from '../base/TreeView.jsx';
import Scrollable from '../base/Scrollable.jsx';
import DefaultModuleForm from './DefaultModuleForm';
import styles from './SettingsWindow.module.css';


/** Defines the application settings
 * 
 * 	State
 * 	@param {boolean} error404 		Whether the entity was not found here...
 * 	@param {Module} module 			The currently selected module
 * 	@param {Module} loadedModule 	The currently loaded module. All objects represent
 * 									the same module. However, technically they are different
 * 									objects
 * 	@param {boolean} isLoading		true if the module settings are currently loading, false
 * 									otherwise
 * 	@param {Error} error 			Error occured during the last loading of the module settings.
 */
class _SettingsWindow extends CoreWindow{

	constructor(props){
		super(props);
		this._moduleTree = new ModuleTreeItem(window.application.model);
		this.handleInputChange = this.handleInputChange.bind(this);
		this.handleSettingsBeforeSave = this.handleSettingsBeforeSave.bind(this);
		this.handleSettingsAfterSave = this.handleSettingsAfterSave.bind(this);
		this.handleSettingsSaveError = this.handleSettingsSaveError.bind(this);

		this.state = {
			...this.state,
			module: window.application.model,
			loadedModule: window.application.model,
			isLoading: false,
			error: null,
		}
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Application Settings");
	}

	/** Reloads the module settings from remote server.
	 * 	@param {Module} loadingModule 	the module which settings must be loaded
	 */
	async loadModule(loadingModule){
		try{
			this.setState({loadedModule: null, isLoading: true, error: null});
			let loadedModule = null;
			if (loadingModule.uuid === window.application.model.uuid){
				loadedModule = await window.application.reloadModel();

			} else {
				loadedModule = await Module.get(loadingModule.uuid);
			}
			this.setState({
				loadedModule: loadedModule,
				isLoading: false,
				error: null,
			});
		} catch (error){
			this.setState({loadedModule: null, isLoading: false, error: error});
		}
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		this.loadModule(this.state.module);
	}

	/** Triggers when the user selectes a given module (or, probably, entry point)
	 */
	handleInputChange(event){
		if (event.value instanceof Module){
			this.setState({
				module: event.value,
			});
			this.loadModule(event.value);
		}
	}

	/** Triggers before the user saves settings
	 */
	handleSettingsBeforeSave(){
		this.setState({isLoading: true});
	}

	/** Triggers after the user saves settings
	 */
	handleSettingsAfterSave(){
		this.setState({isLoading: false});
	}

	/** Triggers an error occured during the settings save
	 * 
	 * 	@param {string} error 		The error that is required to be displayed
	 */
	handleSettingsSaveError(error){
		this.setState({
			isLoading: false,
			error: error,
		})
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
		console.log("Window rendering started.");

		return (
			<CoreWindowHeader
				isLoading={this.state.isLoading}
				isError={this.state.error !== null}
				error={this.state.error}
				header={t("Application Settings")}>
					<div className={styles.base_container}>
						<Scrollable cssSuffix={` ${styles.tree_container}`}>
							<TreeView
								tree={this._moduleTree}
								value={this.state.module}
								onInputChange={this.handleInputChange}/>
						</Scrollable>
						<div className={styles.options_container}>
							{ this.state.loadedModule && <DefaultModuleForm
								inputData={this.state.loadedModule}
								on404={this.handle404}
								onSettingsBeforeSave={this.handleSettingsBeforeSave}
								onSettingsAfterSave={this.handleSettingsAfterSave}
								onSettingsSaveError={this.handleSettingsSaveError}/>
							}
						</div>
					</div>
			</CoreWindowHeader>
		);
	}

}


export default function SettingsWindow(props){

	return <_SettingsWindow/>

}
