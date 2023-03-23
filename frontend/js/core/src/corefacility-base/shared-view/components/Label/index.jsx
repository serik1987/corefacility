import * as React from 'react';
import styles from './style.module.css';


/** A simple widget label
 * 
 * 	Props:
 * 		@param {React.Component} children 	A label message to print
 * 		@param {callback} onClick 			An action to do when the user clicks the label
 */
export default class Label extends React.Component{

	render(){
		return (
			<div className={`label ${styles.wrapper}`} onClick={this.props.onClick}>
				<label>{this.props.children}</label>
			</div>)
	}

}