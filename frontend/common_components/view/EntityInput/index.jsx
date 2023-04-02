import {NotImplementedError} from 'corefacility-base/exceptions/model'
import Entity from 'corefacility-base/model/entity/Entity';
import LoadableDropDownInput from 'corefacility-base/shared-view/components/LoadableDropDownInput';
import MessageBar from 'corefacility-base/shared-view/components/MessageBar';

import ListLoader from '../ListLoader';
import styles from './style.module.css';


/** Base class for all drop-down lists where list items must be uploaded from the external resource based on some hint
 * 	entered by the user.
 * 
 * 	Props:
 *  --------------------------------------------------------------------------------------------------------------------
 *  @param {boolean} inactive           if true, the input box will be inactive and hence will not expand or contract
 *                                      the item box.
 * 
 *  @param {boolean} disabled           When the input box is disabled, it is colored as disabled and the user can't
 *                                      enter any value to it.
 * 
 *  @param {string} error               The error message that will be printed when validation fails
 * 
 *  @param {string} tooltip             Detailed description of the field
 * 
 *  @param {string} placeholder         The input placeholder
 * 
 * 	@param {string} searchTerm 			The search string to be entered. Overrides rawSearchTerm and searchTerm states.
 * 
 * 	@param {Entity} value 				A certain entity provided by the parent component. Has higher priority than the
 * 										entity chosen by the user
 * 	--------------------------------------------------------------------------------------------------------------------
 *  
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} isOpened 			true if the input must be opened, false if it must be closed
 * 
 * 	@param {string} rawSearchTerm		the hint entered by the user (before pre-processing)
 * 
 * 	@param {string} searchTerm 			the hint entered by the user (after pre-processing)
 * 
 * 	@param {Entity} value 				a certain entity chosen by the user or null if no entity has been chosen
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class EntityList extends ListLoader{

	constructor(props){
		super(props);
		this.onInputChange = this.onInputChange.bind(this);
		this.handleOpened = this.handleOpened.bind(this);
		this.handleClosed = this.handleClosed.bind(this);
		this.handleSelectItem = this.handleSelectItem.bind(this);
		this._dropDown = null;

		this.state = {
			...this.state,
			rawSearchTerm: null,
			searchTerm: null,
			isOpened: false,
		}
	}

	/** Loads the item list from the external source
	 *  @async
	 *  @return {undefined}
	 */
	async reload(){
		if (!this.state.isOpened){
			return;
		}	
		await super.reload();
	}

	/** Triggers when the user changes the input in the drop-down input box (Action: new user search according to the 
	 * 	currently stated criteria)
	 */
	onInputChange(event){
		this.setState({
			rawSearchTerm: event.target.value,
			searchTerm: event.value,
		});
	}

	/** Triggers when the user opens drop-down
	 * 
	 * 	@param {SyntheticEvent} event the event that triggered this handler
	 * 	@return {undefined}
	 */
	handleOpened(event){
		this.setState({isOpened: true});
	}

	/** Triggers when the user closes drop-down
	 * 
	 * 	@param {SyntheticEvent} event the event that triggered this handler
	 * 	@return {undefined}
	 */
	handleClosed(event){
		this.setState({isOpened: false});
	}

	/**
	 * 	Returns a string that will be put into an input box when the user clicks on it.
	 */
	getEntityIdentity(entity){
		throw new NotImplementedError('getEntityIdentity');
	}

	/** Triggers when the user picks up an item from the item box.
	 * 
	 * 	@param {Entity} item 	The entity picked up by the user
	 * 	@return {undefined}
	 */
	handleSelectItem(item){
		let identity = this.getEntityIdentity(item);

		if (this.isLoading){
			return;
		}
		this.setState({
			rawSearchTerm: identity,
			searchTerm: identity,
			value: item,
			isOpened: false,
		})
		if (this.props.onItemSelect){
			this.props.onItemSelect(item);
		}
	}

	render(){
		return (
			<LoadableDropDownInput
				inactive={this.props.inactive}
				disabled={this.props.disabled}
				error={this.props.error}
				tooltip={this.props.tooltip}
				placeholder={this.props.placeholder}
				onInputChange={this.onInputChange}
				onOpened={this.handleOpened}
				onClosed={this.handleClosed}
				isOpened={this.state.isOpened}
				inputBoxRawValue={this.state.rawSearchTerm}
				inputBoxvalue={this.state.searchTerm}
				>
					{(this.isLoading || this.isError) && <MessageBar
						isLoading={this.isLoading}
						isError={this.isError}
						error={this.error}
						isAnimatable={false}
						cssSuffix={` ${styles.error_message} ${styles.is_opened}`}
					/>}
					{this.renderItemList()}
			</LoadableDropDownInput>
		);
	}

	componentDidUpdate(prevProps, prevState, snapshot){
		super.componentDidUpdate(prevProps, prevState, snapshot);

		if (!prevState.isOpened && this.state.isOpened){
			this.reload();
		}

		if (this.props.searchTerm !== undefined && this.props.searchTerm !== this.state.searchTerm){
			this.setState({
				searchTerm: this.props.searchTerm,
				rawSearchTerm: this.props.searchTerm,
			});
		}

		if (this.props.value instanceof Entity && this.props.value !== this.state.value){
			let identity = this.getEntityIdentity(this.props.value);
			this.setState({
				searchTerm: identity,
				rawSearchTerm: identity,
				value: this.props.value,
			});
		}

		if (this.props.value === null && this.props.value !== this.state.value){
			this.setState({
				searchTerm: null,
				rawSearchTerm: null,
				value: null,
			});
		}
	}

}