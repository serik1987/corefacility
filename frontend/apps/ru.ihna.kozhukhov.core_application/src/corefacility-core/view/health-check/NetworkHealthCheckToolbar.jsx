import {suitableMemoryUnits} from 'corefacility-base/utils';

import HealthCheckToolbar from './HealthCheckToolbar';


/**
 * 	Plots the chart that reflects the network usage status.
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
export default class NetworkHealthCheckToolbar extends HealthCheckToolbar{

	/**
	 * 	Proper units for all measures
	 */
	get units(){
		return suitableMemoryUnits(this.get_ymax());
	}

	/**
	 *	Returns the ordinate values to be inserted into the graph	
	 */
	get_values(){
		return this.props.values.map(signal => signal.map(value => value / this.units.factor));
	}

	/**
	 * 	Returns the ordinate limits
	 */
	get_ylim(){
		return [0, this.get_ymax() / this.units.factor];
	}

	/**
	 * 	Returns the labels
	 */
	get_labels(){
		return this.props.labels.map(label => `${label} (${this.units.name}/s)`);
	}

	/**
	 * 	Returns the maximum traffic usage
	 */
	get_ymax(){
		return Math.max(...this.props.values.map(signal => Math.max(...signal)));
	}

}