import * as React from 'react';

import SlideDown from './SlideDown.jsx';
import styles from '../base-styles/ContextMenu.module.css';


/** Represents the context menu
 * 
 * 	Props:
 * 	@param {React.Component} caption To open or close the context menu
 * 		the user must click anywhere in this component.
 * 	@param {array of React.Component} component items to be displayed
 */
export default class ContextMenu extends React.Component{

	constructor(props){
		super(props);
		this.handleCaptionClick = this.handleCaptionClick.bind(this);
		this.handleMenuClose = this.handleMenuClose.bind(this);
		this.changeAlignState = this.changeAlignState.bind(this);
		this.__registerSlideDown = this.__registerSlideDown.bind(this);

		this.__slideDown = null;

		this.state={
			menuAlignMode: styles.align_left,
			isOpened: false,
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
		if (this.state.isOpened && this.__slideDown !== null){
			let rect = this.__slideDown.htmlElement.getBoundingClientRect();
			if (rect.right > window.innerWidth){
				this.setState({menuAlignMode: styles.align_right});
			} else if (rect.left < 0){
				this.setState({menuAlignMode: styles.align_left});
			}
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
		let menuClasses = ` ${styles.slide_down} ${this.state.menuAlignMode}`;

		const caption = React.cloneElement(this.props.caption,
			{onClick: this.handleCaptionClick});

		let itemIndex = 0;

		return (
			<div
				className={`${styles.context_menu} context-menu`}
				onClick={event => event.stopPropagation()}
				>
					<div className={`${styles.caption}`}>
						{caption}
					</div>
					<SlideDown
						isOpened={this.state.isOpened}
						cssPrefix={menuClasses}
						ref={this.__registerSlideDown}
						>
							<ul className={styles.items}>
								{this.props.items.map(item => {
									return (<li key={itemIndex++}>{item}</li>);
								})}
							</ul>
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