import {translate as t} from '../../utils.mjs';
import Module from '../../model/entity/module.mjs';
import EntryPoint from '../../model/entity/entry-point.mjs';

import CoreWindow from '../base/CoreWindow.jsx';
import CoreWindowHeader from '../base/CoreWindowHeader.jsx';


/** Defines the application settings
 * 
 * 	State
 * 	@param {boolean} error404 		Whether the entity was not found here...
 */
class _SettingsWindow extends CoreWindow{

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Application Settings");
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		let rootModule = window.application.model;
		let allEntryPoints = {};
		console.log(rootModule.toString());
		for (let entryPoint of await rootModule.findEntryPoints()){
			allEntryPoints[entryPoint.alias] = entryPoint.id;
			console.log(entryPoint.toString());
		}
		for (let corefacilityModule of await Module.find({entry_point: allEntryPoints.synchronizations})){
			console.log(corefacilityModule.toString());
		}
		for (let corefacilityModule of await Module.find({entry_point: allEntryPoints.settings})){
			console.log(corefacilityModule.toString());
		}
		for (let corefacilityModule of await Module.find({entry_point: allEntryPoints.projects})){
			console.log(corefacilityModule.toString());
			for (let entryPoint of await corefacilityModule.findEntryPoints()){
				console.log(entryPoint.toString());
				allEntryPoints[entryPoint.alias] = entryPoint.id;
			}
		}
		for (let corefacilityModule of await Module.find({entry_point: allEntryPoints.processors})){
			console.log(corefacilityModule.toString());
		}
		for (let corefacilityModule of await Module.find({entry_point: allEntryPoints.authorizations})){
			console.log(corefacilityModule.toString());
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
		return (
			<CoreWindowHeader
				isLoading={false}
				isError={false}
				error={null}
				header={t("Application Settings")}
				>
					Layouting the form...
			</CoreWindowHeader>
		);
	}

}


export default function SettingsWindow(props){

	return <_SettingsWindow/>

}
