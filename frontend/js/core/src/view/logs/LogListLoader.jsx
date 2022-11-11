import {translate as t} from '../../utils.mjs';
import Log from '../../model/entity/log.mjs';

import CoreListLoader from '../base/CoreListLoader.jsx';
import Label from '../base/Label.jsx';
import TextInput from '../base/TextInput.jsx';
import Calendar from '../base/Calendar.jsx';
import LogList from './LogList.jsx';
import styles from './LogListLoader.module.css';


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

		this.state = {
			...this.state,
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
	deriveFilterFromProps(){
		return {}
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
	deriveFilterIdentityFromProps(props){
		return "";
	}

	/** The header to be displayed on the top.
	 */
	get listHeader(){
		return t("Logs");
	}

	/**	Renders the filter
	 * 	@return {React.Component} all filter widgets to be rendered
	 */
	renderFilter(){
		return (
			<div className={styles.filter}>
				<Label>{t("Request date")}</Label>
				<Calendar inactive={this.isLoading}/>
				<Label>{t("User")}</Label>
				<TextInput inactive={this.isLoading}/>
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