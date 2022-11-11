import * as React from 'react';

import DropDown from './DropDown.jsx';
import styles from '../base-styles/DropDownMenu.module.css';


/** Represents the context menu
 * 
 * 	Props:
 * 	@param {React.Component} caption To open or close the context menu
 * 		the user must click anywhere in this component.
 * 	@param {array of React.Component} component items to be displayed
 */
export default class DropDownMenu extends React.Component{

	constructor(props){
		super(props);
		this.handleCaptionClick = this.handleCaptionClick.bind(this);
		this.handleMenuClose = this.handleMenuClose.bind(this);

		this.state = {
			isOpened: false,
		}
	}

	/** Expands the menu when this is contracted. Contracts the menu when
	 * 	this is expanded.
	 * 
	 * 	@param {SyntheticEvent} event any event that causes the state change
	 * 		(i.e., clicking on 'expand' button, right click etc.)
	 */
	handleCaptionClick(event){
		this.setState({isOpened: !this.state.isOpened});
	}

	/** Contracts the menu despite of the menu state.
	 * 
	 * 	@param {SyntheticEvent} event any event that causes menu contraction
	 * 		despite of the menu state (i.e., clicking outside the widget).
	 */
	handleMenuClose(event){
		this.setState({isOpened: false});
	}

	render(){

		const caption = React.cloneElement(this.props.caption,
			{onClick: this.handleCaptionClick});

		let itemIndex = 0;

		return (
			<DropDown
				caption={caption}
				isOpened={this.state.isOpened}
				onMenuClose={this.handleMenuClose}
				>
					<ul className={styles.items}>
						{this.props.items.map(item => {
							return (<li key={itemIndex++}>{item}</li>);
						})}
					</ul>
			</DropDown>
		);
	}

}