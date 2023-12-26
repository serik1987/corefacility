import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import PlotChartToolbar from 'corefacility-base/shared-view/components/PlotChartToolbar';

const ONE_HOUR = 3600000;


/**
 * 	This is the base class for plotting graphs related to the health status.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Date} 		minDate 			The minimum date that can actually be viewed using the plot chart toolbars
 * 	@param {Date}		startDate 			The minimum date that will be shown at the very next rendering
 * 	@param {Date} 		endDate				The maximum date that will be shown at the very next rendering
 * 	@param {Date} 		maxDate 			The maximum date that can actually be viewed using the plot chart toolbars
 * 	@param {Array}		timestamps			Dates and times for which the health measures are known
 * 	@param {Array} 		values 				The health state measures at dates and times mentioned in the timestamps
 * 											props
 * 	@param {Array}		constants			Some category-defined auxiliary values
 * 	@param {Array}		labels 				Names of the labels to be presented	
 * 	@param {callback}	onXLimChange 				Triggers when the user changes the X limit either by zooming or
 * 													by the hand tool. The function arguments:
 * 		@param {Array}		xlim 						New X limit suggested by the user (an array of two dates where
 * 														the first one is for minimum value and the second one is for
 * 														maximum value)
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class HealthCheckToolbar extends React.Component{

	/**
	 *	Returns the ordinate values to be inserted into the graph	
	 */
	get_values(){
		throw new NotImplementedError("The HealthCheckToolbar.get_values method is not implemented");
	}

	/**
	 * 	Returns the ordinate limits
	 */
	get_ylim(){
		throw new NotImplementedError("The HealthCheckTolbar.get_ylim method is not implemented");
	}

	/**
	 * 	Returns the labels
	 */
	get_labels(){
		throw new NotImplementedError("The HealthCheckToolbar.get_labels method is not implemented");
	}

	render(){
		/* The label function converts the ticks on the X axis to tick labels to be drawn below the X axis */
		let labelFunction = null;

		{
			/* One extra block will isolate the closure of the labelFunction */

			let previousFullDate = null;
			/* 'Full date' means the date date which tick label contains the day, the month, the year, the our and 
				the minute. In the other cases the tick label contains hours and minutes only */

			labelFunction = (tick, tickIndex) => {
				let tickLabel;

				if (tickIndex === 0){
					previousFullDate = null;
				}

				let date = new Date(tick * ONE_HOUR);
				if (
					previousFullDate === null ||
					previousFullDate.getFullYear() !== date.getFullYear() ||
					previousFullDate.getMonth() !== date.getMonth() ||
					previousFullDate.getDate() !== date.getDate()
				){
					tickLabel = date.toLocaleDateString() + "; ";
					previousFullDate = date;
				} else {
					tickLabel = "";
				}
				tickLabel += `${date.getHours()}:${date.getMinutes().toString().padStart(2, '0')}`;

				return tickLabel;
			}
		}

		return (
			<PlotChartToolbar
				data={{
					x: this.props.timestamps.map(timestamp => timestamp.valueOf() / ONE_HOUR),
					y: this.get_values(),
				}}
				plotTitles={this.get_labels()}
				xLimPhysical={[this.props.minDate.valueOf() / ONE_HOUR, this.props.maxDate.valueOf() / ONE_HOUR]}
				xLimLogical={[this.props.startDate.valueOf() / ONE_HOUR, this.props.endDate.valueOf() / ONE_HOUR]}
				yLim={this.get_ylim()}
				onXLimChange={xLim => this.handleXLimChange(xLim)}
				xTickLabel={labelFunction}
			/>
		);
	}

	/**
	 * 	Triggers when the user changes the xLim in the PlotChartToolbar
	 * 
	 * 	@param {Array}	xLim  			New X limits set by the user.
	 */
	handleXLimChange(xLim){
		let xLimDate = xLim.map(limit => {
			let limitDate = new Date(limit * ONE_HOUR);
			limitDate.setSeconds(0);
			limitDate.setMilliseconds(0);
			return limitDate;
		});

		if (this.props.onXLimChange){
			this.props.onXLimChange(xLimDate);
		}
	}

}