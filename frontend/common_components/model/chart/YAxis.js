import Axis from './Axis';


/**
 * 	Allows to measure parameters specific for the X axis and plot the Y axis itself
 */
export default class YAxis extends Axis{

	/**
	 * 	Direction of the Y axis on the canvas
	 */
	_graphicDirection = -1;

	/**
	 * 	For X axis: width of the plot area
	 * 	For Y axis: height of the plot area
	 */
	get _plotAreaSize(){
		return this._plotArea.height;
	}

	/**
	 * 	The minimum value (converted to the pixels).
	 */
	get minValuePixels(){
		return this._plotArea.bottom;
	}

	/**
	 * 	The maximum value (converted to the pixels).
	 */
	get maxValuePixels(){
		return this._plotArea.top;
	}

	/**
	 * 	Computes positions and sizes of the tick label
	 * 	@param {Number} 			tickIndex 		Label index in the array of ticks
	 * 	@param {Number} 			tick 			A tick related to a given label
	 * 	@param {String} 			tickLabel 		The tick label itself
	 * 	@param {Number} 			tickPixels 		For X axis: abscissa of the tick
	 * 												For Y axis: ordinate of the tick
	 *  @param {String} additionalOptions 			Options that are important for adjustment of the graphic object
	 * 	@return {Object} 							Contains the following properties about tick positions and
	 * 												sizes
	 * 		@param {Number} startBoundary 				Position of the beginning of the tick label
	 * 		@param {Number} endBoundary 				Position of the end of the tick label
	 * 		@param {Number} necessaryLabelSize 			Required label width (for Y axis) or label height (X axis)
	 */
	_measureTickSize(tickIndex, tick, tickLabel, tickPixel){
		let g = this._graphics;
		g.textAlign = 'right';
		g.textBaseline = 'middle';
		let labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		if (labelMetrics.bottomEdge > this.minValuePixels){
			g.textBaseline = 'bottom';
			labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		}
		if (labelMetrics.topEdge < this.maxValuePixels){
			g.textBaseline = 'top';
			labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		}

		return {
			startBoundary: labelMetrics.bottomEdge,
			endBoundary: labelMetrics.topEdge,
			necessaryLabelSize: labelMetrics.necessaryLabelWidth,
			additionalOptions: g.textBaseline,
		}
	}

	/**
	 * 	Returns the positions and sizes of the tick label given that graphic object is properly adjusted
	 * 	@param {CanvasContext2D} 	g 				The graphic object
	 * 	@param {String} 			tickLabel 		The tick label to check
	 * 	@param {Number} 			tickPixels		Position of the tick label on a given axis.
	 * 	@return {Object} 							Contains the following properties:
	 * 		@param {Number} topEdge 					Ordinate of the top edge of the tick label
	 * 		@param {Number} bottomEdge 					Ordinate of the bottom edge of the tick label
	 * 		@param {Number} necessaryLabelWidth 		Actual width of the label
	 */
	__getLabelMetrics(g, tickLabel, tickPixel){
		let textMetrics = g.measureText(tickLabel);
		return {
			topEdge: Math.floor(tickPixel - textMetrics.actualBoundingBoxAscent - this.TICK_LABELS_HALF_GAP),
			bottomEdge: Math.ceil(tickPixel + textMetrics.actualBoundingBoxDescent + this.TICK_LABELS_HALF_GAP),
			necessaryLabelWidth: Math.ceil(textMetrics.actualBoundingBoxLeft - textMetrics.actualBoundingBoxRight),
		}
	}

	/**
	 * 	Plots the axis alone, without axis ticks and tick labels
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 			The graphic object. Please, assume that the line path has been
	 * 													begun before invocation of this method and the line path will
	 * 													be stroked after execution of this method
	 */
	_plotAxis(g){
		g.moveTo(this._plotArea.left - 0.5, this._plotArea.bottom + 0.5);
		g.lineTo(this._plotArea.left - 0.5, this._plotArea.top - 0.5);
	}

	/**
	 * 	Plots a single tick
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 			The graphic object. Please, assume that the line path has been
	 * 													begun before invocation of this method and the line path will
	 * 													be stroked after execution of this method
	 * 	@param {Number} 					position 	Tick position on a given axis, in pixels
	 * 	@param {Number} 					size 		The tick length, in pixels
	 */
	_plotTick(g, position, size){
		g.moveTo(this._plotArea.left - 0.5, position + 0.5);
		g.lineTo(this._plotArea.left - 0.5 - size, position + 0.5);
	}

	/**
	 * 	Plots all tick labels for the axes
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 				The graphic object
	 * 	@param {Number} 					position		Position of a tick on the canvas that must be labeled
	 * 	@param {string} 					label 			The label text to draw
	 * 	@param {string} 					extraOptions 	Vertical alignment of the label
	 */
	_plotTickLabel(g, position, label, extraOptions){
		g.textAlign = 'right';
		g.textBaseline = extraOptions;
		g.fillText(label, this.tickLabelSize, position);
	}

}