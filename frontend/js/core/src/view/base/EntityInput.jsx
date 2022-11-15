import ListLoader from './ListLoader.jsx';
import LoadableDropDownInput from './LoadableDropDownInput.jsx';
import MessageBar from './MessageBar.jsx';
import styles from '../base-styles/EntityInput.module.css';


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
 * 	--------------------------------------------------------------------------------------------------------------------
 *  
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {boolean} isOpened 			true if the input must be opened, false if it must be closed
 * 
 * 	@param {string} rawSearchTerm		the hint entered by the user (before pre-processing)
 * 
 * 	@param {string} searchTerm 			the hint entered by the user (after pre-processing)
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
		console.log("Reloading...");
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
	}

}