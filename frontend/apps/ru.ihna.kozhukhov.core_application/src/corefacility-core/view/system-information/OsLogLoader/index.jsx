import {translate as t, isDateValid} from 'corefacility-base/utils';
import SortedTable from 'corefacility-base/shared-view/components/SortedTable';
import Label from 'corefacility-base/shared-view/components/Label';
import Scrollable from 'corefacility-base/shared-view/components/Scrollable';
import Calendar from 'corefacility-base/shared-view/components/Calendar';
import TextInput from 'corefacility-base/shared-view/components/TextInput';
import PrimaryButton from 'corefacility-base/shared-view/components/PrimaryButton';
import ComboBox from 'corefacility-base/shared-view/components/ComboBox';

import OsLog from '../../../model/entity/OsLog';
import OsLogProvider from '../../../model/providers/OsLogProvider';
import CoreListLoader from '../../base/CoreListLoader';
import style from './style.module.css';


/**
 * 	Responsible for interaction between OsLogList component and the OsLog model.
 * 
 *  Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 *	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} 		isFilterOpened 				true if the filter panel is in expanded state, false otherwise
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class OsLogLoader extends CoreListLoader{

	COLUMNS = [t("Date and time"), t("Hostname"), t("Message")];
	SORTABLE_COLUMNS = [t("Date and time")];

	constructor(props){
		super(props);
		this.handleSortSelection = this.handleSortSelection.bind(this);

		this._dateTimeFrom = null;
		this._dateTimeTo = null;
		this._start = 0;

		this.state = {
			...this.state,

			dateFrom: null,
			timeFrom: null,
			dateFromError: null,

			dateTo: null,
			timeTo: null,
			timeToError: null,

			hostname: null,
			logFile: null,
			messagePattern: null,

			ordering: null,

			currentFilter: {},
		}
	}

	/**
	 * 	Returns the list of all hosts, in a way to be used in ComboBox props
	 */
	get hostList(){
		let hostList = OsLogProvider.hostList.map(hostname => {
			return {
				value: hostname,
				text: hostname,
			}
		});
		hostList.push({
			value: null,
			text: t("All hosts"),
		})
		return hostList;
	}

	/**
	 * 	List of all log files, in a way, suitable for using in the ComboBox props
	 */
	get logFiles(){
		let logFiles = OsLogProvider.logFiles.map(logFile => {
			return {
				value: logFile,
				text: logFile,
			}
		});
		logFiles.push({
			value: null,
			text: t("All files"),
		})
		return logFiles;
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return OsLog;
	}

	/**
	 *  Calculates ordering from the state
	 */
	get ordering(){
		return this.state.ordering ?? 'asc';
	}

	/** The header to be displayed on the top.
	 */
	get listHeader(){
		return t("Operating system logs");
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 * 	@param {object} props props that must be used to calculate the filter.
	 * 	@param {object} state the state that must be used to calculate the filter
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let filter = {
			...state.currentFilter,
			ordering: state.ordering ?? this.ordering,
			limit: OsLogLoader.MAX_LOG_NUMBER,
		}
		return filter;
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {object} state state for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		let params = [
			state.currentFilter && state.currentFilter.start,
			state.currentFilter && state.currentFilter.end,
			state.currentFilter && state.currentFilter.hostname,
			state.currentFilter && state.currentFilter.files,
			state.currentFilter && state.currentFilter.q,
			state.ordering ?? this.ordering,
		]
			.map(param => param ? param : '')
			.join(":");
		return params;
	}

	/** Loads the item list from the external source
	 *  @async
	 *  @return {undefined}
	 */
	async reload(){
		let dateFrom = new Date(this.state.currentFilter.start);
		let dateTo = new Date(this.state.currentFilter.end);

		if (dateTo < dateFrom){
			this._actualFilterIdentity = this._desiredFilterIdentity;
			this.reportFetchFailure(new TypeError(t("The log end date shall not be less than the log start date")));
		} else {
			await super.reload();
			this._start = 0;
		}
	}

	async loadMoreLogs(){
		this._start += OsLogLoader.MAX_LOG_NUMBER;
		let filter = this.deriveFilterFromPropsAndState(this.props, this.state);
		filter.limit_start = this._start;
		try{
			this.reportListFetching();
			let newLogs = await OsLog.find(filter);
			this.reportFetchSuccess();
			this.setState({
				_itemList: [...this.state._itemList, ...newLogs],
			})
		} catch (error){
			this.reportFetchFalure(error);
		}
	}

	/**	Renders the filter
	 * 	@return {React.Component} all filter widgets to be rendered
	 */
	renderFilter(){
		return (
			<div className={style.filter}>
				<div className={style.date_filter}>
					<div className={style.date_from_wrapper}>
						<Label>{t("Show logs from")}</Label>
						<Calendar
							inactive={this.isLoading}
							value={this.state.dateFrom}
							onInputChange={event => this.handleDateFromChange(event.value)}
							error={this.state.dateFromError}
						/>
					</div>
					<div className={style.time_from_wrapper}>
						<TextInput
							inactive={this.isLoading}
							value={this.state.timeFrom}
							onInputChange={event => this.handleTimeFromChange(event.value)}
						/>
					</div>
					<div className={style.date_to_wrapper}>
						<Label>{t("to")}</Label>
						<Calendar
							inactive={this.isLoading}
							value={this.state.dateTo}
							onInputChange={event => this.handleDateToChange(event.value)}
							error={this.state.dateToError}
						/>
					</div>
					<div className={style.time_to_wrapper}>
						<TextInput
							inactive={this.isLoading}
							value={this.state.timeTo}
							onInputChange={event => this.handleTimeToChange(event.value)}
						/>
					</div>
				</div>
				<div className={style.host_filter}>
					<Label>{t("Hostname")}</Label>
					<ComboBox
						valueList={this.hostList}
						onInputChange={event => this.handleHostnameChange(event.value)}
						value={this.state.hostname}
						inactive={this.isLoading}
					/>
				</div>
				<div className={style.file_filter}>
					<Label>{t("Log files")}</Label>
					<ComboBox
						inactive={this.isLoading}
						valueList={this.logFiles}
						onInputChange={event => this.handleFileChange(event.value)}
						value={this.state.logFile}
					/>
				</div>
				<div className={style.message_filter}>
					<Label>{t("Message pattern (use regular expressions)")}</Label>
					<TextInput
						value={this.state.messagePattern}
						onInputChange={event => this.handleMessagePatternChange(event.value)}
						inactive={this.isLoading}
					/>
				</div>
				<div className={style.filter_button}>
					<PrimaryButton onClick={event => this.applyFilter()} inactive={this.isLoading}>
						{t("Apply filter")}
					</PrimaryButton>
				</div>
			</div>

		);
	}

	/** Renders the item list
	 * 	@return {React.Component} the rendered components
	 */
	renderItemList(){
		if (this.itemList === null){
			return (
				<div>
					<p><i>{t("No logs were loaded.")}</i></p>
				</div>
			);
		}

		let data = this.itemList.map(osLog => {
			return [
				osLog.time.toLocaleString(),
				osLog.hostname,
				osLog.message,
			];
		});

		return (
			<Scrollable cssSuffix={style.item_list}>
				<SortedTable
					columns={this.COLUMNS}
					data={data}
					onSortSelection={this.handleSortSelection}
					sortable={this.SORTABLE_COLUMNS}
					sortingColumn={t("Date and time")}
					order={this.ordering}
				/>
				<PrimaryButton type="more" inactive={this.isLoading} onClick={event => this.loadMoreLogs()}>
					{t("More...")}
				</PrimaryButton>
			</Scrollable>
		);
	}

	componentDidUpdate(prevProps, prevState){
		super.componentDidUpdate(prevProps, prevState);

		if (this.state.dateFrom !== null){
			if (this.state.timeFrom !== null && this.state.timeFrom !== ""){
				let date = this.state.dateFrom;
				let dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
				this._dateTimeFrom = new Date(`${dateString} ${this.state.timeFrom}`);
			} else {
				this._dateTimeFrom = new Date(this.state.dateFrom);
				this.setState({timeFrom: this._dateTimeFrom.toLocaleTimeString()});
			}
		} else {
			this._dateTimeFrom = null;
		}
		if (this._dateTimeFrom !== null){
			if (isDateValid(this._dateTimeFrom) && this.state.dateFromError !== null){
				this.setState({dateFromError: null});
			}
			if (!isDateValid(this._dateTimeFrom) && this.state.dateFromError === null){
				this.setState({dateFromError: t("Invalid time")});
			}
		}

		if (this.state.dateTo !== null){
			if (this.state.timeTo !== null && this.state.timeTo !== ""){
				let date = this.state.dateTo;
				let dateString = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
				this._dateTimeTo = new Date(`${dateString} ${this.state.timeTo}`);
			} else {
				this._dateTimeTo = new Date(this.state.dateTo);
				this.setState({timeTo: this._dateTimeTo.toLocaleTimeString()});
			}
		} else {
			this._dateTimeTo = null;
		}
		if (this._dateTimeTo !== null){
			if (isDateValid(this._dateTimeTo) && this.state.dateToError !== null){
				this.setState({dateToError: null});
			}
			if (!isDateValid(this._dateTimeTo) && this.state.dateToError === null){
				this.setState({dateToError: t("Invalid time")});
			}
		}
	}

	/**
	 * 	Triggers when the user changes the sort order
	 * 	@param {string} columnName 			useless
	 * 	@param {string} ordering			'asc' if the user selected ordering in ascending order,
	 * 										'desc' for descending order
	 */
	handleSortSelection(columnName, ordering){
		this.setState({ordering: ordering});
	}

	/**
	 * 	Triggers when the user selected the log starting date
	 * 	@param {Date} dateFrom 				value selected by the user
	 */
	handleDateFromChange(dateFrom){
		this.setState({dateFrom: dateFrom});
	}

	/**
	 * 	Triggers when the user selected the log finish date
	 * 	@param {Date} dateTo 				value selected by the user
	 */
	handleDateToChange(dateTo){
		this.setState({dateTo: dateTo});
	}

	/**
	 * 	Triggers when the user selected the log starting time
	 * 	@param {string} timeFrom 			value selected by the user
	 */
	handleTimeFromChange(timeFrom){
		this.setState({timeFrom: timeFrom});
	}

	/**
	 * 	Triggers when the user selected the log finish time
	 * 	@param {string} timeTo 				value selected by the user
	 */
	handleTimeToChange(timeTo){
		this.setState({timeTo: timeTo});
	}

	/**
	 * 	Triggers when the user selected a particular host
	 * 	@param {string|null} hostname 			the host selected by the user or null if the user selected 'All hosts'
	 */
	handleHostnameChange(hostname){
		this.setState({hostname: hostname});
	}

	/**
	 * 	Triggers when the user selected a particular filename
	 * 	@param {string|null} filename 			the file selected by the user or null if the user selected 'All files'
	 */
	handleFileChange(filename){
		this.setState({logFile: filename});
	}

	/**
	 * 	Triggers when the user tries to change the message pattern
	 * 	@param {string|null} pattern 			the message pattern selected by the user
	 */
	handleMessagePatternChange(pattern){
		this.setState({messagePattern: pattern});
	}

	/**
	 * 	Triggers when the user clicks on the 'Apply filter' button.
	 */
	applyFilter(){
		let currentFilter = {};

		if (this._dateTimeFrom !== null){
			if (!isDateValid(this._dateTimeFrom)){
				return;
			}
			currentFilter.start = this._dateTimeFrom.toISOString();
		}

		if (this._dateTimeTo !== null){
			if (!isDateValid(this._dateTimeTo)){
				return;
			}
			currentFilter.end = this._dateTimeTo.toISOString();
		}

		if (this.state.hostname !== null){
			currentFilter.hostname = this.state.hostname;
		}

		if (this.state.logFile !== null){
			currentFilter.files = this.state.logFile;
		}

		if (this.state.messagePattern !== null){
			currentFilter.q = this.state.messagePattern;
		}

		this.setState({
			currentFilter: currentFilter,
			start: null,
		});
	}

}

OsLogLoader.MAX_LOG_NUMBER = 100;