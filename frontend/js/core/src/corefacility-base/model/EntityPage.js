import client from './HttpClient';


/** EntityPage is an auxiliary class that is used for dealing with paginated responses.
 *  When you download the entity lists for the most of entities using the Entity.find(filter)
 *  method, you don't receive the whole list. Instead, you receive a small part of it called
 *  'the entity page'. This class provides navigation between different pages as well as
 *  looking for items within the page
 */
export default class EntityPage{

	/** Creates a page. The method should be called by the entity provider
	 *  @param {object} pageInfo information about the page. The information must be an object
	 * 				    containing the following fields:
	 *                       'count' total number of entities in the list
	 *                       'previous' URL to the previous entity page (or another location data)
	 *                       'next' URL to the next entity page (or another location data)
	 *                       'entities' Javascript list of all entities containing in a given page
	 *                       'resultToListMapper' a function that defines how the response body
	 *                            must be transformed to the page input parameters.
	 */
	constructor(pageInfo){
		this._count = pageInfo.count;
		this._previous = pageInfo.previous;
		this._next = pageInfo.next;
		this._entityList = pageInfo.entities;
		this._resultToListMapper = pageInfo.resultToListMapper;
	}

	/**
	 *  Returns the entity page with no items
	 */
	static empty(){
		return new EntityPage({
			count: 0,
			previous: null,
			next: null,
			entities: [],
			resultToListMapper: null,
		});
	}

	/** Total number of entities in the whole list */
	get totalCount(){
		return this._count;
	}

	/** Number of entities located in a given page */
	get pageCount(){
		return this._entityList.length;
	}

	/** Moves to the next page or throws RangeError if this is then last page
	 *  @async
	 *  @return {undefined}
	 */
	async next(){
		if (!this._next){
			throw new RangeError("The last page reached");
		}
		return client.get(this._next)
			.then(resultData => this._dataToPageMapper(resultData));
	}

	/** Moves to the previous page or throws RangeError if this is the first page
	 *  @async
	 *  @return {undefined}
	 */
	async previous(){
		if (!this._previous){
			throw new RangeError("The first page reached");
		}
		return client.get(this._previous)
			.then(resultData => this._dataToPageMapper(resultData));
	}

	/** true if this is the very first page, false otherwise */
	get isFirstPage(){
		return this._previous === null;
	}

	/** true if this is the very last page, false otherwise */
	get isLastPage(){
		return this._next === null;
	}

	/** Iterates over all entities containing in the page.
	 *  @generator
	 *  @return {Entity} Each iteration returns a given entity
	 */
	*[Symbol.iterator]() {
		for (let entity of this._entityList){
			yield entity;
		}
	}

	/** Removes the entity from the entity page */
	unshift(entity){
		this._entityList.unshift(entity);
		this._count++;
	}

	/** Maps the response body to the EntityPage's internal fields */
	_dataToPageMapper(resultData){
		this._count = resultData.count;
		this._next = resultData.next;
		this._previous = resultData.previous;
		this._entityList = this._resultToListMapper(resultData.results);
	}

}