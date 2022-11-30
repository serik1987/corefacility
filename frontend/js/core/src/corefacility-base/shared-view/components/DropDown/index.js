import * as React from 'react';

import SlideDown from '../SlideDown';
import styles from './style.module.css';


/** Represents any drop-down component. The component doesn't
 * 	implement sliding up or sliding down
 * 
 * 	Props:
 * 	@param {React.Component} caption Visible part of component
 * 	@param {React.Component} children A part that can be slided up
 * 		or dropped down.
 * 	@oaram {callback} onMenuClose Triggers when the user clicks
 * 		outside the drop down or its active element. The function
 * 		must change the parent's component state in such a way as
 * 		to bring the drop down to CLOSED state.
 *	@param {string} cssSuffix Suffix to be attached to the SlideDown
 * 		class list
 */
export default class DropDown extends React.Component{

	constructor(props){
		super(props);
		this.handleItemClick = this.handleItemClick.bind(this);
		this.handleMenuClose = this.handleMenuClose.bind(this);
		this.changeAlignState = this.changeAlignState.bind(this);
		this.__registerSlideDown = this.__registerSlideDown.bind(this);
		this.__slideDown = null;
		this.__ref = React.createRef();

		this.state = {
			menuAlignMode: styles.align_left,
		}
	}

	__registerSlideDown(component){
		this.__slideDown = component;
	}

	/** Avoids such situation when the menu overflows window
	 * 
	 * 	@param {SyntheticEvent} event that may cause item overflow
	 * 		or null if the overflow could be caused by the component's
	 * 		re-rendering.
	 */
	changeAlignState(){
		if (this.props.isOpened && this.__slideDown !== null){
			let rect = this.__slideDown.htmlElement.getBoundingClientRect();
			if (rect.right > window.innerWidth){
				this.setState({menuAlignMode: styles.align_right});
			} else if (rect.left < 0){
				this.setState({menuAlignMode: styles.align_left});
			}
		}
	}

	/** Contracts the menu despite of the menu state.
	 * 
	 * 	@param {SyntheticEvent} event any event that causes menu contraction
	 * 		despite of the menu state (i.e., clicking outside the widget).
	 */
	handleMenuClose(event){
		if (this.props.onMenuClose){
			this.props.onMenuClose(event);
		}
	}

	handleItemClick(event){
		event.stopPropagation();
	}

	render(){
		let menuClasses = ` ${styles.slide_down} ${this.state.menuAlignMode}`;
		if (this.props.cssSuffix){
			menuClasses += ` ${this.props.cssSuffix}`;
		}

		return (
			<div
				className={`${styles.drop_down} drop-down`}
				onClick={this.handleItemClick}
				ref={this.__ref}
				>
					<div className={styles.caption}>
						{this.props.caption}
					</div>
					<SlideDown
						isOpened={this.props.isOpened}
						cssSuffix={menuClasses}
						ref={this.__registerSlideDown}
						>
							{this.props.children}
					</SlideDown>
			</div>
		);
	}

	componentDidMount(){
		window.addEventListener("resize", this.changeAlignState);
		window.addEventListener("click", this.handleMenuClose);
	}

	componentWillUnmount(){
		window.removeEventListener("resize", this.changeAlignState);
		window.removeEventListener("click", this.handleMenuClose);
	}

	componentDidUpdate(prevProps, prevState){
		this.changeAlignState(null);
	}

}