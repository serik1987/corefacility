import Chart from '../../view/Chart';
import Rectangle from '../../model/chart/Rectangle';
import XAxis from '../../model/chart/XAxis';
import YAxis from '../../model/chart/YAxis';
import ChartEvent from '../../model/chart/ChartEvent';


/**
 * 	Plots a simple 2D graph
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Object}		data 						An object with two properties: x - the abscissa values, y - the
 * 													ordinate values. x must be a 1D Javascript array. y must be 2D
 * 													Javascript array where the first (external) dimension corresponds
 * 													to the number of plots and the second (internal) dimension must have
 * 													as many values as x array.
 * 
 * 	@param {boolean}	noRepaint					true - the chart will not be repainted after rendering
 * 														(suitable for multiple charts at a single page),
 * 													false - the chart will be repainted after rendering
 * 														(suitable for a single stand-alone chart).
 * 
 * 	@param {function} 	onRepaint 					Triggers when the painting has been finished. Callback arguments:
 * 		@param {object} 	paintProperties 			The object with the folowing properties:
 * 			@param {Array} 		colors 						The colors that are actually used at repainting
 * 
 * 	@param {boolean}	visible						true - the chart will be visible (default value),
 * 													false - the chart will be hidden
 * 
 * 	@param {boolean}	followResize				true - repaint canvas automatically after the component resize
 * 													(default value),
 * 													false - this is the parent component that is responsible for the
 * 													resizing
 * 													Set this prop to true is there are multiple charts in the parent
 * 													component and the internal chart resizer work improperly. In this
 * 													case you must develop an external chart resizer.
 * 
 * 	@param {Array} 		xLim						A two-element array containing minimum and maximum value on X axis
 * 
 * 	@param {Array} 		yLim						A two-element array containing minimum and maximum value on Y axis
 * 
 * 	@param {function}	xTickLabel					A function that defines the label for the x axis tick
 * 													The function accepts the following arguments:
 * 			@param {Number} 	tick 						A tick which label must be defined
 * 			@param {Number} 	tickIndex					Index of a tick which label must be defined
 * 			@return {string}								The tick label itself
 * 
 * 	@param {function}	yTickLabel					A function that defines the label for the x axis tick
 * 													The function accepts the following arguments:
 * 			@param {Number} 	tick 						A tick which label must be defined
 * 			@param {Number} 	tickIndex					Index of a tick which label must be defined
 * 			@return {string}								The tick label itself
 * 
 * 	@param {Array} 		lineColors 					Colors that must be used to plot the graph lines. Valid value is
 * 													an array of CSS colors which length is the same as the length of
 * 													data.y
 * 
 * 	@param {callback} 			onMouseEvent		Triggered when the user pressed, released the mouse button or
 * 													moved the mouse cursor over the plot area.
 * 
 * 	@param {string} 			cursor 				What cursor shall be used for the canvas if the canvas generates
 * 													ChartEvent and delivers it to the parent component.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	The component is completely stateless.
 */
export default class PlotChart extends Chart{

	/**
	 * 	A graph where the abscissa / ordinate aspect ratio is less when this value looks so inaccurate
	 */
	MINIMUMN_ASPECT_RATIO = 2;

	/**
	 * 	Maximum precision on tick labels
	 */
	MAXIMUM_TICK_PRECISION = 2;

	/**
	 * 	Total number of iterations during the axes measurement shall not exceed this value.
	 */
	MAXIMUM_AXIS_MEASURE_ITERATIONS = 5_000;

	/**
	 * 	Index of the derivative within the localData array
	 */
	DERIVATIVE_INDEX = 2;

	/**
	 * 	Minimum number of pixels between two consequtive points (on abscissa or on ordinate) required for connecting
	 * 	these points by quadratic Bezier curve. If the number of points is less than this the minimum number of points,
	 * 	two points will be connected by the straight line.
	 */
	MINIMUM_QUADRATIC_SPLINE_PIXELS = 3;

	/**
	 * 	Widths of all graph lines
	 */
	LINE_WIDTH = 2;

	/**
	 *  Default line colors
	 */
	DEFAULT_LINE_COLORS = [
		"#1f77b4",
		"#fd7f0e",
		"#2ca02c",
		"#d62728",
		"#9467bd",
		"#8c564b",
		"#e377c2",
		"#7f7f7f",
		"#bcbd22",
		"#19b3cf",
	];

	/** true if the component shall visualize the canvas borders, false otherwise */
	_debugMode = false;

	/**
	 * 	true if the user has already clicked on the mouse button, false otherwise
	 */
	_mouseButtonPressed = false;

	/**
	 *  X limits that are set during the direct component control (i.e., redrawing without the re-rendering).
	 */
	_manualXLim = null;

	set manualXLim(value){
		this._manualXLim = value;
		if (value !== null){
			let g = this.canvas.getContext('2d');
			g.clearRect(0, 0, this._canvasWidth, this._canvasHeight);
			this.paintFigures(g);
		}
	}

	componentWillUnmount(){
		super.componentWillUnmount();
		this._mouseButtonPressed = false;
	}

	/**
	 * 	Returns the line color for a given graph
	 * 	@param {Number} 			channelIndex 		Index of the graph within the data.y array
	 * 	@return {string} 								A CSS color related to a given graph
	 */
	getLineColor(channelIndex){
		let lineColors = this.props.lineColors ?? this.DEFAULT_LINE_COLORS;
		let colorMultiplicator = Math.floor(channelIndex / lineColors.length);
		let colorIndex = channelIndex - colorMultiplicator * lineColors.length;
		let color = lineColors[colorIndex];
		if (typeof color !== 'string'){
			throw new TypeError("PlotChart: the lineColors prop was incorrectly set");
		}
		return color;
	}

	/**
	 * 	Measures the aspect ratio that the canvas shall have.
	 * 
	 * 	@return the ratio of canvas width to the canvas height.
	 */
	measureAspectRatio(){
		let desiredAspectRatio = this.container.clientWidth / this.container.clientHeight;
		return Math.max(desiredAspectRatio, this.MINIMUMN_ASPECT_RATIO);
	}

	/**
	 *  Paints figures on the canvas. The method assumes that the canvas sizes are properly set and the canvas has
	 * 	been cleared.
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on the canvas. Refer to Javascript help for more information.
	 */
	paintFigures(g){
		// console.log("Paint started", (new Date()).valueOf());
		this._plotArea = this._xAxis = this._yAxis = undefined;
		g.lineWidth = 1;
		this._paintAxes(g);

		g.save();
		g.lineWidth = this.LINE_WIDTH;
		let lineColors = [];
		g.beginPath();
		g.rect(this._plotArea.left, this._plotArea.top, this._plotArea.width, this._plotArea.height);
		g.clip();

		for (let channelIndex = 0; channelIndex < this.props.data.y.length; ++channelIndex){
			let lineColor = g.strokeStyle = this.getLineColor(channelIndex);
			this._paintPlot(g, channelIndex, this.props.data.x, this.props.data.y[channelIndex]);
			lineColors.push(lineColor);
		}
		if (this.props.onRepaint){
			this.props.onRepaint({colors: lineColors});
		}

		g.restore();
		// console.log("Paint finished", (new Date()).valueOf());
	}

	/**
	 * 	Paints the chart axes
	 * 
	 * 	@param {CanvasRenderingContext2D}		g 		The graphic object
	 */
	_paintAxes(g){
		let yAxisWidth = 0; /* The distance from the left edge of the canvas to the left edge of the plot area, px */
		let xAxisHeight = 0;
		/* The distance from the bottom edge of the canvas to the bottom edge of the plot area, px */

		let yAxisWidthPrevious = undefined;
		let xAxisHeightPrevious = undefined;
		/* Values of previous measures at the previous iterations */

		let axisMeasureIterations = 0;
		/* Total number of iterations made */

		while (
				yAxisWidthPrevious === undefined ||
				xAxisHeightPrevious === undefined ||
				(yAxisWidth > yAxisWidthPrevious && yAxisWidth < this._canvasWidth - this.MINIMUM_CANVAS_WIDTH) ||
				(xAxisHeight > xAxisHeightPrevious && xAxisHeight < this._canvasHeight - this.MINIMUM_CANVAS_HEIGHT)
			){
			let xLim = this._manualXLim ?? this.props.xLim;

			this._plotArea = new Rectangle({
				left: yAxisWidth,
				right: this._canvasWidth,
				top: 0,
				bottom: this._canvasHeight - xAxisHeight,
			});

			this._xAxis = new XAxis(this._plotArea, g);
			this._xAxis.limits = xLim;
			this._xAxis.tickLabels = this.props.xTickLabel;

			this._yAxis = new YAxis(this._plotArea, g);
			this._yAxis.limits = this.props.yLim;
			this._yAxis.tickLabels = this.props.yTickLabel;

			yAxisWidthPrevious = yAxisWidth;
			xAxisHeightPrevious = xAxisHeight;

			yAxisWidth = this._yAxis.tickLabelSize + this._yAxis.tickAndAxesSize;
			xAxisHeight = this._xAxis.tickLabelSize + this._xAxis.tickAndAxesSize;

			axisMeasureIterations++;
			if (axisMeasureIterations > this.MAXIMUM_AXIS_MEASURE_ITERATIONS){
				throw new Error("PlotChart.paintFigures: total number of axes measure iterations exceeded");
			}
		}

		/* Uncomment this for debugging */
		// console.log("X dimensions:", yAxis.tickLabelSize, yAxis.tickAndAxesSize, plotArea.width, this._canvasWidth);
		// console.log("Y dimensions:", plotArea.height, xAxis.tickAndAxesSize, xAxis.tickLabelSize, this._canvasHeight);

		this._xAxis.plotGraphics(this._containerStyle);
		this._yAxis.plotGraphics(this._containerStyle);
	}

	/**
	 * 	Paints the chart plot
	 * 
	 * 	@param {CanvasRenderingContext2D} 		g 				The graphics object
	 * 	@param {Number} 						channelIndex	Number of the channel to plot
	 * 	@param {Array}							xData			What has been depicted on abscissa
	 * 	@param {Array} 							yData			What has been depicted on ordinate
	 */
	_paintPlot(g, channelIndex, xData, yData){
		if (xData.length !== yData.length){
			throw new TypeError("PlotChart.paintFigures: the x data and y data must have the same lengths");
		}

		/**
		 * 	One can't plot the graph containing just one point
		 */
		if (xData.length === 1){
			return;
		}

		/* Transform all data to pixels */
		let xDataPixels = xData.map(x => this._xAxis.toPixels(x));
		let yDataPixels = yData.map(y => this._yAxis.toPixels(y));

		/* Remove of all samples where x is the same */
		let [xDataPixelsCleaned, yDataPixelsCleaned] = this.__removeRedundantSamples(xDataPixels, yDataPixels);

		/* Transformation of stand-alone arrays to (x, y, y') pairs, where y' is dy/dx */
		let localData = xDataPixelsCleaned.map((x, i) => {
			return [x, yDataPixelsCleaned[i], undefined];
		});

		/* Sorting the data in ascending order */
		localData.sort((point1, point2) => point1[0] - point2[0]);

		/* Calculation of derivatives */
		this.__calculateDerivatives(localData);

		/* Plotting the data */
		this.__paintCurve(g, localData);
	}

	/**
	 * 	Removes all samples where abscissa values are the same
	 * 
	 * 	@param {Array} 					xDataPixels 			Source abscissa values
	 * 	@param {Array}					yDataPixels 			Source ordinate values
	 * 	@return {Array} 										2xsamples array where the zeroth value contains abscissa
	 * 															values after cleaning and the first value contains
	 * 															ordinate values after cleaning.
	 */
	__removeRedundantSamples(xDataPixels, yDataPixels){
		let xDataPixelsCleaned = new Array(xDataPixels.length);
		let yDataPixelsCleaned = new Array(yDataPixels.length);
		let sameTimestampNumber = (new Array(xDataPixels.length))
			.map(() => 0);
		let targetIndex = 0;
		for (let sourceIndex = 0; sourceIndex < xDataPixels.length; ++sourceIndex){
			let foundIndex = xDataPixelsCleaned.indexOf(xDataPixels[sourceIndex]);
			if (foundIndex === -1){ /* Put new element */
				xDataPixelsCleaned[targetIndex] = xDataPixels[sourceIndex];
				yDataPixelsCleaned[targetIndex] = yDataPixels[sourceIndex];
				sameTimestampNumber[targetIndex] = 1;
				targetIndex++;
			} else {
				yDataPixelsCleaned[foundIndex] += yDataPixels[sourceIndex];
				sameTimestampNumber[foundIndex] += 1;
			}
		}
		xDataPixelsCleaned = xDataPixelsCleaned.slice(0, targetIndex);
		yDataPixelsCleaned = yDataPixelsCleaned
			.slice(0, targetIndex)
			.map((y, index) => Math.round(y / sameTimestampNumber[index]));

		return [xDataPixelsCleaned, yDataPixelsCleaned];
	}

	/**
	 * 	Calculates the derivative of the function to plot.
	 * 	@param {Array} 					localData 			A two dimensional array containing the abscissa values
	 * 														(first rows), ordinate values (the second row) and
	 * 														derivatives of ordinates along the abscissas
	 */
	__calculateDerivatives(localData){
		for (let n = 0; n < localData.length; n++){
			/**
			 * 	The following designations are used in the code below:
			 * 	xn 					means 			x_{n}
			 * 	yn 					means 			y_{n}
			 * 	ypn (y prime n) 	means 			y'_{n}
			 * 	xn_1 				means 			x_{n-1}
			 * 	xn1 				means 			x_{n+1}
			 * 	yn_1 				means 			y_{n-1}
			 * 	yn1 				means 			y_{n+1}
			 * 	and so on
			 * 	(The third column contains Latex code)
			 * 	
			 * 	All numerical differentiation formulas and meaning of all 'magic numbers' are given here:
			 * 	https://en.wikipedia.org/wiki/Numerical_differentiation
			 */
			let [xn, yn, ypn] = localData[n];

			if (n > 0 /* so, we have xn_1, yn_1 */ && n < localData.length - 1 /* so we have xn1, yn1 */){
				/* We have at least three points in this branch */
				let [xn_1, yn_1, ypn_1] = localData[n-1];
				let [xn1, yn1, ypn1] = localData[n+1];
				/* r = 1, N = 2, f'(x1) = ? */
				ypn = ((xn-xn_1)*(xn-xn_1)*yn1 + (xn1-xn_1)*(xn1-2*xn+xn_1)*yn - (xn1-xn)*(xn1-xn)*yn_1) /
					((xn1-xn_1)*(xn1-xn)*(xn-xn_1));
			} else if (n === 0 && localData.length > 2 /* so we have at least three points: xn, xn1, xn2, ... */){
				let [xn1, yn1, ypn1] = localData[n+1];
				let [xn2, yn2, ypn2] = localData[n+2];
				/* r = 1, N = 2, f'(x0) = ? */
				ypn = (-(xn2+xn1-2*xn)*(xn2-xn1)*yn + (xn2-xn)*(xn2-xn)*yn1 - (xn1-xn)*(xn1-xn)*yn2) / 
					((xn2-xn)*(xn1-xn)*(xn2-xn1));
			} else if (n === localData.length - 1 && localData.length > 2 /* we have at least xn, xn_1, xn_2, ... */ ){
				let [xn_1, yn_1] = localData[n-1];
				let [xn_2, yn_2] = localData[n-2];
				/* r = 1, N = 2, f'(x1) = ? */
				ypn = ((2*xn-xn_1-xn_2)*(xn_1-xn_2)*yn - (xn-xn_2)*(xn-xn_2)*yn_1 + (xn-xn_1)*(xn-xn_1)*yn_2) /
					((xn-xn_2)*(xn-xn_1)*(xn_1-xn_2));
			} else {
				/* We have only two points: the first one has an index of 0, the last one has an index of 1 */
				/* r = 1, N = 1 */
				let [x0, y0] = localData[0];
				let [x1, y1] = localData[1];
				ypn = (y1 - y0) / (x1 - x0);
			}

			localData[n][this.DERIVATIVE_INDEX] = ypn;
		}
	}

	/**
	 * 	Paints the curve
	 * 
	 * 	@param {CanvasRenderingContext2D}		g 			The graphics object
	 * 	@param {Array} 							localData 	The data with x, y and its derivative
	 */
	__paintCurve(g, localData){
		/* Uncomment the lines below for the debugging purpose */
		let [previousX, previousY, previousDerivative] = localData[0];
		g.beginPath();
		g.moveTo(previousX, previousY);
		// console.log(previousX, previousY, previousDerivative);
		for (let n = 1; n < localData.length; ++n){
			let [x, y, derivative] = localData[n];

			/* The decision to draw line instead of quadratic spline */
			let drawLine = Math.abs(x - previousX) < this.MINIMUM_QUADRATIC_SPLINE_PIXELS ||
				Math.abs(y - previousY) < this.MINIMUM_QUADRATIC_SPLINE_PIXELS;

			if (!drawLine) {
				let quotent = ((x - previousX) * derivative - (y - previousY)) / (derivative - previousDerivative);
				if (quotent < 0 || quotent > x - previousX){
					drawLine = true;
				} else {
					let px = previousX + quotent;
					let py = previousY + previousDerivative * quotent;
					// console.log(x, y, derivative, 'spline', quotent, px, py);
					g.quadraticCurveTo(px, py, x, y);
				}
			}

			if (drawLine){
				// console.log(x, y, derivative, 'line');
				g.lineTo(x, y);
			}

			previousX = x;
			previousY = y;
			previousDerivative = derivative;
		}
		g.stroke();
	}

	/**
	 * 	Triggers when the user presses the mouse button, releases the mouse button or moves the mouse button
	 * 
	 * 	@param {Event} 		event 		The event triggered by the user
	 */
	_handleMouseEvents(event){
		this.canvas.style.cursor = null;
		if (this.props.onMouseEvent && this._painted && this._xAxis && this._yAxis){
			let clientRect = this.canvas.getBoundingClientRect();
			let xPixels = event.clientX - clientRect.x;
			let yPixels = event.clientY - clientRect.y;
			let x = this._xAxis.toUnits(xPixels);
			let y = this._yAxis.toUnits(yPixels);
			let chartEvent = null;
			let clickIsInPlotArea = x !== null && y !== null;

			switch (event.type){
			case 'mousedown':
				if (clickIsInPlotArea){
					this._mouseButtonPressed = true;
					chartEvent = new ChartEvent({
						type: 'mousedown',
						data: {x: x, y: y},
						isClicked: true,
					});
				}
				break;
			case 'mousemove':
				if (clickIsInPlotArea){
					chartEvent = new ChartEvent({
						type: 'mousemove',
						data: {x: x, y: y},
						isClicked: this._mouseButtonPressed,
					});
				} else if (this._mouseButtonPressed) {
					this._mouseButtonPressed = false;
					chartEvent = new ChartEvent({
						type: 'mouseup',
						data: {x: x, y: y},
						isClicked: false,
					});
				}
				break;
			case 'mouseup':
			case 'mouseleave':
				if (this._mouseButtonPressed){
					this._mouseButtonPressed = false;
					chartEvent = new ChartEvent({
						type: 'mouseup',
						data: {x: x, y: y},
						isClicked: false,
					});
				}
			}

			if (chartEvent !== null){
				this.props.onMouseEvent(chartEvent);
				if (this.props.cursor){
					this.canvas.style.cursor = this.props.cursor;
				}
			}
		}
	}

}