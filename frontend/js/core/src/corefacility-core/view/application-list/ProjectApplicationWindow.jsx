import {useParams} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';

import NavigationWindow from 'corefacility-core/view/base/NavigationWindow';
import Window404 from 'corefacility-core/view/base/Window404';

import ProjectApplicationLoader from './ProjectApplicationLoader';


/** 
 * 	Switches control to a given application
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string}		projectLookup 	Alias of the project to open
 * 	@param {string}		defaultApplicationLookup 	the application lookup to set at the component mount.
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	@param {string} 	applicationLookup 	current application lookup
 * 	@param {string} 	projectName		Name of the currently opened project
 */
class _ProjectApplicationWindow extends NavigationWindow{

	constructor(props){
		super(props);
		this.handleProjectFound = this.handleProjectFound.bind(this);
		this.handleApplicationChanged = this.handleApplicationChanged.bind(this);
		this.handleApplicationSelect = this.handleApplicationSelect.bind(this);

		this.state = {
			...this.state,
			applicationLookup: undefined,
			projectName: null,
			applicationName: null,
		}
	}

	/**
	 *  Default name of the browser tab
	 */
	get browserTitle(){
		return t("Project application");
	}

	/** Renders navigation items
	 * 	@return {array of React.Component} array Hyperlink, p and any
	 * 		other React components: one component means one navigation item
	 */
	renderNavigationItems(){
		return [
			<Hyperlink href="/projects/">{t("Project List")}</Hyperlink>,
			<Hyperlink href={`/projects/${this.props.projectLookup}/apps/`}>
				{this.state.projectName ?? t("Application list")}
			</Hyperlink>,
			<p>{this.state.applicationName ?? t("Project application")}</p>
		];
	}

	/** Renders the rest part of the window; below the window header
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<ProjectApplicationLoader
				projectLookup={this.props.projectLookup}
				appLookup={this.state.applicationLookup}
				on404={this.handle404}
				ref={this.setReloadCallback}
				onProjectFound={this.handleProjectFound}
				onApplicationChanged={this.handleApplicationChanged}
				onApplicationSelect={this.handleApplicationSelect}
			/>
		);
	}

	render(){
		if (this.state.error404){
			return <Window404/>;
		}

		return super.render();
	}

	componentDidMount(){
		this.setState({applicationLookup: this.props.defaultApplicationLookup});
	}

	componentDidUpdate(prevProps, prevState){
		if (prevProps.defaultApplicationLookup !== this.props.defaultApplicationLookup){
			this.setState({applicationLookup: this.props.defaultApplicationLookup});
		}
	}

	/**
	 *  Triggers when the child component (ProjectApplicationLoader) found the project
	 * 	@param {string} name 		Name of the project found
	 */
	handleProjectFound(name){
		this.setState({projectName: name});
	}

	/**
	 * 	Trigges when the application name was changed and such change is required to be updated.
	 */
	handleApplicationChanged(name){
		if (name !== this.state.applicationName){
			this.setState({applicationName: name});
		}
		this._setBrowserTitle(name);
	}

	/**
	 * 	Triggers when the user selects an application from the left pane.
	 * 	@param {Project} project 		Project selected by the user
	 * 	@param {Module} application 	The application selected by the user.
	 */
	handleApplicationSelect(project, application){
		this.setState({
			applicationLookup: application.alias,
			applicationName: application.name,
		});
		window.history.pushState(null, null, `/projects/${project.name}/apps/${application.alias}/`);
	}

}


/**
 * 	This is a wrapper to the _ProjectApplicationWindow that transforms route parameters to props
 */
export default function ProjectApplicationWindow(props){
	let {projectLookup, appLookup} = useParams();

	return (
		<_ProjectApplicationWindow
			projectLookup={projectLookup}
			defaultApplicationLookup={appLookup}
		/>
	);
}