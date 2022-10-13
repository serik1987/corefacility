import client from '../providers/http-client.mjs';

export default class EntityPage{

	constructor(pageInfo){
		this._count = pageInfo.count;
		this._previous = pageInfo.previous;
		this._next = pageInfo.next;
		this._entityList = pageInfo.entities;
		this._resultToListMapper = pageInfo.resultToListMapper;
	}

	get totalCount(){
		return this._count;
	}

	get pageCount(){
		return this._entityList.length;
	}

	async next(){
		if (!this._next){
			throw new RangeError("The last page reached");
		}
		return client.get(this._next)
			.then(resultData => this._dataToPageMapper(resultData));
	}

	async previous(){
		if (!this._previous){
			throw new RangeError("The first page reached");
		}
		return client.get(this._previous)
			.then(resultData => this._dataToPageMapper(resultData));
	}

	get isFirstPage(){
		return this._previous === null;
	}

	get isLastPage(){
		return this._next === null;
	}

	*[Symbol.iterator]() {
		for (let entity of this._entityList){
			yield entity;
		}
	}

	_dataToPageMapper(resultData){
		this._count = resultData.count;
		this._next = resultData.next;
		this._previous = resultData.previous;
		this._entityList = this._resultToListMapper(resultData.results);
	}

}