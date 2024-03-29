/**
 * 	Represents the event generated by charts
 */
export default class ChartEvent{

	/**
	 * 	Constructs the event
	 * 	@param {Object} 	options 		An object containing all event properties
	 */
	constructor(options){
		this._options = options;
	}

	/**
	 *  The Javascipt event type, line 'mousedown', 'movemove', 'mouseup' etc.
	 */
	get type(){
		return this._options.type;
	}

	/**
	 * 	The event data (related to a given chart implementation).
	 */
	get data(){
		return this._options.data;
	}

	/**
	 * 	True if the mouse button has been pressed, false if it has been released
	 */
	get isClicked(){
		return this._options.isClicked;
	}

}