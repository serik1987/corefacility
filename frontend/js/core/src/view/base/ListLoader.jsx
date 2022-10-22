import {NotImplementedError} from '../../exceptions/model.mjs';
import {HttpError} from '../../exceptions/network.mjs';
import Loader from './Loader.jsx';


/** This is the base class for all components that deal with entity lists
 *  The component's job is to receive filter options from the parent or child
 *  components, find all necessary entities using the Entity.find(properties)
 *  method represent them in some children components
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
export default class ListLoader extends Loader{

	constructor(props){
		super(props);

		this._filter = null;
		this._desiredFilterIdentity = null;
		this._actualFilterIdentity = null;

		this.state = {
			_itemList: null,
			_isLoading: false,
			_error:  null,
		}

		this._filter = this.deriveFilterFromProps(this.props);
		this._desiredFilterIdentity = this.deriveFilterIdentityFromProps(this.props);
	}

	/** Returns class of the entity which list must be downloaded from the external server
	 *  using this component
	 */
	get entityClass(){
		throw new NotImplementedError("get entityClass");
	}

	/** Uses the component props (and probably state?) to identify the filter.
	 *  @abstract
	 * 	@return {object} the filter that will be passed as a single argument to the
	 * 	entity's find function
	 */
	deriveFilterFromProps(){
		throw new NotImplementedError("deriveFilterFromProps");
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
		throw new NotImplementedError("deriveFilterIdentity");
	}

	/** The item list that has been recently loaded.
	 *  If such list is not available (e.g., immediately after the first component render),
	 *  this property equals to null.
	 *  Depending on a certain model, the value type is either Javascript array or
	 *  EntityPage instance
	 */
	get itemList(){
		return this.state._itemList;
	}

	/** true if the item list is going to be refreshed
	 *  false otherwise */
	get isLoading(){
		return this.state._isLoading;
	}

	/** true is the last request finished with error, false otherwise */
	get isError(){
		return this.state._error !== null;
	}

	/** the exception generated during the last request */
	get error(){
		return this.state._error;
	}

	/** The filter object. The filter object is set of filter parameters the will be subsituted
	 *  to the entity()'s find function
	 */
	get filter(){
		if (this._filter === null){
			throw new Error("The filter was not set")
		}
		return this._filter;
	}

	/** Tells the component that list fetching is in progress.
	 *  @return {undefined}
	 */
	reportListFetching(){
		this.setState({
			_isLoading: true,
			_error: null,
		})
	}

	/** Tells the component that list fetching has been successfully completed.
	 *  @param {EntityPage|array} the item list that has been recently received from the Web server
	 *  @returns {undefined}
	 */
	reportFetchSuccess(itemList){
		this.setState({
			_itemList: itemList,
			_isLoading: false,
			_error: null,
		})
	}

	/** Tells the component that there was unabled to fetch the list.
	 *  @param {Error} the Javascript exception that has been thrown during the fetch
	 *  @returns {undefined}
	 */
	reportFetchFailure(error){
		this.setState({
			_isLoading: false,
			_error: error,
		});
	}

	/** Loads the item list from the external source
	 *  @async
	 *  @return {undefined}
	 */
	async reload(){
		if (this.isLoading){
			return;
		}
		this.reportListFetching();
		let filterIdentity = this._desiredFilterIdentity;
		try{
			let itemList = await this.entityClass.find(this.filter);
			this.reportFetchSuccess(itemList);
		} catch (error){
			this.reportFetchFailure(error);
		} finally{
			this._actualFilterIdentity = filterIdentity;
		}
	}

	shouldComponentUpdate(props, state){
		this._filter = this.deriveFilterFromProps(props);
		this._desiredFilterIdentity = this.deriveFilterIdentityFromProps(props);

		return true;
	}

	componentDidUpdate(prevProps, prevState, snapshot){
		if (this._desiredFilterIdentity !== this._actualFilterIdentity){
			this.reload();
		}
	}

}