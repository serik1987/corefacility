import {Navigate} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import Module from 'corefacility-base/model/entity/Module';
import Loader from 'corefacility-base/view/Loader';
import Hyperlink from 'corefacility-base/shared-view/components/Hyperlink';
import ChildModuleFrame from 'corefacility-base/shared-view/components/ChildModuleFrame';

import FunctionalMap from 'corefacility-imaging/model/entity/FunctionalMap';

import style from './style.module.css';


/**
 * 	Wraps the ROI application
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string}			lookup 					ID of the functional map which lookup must be given
 * 	@param {Number} 		reloadTime 				The component will reload the data after its next rendering if
 * 													value of this prop has been increased by the parent component
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} 		isLoading 				Either functional map or application is loading.
 * 	@param {Error} 			error 					An error occured during the last loading process.
 */
export default class RoiWrapper extends Loader{

	constructor(props){
		super(props);
		this._application = null;

		this.state = {
			isLoading: false,
			error: null,
			functionalMap: null,
			application: null,
			redirectUri: null,
		}
	}

	/**
	 * 	Loads the functional map together with the ROI application
	 */
	async reload(){
		try{
			this.setState({isLoading: true, error: null});
			let result = await client.get(
				`/api/${window.SETTINGS.client_version}/core/projects/` +
				`${window.application.project.id}/imaging/processors/${this.props.lookup}/`
			);
			result.map_info.parent = window.application.project;
			let functionalMap = FunctionalMap.deserialize(result.map_info);
			let applicationList = Module
				.deserialize(result.module_list, true)
				.filter(application => application.alias === 'roi');
			if (applicationList.length !== 1){
				throw new Error(t("The ROI selection application has not been connected to the project"));
			}
			let application = applicationList[0];
			this.setState({
				isLoading: false,
				functionalMap: functionalMap,
				application: application,
			});
		} catch (error){
			this.setState({isLoading: false, error: error});
		}
	}

	/**
	 *  Renders the ROI application together with its wrapper.
	 */
	render(){
		if (this.state.redirectUri){
			return <Navigate to={this.state.redirectUri}/>
		}

		if (this.state.isLoading){
			return <div className={style.message}>{t("Please, wait while ROI selection application is loading.")}</div>;
		} else if (this.state.error){
			return (
				<div className={`${style.message} ${style.error_wrapper}`}>
					<div className={style.error_message}>{this.state.error.message}</div>
					<Hyperlink onClick={event => this.reload()}>{t("Try again.")}</Hyperlink>
					<br/>
					<Hyperlink href="/">{t("Go Home.")}</Hyperlink>
				</div>
			);
		} else if (this.state.application && this.state.functionalMap) {
			return (
				<ChildModuleFrame
					application={this.state.application}
					cssSuffix={style.main}
					onApplicationMount={event => this.handleApplicationMount(event.source)}
					onFetchList={event => this.handleApplicationStateChanged('fetchList', event.value)}
					onFetchSuccess={event => this.handleApplicationStateChanged('fetchSuccess', event.value)}
					onFetchFailure={event => this.handleApplicationStateChanged('fetchFailure', event.value)}
					onRedirect={event => this.handleRedirect(event)}
				/>
			);
		}
	}

	componentDidMount(){
		super.componentDidMount();
		window.application.notifyStateChanged();
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.reloadTime > prevProps.reloadTime){
			this.reload();
		}
	}

	/**
	 * 	Triggers when the ROI application has been successfully loaded and initialized
	 * 	@param {RoiApp} application 		An instance of the ROI application
	 */
	handleApplicationMount(application){
		this._application = application;
		application.receiveParentEntities({
			user_info: window.application.user.serialize(),
			project_info: window.application.project.serialize(),
			functional_map_info: this.state.functionalMap.serialize(),
		})
	}

	handleApplicationStateChanged(method, value){
		window.postMessage({
			method: method,
			info: value,
		}, window.location.origin);
	}

	handleRedirect(event){
		this.setState({redirectUri: event.value});
	}

}