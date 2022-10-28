import * as React from 'react';
import styles from '../base-styles/Label.module.css';


export default class Label extends React.Component{

	render(){
		return (
			<div className={`label ${styles.wrapper}`}>
				<label>{this.props.children}</label>
			</div>)
	}

}