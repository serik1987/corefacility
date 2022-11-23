import {translate as t} from '../../utils.mjs';
import Log from '../../model/entity/log.mjs';

import CoreListLoader from '../base/CoreListLoader.jsx';
import Label from '../base/Label.jsx';
import TextInput from '../base/TextInput.jsx';
import DateRange from '../base/DateRange.jsx';
import RadioInput from '../base/RadioInput.jsx';
import RadioButton from '../base/RadioButton.jsx';
import PrimaryButton from '../base/PrimaryButton.jsx';
import UserInput from '../user-list/UserInput.jsx';
import LogList from './LogList.jsx';
import styles from './LogListLoader.module.css';


const UserFilterOption = {
	ALL: Symbol("all"),
	ANONYMOUS: Symbol("anonymous"),
	CERTAIN: Symbol("certain"),
}
Object.freeze(UserFilterOption);

const IpFilterOption = {
	ANY: Symbol("any"),
	CERTAIN: Symbol("certain"),
}
Object.freeze(IpFilterOption);

const ResponseStatusFilterOption = {
	ANY: Symbol("any"),
	SUCCESSES: Symbol("successes"),
	FAILS: Symbol("fails"),
}
Object.freeze(ResponseStatusFilterOption);


/** Represents list of all logs, allows to filter them by some criteria.
 * 
 *  Props:
 * 		The component accepts only props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 */
export default class LogListLoader extends CoreListLoader{

	/** Validates the IPv4 address
	 * 
	 * 	@param {string} value 		a value to be validated
	 * 	@return {boolean} 			true if the value is a valid IP address, false otherwise
	 */
	static validateIpv4(value){
		if (value === null){
			return false;
		}

		let isValidIp4 = false;
		let octets = value.split(".");

		if (octets.length === 4){
			let invalidOctetFound = false;
			for (let octet of octets){
				let octetByte = parseInt(octet);
				if (!(0 <= octetByte && octetByte <= 255)){
					invalidOctetFound = true;
					break;
				}
			}
			isValidIp4 = !invalidOctetFound;
		}

		return isValidIp4;
	}

	/** Validates the IPv6 address
	 * 
	 * 	@param {string} value 		a value to be validated
	 * 	@return {boolean} 			true if the value is valid, false otherwise
	 */
	static validateIpv6(value){
	    /* This code is converted from ipaddress.ipaddress._ip_int_from_string using the Python-to-Javacript converter:
	    	https://extendsclass.com/python-to-javascript.html
	   	*/
	   	const _min_parts = 3;
	   	const _HEXTET_COUNT = 8;
	   	const _max_parts = _HEXTET_COUNT + 1;
	   	let _pj;
		let parts, parts_hi, parts_lo, parts_skipped, skip_index;
		let i, _pj_a;

	  	function _pj_snippets(container) {
  			function in_es6(left, right) {
    			if (right instanceof Array || typeof right === "string") {
      				return right.indexOf(left) > -1;
    			} else {
      				if (right instanceof Map || right instanceof Set || right instanceof WeakMap || right instanceof WeakSet) {
        				return right.has(left);
      				} else {
        				return left in right;
      				}
    			}
  			}

  			container["in_es6"] = in_es6;
  			return container;
		}

		_pj = {};
		_pj_snippets(_pj);

		if (!value) {
			return false;
  		}

  		parts = value.split(":");
  		if (parts.length < _min_parts) {
    		return false;
  		}

  		if (_pj.in_es6(".", parts.slice(-1)[0])) {
  			let lastPart = parts.pop();
  			if (!LogListLoader.validateIpv4(lastPart)){
  				return false;
  			}
  			let ipv4Parts = lastPart.split(".")
  				.map(part => parseInt(part));
  			let hexReducer = (accumulator, currentValue)  => (accumulator << 8) + currentValue;
  			let ip4High = ipv4Parts.slice(0, 2).reduce(hexReducer).toString(16);
  			let ip4Low = ipv4Parts.slice(2, 4).reduce(hexReducer).toString(16);
  			parts.push(ip4High);
  			parts.push(ip4Low);
		}

		if (parts.length > _max_parts){
			return false;
		}

		skip_index = null;
		for (i = 1, _pj_a = parts.length - 1; i < _pj_a; i += 1) {
			if (!parts[i]) {
				if (skip_index !== null) {
					return false;
				}

				skip_index = i;
			}
		}

		if (skip_index !== null) {
			parts_hi = skip_index;
			parts_lo = parts.length - skip_index - 1;

			if (!parts[0]) {
				parts_hi -= 1;

				if (parts_hi) {
					return false;
				}
			}

			if (!parts.slice(-1)[0]) {
				parts_lo -= 1;

				if (parts_lo) {
					return false;
				}
			}

			parts_skipped = _HEXTET_COUNT - (parts_hi + parts_lo);

			if (parts_skipped < 1) {
				return false;
			}
		} else {
	    	if (parts.length !== _HEXTET_COUNT) {
	    		return false;
	    	}

			if (!parts[0]) {
				return false;
	    	}

			if (!parts.slice(-1)[0]) {
				return false;
			}

			parts_hi = parts.length;
			parts_lo = 0;
			parts_skipped = 0;
		}

		return parts
		    .filter(part => part)
		    .filter(part => !part.match(/^[0-9abcdef]{1,4}$/i))
		    .length
		    	=== 0;
	}

	constructor(props){
		super(props);
		this.handleRequestDate = this.handleRequestDate.bind(this);
		this.handleUserFilterSelect = this.handleUserFilterSelect.bind(this);
		this.handleUserSelect = this.handleUserSelect.bind(this);
		this.handleIpFilterSelect = this.handleIpFilterSelect.bind(this);
		this.handleIpInput = this.handleIpInput.bind(this);
		this.handleIpFilter = this.handleIpFilter.bind(this);
		this.handleStatusFilter = this.handleStatusFilter.bind(this);

		this.state = {
			...this.state,
			requestDateFrom: null,
			requestDateTo: null,
			userFilter: UserFilterOption.ALL,
			user: null,
			ipFilter: IpFilterOption.ANY,
			ip: null,
			ipInput: null,
			ipError: null,
			statusFilter: ResponseStatusFilterOption.ANY,
		}
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		return Log;
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 *  @abstract
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromPropsAndState(props, state){
		let queryParams = {};
		if (state.requestDateFrom){
			queryParams.from = state.requestDateFrom.toISOString();
		}
		if (state.requestDateTo){
			queryParams.to = state.requestDateTo.toISOString();
		}
		switch (state.userFilter){
			case UserFilterOption.ANONYMOUS:
				queryParams.anonymous = "yes";
				break;
			case UserFilterOption.CERTAIN:
				if (state.user){
					queryParams.user = state.user.id;
				}
				break;
			default:
		}
		if (state.ipFilter === IpFilterOption.CERTAIN){
			queryParams.ip_address = state.ip;
		}
		switch (state.statusFilter){
			case ResponseStatusFilterOption.SUCCESSES:
				queryParams.successes = "yes";
				break;
			case ResponseStatusFilterOption.FAILS:
				queryParams.fails = "yes";
				break;
			default:
		}
		return queryParams;
	}

	/** The function transforms the filter props (and pronbably the state?) to
	 * 	identify the filter identity. The filter identity is a short string that
	 *  follow the following conditions:
	 * 		- if the user did not adjust the filter, the string remains to be unchanged
	 * 		- if the user adjusted at least on of the filter property, the string changes
	 * 	@abstract
	 * 	@return {object} props props for which the filter must be calculated
	 * 	@return {string} the filter identity
	 */
	deriveFilterIdentityFromPropsAndState(props, state){
		let requestDateFrom = state.requestDateFrom ? state.requestDateFrom.toISOString() : "";
		let requestDateTo = state.requestDateTo ? state.requestDateTo.toISOString() : "";
		let userFilter = state.userFilter ? state.userFilter.toString() : UserFilterOption.ALL.toString();
		let user = state.user ? state.user.id : "null";
		let ip = (state.ipFilter === IpFilterOption.CERTAIN && state.ip !== null) ? state.ip : "";
		let responseStatus = state.statusFilter ? state.statusFilter.toString() :
		    ResponseStatusFilterOption.ANY.toString();
		return `${requestDateFrom};${requestDateTo};${userFilter};${user};${ip};${responseStatus}`;
	}

	/** The header to be displayed on the top.
	 */
	get listHeader(){
		return t("Logs");
	}

	/** Triggers when the user clicks on the request date
	 */
	handleRequestDate(event){
		this.setState({
			requestDateFrom: event.from,
			requestDateTo: event.to,
		});
	}

	/** Handles selection of a proper user.
	 */
	handleUserSelect(user){
		this.setState({user: user});
	}

	/** Handles selection of a proper user filter.
	 */
	handleUserFilterSelect(event){
		this.setState({userFilter: event.value});
	}

	/** Handles selection of the type of IP address filter.
	 */
	handleIpFilterSelect(event){
		this.setState({
			ipFilter: event.value,
			ipError: null,
		});
	}

	/** Handles change in current IP address
	 */
	handleIpInput(event){
		this.setState({
			ipInput: event.value,
			ipError: null,
		});
	}

	/** Handles submission of the current IP address
	 */
	handleIpFilter(event){
		let value = this.state.ipInput;

		if (LogListLoader.validateIpv4(value) || LogListLoader.validateIpv6(value)){
			this.setState({
				ip: this.state.ipInput,
				ipError: null,
			});
		} else {
			this.setState({
				ipError: t("Enter a valid IPv4 or IPv6 address."),
			});
		}
	}

	/** Handles the status filter
	 */
	handleStatusFilter(event){
		this.setState({statusFilter: event.value});
	}

	/**	Renders the filter
	 * 	@return {React.Component} all filter widgets to be rendered
	 */
	renderFilter(){
		return (
			<div className={styles.filter}>
				<Label>{t("Request date")}</Label>
				<DateRange
					inactive={this.isLoading}
					onInputChange={this.handleRequestDate}
					dateFrom={this.state.requestDateFrom}
					dateTo={this.state.requestDateTo}
				/>

				<Label>{t("Users")}</Label>
				<div className={styles.col_layout}>
					<RadioInput
					    className={styles.radio_layout}
					    onInputChange={this.handleUserFilterSelect}
					    value={this.state.userFilter}
					    >
                            <RadioButton
                                value={UserFilterOption.ALL}
                                tooltip={t("All users")}
                                inactive={this.isLoading}
                                >
                                    {t("all")}
                            </RadioButton>
                            <RadioButton
                                value={UserFilterOption.ANONYMOUS}
                                tooltip={t("Anonymous requests only")}
                                inactive={this.isLoading}
                                >
                                    {t("anonymous")}
                            </RadioButton>
                            <RadioButton
                                value={UserFilterOption.CERTAIN}
                                tooltip={t("Requests from a given user")}
                                inactive={this.isLoading}
                                >
                                    {t("certain")}
                            </RadioButton>
					</RadioInput>
					{this.state.userFilter === UserFilterOption.CERTAIN &&
						<UserInput
							inactive={this.isLoading}
							tooltip={t("Shows only those requests that has been sent by a certain user.")}
							placeholder={t("Please, specify surname, name or login of such a user...")}
							onItemSelect={this.handleUserSelect}
						/>
					}
				</div>

				<Label>{t("IP address")}</Label>
				<div className={styles.col_layout}>
					<RadioInput
						className={styles.radio_layout}
						onInputChange={this.handleIpFilterSelect}
						value={this.state.ipFilter}
						>
							<RadioButton
								value={IpFilterOption.ANY}
								tooltip={t("Show requests sent from any IP address")}
								inactive={this.isLoading}
								>
									{t("any")}
							</RadioButton>
							<RadioButton
								value={IpFilterOption.CERTAIN}
								tooltip={t("Show requests from a certain IP address")}
								inactive={this.isLoading}
								>
									{t("certain")}
							</RadioButton>
					</RadioInput>
					{this.state.ipFilter === IpFilterOption.CERTAIN &&
						<div className={styles.row_layout}>
							<TextInput
								value={this.state.ipInput}
								inactive={this.isLoading}
								tooltip={t("Show requests from a certain IP address")}
								placeholder={t("Please, specify...")}
								onInputChange={this.handleIpInput}
								error={this.state.ipError}
							/>
							<PrimaryButton type="submit" onClick={this.handleIpFilter} inactive={this.isLoading}>
								{t("Apply")}
							</PrimaryButton>
						</div>
					}
				</div>

				<Label>{t("Response status")}</Label>
				<RadioInput
					value={this.state.statusFilter}
					className={styles.radio_layout}
					onInputChange={this.handleStatusFilter}
					inactive={this.isLoading}
					>
						<RadioButton
						    value={ResponseStatusFilterOption.ANY}
						    tooltip={t("Display all responses")}
						    inactive={this.isLoading}
						    >
							    {t("any")}
						</RadioButton>
						<RadioButton
						    value={ResponseStatusFilterOption.SUCCESSES}
						    tooltip={t("Display successful responses only")}
						    inactive={this.isLoading}
						    >
							    {t("200-299 only")}
						</RadioButton>
						<RadioButton
						    value={ResponseStatusFilterOption.FAILS}
						    tooltip={t("Display failed responses only")}
						    inactive={this.isLoading}
						    >
							    {t("400-599 only")}
						</RadioButton>
				</RadioInput>
			</div>
		);
	}

	/** Renders the item list
	 *  @return {undefined} nothing
	 */
	renderItemList(){
		return <LogList
			items={this.itemList}
			isLoading={this.isLoading}
			isError={this.isError}
			ref={this.registerItemList}
		/>
	}

}