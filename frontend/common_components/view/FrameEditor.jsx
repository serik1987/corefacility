import ListEditor from './ListEditor';


/**
 * 	Displays the reloading, error and loading states through the interframe communication. This component can directly
 * 	interact with the ChildModuleFrame component (escaping the application itself).
 * 
 *  Props:
 * 		The component accepts props responsible for the filter adjustment.
 * 		Such props must be defined by the deriveFilterFromProps and
 * 		deriveFilterIdentityFromProps abstract methods.
 * 	Also there are the following props responsible for the list CRUD operations
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {callback}	onItemAddOpen			This is an asynchronous method that opens
 * 												add user box (either page or modal box)
 * 												The promise always fulfills when the user closes
 * 												the box. The promise can never be rejected.
 * 												Promise must be fulfilled by the entity that has already
 * 												been created or by false if the entity create was failed
 * 
 * 	@param {Number} 	reloadTime 				Timestamp of the last reload. Must be equal to 'reloadDate' state of
 * 												the parent 'Application' component
 * 
 *	State:
 * 		The component state represents items found and the loading progress for
 * 		the item list.
 * 		The state parameters are interconnected to each other and some states
 * 		are not valid (e.g., the state {loading=true, error=true} is not valid).
 * 		For this reason, please, don't use or set the state directly because
 * 		this may result to damages. Use reportListFetching, reportListSuccess and
 * 		reportListFailure instead of them.
 * 
 * 	Also, one of the descendant of the ListEditor must be an instance of the ItemList with the following
 * 	props defined:
 * 	@param {callback} onItemAddOpen 			This method must be triggered the the user adds an entity to
 * 												the entity list by means of the entity list facility
 * 	@param {callback} onItemSelect				This method must be triggered when the user changes the entity
 * 												and wants editor to send the changes to the Web server.
 * 	@param {callback} onItemRemove 				This method must be triggered when the user removes the entity
 * 												and wants editor to send the changes to the Web Server.
 */
export default class FrameEditor extends ListEditor{

	/**
	 * 	Prepares the component for the interframe transmission.
	 * 	The main trouble is 'this' object can't be included to the postMessage data due to circular object references.
	 * 	Such method removes all circular transmission, all private and protected properties (started from _ or __) and
	 * 	binds all functions of a new object to the old one.
	 * 	@return {object} version of the FrameEditor suitable for the transmission.
	 */
	__prepare(){
		let result = {};
		for (let property in this){
			if (!property.startsWith('_')){ /* Property is neither private nor protected */
				if (typeof this[property] === 'function'){
					result[property] = this[property].bind(this);
				} else {
					result[property] = this[property];
				}
			}
		}
		console.log(result);
		console.log(JSON.parse(JSON.stringify(result)));
		return result;
	}

	/** Tells the component that list fetching is in progress.
	 *  @return {undefined}
	 */
	reportListFetching(){
		super.reportListFetching();
		if (window !== window.parent){
			window.postMessage({
				method: 'fetchList',
				info: null,
			}, window.location.origin);
		}
	}

	/** Tells the component that list fetching has been successfully completed.
	 *  @param {EntityPage|array} the item list that has been recently received from the Web server
	 *  @returns {undefined}
	 */
	reportFetchSuccess(itemList){
		super.reportFetchSuccess(itemList);
		if (window !== window.parent){
			window.postMessage({
				method: 'fetchSuccess',
			});
		}
	}

	/** Tells the component that there was unabled to fetch the list.
	 *  @param {Error} the Javascript exception that has been thrown during the fetch
	 *  @returns {undefined}
	 */
	reportFetchFailure(error){
		super.reportFetchFailure(error);
		if (window !== window.parent){
			window.postMessage({
				method: 'fetchFailure',
				info: error.message,
			}, window.location.origin);
			console.error(error);
		}
	}

	componentDidMount(){
		super.componentDidMount();
		window.application.notifyStateChanged();
	}

	componentDidUpdate(prevProps, prevState){
		super.componentDidUpdate(prevProps, prevState);
		if (prevProps.reloadTime !== this.props.reloadTime){
			this.reload();
		}
	}

}