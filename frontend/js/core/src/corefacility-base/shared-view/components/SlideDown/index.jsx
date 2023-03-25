import * as React from 'react';

import {wait} from 'corefacility-base/utils';

import styles from './style.module.css';


/** Minimum amount of time required for CSS to apply all styles, in ms */
const MINIMUM_CSS_RESPONSE_TIME = 1;

/** After this time the animation is considered as completely over, even though there is not 'transitionend' event */
const ANIMATION_TIMEOUT_TIME = 1000;


/** All content inside this container has two states: minimized and maximized.
 * 	In minimized state the item height always equal to 0px. In maximized state
 * 	it always equals to auto.
 * 
 * 	The component always slides down when moving minimized -> maximized state.
 * 	The component always slides up when moving maximized -> minimized state.
 * 
 * 	The component doesn't have its own machinery for sliding up or sliding down.
 * 	Such a logics must be done by the parent component and result to changes in
 * 	'isOpened' prop.
 * 	
 * 
 * 	Props:
 * 	@param {boolean} isOpened true if the component is in expanded state, false
 * 		if the component is in contracted state.
 * 	@param {string} cssSuffix additional CSS classes that will be appended to
 * 		the root CSS element for its customization. We recommend to adjust borders
 * 		and shadow through the CSS suffix.
 * 		do NOT use this element to set the padding property: the slide down works
 * 		correctly given that it doesn't have any padding!
 * 		Slide down's border emerge immeditely and doesn't participate in animation
 * 		process, So, don't make widget borders wider than 1-2 px
 * 	@param {callback} onTransitionEnd triggers after transition finish
 *
 */
export default class SlideDown extends React.Component{

	/** Slides an arbitrary HTML element down given that height is its
	 * 	transition-property and transition-duration and transition-timing-function
	 * 	were properly set.
	 * 
	 * 	The element is considered to be in opened state.
	 * 
	 * 	@param {HTMLElement} htmlElement the element that is needed to slide down.
	 */
	static async slideDown(htmlElement){
		let itemHeight = htmlElement.clientHeight;
		htmlElement.style.height = "0px";
		htmlElement.style.overflow = "hidden";
		await wait(MINIMUM_CSS_RESPONSE_TIME);
		htmlElement.style.height = `${itemHeight}px`;
		htmlElement.addEventListener("transitionend", event => {
			htmlElement.style.height = null;
			htmlElement.style.overflow = null;
		}, {once: true});
		await wait(ANIMATION_TIMEOUT_TIME);
		htmlElement.style.height = null;
		htmlElement.style.display = null;
	}

	/** Slides an arbitrary HTML element up given that height is its
	 * 	transition-property and transition-duration and transition-timinig function
	 * 	were properly set.
	 * 
	 * 	The element is considered to be in closed state.
	 * 
	 * 	@param {HTMLElement} htmlElement the element that is needed to slide up.
	 * 	@param {string} display value of the display CSS property when the element is
	 * 		in opened state
	 * 	@param {callback onTransitionEnd triggers when the slide down finishes transition
	 */
	static async slideUp(htmlElement, display="block", onTransitionEnd=null){
		let eventIsTriggered = false;

		htmlElement.style.display = display;
		let itemHeight = htmlElement.clientHeight;
		htmlElement.style.height = `${itemHeight}px`;
		await wait(MINIMUM_CSS_RESPONSE_TIME);
		htmlElement.style.height = "0px";
		htmlElement.addEventListener("transitionend", event => {
			htmlElement.style.height = null;
			htmlElement.style.display = null;
			if (!eventIsTriggered && onTransitionEnd){
				eventIsTriggered = true;
				onTransitionEnd(event);
			}
		}, {once: true});
		await wait(ANIMATION_TIMEOUT_TIME);
		htmlElement.style.height = null;
		htmlElement.style.display = null;
		if (!eventIsTriggered && onTransitionEnd){
			eventIsTriggered = true;
			onTransitionEnd({
				target: htmlElement,
				type: 'timeout',
			});
		}
	}

	constructor(props){
		super(props);
		this.__slidingRef = React.createRef();
	}

	/** HTML element that has to be slided down or slided up */
	get htmlElement(){
		return this.__slidingRef.current;
	}

	render(){
		let menuClasses = styles.slide_down;
		if (this.props.cssSuffix){
			menuClasses += this.props.cssSuffix;
		}
		if (this.props.isOpened){
			menuClasses += ` ${styles.opened}`;
		}

		return (
			<div className={menuClasses} ref={this.__slidingRef}>
				{this.props.children}
			</div>
		);
	}

	componentDidUpdate(prevProps, prevState){
		if (!prevProps.isOpened && this.props.isOpened){
			this.constructor.slideDown(this.htmlElement);
		}
		if (prevProps.isOpened && !this.props.isOpened){
			if (this.props.onTransitionEnd){
				this.constructor.slideUp(this.htmlElement, 'block', this.props.onTransitionEnd);	
			} else {
				this.constructor.slideUp(this.htmlElement);
			}
		}
	}

}