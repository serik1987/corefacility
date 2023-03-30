import * as React from 'react';
import styles from './style.module.css';


/** A simple widget label
 * 
 * 	Props:
 * 		@param {React.Component} children 	A label message to print
 * 		@param {callback} onClick 			An action to do when the user clicks the label
 * 		@param {string} tooltip 			A tooltip for the label
 * 		@param {string} cssSuffix 			Additional CSS classes to append
 */
export default class Label extends React.Component{

	render(){
		let cssClasses = `label ${styles.wrapper}`;
		if (this.props.cssSuffix){
			cssClasses += ` ${this.props.cssSuffix}`;
		}

		return (
			<div className={cssClasses} onClick={this.props.onClick} title={this.props.tooltip}>
				<label>{this.props.children}</label>
			</div>)
	}

}