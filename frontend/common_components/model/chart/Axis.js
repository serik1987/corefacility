import {NotImplementedError} from '../../exceptions/model';
import Rectangle from './Rectangle';

/**
 * 	Represents the base class that allows to measure axes parameters as well as plot axes labels and ticks
 */
export default class Axis{

	/**
	 * 	The supported ways to give the limits
	 */
	SUPPORTED_LIMIT_MODES = ['auto', 'manual'];

	/**
	 * 	Index for the minimum value in the limits property
	 */
	MINIMUM_VALUE_INDEX = 0;

	/**
	 * 	Index of the maximum value in the limits property
	 */
	MAXIMUM_VALUE_INDEX = 1;

	/**
	 *  The constant tick size in pixels
	 */
	TICK_SIZE = 15;

	/**
	 *	Size of X and Y axis
	 */
	AXES_SIZE = 1;

	/**
	 * 	The minimum size between two major ticks, in pixels
	 */
	MINIMUM_GRID_SIZE = 100;

	/**
	 * 	Set of available round factors for the grid.
	 * 	All grid sizes must be multiple to the round factor multiplied by 10^n where n is Integer.
	 */
	ROUND_FACTORS = [1, 2, 5];

	/**
	 * 	One half of the minimum gap between two neighbour tick labels.
	 */
	TICK_LABELS_HALF_GAP = 5;

	/**
	 * 	Length of the major ticks
	 */
	MAJOR_TICK_SIZE = 10;

	/**
	 * 	Length of the minor ticks
	 */
	MINOR_TICK_SIZE = 4;

	/**
	 *  Number of minor ticks located between two neighbour major ticks
	 */
	MINOR_TICK_NUMBER = 10;

	/**
	 *  All minor ticks that are multiple to this value are stated to be 'intermediate':
	 * 	They are longer than any other peaks.
	 */
	INTERMEDIATE_TICK_INDEX = 5;

	/**
	 * 	Size of the intermediate ticks
	 */
	INTERMEDIATE_TICK_SIZE = 7;

	/**
	 *  Total number of minor ticks can't exceed this value
	 */
	MAXIMUM_MINOR_TICK_NUMBER = 100;

	/**
	 * 	Constructs the axis.
	 * 
	 * 	@param {Rectangle}	 		plotArea 		The rectangle that reflects coordinates of the plotting area
	 * 	@param {CanvasContext2D}	graphics 		The graphics object
	 */
	constructor(plotArea, graphics){
		if (!(plotArea instanceof Rectangle)){
			throw new TypeError("Axis: plotArea must be a rectangle");
		}

		this._limitMode = 'auto';
		this._plotArea = plotArea;
		this._graphics = graphics;
		this._labelFunction = undefined;
		this._clearMeasurements();
	}

	/**
	 * 	'auto' for automatic limit set,
	 * 	'manual' for manual limit set
	 */
	get limitMode(){
		return this._limitMode;
	}

	/**
	 * 	'auto' for automatic limit set,
	 * 	'manual' for manual limit set
	 */
	set limitMode(limitMode){
		if (this.SUPPORTED_LIMIT_MODES.indexOf(limitMode) === -1){
			throw new TypeError("The limit mode is not supported");
		} else {
			this._limitMode = limitMode;
			if (limitMode === 'auto'){
				this._limits = undefined;
			}
		}
		this._clearMeasurements();
	}

	/**
	 * 	A two-element Javascript array where the first element relates to the minimum value
	 * 	and the last one related to the maximum value.
	 */
	get limits(){
		switch (this._limitMode){
		case 'manual':
			return this._limits;
		default:
			throw new NotImplementedError("Undefined limit mode");
		}
	}

	set limits(limits){
		if (limits instanceof Array && limits.length === 2 && limits.every(limit => typeof limit === 'number')){
			this._limitMode = 'manual';
			this._limits = limits;
			this._clearMeasurements();
		} else {
			throw new TypeError("Axis: bad limits");
		}
	}

	/**
	 * 	The minimum value
	 */
	get minValue(){
		return this.limits[this.MINIMUM_VALUE_INDEX];
	}

	/**
	 * 	The maximum value
	 */
	get maxValue(){
		return this.limits[this.MAXIMUM_VALUE_INDEX];
	}

	/**
	 * 	The minimum value (converted to the pixels).
	 */
	get minValuePixels(){
		throw new NotImplementedError("Axis: get minValuePixels is not defined");
	}

	/**
	 * 	The maximum value (converted to the pixels).
	 */
	get maxValuePixels(){
		throw new NotImplementedError("Axis: get maxValuePixels is not defined");
	}

	/**
	 *  For X axis: returns height of the tick labels.
	 * 	For Y axis: returns the width of the tick labels.
	 */
	get tickLabelSize(){
		if (this._tickLabelSize === undefined){
			this._measureAxis();
		}
		return this._tickLabelSize;
	}

	/**
	 * 	Returns size of the bounding occupied by axes and ticks
	 */
	get tickAndAxesSize(){
		return this.TICK_SIZE + this.AXES_SIZE;
	}

	/**
	 *  Returns the array of axes ticks
	 */
	get ticks(){
		if (this._ticks === undefined){
			this._measureAxis();
		}
		return this._ticks;
	}

	get tickLabels(){
		if (this._tickLabels === undefined){
			this._measureAxis();
		}
		return this._tickLabels;
	}

	/**
	 * 	Sets the tick labels
	 * 		value is a function that defines label for a given tick. It must have the following arguments:
	 * 		@param {Number} 		tick 		the tick which label must be defined
	 * 		@param {Number} 		tickIndex 	the index of a tick within the tick array 		
	 */
	set tickLabels(value){
		if (typeof value === 'function'){
			this._labelFunction = value;
		}
		this._clearMeasurements();
	}

	/**
	 * 	For X axis: width of the plot area
	 * 	For Y axis: height of the plot area
	 */
	get _plotAreaSize(){
		throw new NotImplementedError("Axis: get _plotAreaSize is not implemented");
	}

	/**
	 *  Converts the value from native units (as received from the props) to pixels
	 * 
	 * 	@param {Number} 		value 			The value in the native units
	 * 	@return {Number} 						The value in pixels
	 */
	toPixels(value){
		return Math.round(this.minValuePixels + this._graphicDirection * (value - this.minValue) * this._scale);
	}

	/**
	 *  Converts the value from pixels to native units (as received from the props)
	 * 
	 * 	@param {Number} 		valuePixels		The value in pixels
	 * 	@return {Number|null} 					The value in native units or null if the value is outside the plot
	 * 											area
	 */
	toUnits(valuePixels){
		let value = this.minValue + this._graphicDirection * (valuePixels - this.minValuePixels) / this._scale;
		if (value < this.minValue || value > this.maxValue){
			value = null;
		}
		return value;
	}

	/**
	 * 	Provides an important axes measurements and saves these measurements to the private fields.
	 */
	_measureAxis(){
		this._scale = (this._plotAreaSize) / (this.maxValue - this.minValue);
		/* We 'sacrifice' the very right pixel and the very top pixels to be able to put graph points exactly
			at the middle of the pixel */

		let measuringAxisFinished = false;
		this._gridSizePixels = this.MINIMUM_GRID_SIZE;
		while (!measuringAxisFinished){
			let gridSize = this._gridSizePixels / this._scale;
			gridSize = this._roundGridSize(gridSize);
			this._gridSizePixels = Math.round(gridSize * this._scale);

			let initialTick = gridSize * Math.ceil(this.minValue / gridSize);
			this._ticks = [];
			for (let tick = initialTick; tick <= this.maxValue; tick += gridSize){
				this._ticks.push(tick)
			}

			this._tickLabels = this._ticks.map((tick, tickIndex) => {
				let tickLabel = null;

				if (tickLabel === null && this._labelFunction !== undefined){
					tickLabel = this._labelFunction(tick, tickIndex);
					if (tickLabel === undefined){
						tickLabel = null;
					}
				}

				if (tickLabel === null){
					tickLabel = tick.toFixed(this.MAXIMUM_TICK_PRECISION)
						.replace(/^([+\-]?\d*\.\d*?)0+$/, "$1")
						.replace(/^([+\-]?\d*)\.$/, "$1");
				}

				return tickLabel;
			});

			let startBoundary = [];
			let endBoundary = [];
			this._tickLabelSize = 0;
			this._tickAdditionalOptions = [];
			for (let tickIndex = 0; tickIndex < this._ticks.length; ++tickIndex){
				let tick = this._ticks[tickIndex];
				let tickLabel = this._tickLabels[tickIndex];
				let tickPixel = this.toPixels(tick);
				let tickLabelMetrics = this._measureTickSize(tickIndex, tick, tickLabel, tickPixel);
				startBoundary.push(tickLabelMetrics.startBoundary);
				endBoundary.push(tickLabelMetrics.endBoundary);
				if (tickLabelMetrics.necessaryLabelSize > this._tickLabelSize){
					this._tickLabelSize = tickLabelMetrics.necessaryLabelSize;
				}
				this._tickAdditionalOptions.push(tickLabelMetrics.additionalOptions);
			}

			let extraGapStartBoundary = endBoundary.slice(0, -1);
			let extraGapEndBoundary = startBoundary.slice(1);
			let extraGaps = extraGapEndBoundary.map((endBoundary, index) => {
				return this._graphicDirection * (endBoundary - extraGapStartBoundary[index]);
			});
			let minimumExtraGap = Math.min(...extraGaps);

			if (minimumExtraGap > 0){
				measuringAxisFinished = true;
			} else {
				this._gridSizePixels -= minimumExtraGap;
			}

			/* Uncomment the lines below for the debugging purpose */
			// console.log("Plot area size:", this._plotAreaSize);
			// console.log("Scale factor:" , this._scale);
			// console.log("Grid size:", gridSize);
			// console.log("Grid size (pixels): ", gridSizePixels);
			// console.log("Value limits:", this.minValue, this.maxValue);
			// console.log("Value limits (pixels): ", this.minValuePixels, this.maxValuePixels);
			// console.log("Axes ticks:", this._ticks);
			// console.log("Axes tick labels:", this._tickLabels);
			// console.log("Tick start boundary", startBoundary);
			// console.log("Tick end boundary", endBoundary);
			// console.log("Tick label size:", this._tickLabelSize);
			// console.log("Additional tick options:", this._tickAdditionalOptions);
			// console.log("Extra gap:", minimumExtraGap);
			// console.log("Measuring axis has been finished:", measuringAxisFinished);
			// console.log("----------------------------------------");
		}
	}

	/**
	 * 	Computes positions and sizes of the tick label
	 * 	@param {Number} 			tickIndex 		Label index in the array of ticks
	 * 	@param {Number} 			tick 			A tick related to a given label
	 * 	@param {String} 			tickLabel 		The tick label itself
	 * 	@param {Number} 			tickPixels 		For X axis: abscissa of the tick
	 * 												For Y axis: ordinate of the tick
	 * 	@return {Object} 							Contains the following properties about tick positions and
	 * 												sizes
	 * 		@param {Number} startBoundary 				Position of the beginning of the tick label
	 * 		@param {Number} endBoundary 				Position of the end of the tick label
	 * 		@param {Number} necessaryLabelSize 			Required label width (for Y axis) or label height (X axis)
	 * 		@param {String} additionalOptions 			Options that are important for adjustment of the graphic object
	 */
	_measureTickSize(tickIndex, tick, tickLabel, tickPixel){
		throw new NotImplementedError("Axis: _measureTickSize was not implemented");
	}

	/**
	 * 	Clears all axes measurements
	 */
	_clearMeasurements(){
		this._tickLabelSize = undefined;
		this._scale = undefined;
		this._gridSizePixels = undefined;
		this._ticks = undefined;
		this._tickLabels = undefined;
		this._tickAdditionalOptions = undefined;
	}

	/**
	 * 	Increases the grid size in such a way as it is multiple to the round factor multiplied by 10^n.
	 * 	This operation obtains "beautiful" grid sizes like 1, 2, 5, 10, 20, 50, 0.1, 0.2, 0.5, 0.01, 0.02, 0.05, ...
	 * 
	 * 	@param {Number} 	gridSize 			The grid size before rounding
	 * 	@return {Number} 						The grid size after rounding
	 */
	_roundGridSize(gridSize){
		let roundedGridSize = Infinity;
		for (let roundFactor of this.ROUND_FACTORS){
			let gridSizeLog = Math.log10(gridSize / roundFactor);
			let roundedGridSizeLog = Math.ceil(gridSizeLog);
			let roundedGridSizeLocal = roundFactor * (10 ** roundedGridSizeLog);
			if (roundedGridSizeLocal < roundedGridSize){
				roundedGridSize = roundedGridSizeLocal;
			}
		}
		return roundedGridSize;
	}

	/**
	 * 	Plots the axis around the the plot area and using the graphics object given in the constructor
	 * 
	 * 	@param {Object} 		containerStyle	All CSS styles for the container
	 */
	plotGraphics(containerStyle){
		let g = this._graphics;

		if (this._ticks === null || this._ticks === undefined){
			this._measureAxis();
		}

		g.strokeStyle = containerStyle.color;
		g.beginPath();
		this._plotAxis(g);
		this._plotTicks(g);
		g.stroke();

		this._plotTickLabels(g);
	}

	/**
	 * 	Plots all ticks for the axes
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 			The graphic object. Please, assume that the line path has been
	 * 													begun before invocation of this method and the line path will
	 * 													be stroked after execution of this method
	 */
	_plotTicks(g){
		let previousMajorTickPixel = this.minValuePixels;
		this._ticks.map((tick, tickIndex) => {
			let tickPixel = this.toPixels(tick);
			this._plotTick(g, tickPixel, this.MAJOR_TICK_SIZE);

			let minorGridSizePixels = this._gridSizePixels / this.MINOR_TICK_NUMBER;
			let minorTickIndex;
			for (
				let minorTickPixel = tickPixel - this._graphicDirection * minorGridSizePixels, minorTickIndex = 1;
				this._graphicDirection * minorTickPixel > this._graphicDirection * previousMajorTickPixel + 1;
				minorTickPixel -= this._graphicDirection * minorGridSizePixels, minorTickIndex ++
			) {
				let tickSize;
				if (minorTickIndex % this.INTERMEDIATE_TICK_INDEX === 0){
					tickSize = this.INTERMEDIATE_TICK_SIZE;
				} else {
					tickSize = this.MINOR_TICK_SIZE;
				}
				this._plotTick(g, Math.round(minorTickPixel), tickSize);
			}

			previousMajorTickPixel = tickPixel;

			if (tickIndex === this._ticks.length - 1){
				for (
					let minorTickPixel = tickPixel + this._graphicDirection * minorGridSizePixels;
					this._graphicDirection * minorTickPixel < this._graphicDirection * this.maxValuePixels - 1;
					minorTickPixel += this._graphicDirection * minorGridSizePixels
				){
					this._plotTick(g, Math.round(minorTickPixel), this.MINOR_TICK_SIZE);
				}
			}
		});
	}

	/**
	 * 	Plots all tick labels for the axes
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 			The graphic object
	 */
	_plotTickLabels(g){
		this._ticks.map((tick, tickIndex) => {
			let position = this.toPixels(tick);
			let label = this._tickLabels[tickIndex];
			let extraOptions = this._tickAdditionalOptions[tickIndex];
			this._plotTickLabel(g, position, label, extraOptions);
		});
	}

	/**
	 * 	Plots the axis alone, without axis ticks and tick labels
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 			The graphic object. Please, assume that the line path has been
	 * 													begun before invocation of this method and the line path will
	 * 													be stroked after execution of this method
	 */
	_plotAxis(g){
		throw new NotImplementedError("Axis._plotAxis: implement this method!");
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
		throw new NotImplementedError("Axis._plotTick: implement this method!");
	}

	/**
	 * 	Plots all tick labels for the axes
	 * 
	 * 	@param {CanvasRenderingContext2D}	g 				The graphic object
	 * 	@param {Number} 					position		Position of a tick on the canvas that must be labeled
	 * 	@param {string} 					label 			The label text to draw
	 * 	@param {string} 					extraOptions 	Implementation-dependent
	 */
	_plotTickLabel(g, position, label, extraOptions){
		throw new NotImplementedError("Axis._plotTickLabel: the method has not been implemented");
	}

}
