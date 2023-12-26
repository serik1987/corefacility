import Axis from './Axis';


/**
 * 	Allows to measure parameters specific for the X axis and plot the X axis itself
 */
export default class XAxis extends Axis{

	/**
	 *  Direction of the X axis on the canvas
	 */
	_graphicDirection = 1;

	/**
	 * 	For X axis: width of the plot area
	 * 	For Y axis: height of the plot area
	 */
	get _plotAreaSize(){
		return this._plotArea.width;
	}

	/**
	 * 	The minimum value (converted to the pixels).
	 */
	get minValuePixels(){
		return this._plotArea.left;
	}

	/**
	 * 	The maximum value (converted to the pixels).
	 */
	get maxValuePixels(){
		return this._plotArea.right;
	}

	/**
	 * 	Computes positions and sizes of the tick label
	 * 	@param {Number} 			tickIndex 		Label index in the array of ticks
	 * 	@param {Number} 			tick 			A tick related to a given label
	 * 	@param {String} 			tickLabel 		The tick label itself
	 * 	@param {Number} 			tickPixels 		For X axis: abscissa of the tick
	 * 												For Y axis: ordinate of the tick
	 * 	@param {String} additionalOptions 			Options that are important for adjustment of the graphic object
	 * 	@return {Object} 							Contains the following properties about tick positions and
	 * 												sizes
	 * 		@param {Number} startBoundary 				Position of the beginning of the tick label
	 * 		@param {Number} endBoundary 				Position of the end of the tick label
	 * 		@param {Number} necessaryLabelSize 			Required label width (for Y axis) or label height (X axis)
	 */
	_measureTickSize(tickIndex, tick, tickLabel, tickPixel){
		let g = this._graphics;
		g.textAlign = 'center';
		g.textBaseline = 'top';
		let labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		if (labelMetrics.leftEdge < this.minValuePixels){
			g.textAlign = 'left';
			labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		}
		if (labelMetrics.rightEdge > this.maxValuePixels){
			g.textAlign = 'right';
			labelMetrics = this.__getLabelMetrics(g, tickLabel, tickPixel);
		}
		return {
			startBoundary: labelMetrics.leftEdge,
			endBoundary: labelMetrics.rightEdge,
			necessaryLabelSize: labelMetrics.necessaryLabelHeight,
			additionalOptions: g.textAlign,
		}
	}

	/**
	 * 	Returns the positions and sizes of the tick label given that graphic object is properly adjusted
	 * 	@param {CanvasContext2D} 	g 				The graphic object
	 * 	@param {String} 			tickLabel 		The tick label to check
	 * 	@param {Number} 			tickPixels		Position of the tick label on a given axis.
	 * 	@return {Object} 							Contains the following properties:
	 * 		@param {Number} leftEdge 					Abscissa of the left edge of the tick label
	 * 		@param {Number} rightEdge 					Abscissa of the right edge of the tick label
	 * 		@param {Number} necessaryLabelHeight 		Actual height of the label
	 */
	__getLabelMetrics(g, tickLabel, tickPixel){
		let textMetrics = g.measureText(tickLabel);
		return {
			leftEdge: Math.floor(tickPixel - textMetrics.actualBoundingBoxLeft - this.TICK_LABELS_HALF_GAP),
			rightEdge: Math.ceil(tickPixel + textMetrics.actualBoundingBoxRight + this.TICK_LABELS_HALF_GAP),
			necessaryLabelHeight:
				Math.ceil(textMetrics.actualBoundingBoxDescent - textMetrics.actualBoundingBoxAscent),
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
		g.lineTo(this._plotArea.right - 0.5, this._plotArea.bottom + 0.5);
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
		g.moveTo(position - 0.5, this._plotArea.bottom + 0.5);
		g.lineTo(position - 0.5, this._plotArea.bottom + 0.5 + size);
	}

	/**
	 * 	Plots all tick labels for the axes
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 				The graphic object
	 * 	@param {Number} 					position		Position of a tick on the canvas that must be labeled
	 * 	@param {string} 					label 			The label text to draw
	 * 	@param {string} 					extraOptions 	Horizontal alignment of the tick label
	 */
	_plotTickLabel(g, position, label, extraOptions){
		let yPosition = this._plotArea.bottom + this.tickAndAxesSize;
		g.textAlign = extraOptions;
		g.textBaseline = 'top';
		g.fillText(label, position, yPosition);
	}

}