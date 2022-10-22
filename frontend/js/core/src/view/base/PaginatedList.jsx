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
 * 		@param {boolean} isLoading		true if the parent component is in 'loading' state.
 * 		@param {boolean} isError		true if the parent component is failed to reload this item list.
 * 						WHEN THE PARENT COMPONENT IS LOADING OR HAVE ERROR STATE, the navigation between
 * 						pages is not possible
 * 		@param {EntityPage}	items 		the entity page to show
 * 		@param {callback} onItemSelect		The function calls when the user clicks on a single item in the list
 * 
 * 	State:
 * 		@param {Array of Entity} items 	full list of all items containing in all downloaded entity pages.
 * 										Items from pages that are not downloaded yet were not shown.
 * 		@param {boolean} isLoading		true the following page is still loading, false otherwise
 * 		@param {Error|null} error 		The error object if the component is in the error state/
 */
export default class PaginatedList extends ItemList{

	MIN_AUTONEXT_SCROLL_BUTTON = 80;

	constructor(props){
		super(props);
		this.handlePagination = this.handlePagination.bind(this);
		this.handleScroll = this.handleScroll.bind(this);
		this.setFetchSuccess(false, false);
	}

	/** The entity page containing in the props.
	 *  The entity page is unavailable when the parent component is in error or loading state */
	get entityPage(){
		if (this.props.isLoading || this.props.isError){
			return null;
		} else {
			return this.props.items;
		}
	}

	/** Items containing in all pages that have already been downloaded from the server */
	get items(){
		return this.state.items;
	}

	/** true if downloading the next page is still in progress, false otherwise */
	get isLoading(){
		return this.state.isLoading;
	}

	/** true if fetching the following page was failed, false otherwise */
	get isError(){
		return this.state.error !== null;
	}

	/** If fetching the next page fails, this field equals to the Javascript error class of this failure */
	get error(){
		return this.state.error;
	}

	/** Sets the component state to FETCHING */
	setFetchInProgress(){
		this.setState({
			isLoading: true,
			error: null,
		})
	}

	/** Sets the component state to error.
	 * 		@param {Error} error 		Instance of the Javascript class responsible for that error
	 */
	setFetchFailure(error){
		if (!error){
			throw new TypeError("The error must be a valid Javascript exception");
		}
		this.setState({
			isLoading: false,
			error: error,
		});
	}

	/**Sets the component state to success.
	 * 		@param {boolean} appendItems	true if the downloaded page must be attached to the current list, false otherwise
	 * 		@param {boolean} update 		true, if you need to change the component state, false if you set initial state
	 */
	setFetchSuccess(appendItems = false, update = true){
		let newItems = null;

		if (this.props.items === null){
			newItems = [];
		} else if (appendItems){
			newItems = [...this.state.items, ...this.props.items];
		} else {
			newItems = [...this.props.items];
		}

		if (update){
			this.setState({
				items: newItems,
				isLoading: false,
				error: null,
			});
		} else {
			this.state = {
				items: newItems,
				isLoading: false,
				error: null,
			}
		}
	}

	/** Handles press to the 'MORE...' button. Downloads new page and appends it to the end of the given list
	 * 		@async
	 * 		@param {SyntheticEvent} event 		The event object
	 */
	async handlePagination(event){
		if (this.props.isLoading || this.props.isError || this.isLoading){
			return;
		}

		this.setFetchInProgress();
		try{
			await this.entityPage.next();
			this.setFetchSuccess(true);
		} catch (error){
			this.setFetchFailure(error);
		}
	}

	/** Handles the page scrolling
	 * @async
	 * @param {SyntheticEvent} event 	the event object
	 */
	async handleScroll(event){
		if (event.detail.bottom < this.MIN_AUTONEXT_SCROLL_BUTTON && !this.entityPage.isLastPage){
			await this.handlePagination(event);
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (prevProps.items !== this.props.items){
			this.setFetchSuccess();
		}
	}

	render(){
		let statusBar = null;
		let hyperlink = null;
		if (!this.props.isLoading && !this.props.isError && this.entityPage !== null){
			if (!this.isLoading && !this.isError){
				if (!this.entityPage.isLastPage){
					statusBar = <PrimaryButton
						type="more"
						onClick={this.handlePagination}>
							{t("More...")}
				</PrimaryButton>;
				}
			} else {
				statusBar = <MessageBar
					isLoading={this.isLoading}
					isError={this.isError}
					error={this.error}
					isAnimatable={false}
					isInline={true}
				/>;
			}
			if (this.isError){
				hyperlink = <Hyperlink onClick={this.handlePagination}>
					Try again.
				</Hyperlink>;
			}
		}

		return (<Scrollable onScroll={this.handleScroll}>
			{this.renderContent()}
			<div class={styles.status_wrapper}>
				{statusBar} {hyperlink}
			</div>
		</Scrollable>);
	}

}