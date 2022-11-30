import * as React from 'react';

import {wait} from 'corefacility-base/utils';

import Scrollable from '../Scrollable';
import styles from './style.module.css';


/** This is the base class for all dialog boxes
 * 	
 * 	To create your own custom dialog box you can simply create a subclass,
 * 		implement all abstract method and add the form rendering as result of the
 * 		renderContent() method invocation.
 * 
 *  Props foa all dialog boxes:
 * 		@param {dialogId} the dialog ID that has been set during its registration inside the
 * 			DialogWrapper.
 * 		@param {object} options all other options except the dialog ID were collected
 * 			within a single options. To render the dialog box with given options, set them
 * 			as the third argument.
 * 		@param {boolean} inactive The inactive dialog can't be closed by the user.
 * 		@param {string} title The title to be displayed above the dialog box.
 * 
 * 	State:
 * 		The most of state variables are not allowed to change even though you inherit from the
 * 		dialog box. listed below are state parameters that you can change.
 * 		@param {number} x
 * 		@param {number} y (x, y) are initial coordinates of the top-left corner. By the default,
 * 			the dialog box is displaced at the center of the browser window.
 * 		@param {object} inputData the data passed to the dialog box
 */
export default class DialogBox extends React.Component{

	DEFAULT_TRANSITION_DURATION = 270; /* Transition duration during the dialog opening and closing in ms */
	MINIMUM_TRANSITION_DURATION = 1; /* Minimum amount of time required to update all CSS stylesheet */

	constructor(props){
		super(props);
		this.handleMouseDown = this.handleMouseDown.bind(this);
		this.handleMouseMove = this.handleMouseMove.bind(this);
		this.handleMouseUp = this.handleMouseUp.bind(this);
		this.handleOutsideClick = this.handleOutsideClick.bind(this);
		this.handleOutApp = this.handleOutApp.bind(this);

		this.state = {
			inputData: null,
			__isOpening: false, /* CSS animation is going on */
			__isOpened: false,
			__isClosing: false, /* CSS animation is going on */
			x: null,			/* Position of the dialog box on the screen */
			y: null,
		}
		this.resolve = null;

		this.__dialogRef = React.createRef();
		this.__mouseX = null;
		this.__mouseY = null;
	}

	get visible(){
		return this.state.__isOpening || this.state.__isOpened || this.state.__isClosing;
	}

	/** Defines duration of the box opening / closing animatiom in milliseconds */
	get transitionDuration(){
		return this.props.options.transitionDuration || this.DEFAULT_TRANSITION_DURATION;
	}

	/** For internal use only. */
	get __wrapperClasses(){
		let wrapperClasses = styles.dialog_wrapper;
		if (this.state.__isOpening || this.state.__isOpened || this.state.__isClosing){
			wrapperClasses += ` ${styles.opened}`;
		}
		return wrapperClasses;
	}

	/** For internal use only. */
	get __wrappedClasses(){
		let wrappedClasses = styles.dialog_box;
		if (this.state.__isOpening || this.state.__isClosing){
			wrappedClasses += ` ${styles.mini}`;
		}
		return wrappedClasses;
	}

	/** Opens new dialog box and returns new promise
	 * 	The promise will be fulfilled by the returned value
	 * 	when the user close the dialog box. The promise will
	 * 	never be rejected.
	 *	
	 * 	@param {object} inputData	the input data passed to the dialog box
	 * 	@return {Promise} the promise will be fulfilled when the user closes the dialog box.
	 */
	async openDialog(inputData){
		let self = this;

		this.setState({
			inputData: inputData,
			__isOpening: true,
			__isOpened: false,
			__isClosing: false,
		});
		await wait(this.MINIMUM_TRANSITION_DURATION);
		this.setState({
			__isOpening: false,
			__isOpened: true,
			__isClosing: false,
		});
		return new Promise((resolve, reject) => {
			self.resolve = resolve;
		});
	}

	/** Closes the dialog box. The component will hide the dialog box component
	 * 	and fulfills the promise returned by the openDialog method.
	 * 	
	 * 	@param 	{any}	result		The fulfillment value for the promise.
	 * 	@return {undefined}
	 */
	async closeDialog(result){
		if (!this.state.__isOpened){
			return;
		}
		this.setState({
			__isOpening: false,
			__isOpened: false,
			__isClosing: true,
		});
		await wait(this.transitionDuration);
		this.setState({
			inputData: null,
			__isOpening: false,
			__isOpened: false,
			__isClosing: false,
		});
		if (this.resolve !== null){
			this.resolve(result);
		}
		this.resolve = null;
	}

	/** The event triggers when the user clicks outside the dialog box.
	 * 	To close the dialog box the user must click anywhere outslide the box.
	 * 	Corresponding promise will be fulfilled by false
	 */
	handleOutsideClick(event){
		if (!this.props.inactive && (this.__mouseX === null || this.__mouseY === null)){
			this.closeDialog(false);
		} else {
			this.__mouseX = this.__mouseY = null;
		}
	}

	/* The event triggers when the mouse leaves the Browser Tab */
	handleOutApp(event){
		this.__mouseX = this.__mouseY = null;
	}

	/** the event triggers when the user presses the dialog box title
	 * 	The user can change the dialog box position by dragging the dialog header
	 */
	handleMouseDown(event){
		if (!event.altKey && !event.ctrlKey && !event.shiftKey
			&& event.button === 0 && event.buttons === 1){
			this.__mouseX = event.clientX;
			this.__mouseY = event.clientY;
		} else {
			this.__mouseX = this.__mouseY = null;
		}
	}

	/** The event triggers when the user moves the mouse cursor */
	handleMouseMove(event){
		if (this.__mouseX !== null && this.__mouseY !== null){
			let dialog = this.__dialogRef.current;
			let clientRect = dialog.getBoundingClientRect();
			let deltaX = event.clientX - this.__mouseX;
			let deltaY = event.clientY - this.__mouseY;
			this.__mouseX += deltaX;
			this.__mouseY += deltaY;

			if (clientRect.right + deltaX < window.innerWidth &&
					clientRect.left + deltaX >= 0){
				dialog.style.left = `${clientRect.left + deltaX}px`;
			}

			if (clientRect.bottom + deltaY < window.innerHeight &&
					clientRect.top + deltaY >= 0){
				dialog.style.top = `${clientRect.top + deltaY}px`;
			}
		}
	}

	/** The event triggers when the user releases the button */
	handleMouseUp(event){
		this.__mouseX = this.__mouseY = null;
	}

	render(){
		return (
			<div
				className={this.__wrapperClasses}
				onClick={this.handleOutsideClick}
				onMouseMove={this.handleMouseMove}
				onMouseLeave={this.handleOutApp}
				>
				<div className={this.__wrappedClasses}
					ref={this.__dialogRef}
					onMouseUp={this.handleMouseUp}
					onClick={event => { event.stopPropagation(); }}
					style={{
						left: `${this.state.x}px`,
						top: `${this.state.y}px`,
						transitionDuration: `${this.transitionDuration}ms`,
					}}
					>
					<div class={styles.dialog_header} onMouseDown={this.handleMouseDown}>
						<h1>{this.props.title}</h1>
					</div>
					<div class={styles.dialog_content}>
						<Scrollable overflowX={true} overflowY={true}>
							{ this.props.children }
						</Scrollable>
					</div>
				</div>
			</div>
		);
	}

	componentDidUpdate(props, state){
		if (this.state.x === null && this.state.y === null){
			let dlg = this.__dialogRef.current;
			this.setState({
				x: (window.innerWidth - dlg.offsetWidth) / 2,
				y: (window.innerHeight - dlg.offsetHeight) / 2,
			});
		}
	}

}