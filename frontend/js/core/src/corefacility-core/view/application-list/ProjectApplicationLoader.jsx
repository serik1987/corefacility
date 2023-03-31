import {translate as t} from 'corefacility-base/utils';
import Sidebar from 'corefacility-base/shared-view/components/Sidebar';
import SidebarItem from 'corefacility-base/shared-view/components/SidebarItem';

import CoreWindowHeader from 'corefacility-core/view/base/CoreWindowHeader';

import ProjectApplicationListLoader from './ProjectApplicationListLoader';


/**
 * 	Represents sidebar of all applciations connected to a particular project, together with an application selected by
 * 	a single user.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 		projectLookup 		ID or alias of the project which application list is required to be
 * 												displayed.
 * 	@param {string} 		appLookup 			Alias of the application to open
 * 	@param {callback} 		on404 				Triggers when no requested resource was found. Callback has no
 * 												arguments.
 * 	@param {callback} 		onProjectFound		Triggers when the project has been found. Callback arguments:
 * 		@param {string} name 						Name of the project that has been found
 * 	@param {callback} 		onApplicationChanged Triggers when the application has been found. Callback arguments:
 * 		@param {string} name 						The application name or null, if application was not specified
 * 	@param {callback} 		onApplicationSelect  Triggers when the user selects another application. Callback arguments:
 * 		@param {Module} application 				The application selected by the user.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	_isLoading, _isError, _error props are nor specified for direct access. Use instead:
 * 		(a) isLoading, isError, error Javascript properties
 * 		(b) reportListFetching, reportFetchSuccess(itemList), reportFetchFailure(error) methods
 * 	@param {string} 		editorHeader 		Header for the editor
 * 
 */
export default class ProjectApplicationLoader extends ProjectApplicationListLoader{

	constructor(props){
		super(props);

		this._application = null;
	}

	shouldComponentUpdate(nextProps, nextState){
		if (this.state._itemList !== nextState._itemList || this.props.appLookup !== nextProps.appLookup){
			if (nextState._itemList){
				let filteredList = nextState._itemList.filter(app => app.alias === nextProps.appLookup);
				if (filteredList.length === 1){
					this._application = filteredList[0];
				} else {
					this._application = null;
				}
			} else {
				this._application = null;
			}

			if (nextProps.onApplicationChanged){
				nextProps.onApplicationChanged(this._application && this._application.name);
			}
		}

		return true;
	}

	render(){
		let applicationSelected = false;

		if (!this.itemList || this.itemList.length === 0){
			return (
				<CoreWindowHeader
					isLoading={this.isLoading}
					isError={this.isError}
					error={this.error}
					header={this._project ? this._project.name : t("Project application")}
				/>
			);
		} else {
			return (
				<Sidebar
					items={
						this.itemList.map(app => {
							let isCurrent = this._application && this._application.uuid === app.uuid;
							if (isCurrent){
								applicationSelected = true;
							}

							return (
								<SidebarItem
									current={isCurrent}
									text={app.name}
									onClick={event => this.handleApplicationSelect(event, app)}
									inactive={this.isLoading}
								/>
							);
						})
					}
				>
					<CoreWindowHeader
						isLoading={this.isLoading}
						isError={this.isError}
						error={this.error}
						header={this._project && this._project.name}
					>
						{applicationSelected && <p>TO-DO: render the right side tomorrow...</p>}
						{!applicationSelected && <div>
							<h2>{t("The requested application is absent in the application list.")}</h2>
							<p>{t("Choose another application from the left list.")}</p>
						</div>}
					</CoreWindowHeader>
				</Sidebar>
			);
		}
	}

	/**
	 * 	Triggers when the user selects an application from the left pane.
	 * 	@param {SyntheticEvent} event 			The event that triggered this action
	 * 	@param {Module} 		application 	Application selected by the user
	 */
	handleApplicationSelect(event, application){
		if (this.props.onApplicationSelect && this._project){
			this.props.onApplicationSelect(this._project, application);
		}
	}

}