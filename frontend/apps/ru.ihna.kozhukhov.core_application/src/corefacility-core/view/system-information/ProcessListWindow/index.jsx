import {translate as t, humanReadableMemory} from 'corefacility-base/utils';
import {UnauthorizedError} from 'corefacility-base/exceptions/network';
import client from 'corefacility-base/model/HttpClient';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';
import StaticSortedTable from 'corefacility-base/shared-view/components/StaticSortedTable';

import CoreWindow from '../../base/CoreWindow';
import CoreWindowHeader from '../../base/CoreWindowHeader';

import style from './style.module.css';


/** 
 * 	Displays list of all processes
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean}	error404		true will display the error404 window indicating that such entity was not found.
 * 	@param {boolean} 	isLoading 		true if the process list is loading due to the user's request, false otherwise
 * 	@param {String} 	error 			If error occured during the process list loading, an error message contains
 * 										in this state property.
 *	@param {Array}		columns 		Names of the process properties to show
 * 	@param {Array}		data 			Values of the process properties to show
 */
export default class ProcessListWindow extends CoreWindow{

	FIELD_DESCRIPTIONS = {
		'USER': t("User"),
		'PID': "PID",
		'%CPU': t("% CPU"),
		'%MEM': t("% Memory"),
		'VSZ': t("Virtual memory size"),
		'RSS': t("# pages consuming"),
		'STAT': t("Status"),
		'START': t("Start time"),
		'TIME': t("Duration"),
		'TTY': t("Terminal number"),
		'COMMAND': t("Command")
	}

	MAXIMUM_COMMAND_NAME_SIZE = 30;

	REFRESH_INTERVAL = 15000; // Refresh interval for the process list table, in milliseconds

	constructor(props){
		super(props);
		this.__timerID = null;
		this.__isRefreshing = false;

		this.state = {
			...this.state,
			isLoading: false,
			error: null,
			columns: null,
			data: null,
		}
	}

	/** A string to be show at the web browser tab */
	get browserTitle(){
		return t("Process list");
	}

	static decryptProcessStatus(status){
		let processStatuses = {
			"R": t("Running"),
			"S": t("Sleeping"),
			"D": t("Sleeping"),
			"Z": t("Zombie"),
			">": t("High priority"),
			"<": t("Low priority"),
			"s": t("Session leader"),
		}

		let statusDescription = [];
		for (let statusChar in processStatuses){
			if (status.search(statusChar) !== -1){
				statusDescription.push(processStatuses[statusChar]);
			}
		}
		return statusDescription.join(", ");
	}

	/**
	 * 	Reloads the process list.
	 * 	@async
	 */
	async reload(){
		if (this.__isRefresing){
			return;
		}

		try{
			this.__isRefreshing = true;
			this.setState({error: null});
			let reloadUrl = `/api/${window.SETTINGS.client_version}/procinfo/`;
			let result = await client.get(reloadUrl);
			let columns = [];
			let data = [];
			if (result.length > 0){
				columns = Object.keys(result[0]);
				data = result.map(processInfo => {
					return columns.map(column => {
						let value = processInfo[column];
						if (column === 'VSZ'){
							value = humanReadableMemory(value);
						}
						if (column === 'STAT'){
							value = ProcessListWindow.decryptProcessStatus(value);
						}
						if (column === 'COMMAND' && value.length > this.MAXIMUM_COMMAND_NAME_SIZE){
							value = value.slice(0, this.MAXIMUM_COMMAND_NAME_SIZE) + "...";
						}
						return value;
					});
				});
				columns = columns.map(column => this.FIELD_DESCRIPTIONS[column]);
			}
			this.setState({
				columns: columns,
				data: data,
			});
			this.__timerID = setTimeout(() => this.reload(), this.REFRESH_INTERVAL);
		} catch (error){
			this.setState({
				error: error.message,
			})
			if (error instanceof UnauthorizedError){
				window.location.reload();
			}
		} finally{
			this.__isRefreshing = false;
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
	 *  @abstract
	 *  @return {React.Component} The content must have exactly one
	 * 						 	  descendant component that is called with 'ref' prop
	 * 							  which value is set to {this.setReloadCallback}.
	 *                            Such a component must implement the reload() method
	 */
	renderContent(){
		return (
			<CoreWindowHeader
				isLoading={this.state.isLoading}
				isError={this.state.error !== null}
				error={this.state.error}
				header={t("Process list")}
			>
				<Scrollable cssSuffix={style.container}>
					{this.state.columns === null && <i>{t("Please wait while the process list is loading.")}</i>}
					{this.state.columns !== null && <StaticSortedTable
						columns={this.state.columns}
						data={this.state.data}
						order={this.state.order}
						sortable={[
							this.FIELD_DESCRIPTIONS['USER'],
							this.FIELD_DESCRIPTIONS['PID'],
							this.FIELD_DESCRIPTIONS['%CPU'],
							this.FIELD_DESCRIPTIONS['%MEM'],
							this.FIELD_DESCRIPTIONS['VSZ'],
							this.FIELD_DESCRIPTIONS['RSS'],
							this.FIELD_DESCRIPTIONS['COMMAND']
						]}
					/>}
				</Scrollable>
			</CoreWindowHeader>
		);
	}

	componentDidMount(){
		this.reload();
	}

	componentWillUnmount(){
		if (this.__timerID !== null){
			clearTimeout(this.__timerID);
		}
	}

	/** Process the click for reload button
	 * 	@param {SyntheticEvent} the event object
	 *  @return {undefined}
	 */
	async onReload(event){
		this.setState({isLoading: true});
		await this.reload();
		this.setState({isLoading: false});
	}

}

