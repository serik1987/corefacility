import * as React from 'react';
import styles from './style.module.css';


/** A simple widget label
 * 
 * 	Props:
 * 		@param {React.Component} children 	A label message to print
 */
export default class Label extends React.Component{

	render(){
		return (
			<div className={`label ${styles.wrapper}`}>
				<label>{this.props.children}</label>
			</div>)
	}

}