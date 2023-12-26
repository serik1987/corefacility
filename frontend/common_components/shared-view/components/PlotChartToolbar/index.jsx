import * as React from 'react';

import ChartToolbar from '../../../view/ChartToolbar';
import PlotChart from '../PlotChart';
import ChartLegend from '../ChartLegend';

import style from './style.module.css';


/**
 * 	Implements necessary tools that are important for control of the 2D plot chart.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Object}		data 						An object with two properties: x - the abscissa values, y - the
 * 													ordinate values. x must be a 1D Javascript array. y must be 2D
 * 													Javascript array where the first (external) dimension corresponds
 * 													to the number of plots and the second (internal) dimension must have
 * 													as many values as x array.
 * 
 * 	@oaram {Array}		plotTitles 					Titles for the plot. The titles will be displayed at the legend
 * 													below the graphs. Don't specify this prop in order to hide the
 * 													the legend
 * 
 * 	@param {boolean}	noRepaint					true - the chart will not be repainted after rendering
 * 														(suitable for multiple charts at a single page),
 * 													false - the chart will be repainted after rendering
 * 														(suitable for a single stand-alone chart).
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
 * 	@param {Array} 		xLimPhysical				The largest X limit that can be set by the user.
 * 
 * 	@param {Array} 		xLimLogical					The X limit set by the current user given that the xLimLogical
 * 													state is undefined. If the xLimLogical state is define the
 * 													xLimLogical prop is null
 * 
 * 	@param {callback}	onXLimChange 				Triggers when the user changes the X limit either by zooming or
 * 													by the hand tool. The function arguments:
 * 		@param {Array}		xlim 						New X limit suggested by the user (an array of two numbers where
 * 														the first one is for minimum value and the second one is for
 * 														maximum value)
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
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Array} 		xLimLogical 				The X limit set recently set by the current user using the toolbar
 * 													If value of this state is undefined, the this.props.xLimLogical
 * 													will be applied
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	If both this.state.xLimLogical and this.props.xLimLogical are undefined, the physical limit will be applied.
 */
export default class PlotChartToolbar extends ChartToolbar{

	_xLimBeforeMotionStart = null;

	/**
	 * 	The desired XLim that the user wants to set by means of the hand tool
	 */
	_xLimDesired = null;

	constructor(props){
		super(props);
		
		this.state = {
			...this.state,
			chartColors: undefined,
			xLimLogical: undefined,
		}
	}

	/**
	 * 	The X limit that will be definitely set.
	 */
	get xLim(){
		/* Briefly, if the user has been recently set the X limits the previous settings made by the parent component
			will be discarded
			*/

		if (this.state.xLimLogical !== undefined){
			return this.state.xLimLogical;
		} else if (this.props.xLimLogical !== undefined){
			return this.props.xLimLogical;
		} else {
			return this.props.xLimPhysical;
		}
	}

	/**
	 * 	Triggers when the user starts moving the graph by means of 'hand' tool.
	 * 	"Starts moving the graph" means the the user presses the mouse button.
	 */
	startGraphMotion(){
		this._xLimBeforeMotionStart = this.xLim;
	}

	/**
	 * 	Triggers when the user continues moving the graph by means of 'hand' tool.
	 * 	"Continues moving the graph" means that the user move the mouse when its left button is hold.
	 * 
	 * 	@param {object} 		context 	Implementation-dependent information about the current position of the
	 * 										mouse cursor
	 */
	moveGraph(context){
		let desiredPositionChange = context.x - this._draggingStartContext.x;
		let [xMinBeforeMotionStart, xMaxBeforeMotionStart] = this._xLimBeforeMotionStart;
		let [xMinPhysical, xMaxPhysical] = this.props.xLimPhysical;
		let xMinDesired = xMinBeforeMotionStart - desiredPositionChange;
		let xMaxDesired = xMaxBeforeMotionStart - desiredPositionChange;

		let rightLimitExceesion = xMaxDesired - xMaxPhysical;
		if (rightLimitExceesion > 0){
			xMaxDesired -= rightLimitExceesion;
			xMinDesired -= rightLimitExceesion;
		}

		let leftLimitExceesion = xMinPhysical - xMinDesired;
		if (leftLimitExceesion > 0){
			xMaxDesired += leftLimitExceesion;
			xMinDesired += leftLimitExceesion;
		}

		this._xLimDesired = [xMinDesired, xMaxDesired];
		this.setState({
			xLimLogical: this._xLimDesired,
		});
	}

	/**
	 * 	Triggers when the user finishes moving the graph by means of 'hand' tool.
	 * 	"Finishes moving the graph" means the the user releases the mouse button after he moved the graph to a given
	 * 	position
	 */
	finishGraphMotion(){
		let xLimDesired = this._xLimDesired;

		this._xLimDesired = null;
		this._xLimBeforeStart = null;

		// this._chartRef.current.manualXLim = null;
		// this.setState({
		// 	xLimLogical: xLimDesired,
		// });
		// if (this.props.onXLimChange){
		// 	this.props.onXLimChange(xLimDesired);
		// }
		this.props.onXLimChange(xLimDesired);

	}

	render(){
		let legendData = null;
		if (this.state.chartColors && this.props.plotTitles){
			legendData = {};
			for (let channelIndex = 0; channelIndex < this.props.plotTitles.length; channelIndex++){
				legendData[this.props.plotTitles[channelIndex]] = this.state.chartColors[channelIndex];
			}
		}

		return (
			<div className={style.container}>
				{this.renderToolbar()}
				<PlotChart
					data={this.props.data}
					noRepaint={this.props.noRepaint}
					onRepaint={paintProperties => this.onRepaint(paintProperties)}
					visible={this.props.visible}
					followResize={this.props.followResize}
					xLim={this.xLim}
					yLim={this.props.yLim}
					xTickLabel={this.props.xTickLabel}
					yTickLabel={this.props.yTickLabel}
					onMouseEvent={event => this.handleMouseEvents(event)}
					cursor={this.toolCursors[this.state.currentTool]}
				/>
				{legendData && <ChartLegend legendData={legendData}/>}
			</div>
		);
	}

	componentDidUpdate(prevProps, prevState){
		/* Briefly, if the limits have been recently sent by the parent component, all user settings of the
			limits will be discarded
		*/
		let [xMinLogical, xMaxLogical] = this.props.xLimLogical;
		let [xMinLogicalPrevious, xMaxLogicalPrevious] = prevProps.xLimLogical;
		if (xMinLogicalPrevious !== xMinLogical || xMaxLogicalPrevious !== xMaxLogical){
			this.setState({xLimLogical: undefined});
		}
	}

	/**
	 * 	Triggers when the object is repainted
	 * 	@param {object} 		paintProperties 		an information about plotted graphs, according to the 
	 * 													specification of the PlotChart's onRepaint property.
	 */
	onRepaint(paintProperties){
		let renderCriteria = 
			this.state.chartColors === undefined ||
			this.state.chartColors.length !== paintProperties.colors.length ||
			this.state.chartColors.some((color, index) => color !== paintProperties.colors[index]);

		if (renderCriteria){
			this.setState({chartColors: paintProperties.colors});
		}
	}

	/**
	 *  Changes the scale by a given factor
	 * 
	 * 	@param {Number} 		factor 		The new scale equals to the old scale multiplied by a given factor
	 */
	changeScale(factor){
		let [xMinLogical, xMaxLogical] = this.xLim;
		let [xMinPhysical, xMaxPhysical] = this.props.xLimPhysical;
		let physicalRange = xMaxPhysical - xMinPhysical;
		let logicalRange = xMaxLogical - xMinLogical;
		let suggestedLogicalRange = logicalRange / factor;
		let minimumRange = 2 * this.__getSampleStep(this.props.data.x);
			/* At least two points shall be visible after Zooom In */
		let suggestedXMin, suggestedXMax;

		if (suggestedLogicalRange < minimumRange){
			suggestedLogicalRange = minimumRange;
			factor = logicalRange / suggestedLogicalRange;
		}

		if (suggestedLogicalRange > physicalRange){
			suggestedXMin = xMinPhysical;
			suggestedXMax = xMaxPhysical;
		}

		if (suggestedXMin === undefined || suggestedXMax === undefined){
			suggestedXMin = ((factor + 1) * xMinLogical + (factor - 1) * xMaxLogical) / (2 * factor);
			suggestedXMax = ((factor + 1) * xMaxLogical + (factor - 1) * xMinLogical) / (2 * factor);
		}

		if (suggestedXMax > xMaxPhysical){
			suggestedXMax = xMaxPhysical;
			suggestedXMin = xMaxPhysical - suggestedLogicalRange;
		}

		if (suggestedXMin < xMinPhysical){
			suggestedXMin = xMinPhysical;
			suggestedXMax = xMinPhysical + suggestedLogicalRange;
		}

		let suggestedXLimLogical = [suggestedXMin, suggestedXMax];
		this.setState({
			xLimLogical: suggestedXLimLogical,
		});
		if (this.props.onXLimChange){
			this.props.onXLimChange(suggestedXLimLogical);
		}
	}

	/**
	 * 	Returns the maximum distance between two consequtive samples
	 * 
	 * 	@param {Array} 		samples 		the samples
	 * 	@return {Number} 					Difference between the farthest consequtive samples
	 */
	__getSampleStep(samples){
		let highSamples = samples.slice(1);
		let lowSamples = samples.slice(0, -1);
		let sampleDistance = highSamples.map((highSample, sampleIndex) => highSample - lowSamples[sampleIndex]);
		return Math.max(...sampleDistance);
	}

}