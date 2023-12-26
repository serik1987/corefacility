import {useParams, Navigate} from 'react-router-dom';

import {translate as t} from 'corefacility-base/utils';
import client from 'corefacility-base/model/HttpClient';
import Sidebar from 'corefacility-base/shared-view/components/Sidebar';
import SidebarItem from 'corefacility-base/shared-view/components/SidebarItem';
import {ReactComponent as MemoryIcon} from 'corefacility-base/shared-view/icons/memory.svg';
import {ReactComponent as DiskIcon} from 'corefacility-base/shared-view/icons/disk.svg';
import {ReactComponent as EthernetIcon} from 'corefacility-base/shared-view/icons/ethernet.svg';
import {ReactComponent as ThermostatIcon} from 'corefacility-base/shared-view/icons/thermostat.svg';

import CoreWindow from '../../base/CoreWindow';
import CoreWindowHeader from '../../base/CoreWindowHeader';
import Window404 from '../../base/Window404';
import style from './style.module.css';

import CpuHealthCheckToolbar from '../CpuHealthCheckToolbar';
import MemoryHealthCheckToolbar from '../MemoryHealthCheckToolbar';
import NetworkHealthCheckToolbar from '../NetworkHealthCheckToolbar';
import TemperatureHealthCheckToolbar from '../TemperatureHealthCheckToolbar';

const CATEGORIES = ['cpu', 'network', 'disk', 'memory', 'temperature'];

const HEALTH_CHECK_TOOLBARS = {
	cpu: CpuHealthCheckToolbar,
	memory: MemoryHealthCheckToolbar,
	disk: MemoryHealthCheckToolbar,
	network: NetworkHealthCheckToolbar,
	temperature: TemperatureHealthCheckToolbar,
}


/** 
 * 	Displays the health check parameters.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {string} 	category		One of the following categories of health check measures:
 * 										'cpu' the CPU engagement
 * 										'memory' free RAM and swap memory
 * 										'disk' the disk usage
 * 										'network' the network usage
 * 										'temperature' the temperature data
 * 										
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404			true will display the error404 window indicating that such entity was not
 * 											found.
 * 	@param {Date} 		minDate 			The minimum date that the user can set
 * 	@param {Date} 		maxDate 			The maximum date that the user can set
 * 	@param {Date} 		actualStartDate		The start time of the time frame applied at the previous loading begin
 * 	@param {Date}		actualEndDate 		The end date of the time frame applied at the previous loading begin
 * 	@param {Date}		desiredStartDate	The start date defined by the user during the Zoom in, Zoom out or Hand
 * 											tools or null if none of these tools were be selected by the user.
 * 	@param {Date} 		desiredEndDate		The end date defined by the user during the Zoom in, Zoom out or Hand
 * 											tools or null if either none of these tools were selected by the user or
 * 											the desired date coincides with the current date
 * 	@param {Date} 		desiredViewInterval Different between the desired end date and the desired start date or null if
 * 											such information is not applicable
 * 	@param {boolean}	isLoading			true if the user-triggered loading is in progress, false otherwise
 * 	@param {boolean} 	error 				error message related to the previous loading or null if the previous
 * 											loading is succeeded
 * 	@param {string} 	actualCategory 		The category of health check parameters downloaded during the last HTTP
 * 											request or null if no health check values have been downloaded yet.
 * 	@param {Array} 		timestamps			Positions of samples for which the graph shall be plotted.
 * 	@param {Array} 		values				Sample values for different channels
 * 	@param {Array} 		labels 				The legend for the graph
 * 	@param {Array}  	constants 			Some auxiliary information received from the Web server
 * 	@param {boolean}	xLimitsChanged		Two at the stage between the user-controlled limits change and the very
 * 											first rendering and false otherwise.
 */
class HealthCheckWindow extends CoreWindow{

	/** By default, size of the time frame is one day */
	DEFAULT_VIEW_WINDOW_SIZE = 86400000;

	constructor(props){
		super(props);
		this._timer = null;
		
		this.state = {
			...this.state,
			actualStartDate: null,
			actualEndDate: null,
			desiredStartDate:  null,
			desiredEndDate: null,
			desiredViewInterval: null,
			minDate: null,
			maxDate: null,
			actualCategory: null,
			timestamps: null,
			values: null,
			constants: null,
			labels: null,

			isLoading: false,
			error: null,
			xLimitsChanged: false,
		}
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Health status");
	}

	/**
	 *  The start of the viewing window or null for automatic selection
	 */
	get startDate(){
		return this.state.desiredStartDate;
	}

	/**
	 * 	Size of the viewing window in seconds or null for automatic selection
	 */
	get viewWindowSize(){
		return this.state.desiredViewInterval ?? this.DEFAULT_VIEW_WINDOW_SIZE;
	}

	/**
	 *  The end of the viewing window or null for automatic selection
	 */
	get endDate(){
		return this.state.desiredEndDate;
	}

	/**
	 *  Reloads the information from the Web server
	 */
	async reload(){
		if (this.state.isLoading){
			return;
		}

		this._timer = null;
		this.setState({error: null});
		this.discardScheduledReload();

		try{
			let startDate = this.startDate;
			let endDate = this.endDate;
			let viewWindowSize = this.viewWindowSize;
			if (startDate !== null && endDate === null){
				endDate = new Date(startDate + viewWindowSize);
			}
			if (startDate === null){
				if (endDate === null){
					endDate = new Date();
				}
				startDate = new Date(endDate - viewWindowSize);
			}
			this.setState({
				actualStartDate: startDate,
				actualEndDate: endDate,
			});

			let url = new URL(window.location.href);
			url.pathname = `/api/${window.SETTINGS.client_version}/health-check/${this.props.category}/`;
			url.searchParams.append('from', startDate.toISOString());
			url.searchParams.append('to', endDate.toISOString());
			let response = await client.get(url.toString());

			this.setState({
				minDate: new Date(response.minimum_date),
				maxDate: new Date(response.current_date),
				timestamps: response.timestamps.map(timestamp => new Date(timestamp)),
				actualCategory: this.props.category,
				values: response.values,
				labels: response.labels,
				constants: response.constants,

			});

			if (response.repeat_after){
				this._timer = setTimeout(() => this.reload(), response.repeat_after * 1000);
			}
		} catch (error){
			this.setState({error: error.message});
		}

	}

	/**
	 * 	Discards the reload scheduled during the previous reload.
	 */
	discardScheduledReload(){
		if (this._timer !== null){
			clearTimeout(this._timer);
			this._timer = null;
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
		if (CATEGORIES.indexOf(this.props.category) === -1){
			throw new TypeError("HealthCheckWindow: value of the 'category' prop is not suitable.");
		}

		let HealthPlotComponent = HEALTH_CHECK_TOOLBARS[this.state.actualCategory];

		return (
			<CoreWindowHeader
				isLoading={this.state.isLoading}
				isError={this.state.error !== null}
				error={this.state.error}
				header={t("Health status")}
				cssSuffix={style.healthcheck_window_header}
			>
				<Sidebar
					items={[
						<SidebarItem
							current={this.props.category === 'cpu'}
							icon={<MemoryIcon/>}
							text={t("CPU")}
							href="/health-check/cpu/"
							inactive={this.state.isLoading}
						/>,
						<SidebarItem
							current={this.props.category === 'memory'}
							icon={<MemoryIcon/>}
							text={t("Memory")}
							href="/health-check/memory/"
							inactive={this.state.isLoading}
						/>,
						<SidebarItem
							current={this.props.category === 'disk'}
							icon={<DiskIcon/>}
							text={t("Disks")}
							href="/health-check/disk/"
							inactive={this.state.isLoading}
						/>,
						<SidebarItem
							current={this.props.category === 'network'}
							icon={<EthernetIcon/>}
							text={t("Network")}
							href="/health-check/network/"
							inactive={this.state.isLoading}
						/>,
						<SidebarItem
							current={this.props.category === 'temperature'}
							icon={<ThermostatIcon/>}
							text={t("Temperature")}
							href="/health-check/temperature/"
							inactive={this.state.isLoading}
						/>,
					]}
				>
					<div className={style.container}>
						{HealthPlotComponent && <HealthPlotComponent
							minDate={this.state.minDate}
							startDate={this.state.actualStartDate}
							endDate={this.state.actualEndDate}
							maxDate={this.state.maxDate}
							timestamps={this.state.timestamps}
							values={this.state.values}
							constants={this.state.constants}
							labels={this.state.labels}
							onXLimChange={dateLimits => this.handleDateLimitsChange(dateLimits)}
						/>}
					</div>
				</Sidebar>
			</CoreWindowHeader>
		);
	}

	componentDidMount(){
		this.reload();
	}

	componentWillUnmount(){
		this.discardScheduledReload();
	}

	componentDidUpdate(prevProps, prevState){
		if (this.state.xLimitsChanged){
			this.setState({xLimitsChanged: false});
			this.reload();
		}
	}

	/** Process the click for reload button
	 * 	@async
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		this.setState({isLoading: true});
		await this.reload();
		this.setState({isLoading: false});
	}

	/**
	 * 	Triggers when the date limits has been changed
	 * 	@param {Array} 	dateLimits 			Array of two items where the first item is the minimum date and the second
	 * 										item is the maximum date.
	 */
	handleDateLimitsChange(dateLimits){
		let [desiredStartDate, desiredEndDate] = dateLimits;

		if (desiredEndDate.valueOf() === this.state.maxDate.valueOf()){
			this.setState({
				desiredStartDate: null,
				desiredViewInterval: desiredEndDate - desiredStartDate,
				desiredEndDate: null,
			});
		} else {
			this.setState({
				desiredStartDate: desiredStartDate,
				desiredEndDate: desiredEndDate,
				desiredViewInterval: null,
			})
		}

		this.setState({xLimitsChanged: true});
	}

}


let components = {};
for (let category of CATEGORIES){
	components[category] = function(props){
		return <HealthCheckWindow category={category}/>;
	};
}

let HealthCheckCpu = components['cpu'];
let HealthCheckMemory = components['memory'];
let HealthCheckDisk = components['disk'];
let HealthCheckNetwork = components['network'];
let HealthCheckTemperature = components['temperature'];

export {HealthCheckCpu, HealthCheckMemory, HealthCheckDisk, HealthCheckNetwork, HealthCheckTemperature};
