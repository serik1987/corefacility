import * as React from 'react';

import styles from './style.module.css';


/** Defines a simple progress bar widget
 * 
 * 	Props
 * 	@param {number} progress 				The progress to show on the progress bar. Must be within 0 and 100
 */
export default class ProgressBar extends React.Component{

	render(){
		let progress = this.props.progress;
		if (progress < 0){
			progress = 0;
		}
		if (progress > 100){
			progress = 100;
		}

		return (
			<div className={styles.outer_block}>
				<div className={styles.inner_block} style={{width: `${progress}%`}}></div>
			</div>
		);
	}

}
