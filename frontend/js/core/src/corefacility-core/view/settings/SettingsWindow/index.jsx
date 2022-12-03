import {translate as t} from 'corefacility-base/utils';
import EntityState from 'corefacility-base/model/entity/EntityState';
import Module from 'corefacility-base/model/entity/Module';
import TreeView from 'corefacility-base/shared-view/components/TreeView';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';

import CoreModule from 'corefacility-core/model/entity/CoreModule';
import IhnaSynchronizationModule from 'corefacility-core/model/entity/IhnaSynchronizationModule';
import ModuleTreeItem from 'corefacility-core/model/tree/ModuleTreeItem';

import CoreWindow from '../../base/CoreWindow';
import CoreWindowHeader from '../../base/CoreWindowHeader';
import DefaultModuleForm from '../DefaultModuleForm';
import CoreModuleForm from '../CoreModuleForm';
import IhnaSynchronizationModuleForm from '../IhnaSynchronizationModuleForm';
import styles from './style.module.css';


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

		this._moduleClasses = {
			[window.application.model.uuid]: CoreModule,
		}

		this._pseudomoduleClasses = {
			ihna_employees: IhnaSynchronizationModule,
		}

		this._moduleForms = {
			[window.application.model.uuid]: CoreModuleForm,
		}

		this._pseudomoduleForms = {
			ihna_employees: IhnaSynchronizationModuleForm,
		}

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
			let ModuleClass = await this._getModuleClass(loadingModule);
			let loadedModule = await this._getLoadedModule(loadingModule, ModuleClass);
			this.setState({loadedModule: loadedModule, isLoading: false, error: null});
		} catch (error){
			this.setState({loadedModule: null, isLoading: false, error: error});
		}
	}

	async _getModuleClass(loadingModule){
		if (loadingModule.uuid in this._moduleClasses){
			return this._moduleClasses[loadingModule.uuid];
		}

		if (loadingModule.pseudomodule_identity in this._pseudomoduleClasses){
			this._moduleClasses[loadingModule.uuid] = this._pseudomoduleClasses[loadingModule.pseudomodule_identity];
			this._moduleForms[loadingModule.uuid] = this._pseudomoduleForms[loadingModule.pseudomodule_identity];
		} else {
			this._moduleClasses[loadingModule.uuid] = Module;
			this._moduleForms[loadingModule.uuid] = DefaultModuleForm;
		}

		return this._moduleClasses[loadingModule.uuid];
	}

	async _getLoadedModule(loadingModule, ModuleClass){
		let loadedModule = null;

		if (loadingModule.uuid === window.application.model.uuid){
			loadedModule = await window.application.reloadModel();
		} else {
			loadedModule = await ModuleClass.get(loadingModule.uuid);
		}

		return loadedModule;
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
		this.setState({isLoading: true, error: null});
	}

	/** Triggers after the user saves settings
	 */
	handleSettingsAfterSave(){
		this.setState({isLoading: false, error: null});
	}

	/** Triggers an error occured during the settings save
	 * 
	 * 	@param {string} error 		The error that is required to be displayed
	 */
	handleSettingsSaveError(error){
		this.setState({isLoading: false, error: error});
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
		let ModuleForm = this._moduleForms[this.state.module.uuid];

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
						<Scrollable cssSuffix={` ${styles.options_container}`}>
							{ this.state.loadedModule && <ModuleForm
								inputData={this.state.loadedModule}
								on404={this.handle404}
								onSettingsBeforeSave={this.handleSettingsBeforeSave}
								onSettingsAfterSave={this.handleSettingsAfterSave}
								onSettingsSaveError={this.handleSettingsSaveError}/>
							}
						</Scrollable>
					</div>
			</CoreWindowHeader>
		);
	}

}


export default function SettingsWindow(props){

	return <_SettingsWindow/>

}
