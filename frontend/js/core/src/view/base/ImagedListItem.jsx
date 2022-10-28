import * as React from 'react';

import ListItem from './ListItem.jsx';
import SlideDown from './SlideDown.jsx';
import styles from '../base-styles/ImagedListItem.module.css';



/** The item list that renders to some wide rectangular section that contains an image on the left
 * 	and some short information about the entity on the right.
 * 
 *  Props:
 *  	@param {string} onClick		a callback that will be invoked when the user clicks the button
 * 										data of the event passed to the callback has event.detail
 * 										property equal to a certain item attached to the list
 * 	WARNING: when you render this component within an instance of ItemList, you can set
 *  this property to this.onItemSelect to lift up the state
 * 		@param {boolean} inactive   if the button is inactive, clicking on it has no effect
 * 		@param {boolean} disabled	if the button is disabled, it is inactive and is shown as grey 
 * 		@param {string} href		the route to be moved when you click the button
 * 		@param {Entity} item 		The item attached to the list
 * 		@param {string|URL}	img		URL of the image that will be shown on the left
 * 		@param {number} imageWidth	The image width in px
 * 		@param {number} imageHeight	The image height in px
 * 	Children are entity information that will be placed at the right of the image
 */
export default class ImagedListItem extends ListItem{

	constructor(props){
		super(props);
		this.htmlRoot = React.createRef();
	}

	/** Evoked after the very first render when 'recentlyAdded' tag was set.
	 */
	itemAddAnimationStart(){
		SlideDown.slideDown(this.htmlRoot.current);
	}

	renderContent(){
		let className = styles.imaged;
		if (this.props.disabled){
			className += ` ${styles.disabled}`;
		}
		if (this.props.inactive){
			className += ` ${styles.inactive}`;
		}

		return (
		<li
			key={this.props.item.id}
			className={className}
			onClick={this.handleClick}
			ref={this.htmlRoot}
			>
				<div>
					<img
						src={this.props.img.toString()}
						className={styles.logo}
						alt={this.props.img.toString()}
						width={this.props.imageWidth}
						height={this.props.imageHeight}
					/>
					<section>
						{this.props.children}
					</section>
				</div>
		</li>
		);
	}

}