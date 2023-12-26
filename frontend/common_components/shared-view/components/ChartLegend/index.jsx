import * as React from 'react';

import style from './style.module.css';


/**
 * 	Plots the legend to the chart
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {Object} 		legendData 				Data to be used to plot the legend. The data must be represented
 * 													in the the form of object which keys are plot titles and values
 * 													are plot colors.
 */
export default function ChartLegend(props){
	return (
		<div className={`${style.legend} legend`}>
			{Object.keys(props.legendData).map(title => {
				return (
					<div className={style.legend_item}>
						<div className={style.legend_color} style={{borderColor: props.legendData[title]}}></div>
						<div className={style.legend_title}>{title}</div>
					</div>
				);
			})}
		</div>
	);
}