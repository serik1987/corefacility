import Chart from '../../view/Chart';
import Rectangle from 'corefacility-base/model/chart/Rectangle.js';


/**
 * 	Represents the pie charts. A pie chart is a circular statistical graphic which is divided into slices to illustrate
 * 	numerical proportion.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array}		data 						Sequence of values to be shown on the pie chart. The pie chart
 * 													will illustrate the proportion of each value to the sum of all
 * 													values.
 * 	@param {Array} 		colors 						Colors to fill the pies (array of fill color values, number of
 * 													elements must be the same as number of elements in the data array,
 * 												 	each element will be assigned to the fillStyle Context2D property.
 * 	@param {Number}		bagelInnerRadius			When this property is not null or undefined, the chart is turned to
 * 													so 'bagel' model. This means that there is a white circle at the
 * 													center of the pie chart that covers central parts of the pie. In
 * 													this case the pie chart looks like a bagel, not circle.
 * 													Value of this prop is internal radius of the bagel, in percent of
 * 													half of external radius of the bagel
 * 	@param {boolean}	noRepaint					true - the chart will not be rendered after repaint,
 * 													false - the chart will be rendered after repaint.
 * 	@param {boolean}	visible						true - the chart will be visible (default value),
 * 													false - the chart will be hidden
 * 	@param {boolean}	followResize				true - run callbacks at the canvas resize (default value),
 * 													false - don't run callbacks at the canvas resize
 * 													Set this prop to true is there are multiple charts in the parent
 * 													component and the internal chart resizer work improperly. In this
 * 													case you must develop an external chart resizer.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class PieChart extends Chart{

	_debugMode = false;

	/**
	 * 	Returns the fill color for a given index. The fill colors will be taken from the props. If no props tell us
	 * 	about colors the colors will be taken randomly.
	 * 
	 * 	@param {index} number of a pie which color shall be revealed.
	 * 	
	 */
	getFillColor(index){
		let fillColor = this.props.colors && this.props.colors[index];
		if (fillColor === undefined){
			let colorComponents = [1, 1, 1].map(useless => {
				return Math.round(255 * Math.random());
			});
			fillColor = `rgb(${colorComponents.join(',')})`;
		}
		return fillColor;
	}

	/**
	 * 	Measures the aspect ratio that the canvas shall have.
	 * 
	 * 	@return the ratio of canvas width to the canvas height.
	 */
	measureAspectRatio(){
		return 1;
	}

	/**
	 *  Paints figures on the canvas.
	 * 
	 * 	@param {context} g  the rendering context where to paint
	 */
	paintFigures(g){
		if (!(this.props.data instanceof Array)){
			throw new TypeError("PieChart: value of the data prop must be a Javascript array");
		}
		let badData = this.props.data.filter(value => !isFinite(value));
		if (badData.length > 0){
			throw new TypeError("PieChart: each element of the array in the data prop must be a finite number");
		}
		let whole = this.props.data.reduce((a, b) => a+b, 0);
		let relativeData = this.props.data.map(value => value / whole);

		if (whole === 0){
			return;
		}
		let chartRectangle = new Rectangle({left: 0, top: 0, width: this._canvasWidth, height: this._canvasHeight});
		this._drawPieChart(g, relativeData, chartRectangle);
		if (this.props.bagelInnerRadius > 0){
			this._drawBagelHole(g, chartRectangle);
		}
	}

	/**
	 * 	Responsible for immediate draw of the pie chart.
	 * 	@param {context} g  				The rendering context.
	 * 	@param {Array} relativeData 		An array to plot. The sum of all array elements must be 1.
	 * 	@param {Rectangle} rectangle 		A square area on the canvas where the pie chart shall be plotted.
	 */
	_drawPieChart(g, relativeData, rectangle){
		if (rectangle.width !== rectangle.height){
			throw new TypeError(
				"PieChart: Error in rectangle argument: width must be the same as height in square area"
			);
		}

		let angles = relativeData.map((element, index) => {
			return relativeData.slice(0, index+1).reduce((a, b) => a+b) * 2 * Math.PI;
		});
		angles = [0, ...angles.slice(0, -1), 2 * Math.PI];

		let X0 = rectangle.left;
		let Y0 = rectangle.top;
		let R = Math.floor(rectangle.width / 2);
		let Xc = X0 + R;
		let Yc = Y0 + R;
		let x = angles.map(phi => Math.round(X0 + R * (1 - Math.cos(phi))));
		let y = angles.map(phi => Math.round(Y0 + R * (1 - Math.sin(phi))));
		
		for (let i = 0; i < this.props.data.length; i++){
			let fillColor = this.getFillColor(i);
			g.fillStyle = fillColor;
			g.beginPath();
			g.moveTo(Xc, Yc);
			g.lineTo(x[i], y[i]);
			g.arc(Xc, Yc, R, angles[i] - Math.PI, angles[i+1] - Math.PI);
			g.fill();
		}
	}

	/**
	 * 	Draws the bagel hole for the chart
	 * 
	 * 	@param {context} g 				The drawing tool
	 * 	@param {Rectangle} rectangle 	The rectrangle where the chart is located.
	 */
	_drawBagelHole(g, rectangle){
		let outerRadius = Math.floor(rectangle.width / 2);
		let Xc = rectangle.left + outerRadius;
		let Yc = rectangle.top + outerRadius;
		let innerRadius = Math.round(this.props.bagelInnerRadius * outerRadius);

		g.fillStyle = "#fff";
		g.beginPath();
		g.arc(Xc, Yc, innerRadius, 0, 2 * Math.PI);
		g.fill();
	}

}