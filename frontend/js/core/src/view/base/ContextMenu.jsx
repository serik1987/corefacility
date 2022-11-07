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
		this.__menuRef = React.createRef();

		this.state={
			menuAlignMode: styles.align_left,
			isOpened: false,
		}
	}

	get menu(){
		return this.__menuRef.current;
	}

	changeAlignState(event){
		if (this.state.isOpened){
			let rect = this.menu.getBoundingClientRect();
			if (rect.right > window.innerWidth){
				this.setState({menuAlignMode: styles.align_right});
			} else if (rect.left < 0){
				this.setState({menuAlignMode: styles.align_left});
			}
		}
	}

	handleCaptionClick(event){
		this.setState({isOpened: !this.state.isOpened});
	}

	handleMenuClose(event){
		this.setState({isOpened: false});
	}

	render(){
		let menuClasses = `${styles.items} ${this.state.menuAlignMode}`;
		if (this.state.isOpened){
			menuClasses += ` ${styles.opened}`;
		}

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
					<div className={menuClasses} ref={this.__menuRef}>
						<ul>
							{this.props.items.map(item => {
								return (
									<li key={itemIndex++}>
										{item}
									</li>
								);
							})}
						</ul>
					</div>
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
		if (!prevState.isOpened && this.state.isOpened){
			SlideDown.slideDown(this.menu);
		}
		if (prevState.isOpened && !this.state.isOpened){
			SlideDown.slideUp(this.menu);
		}
	}

}