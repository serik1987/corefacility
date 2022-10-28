import {wait} from '../../utils.mjs';
import * as React from 'react';


/** Minimum amount of time required for CSS to apply all styles */
const MINIMUM_CSS_RESPONSE_TIME = 1;


/** All content inside this container has two states: minimized and maximized.
 * 	In minimized state the item height always equal to 0px. In maximized state
 * 	it always equals to auto.
 * 
 * 	The component always slides down when moving minimized -> maximized state.
 * 	The component always slides up when moving maximized -> minimized state.
 *
 */
export default class SlideDown extends React.Component{

	/** Slides an arbitrary HTML element down given that height is its
	 * 	transition-property and transition-duration and transition-timing-function
	 * 	were properly set.
	 * 		@param {HTMLElement} htmlElement the element that is needed to slide down.
	 */
	static async slideDown(htmlElement){
		let itemHeight = htmlElement.clientHeight;
		htmlElement.style.height = "0px";
		await wait(MINIMUM_CSS_RESPONSE_TIME);
		htmlElement.style.height = `${itemHeight}px`;
		htmlElement.addEventListener("transitionend", event => {
			htmlElement.style.height = null;
		}, {once: true});
	}

}