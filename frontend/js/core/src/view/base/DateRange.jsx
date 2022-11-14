import * as React from 'react';

import {translate as t} from '../../utils.mjs';

import Calendar from './Calendar.jsx';
import styles from '../base-styles/DateRange.module.css';


/** Implements the date range.
 * 
 * 	
 * 
 * 	The calendar could work in the following modes:
 * 		Fully controlled mode 			Value of the widget is fully controlled by the parent widget. In order to allow
 * 										the user to change the calendar value the parent widget must define handler
 * 										for onInputChange event.
 * 										To switch into this mode, define value ad onInputChange props.
 * 
 * 		Fully uncontrolled mode 		Value of the widget is fully controlled by the user. There is nothing to do to
 * 										allow the user to change the widget's value. However, the parent can't setup
 * 										the value itself.
 * 										The widget works in this mode by default.
 * 
 * 	Props:
 * ---------------------------------------------------------------------------------------------------------------------
 * 	@param {callback} onInputChange		The event is triggered when then user changes the data and confirms the data
 * 										change. The user confirms the date change either by contracting the widget or
 * 										by clicking on a certain date. The function takes the only argument - event
 * 										event.value contains the date that has been currently set. (a Date instance).
 * 										Hours, Minutes, Seconds and Milliseconds are 0, timezone is frontend's local
 * 										time.
 * 
 * 	@param {boolean} inactive			if true, the input box will be inactive and hence will not expand or contract
 *	 									the item box.
 *	@param {boolean} disabled			When the input box is disabled, it is colored as disabled and the user can't
 * 										enter any value to it
 * 
 *	@param {string} error				The error message that will be printed when validation fails
 * 
 *	@param {string} htmlType			Type of the HTML's input element. For list of available types see here:
 * 											https://developer.mozilla.org/en-US/docs/Web/HTML/Element/input#input_types
 * 										The following types are supported: email, password, search, tel, text, url
 * 
 *	@param {string} tooltip				Detailed description of the field
 * 
 * 	@param {Date} defaultValue			Value of the widget at the time of its creation (the constructor call).
 * 										Useless for fully controlled mode.
 * 
 * 	@param {Date} value 				If this is an instance of Javascript Date object or null, it defines that that
 * 										widget is in fully controlled mode and also equals to the date set up at last
 * 										widget opening.
 * 										undefined means that the widget is fully uncontrolled.
 * 
 * 	@param {Date} defaultDateFrom		The start date at the widget construction time. Not equals to the current
 * 										start date
 * 
 * 	@param {Date} defaultDateTo			The finish date at the widget construction time. Not equals to the current
 * 										finish date.
 * 
 *	@param {Date} dateFrom 				Defines start date in fully controlled mode. Must be undefined in fully
 * 										uncontrolled mode.
 * 
 * 	@param {Date} dateTo 				Defines finish date in fully controlled mode. Must be undefined in fully
 * 										uncontrolled mode.
 * ---------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * ---------------------------------------------------------------------------------------------------------------------
 * 	@param {string} inputBoxValue		Current value of the input box when it works in fully uncontrolled mode.
 * 										Useless when it works in fully controlled mode.
 * 
 * 	@param {string} inputBoxRawValue	The same as value but before input preprocessing (removing leading and trailing
 * 										whitespaces etc.)
 * 
 * 	@param {Date|null} value			Represents the current date selected by the user.
 * 										When the widget is in fully controlled mode, this state field equals to
 * 										undefined when the widget is closed.
 * ---------------------------------------------------------------------------------------------------------------------
 */
export default class DateRange extends React.Component{

	constructor(props){
		super(props);
		this.handleFromChange = this.handleFromChange.bind(this);
		this.handleToChange = this.handleToChange.bind(this);

		this.state = {
			from: null,
			to: null,
		}

		if (this.props.defaultDateFrom){
			this.state.from = new Date(this.props.defaultDateFrom);
		}
		if (this.props.defaultDateTo){
			this.state.to = new Date(this.props.defaultDateTo);
		}
	}

	handleFromChange(event){
		let dateFrom = null;
		if (event.value !== null){
			dateFrom = new Date(event.value);
		}
		let dateTo = this.state.to;
		if (dateFrom !== null && dateTo !== null && dateTo <= dateFrom){
			dateTo = new Date(dateFrom.getFullYear(), dateFrom.getMonth(), dateFrom.getDate() + 1);
		}
		this.handleRangeChange(event, dateFrom, dateTo);
	}

	handleToChange(event){
		let dateFrom = this.state.from;
		let dateTo = null;
		if (event.value !== null){
			dateTo = new Date(event.value);
			dateTo.setDate(dateTo.getDate() + 1); // The user entered dateTo as included. Our frontend and backend treat the
				// date as mainly NOT included.
		}
		if (dateFrom !== null && dateTo !== null && dateFrom >= dateTo){
			dateFrom = new Date(dateTo.getFullYear(), dateTo.getMonth(), dateTo.getDate() - 1);
		}
		this.handleRangeChange(event, dateFrom, dateTo);
	}

	handleRangeChange(event, dateFrom, dateTo){
		/* More generally, the operator && returns the value of the first falsy operand encountered when evaluating from
		 * left to right, or the value of the last operand if they are all truthy.
		 *
		 *(C) https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Logical_AND
		 */
		let timestampFrom = dateFrom && dateFrom.getTime();
		let timestampTo = dateTo && dateTo.getTime();
		let stateTimestampFrom = this.state.from && this.state.from.getTime();
		let stateTimestampTo = this.state.to && this.state.to.getTime();
		if (timestampFrom === stateTimestampFrom && timestampTo === stateTimestampTo){
			return;
		}
		this.setState({
			from: dateFrom,
			to: dateTo,
		});
		if (this.props.onInputChange){
			this.props.onInputChange({...event, from: dateFrom, to: dateTo});
		}
	}


	render(){
		let dateFrom = null;
		let dateTo = null;

		if (this.state.from !== null){
			dateFrom = new Date(this.state.from);
		}
		if (this.state.to !== null){
			dateTo = new Date(this.state.to);
			dateTo.setDate(dateTo.getDate() - 1); // For the DateRange, the date is not included, for the user the date is
				// included.	
		}

		return (
			<div className={styles.container}>
				<span>{t("From") + ": "}</span>
				<Calendar
					value={dateFrom}
					maxDate={this.state.to}
					onInputChange={this.handleFromChange}
					inactive={this.props.inactive}
					disabled={this.props.disabled}
					tooltip={this.props.tooltip}
					error={this.props.error}
				/>
				<span>{" " + t("To") + ": "}</span>
				<Calendar
					value={dateTo}
					minDate={this.state.from}
					onInputChange={this.handleToChange}
					inactive={this.props.inactive}
					disabled={this.props.disabled}
					tooltip={this.props.tooltip}
				/>
			</div>
		);
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.dateFrom !== undefined){
			let desiredTimestampFrom = this.props.dateFrom && this.props.dateFrom.getTime();
			let actualTimestampFrom = this.state.from && this.state.from.getTime();
			if (desiredTimestampFrom !== actualTimestampFrom){
				this.setState({from: this.props.dateFrom});
			}
		}
		if (this.props.dateTo !== undefined){
			let desiredTimestampTo = this.props.dateTo && this.props.dateTo.getTime();
			let actualTimestampTo = this.state.to && this.state.to.getTime();
			if (desiredTimestampTo !== actualTimestampTo){
				this.setState({to: this.props.dateTo});
			}
		}
	}

}