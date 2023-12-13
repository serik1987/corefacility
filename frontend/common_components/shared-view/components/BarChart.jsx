import Chart from '../../view/Chart';


/**
 * 	The base class for all charts. Charts are ways for graphical draw of some information.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Object}		data 						The input data of the bar that shall be represented in the following
 * 													form: category => values where category is a tick label for a given
 * 													bar in the bar chart and values are an array of stacked bars near
 * 													this tick label. values can be a single Number (in case of single
 * 													bar) or a Javascript Array of Numbers (in case of stacked bar).
 * 	@param {boolean}	noRepaint					true - the chart will not be rendered after repaint,
 * 													false - the chart will be rendered after repaint.
 * 	@param {boolean}	visible						true - the chart will be visible (default value),
 * 													false - the chart will be hidden
 * 	@param {boolean}	followResize				true - run callbacks at the canvas resize (default value),
 * 													false - don't run callbacks at the canvas resize
 * 													Set this prop to true is there are multiple charts in the parent
 * 													component and the internal chart resizer work improperly. In this
 * 													case you must develop an external chart resizer.
 * 	@param {Number}		barWidth					Widths of bar lines, px
 * 	@param {Number} 	gaps 						Gaps between bars, between the bar and the chart width, between
 * 													the Y axis and the text, px
 * 	@param {Array} 		colors 						Defines colors of the bars. Different bars located at different
 * 													tick labels are colored similarly. However, bars related to the
 * 													same tick label will be colored in different way. Zeroth array
 * 													element tells how to color the very left bar, first element - how
 * 													to color the bar that is next to the very left bar, and so on
 * 	@param {Object} 	labeledText  				The text to be drawn inside the bar. Value of this prop is an object
 * 													like label => the text to be drawn.
 * 	@param {String} 	labeledTextColor 			The labeled text color to draw.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class BarChart extends Chart{

	DEFAULT_BAR_WIDTH = 20;
	DEFAULT_GAPS = 5;
	DEFAULT_COLORS = ["rgb(34, 139, 34)", "rgb(199, 226, 199)"];
	AXES_WIDTH = 1;

	_debugMode = false;

	/** Widths of the label. Not available at _drawLabels method and the previous */
	_labelWidth = null;

	/** Abscissas of the left corner of bars. Available only at _drawBars and below */
	_barPosition = null;

	/**
	 * 	Widths of bar lines, px
	 */
	get barWidth(){
		return this.props.barWidth ?? this.DEFAULT_BAR_WIDTH;
	}

	/**
	 *  Gaps between bars, between the bar and the chart width, between the Y axis and the text, px
	 */
	get gaps(){
		return this.props.gaps ?? this.DEFAULT_GAPS;
	}

	/**
	 * 	Define bar colors.
	 */
	get colors(){
		return this.props.colors ?? this.DEFAULT_COLORS;
	}

	/**
	 *  A Javascript array containing the list of all labels
	 */
	get labels(){
		return Object.keys(this.props.data);
	}

	/**
	 * 	Returns the bar ordinate.
	 * 	
	 * 	@param {Number} barNumber 			the number of a bar
	 */
	getBarY(barNumber){
		return Math.round(this.gaps * (barNumber + 1) + this.barWidth * barNumber);
	}

	/**
	 * 	Measures the aspect ratio that the canvas shall have.
	 * 
	 * 	@return the ratio of canvas width to the canvas height.
	 */
	measureAspectRatio(){
		let barNumber = this.labels.length;
		let desiredChartWidth = this.container.clientWidth;
		let desiredChartHeight = barNumber * this.barWidth + (barNumber + 1) * this.gaps;

		return desiredChartWidth / desiredChartHeight;
	}

	/**
	 *  Paints figures on the canvas. The method assumes that the canvas sizes are properly set and the canvas has
	 * 	been cleared.
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on the canvas. Refer to Javascript help for more information.
	 */
	paintFigures(g){
		this._drawLabels(g);
		this._drawAxis(g);
		this._drawBars(g);
		if (this.props.labeledText){
			this._drawLabeledText(g);
		}
	}

	/**
	 * 	Draws labels for the axis
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on the canvas. Refer to Javascript help for more information.
	 */
	_drawLabels(g){
		this._labelWidth = 0;

		for (let i = 0; i < this.labels.length; ++i){
			let label = this.labels[i];
			let top = this.getBarY(i);
			let bottom = Math.round(top + this.barWidth);
			let middle = Math.round(0.5 * (top + bottom));

			g.fillStyle = this._containerStyle.color;
			g.textBaseline = 'middle';
			g.fillText(label, 0, middle);

			this._labelWidth = Math.max(this._labelWidth, g.measureText(label).width);
		}
	}

	/**
	 * 	Draws the axis
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on the canvas. Refer to Javascript help for more information.
	 */
	_drawAxis(g){
		this._barPosition = Math.round(this._labelWidth + this.gaps + this.AXES_WIDTH);
		let axisPosition = this._barPosition - 0.5 * this.AXES_WIDTH;
		
		g.strokeStyle = this._containerStyle.borderColor;
		g.beginPath();
		g.moveTo(axisPosition, 0);
		g.lineTo(axisPosition, this._canvasHeight);
		g.stroke();
	}

	/**
	 * 	Draws bars
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on t1he canvas. Refer to Javascript help for more information.
	 */
	_drawBars(g){
		let maximumValue = 0;
		for (let i = 0; i < this.labels.length; ++i){
			let label = this.labels[i];
			maximumValue = Math.max(maximumValue, this.props.data[label].reduce((x, y) => x + y, 0));
		}

		for (let i = 0; i < this.labels.length; ++i){
			let left = this._barPosition;
			let top = this.getBarY(i);
			let width = this._canvasWidth - this._barPosition;
			let height = this.barWidth;

			let series = this.props.data[this.labels[i]];
			if (!(series instanceof Array)){
				series = [series];
			}
			
			let colorIndex = -1;
			let barPosition = left;
			series.forEach(value => {
				colorIndex++;
				if (colorIndex >= this.colors.length){
					colorIndex = 0;
				}
				let color = this.colors[colorIndex];
				let relativeValue = Math.round(value * width / maximumValue);

				g.fillStyle = color;
				g.fillRect(barPosition, top, relativeValue, height);

				barPosition += relativeValue;
			});
		}
	}

	/**
	 * 	Draws a special text inside the bar.
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on t1he canvas. Refer to Javascript help for more information.
	 */
	_drawLabeledText(g){
		g.fillStyle = this.props.labeledTextColor ?? this._containerStyle.color;

		for (let i = 0; i < this.labels.length; ++i){
			let label = this.labels[i];
			let left = this._barPosition;
			let top = this.getBarY(i);
			let right = this._canvasWidth;
			let bottom = top + this.barWidth;

			g.textAlign = 'center';
			g.textBaseline = 'middle';
			let x = 0.5 * (left + right);
			let y = 0.5 * (top + bottom);
			g.fillText(this.props.labeledText[label], x, y, right - left);
		}
	}

}