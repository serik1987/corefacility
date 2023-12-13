/**
 * 	Defines some rectangular area and provides operations on it.
 */
export default class Rectangle{

	left = 0;
	top = 0;
	width = 0;
	height = 0;

	/**
	 * 	Construction of the area.
	 * 
	 * 	@param {options} an object with the following fields:
	 * 		left abscissa of the left side (mandatory)
	 * 		right abscissa of the right side (optional)
	 * 		top	ordinate of the top side (mandatory)
	 * 		bottom ordinate of the bottom side (optional)
	 * 		width the rectangle width (optional)
	 * 		height the rectangle height (optional)
	 */
	constructor(options){
		if (options.left !== undefined){
			this.left = options.left;
		}
		if (options.top !== undefined){
			this.top = options.top;
		}
		if (options.width !== undefined){
			this.width = options.width;
		}
		if (options.height !== undefined){
			this.height = options.height;
		}
		if (options.right !== undefined){
			this.width = options.right - this.left;
		}
		if (options.bottom !== undefined){
			this.height = options.bottom - this.top;
		}
	}

	get right(){
		return this.left + this.width;
	}

	get bottom(){
		return this.top + this.height;
	}

	get area(){
		return this.width * this.height;
	}

}