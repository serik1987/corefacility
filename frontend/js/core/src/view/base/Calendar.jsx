import {translate as t} from '../../utils.mjs';

import DropDownInput from './DropDownInput.jsx';
import Icon from './Icon.jsx';
import Hyperlink from './Hyperlink.jsx';
import {ReactComponent as PreviousIcon} from '../base-svg/arrow_back.svg';
import {ReactComponent as NextIcon} from '../base-svg/arrow_forward.svg';
import styles from '../base-styles/Calendar.module.css';


/** Number of monday in the Javascript */
const MONDAY = 1;

/** Number of sunday in the Javascript */
const SUNDAY = 0;

/** Enumerates all days in the week: their Javascript numbers are presented here... */
const DAYS_IN_WEEK = [MONDAY, 2, 3, 4, 5, 6, SUNDAY];

/** Total number of milliseconds in one second */
const ONE_SECOND = 1000;

const MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August",
	"September", "October", "November", "December"];

const WEEK_DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

/* Defines date in Russian format */
const POSITION_DATE = 1;
const POSITION_MONTH = 2;
const POSITION_YEAR = 3;

/* Number of years in one century */
const CENTURY = 100;

const ONE_NUMBER_PATTERN = /^[^\d]*(\d+)[^\d]*$/;
const TWO_NUMBER_PATTERN = /^[^\d]*(\d+)[^\d]+(\d+)[^\d]*$/;
const THREE_NUMBER_PATTERN = /^[^\d]*(\d+)[^\d]+(\d+)[^\d]+(\d+)[^\d]*$/;


/** Implements the calendar.
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
 *  @param {string} placeholder			The input placeholder
 * 
 * 	@param {Date} defaultValue			Value of the widget at the time of its creation (the constructor call).
 * 										Useless for fully controlled mode.
 * 
 * 	@param {Date} value 				If this is an instance of Javascript Date object or null, it defines that that
 * 										widget is in fully controlled mode and also equals to the date set up at last
 * 										widget opening.
 * 										undefined means that the widget is fully uncontrolled.
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
export default class Calendar extends DropDownInput{

	static JANUARY = 0;
	static FEBRUARY = 1;
	static MARCH = 2;
	static APRIL = 3;
	static MAY = 4;
	static JUNE = 5;
	static JULY = 6;
	static AUGUST = 7;
	static SEPTEMBER = 8;
	static OCTOBER = 9;
	static NOVEMBER = 10;
	static DECEMBER = 11;

	constructor(props){
		super(props);
		this.handleDate = this.handleDate.bind(this);
		this.setCurrentDate = this.setCurrentDate.bind(this);
		this.clearDate = this.clearDate.bind(this);

		let date = this.props.defaultValue;
		if (date === undefined){
			date = null;
		}

		this.state = {
			...this.state,
			value: date,
			month: null,
			year: null,
		}

		this._currentDate = null;
		this._valueDate = null;
		this._month = null;
		this._year = null;
	}

	/** Checks whether given number is a valid year
	 * 	@param {number} number a number to check
	 * 	@return {boolean} true if the number is a valid year, false otherwise
	 */
	isYear(number){
		let currentYear = this._currentDate.getFullYear() || new Date().getFullYear();
		let minYear = currentYear - CENTURY;
		let maxYear = currentYear + CENTURY;
		if (this.isDate(this.props.minDate)){
			let minDateYear = this.props.minDate.getFullYear();
			if (minDateYear > minYear){
				minYear = minDateYear;
			}
		}
		if (this.isDate(this.props.maxDate)){
			let maxDate = new Date(this.props.maxDate);
			maxDate.setMilliseconds(maxDate.getMilliseconds() - 1);
			let maxDateYear = maxDate.getFullYear();
			if (maxDateYear < maxYear){
				maxYear = maxDateYear;
			}
		}
		return minYear <= number && number <= maxYear;
	}

	/** Checks whether argument is a valid date. The date is treated to be a valid date when: (a) this is an instance of
	 * 	of Javascript's Date class; (b) Javascript doesn't recognise it as 'invalid date'
	 * 	@param {any} date 		The date to check
	 * 	@return {boolean}		true if the argument is a valid date, false otherwise
	 */
	isDate(date){
		return date instanceof Date && !isNaN(date);
	}

	/** Checks whether given date exists
	 * 	@param {number} year
	 * 	@param {number} month
	 * 	@param {number} day
	 * 	@return {boolean} true if a triple {year, month, day} relates to a valid date, false otherwise
	 */
	hasDate(year, month, day){
		let date = new Date(year, month, day);
		if (date.getFullYear() === year && date.getMonth() === month &&
			date.getDate() === day){
				if (this._checkDateInRange(date)){
					return date;
				} else {
					return null;
				}
		} else {
			return null;
		}
	}

	/** Returns the callback that handles press on "Previous month" or "Next month" button
	 * 	@param {number} increment Amount of months to be changed. The increment is positive if you want to increase
	 * 	the month and negative if you want to decrease.
	 * 	@return {callback} the callback function that can be set as onClick button event
	 */
	monthHandlerGenerator(increment){
		let self = this;
		return (event => {
			this._refreshMonthAndYear();
			this._month += increment;
			if (this._month > this.constructor.DECEMBER){
				this._month = this.constructor.JANUARY;
				this._year += 1;
			}
			if (this._month < this.constructor.JANUARY){
				this._month = this.constructor.DECEMBER;
				this._year -= 1;
			}
			this.setState({month: this._month, year: this._year});
		}).bind(this);
	}

	/** Sets the calendar's date to the current one
	 * 	@param {SyntheticEvent} event the event that has bee triggered this action
	 * 	@return {undefined}             nothing
	 */
	setCurrentDate(event){
		let currentDate = new Date();
		let date = new Date(currentDate.getFullYear(), currentDate.getMonth(), currentDate.getDate());
		this.setState({
			value: date,
			month: date.getMonth(),
			year: date.getFullYear(),
			inputBoxRawValue: date.toLocaleDateString(),
			inputBoxValue: date.toLocaleDateString(),
		})
	}

	/** Clears the calendar date
	 * 	@param {SyntheticEvent} event 		the event that has been triggered the action
	 * 	@return {undefined}
	 */
	clearDate(event){
		this.setState({
			value: null,
			month: null,
			year: null,
			inputBoxRawValue: null,
			inputBoxValue: null,
		});
	}

	/** Handles click on a given date within the calendar
	 * 	@param {SyntheticEvent} event 		The event that has been triggered such a click
	 * 										The event must contain target!
	 * 	@return {undefined}
	 */
	handleDate(event){
		let date = new Date(event.target.dataset.date);
		if (!this._checkDateInRange(date)){
			return;
		}
		this.setState({
			isOpened: false,
			value: date,
			month: null,
			year: null,
		});
		event.value = date;
		this.handleMenuClose(event);
	}

	/** Handles the input change of the box. (The state must be changed.)
	 * 	To be re-defined in subclasses
	 * 
	 * 	@param {SyntheticEvent} the event that has been triggered
	 * 	@return {undefined}
	 */
	handleInputChange(event){
		super.handleInputChange(event);
		this._refreshMonthAndYear();

		/* The very beginning attempt: empty string is always date clearing */
		if (event.value === null){
			this.setState({
				value: null,
			});
			return;
		}

		/* User has entered just one number */
		let oneNumberMatch = event.value.match(ONE_NUMBER_PATTERN);
		if (oneNumberMatch !== null){
			let number = parseInt(oneNumberMatch[POSITION_DATE]);
			let buffer = null;

			/* Attempt 1. The user has entered a valid day */
			buffer = this.hasDate(this._year, this._month, number);
			if (buffer){
				this.setState({
					value: buffer,
					month: this._month,
					year: this._year,
				});
				return;
			}

			/* Attempt 2. The user has entered a valid year */
			if (this.isYear(number)){
				this.setState({
					value: null,
					month: this._correctMonthForYear(number, this._month),
					year: number,
				});
				return;
			}

			/* If nothing is suited - don't apply another parsing methods */
			return;
		}

		/* The User has entered two numbers */
		let twoNumberMatch = event.value.match(TWO_NUMBER_PATTERN);
		if (twoNumberMatch !== null){
			let number1 = parseInt(twoNumberMatch[POSITION_DATE]);
			let number2 = parseInt(twoNumberMatch[POSITION_MONTH]);
			let buffer = null;

			/* Attempt 3. This is day and month */
			buffer = this.hasDate(this._year, number2 - 1, number1);
			if (buffer){
				this.setState({
					value: buffer,
					month: number2 - 1,
					year: this._year,
				});
				return;
			}

			/* Attempt 4. This is month and year */
			if (this.isYear(number2)){
				let month = this._correctMonthForYear(number2, number1 - 1);
				if (month === number1 - 1){
					this.setState({
						value: null,
						month: number1 - 1,
						year: number2
					});
					return;
				}
			}

			/* If nothing is suited - don't apply another parsing methods */
			return;
		}

		/* The user entered three numbers */
		let threeNumberMatch = event.value.match(THREE_NUMBER_PATTERN);
		if (threeNumberMatch !== null){
			let day = parseInt(threeNumberMatch[POSITION_DATE]);
			let month = parseInt(threeNumberMatch[POSITION_MONTH]);
			let year = parseInt(threeNumberMatch[POSITION_YEAR]);
			let buffer = null;

			/* Attempt 5. The user has entered day, month and year (i.e., full date) */
			buffer = this.hasDate(year, month - 1, day);
			if (buffer){
				this.setState({
					value: buffer,
					month: buffer.getMonth(),
					year: buffer.getFullYear(),
				});
				return;
			}
		}

		/* The last effort - using standard Javascript string-to-date converter */
		let date = new Date(event.value);
		if (!isNaN(date) && this._checkDateInRange(date)){
			this.setState({
				value: date,
				month: date.getMonth(),
				year: date.getFullYear(),
			});
			return;
		}

		/* If all attempts to guess what user actually means failed - setting null date */
		this.setState({
			value: null,
			month: null,
			year: null,
		});
	}

	/** Handles click outside the window (The drop down must be closed.)
	 * 
	 *  @param {SyntheticEvent} the event that has been triggered on menu close
	 * 	@return {undefined}
	 */
	handleMenuClose(event){
		let date = event.value || this.state.value;
		super.handleMenuClose(event);
		if (date === null){
			this.setState({
				inputBoxRawValue: null,
				inputBoxValue: null,
			});
		} else {
			this.setState({
				inputBoxRawValue: date.toLocaleDateString(),
				inputBoxValue: date.toLocaleDateString(),
			});
		}
		if (this.props.onInputChange){
			event.value = date;
			if (this.props.value !== undefined){ /* In fully controlled mode: trigger the componentDidUpdate! */
				this.setState({value: undefined});
			}
			this.props.onInputChange(event);
		}
	}

	/** Changes the current month, current date and current year based on the state
	 * 	@return {undefined}
	 */
	_refreshMonthAndYear(){
		this._currentDate = new Date();
		this._valueDate = this.state.value || this._currentDate;
		if (!this._checkDateInRange(this._valueDate)){
			if (this.isDate(this.props.minDate)){
				this._valueDate = new Date(this.props.minDate);
			} else {
				let maxDate = new Date(this.props.maxDate);
				maxDate.setDate(maxDate.getDate() - 1);
				this._valueDate = maxDate;
			}
		}
		if (this.state.month === null){
			this._month = this._valueDate.getMonth();
		} else {
			this._month = this.state.month;
		}
		if (this.state.year === null){
			this._year = this._valueDate.getFullYear();
		} else {
			this._year = this.state.year;
		}
	}

	/** If the date is less than the minDate prop, sets the date to the min date.
	 * 	If the date is greater than the maxDate prop, sets the date to the max date.
	 * 
	 * 	@param {Date} the date before correction (assumed not to be equal to null or undefined)
	 * 	@return {Date} the date after correction
	 */
	_correctDateAccordingToProps(date){
		if (this.isDate(this.props.minDate) && date < this.props.minDate){
			date = new Date(this.props.minDate);
		}
		if (this.isDate(this.props.maxDate) && date > this.props.maxDate){
			date = new Date(this.props.maxDate);
		}
		return date;
	}

	/** Checks whether the date lies within the range set up by minDate and maxDate props
	 * 
	 * 	@param {Date} the date to be checked
	 * 	@return {boolean} true if the date lies within the given range, false otherwise
	 */
	_checkDateInRange(date){
		if (this.isDate(this.props.minDate) && date < this.props.minDate){
			return false;
		}
		if (this.isDate(this.props.maxDate) && date >= this.props.maxDate){
			return false;
		}
		return true;
	}

	/** Changes the month in such a way as pair (year, month) lies within the range defined by (minDate, maxDate) props.
	 * 
	 * 	@param {number} year 		The year in the range
	 * 	@param {number} month 		Month before correction
	 * 	@return {number} 			Month after correction
	 */
	_correctMonthForYear(year, month){
		let minMonth = this.constructor.JANUARY;
		let maxMonth = this.constructor.DECEMBER;
		if (this.isDate(this.props.minDate) && this.props.minDate.getFullYear() === year){
			minMonth = Math.max(minMonth, this.props.minDate.getMonth());
		}
		if (this.isDate(this.props.maxDate)){
			let maxDate = new Date(this.props.maxDate);
			maxDate.setMilliseconds(maxDate.getMilliseconds() - 1);
			if (maxDate.getFullYear() === year){
				maxMonth = Math.min(maxMonth, maxDate.getMonth());
			}
		}
		if (month < minMonth){
			month = minMonth;
		}
		if (month > maxMonth){
			month = maxMonth;
		}
		return month;
	}

	/**	In fully controlled mode: Updates the widget state according to the value props
	 * 	In fully uncontrolled mode: throws an exception
	 */
	_deriveStateFromProps(){
		if (this.isDate(this.props.value)){
			let value = new Date(this.props.value);
			value = this._correctDateAccordingToProps(value);
			this.setState({
				value: value,
				inputBoxRawValue: value.toLocaleDateString(),
				inputBoxValue: value.toLocaleDateString(),
			});
		} else if (this.props.value === null){
			this.setState({
				value: null,
				inputBoxRawValue: null,
				inputBoxValue: null,
			});
		} else {
			throw new Error(`The 'value' prop can't be ${this.props.value}: 
				either a valid Date object or null or undefined`);
		}
	}

	renderChildren(){
		this._refreshMonthAndYear();
		let prevButtonDisabled = false;
		let nextButtonDisabled = false;
		let calendarStart = new Date(this._year, this._month, 1);
		let calendarEnd = new Date(calendarStart);
		calendarEnd.setMonth(calendarStart.getMonth() + 1, calendarStart.getDate() - 1);

		if (this.isDate(this.props.minDate) && this.props.minDate >= calendarStart){
			prevButtonDisabled = true;
		}

		if (this.isDate(this.props.maxDate)){
			let maxDate = new Date(this.props.maxDate);
			maxDate.setDate(maxDate.getDate() - 1);
			if (maxDate <= calendarEnd){
				nextButtonDisabled = true;
			}
		}

		if (this.state.value === undefined){
			return <p>Undefined component state!</p>;
		}

		while (calendarStart.getDay() !== MONDAY){
			calendarStart.setDate(calendarStart.getDate() - 1);
		}

		while (calendarEnd.getDay() !== SUNDAY){
			calendarEnd.setDate(calendarEnd.getDate() + 1);
		}

		let calendarDays = [];

		let calendarCurrent = new Date(calendarStart);

		while (calendarCurrent <= calendarEnd){
			let dayStyles = styles.day;
			if (calendarCurrent.getMonth() === this._month){
				dayStyles += ` ${styles.cmonth}`;
			}
			if (
				calendarCurrent.getFullYear() === this._currentDate.getFullYear() &&
				calendarCurrent.getMonth() === this._currentDate.getMonth() &&
				calendarCurrent.getDate() === this._currentDate.getDate()
			) {
				dayStyles += ` ${styles.cdate}`;
			}
			if (this.state.value !== null && 
				calendarCurrent.getFullYear() === this.state.value.getFullYear() &&
				calendarCurrent.getMonth() === this.state.value.getMonth() &&
				calendarCurrent.getDate() === this.state.value.getDate()){
					dayStyles += ` ${styles.vdate}`;
			}
			if (!this._checkDateInRange(calendarCurrent)){
				dayStyles += ` ${styles.disabled}`;
			}

			calendarDays.push(
				<span className={styles.day_wrapper}>
					<a
						onClick={this.handleDate}
						className={dayStyles}
						data-date={calendarCurrent.toISOString()}
						>
							{calendarCurrent.getDate()}
					</a>
				</span>
			);

			calendarCurrent.setDate(calendarCurrent.getDate() + 1);
		}

		return (
			<div className={styles.calendar}>
				<div className={styles.hyperlinks_panel}>
					<Hyperlink
						onClick={this.setCurrentDate}
						disabled={!this._checkDateInRange(this._currentDate)}
						>
							{t("Current date")}
					</Hyperlink>
					<Hyperlink onClick={this.clearDate}>{t("Clear date")}</Hyperlink>
				</div>
				<div className={styles.month_panel}>
					<div className={styles.month_box}>
						<span>{t(MONTH_NAMES[this._month])}</span>
						{" "}
						<span>{this._year}</span>
					</div>
					<Icon
						tooltip={t("Previous month")}
						src={<PreviousIcon/>}
						onClick={this.monthHandlerGenerator(-1)}
						disabled={prevButtonDisabled}
					/>
					<Icon
						tooltip={t("Next month")}
						src={<NextIcon/>}
						onClick={this.monthHandlerGenerator(1)}
						disabled={nextButtonDisabled}
					/>
				</div>
				<div className={styles.calendar_panel}>
					{WEEK_DAY_NAMES.map(dayName => {
						return (<span className={styles.day_wrapper}>
							<span className={styles.day}>{t(dayName)}</span>
						</span>);
					})}
					{calendarDays}
				</div>
			</div>
		);
	}

	componentDidMount(){
		if (this.props.value !== undefined){ /* In fully controlled mode */
			this._deriveStateFromProps();
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.value !== undefined /* In case of fully controlled state, */
			&& this.state.value === undefined){ /* Given that the state has been cleared previously */
			this._deriveStateFromProps();
		}
	}

}