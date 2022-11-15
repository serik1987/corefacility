import {translate as t} from '../../utils.mjs';
import Log from '../../model/entity/log.mjs';

import CoreListLoader from '../base/CoreListLoader.jsx';
import Label from '../base/Label.jsx';
import TextInput from '../base/TextInput.jsx';
import DateRange from '../base/DateRange.jsx';
import RadioInput from '../base/RadioInput.jsx';
import RadioButton from '../base/RadioButton.jsx';
import UserInput from '../user-list/UserInput.jsx';
import LogList from './LogList.jsx';
import styles from './LogListLoader.module.css';


const UserFilterOption = {
	ALL: Symbol("all"),
	ANONYMOUS: Symbol("anonymous"),
	CERTAIN: Symbol("certain"),
}
Object.freeze(UserFilterOption);


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

	constructor(props){
		super(props);
		this.handleRequestDate = this.handleRequestDate.bind(this);
		this.handleUserFilterSelect = this.handleUserFilterSelect.bind(this);
		this.handleUserSelect = this.handleUserSelect.bind(this);

		this.state = {
			...this.state,
			requestDateFrom: null,
			requestDateTo: null,
			userFilter: UserFilterOption.ALL,
			user: null,
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
		if (state.user){
			queryParams.user = state.user.id;
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
		let user = state.user ? state.user.id : "null";
		return `${requestDateFrom};${requestDateTo};${user}`;
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

	/**	Renders the filter
	 * 	@return {React.Component} all filter widgets to be rendered
	 */
	renderFilter(){
		let userIdentity = null;
		if (this.state.user){
			userIdentity = this.state.user.surname || this.state.user.login;
		}

		return (
			<div className={styles.filter}>
				<Label>{t("Request date")}</Label>
				<DateRange
					inactive={this.isLoading}
					onInputChange={this.handleRequestDate}
					dateFrom={this.state.requestDateFrom}
					dateTo={this.state.requestDateTo}
				/>
				<Label>{t("User")}</Label>
				<div className={styles.user_selector}>
					<RadioInput
					    className={styles.user_filter_selector}
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
					<UserInput
						inactive={this.isLoading}
						tooltip={t("Shows only those requests that has been sent by a certain user.")}
						placeholder={t("Please, specify surname, name or login of such a user...")}
						onItemSelect={this.handleUserSelect}
					/>
				</div>
				<Label>{t("IP address")}</Label>
				<TextInput inactive={this.isLoading}/>
				<Label>{t("Response status")}</Label>
				<TextInput inactive={this.isLoading}/>
			</div>
		);
	}

	/** Renders the item list
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