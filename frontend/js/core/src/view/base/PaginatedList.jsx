import {translate as t} from '../../utils.mjs';
import EntityPage from '../../model/entity/page.mjs';
import ItemList from './ItemList.jsx';
import Scrollable from './Scrollable.jsx';
import PrimaryButton from './PrimaryButton.jsx';
import Hyperlink from './Hyperlink.jsx';
import MessageBar from './MessageBar.jsx';
import styles from '../base-styles/PaginatedList.module.css';


/** Represents paginated list.
 * 
 *  Paginated lists are entity lists that are downloaded from the server by small pieces.
 *  Such lists exists as instances of the EntityPage.
 *  The component allows to display several such pages as a single list and provide features
 * 	for downloading more pages and attaching them at the end of the list.
 * 
 * 	This component is unable to manage such lists, provide CRUD operations on them and even
 * 	download the first page. This is considered to be a feature of the parent component.
 * 
 * 	Props:
* 		@param {EntityPage|null} items 		The item list, as it passed by the parent component.
 * 											Must be an instance of EntityPage
 * 		@param {boolean} isLoading			true if the parent component is in 'loading' state.
 * 		@param {boolean} isError			true if the parent component is failed to reload the list.
 * 		@param {callback} onItemSelect		The function calls when the user clicks on a single item in the list (optional)
 * 
 * 	State:
 * 		@param {Array of Entity} items 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 	You should not read or modify any states beginning with underscores (_isLoading, _error, etc.) due to 
 * 	high risk of state damaging. Use getters or setters instead
 */
export default class PaginatedList extends ItemList{

	MIN_AUTONEXT_SCROLL_BUTTON = 80;
	/** Minimum bottom position of the scroll required for automatic press of the "More..." button */

	constructor(props){
		super(props);
		this.handlePagination = this.handlePagination.bind(this);
		this.handleScroll = this.handleScroll.bind(this);
		this.state = {
			...this.state,
			_isLoading: false,
			_error: null,
		}
	}

	/** @return {boolean} true if either parent or current component await for fetching */
	get isLoading(){
		return this.props.isLoading || this.state._isLoading;
	}

	/** @return {boolean} true if either parent or current component failed to fetch the data */
	get isError(){
		return this.props.isError || this.state._error !== null;
	}

	/** @return {Error|null} If fetching the next page fails, this field equals to the Javascript error class of this failure */
	get error(){
		return this.state._error;
	}

	/** Sets the component state to FETCHING
	 * 	@return {undefined}
	 */
	setFetchInProgress(){
		this.setState({
			_isLoading: true,
			_error: null,
		})
	}

	/** Sets the component state to error.
	 * 		@param {Error} error 		Instance of the Javascript class responsible for that error
	 * 		@return {undefined}
	 */
	setFetchFailure(error){
		if (!error){
			throw new TypeError("The error must be a valid Javascript exception");
		}
		this.setState({
			_isLoading: false,
			_error: error,
		});
	}

	/**Sets the component state to success.
	 * @return {undefined}
	 */
	setFetchSuccess(){
		this.setState({
			_isLoading: false,
			_error: null,
		})
	}

	/** Handles press to the 'MORE...' button. Downloads new page and appends it to the end of the given list
	 * 		@async
	 * 		@param {SyntheticEvent} event 		The event object
	 */
	async handlePagination(event){
		if (this.isLoading){
			return;
		}

		this.setFetchInProgress();
		try{
			await this.props.items.next();
			this.liftDown(true);
			this.setFetchSuccess();
		} catch (error){
			this.setFetchFailure(error);
		}
	}

	/** Handles the page scrolling
	 * @async
	 * @param {SyntheticEvent} event 	the event object
	 */
	async handleScroll(event){
		if (event.detail.bottom > this.MIN_AUTONEXT_SCROLL_BUTTON || this.isLoading ||
				this.isError || this.props.items.isLastPage){
			return;
		}

		await this.handlePagination(event);
	}

	render(){
		let container = null;
		let statusBar = null;
		let hyperlink = null;	

		if (!(this.props.items instanceof EntityPage) && this.props.items !== null){
			throw new TypeError("Value of the 'items' prop must be an instance of the EntityPage");
		}

		if (!this.isLoading && !this.isError && this.props.items !== null && !this.props.items.isLastPage){
			statusBar = <PrimaryButton type="more" onClick={this.handlePagination}>{t("More...")}</PrimaryButton>;
		}

		if (!this.props.isLoading && !this.props.isError && (this.isError || this.isLoading)){
			/* Display message bar only if doesn't duplicate another one at the top of the window */
			statusBar = <MessageBar
				isLoading={this.isLoading}
				isError={this.isError}
				error={this.error}
				isAnimatable={false}
				isInline={true}
				/>;
		}

		if (!this.props.isError && this.isError){
			/* Display Try Again only if you need to load the next page to cope with the problem */
			hyperlink = <Hyperlink onClick={this.handlePagination}>{t("Try again.")}</Hyperlink>;
		}

		if (statusBar || hyperlink){
			container = <div class={styles.status_wrapper}>{statusBar} {hyperlink}</div>;
		}

		return (<Scrollable onScroll={this.handleScroll} ref={this.registerScroll}>
			{this.renderContent()}
			{container}
		</Scrollable>);
	}

}