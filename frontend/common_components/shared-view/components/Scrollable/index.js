import * as React from 'react';

import styles from './style.module.css';


/** This is a container that contains some React component which size
 *  is larger than the size of the component itself. The container also provides
 *  vertical and horizontal scroll bars to scroll the content.
 * 
 *  Props:
 * 		@param {boolean} overflowX 		if true, the horizontal scroll bar will be displayed
 * 										when the width of content is larger than the width of
 * 										container and will be hidden otherwise.
 * 										if false, the horizontal scroll bar will not be
 * 										hidden irrespectively on the width of content.
 * 										The default value is false.
 * 
 * 		@param {boolean} overflowY 		if true, the vertical scroll bar will be displayed
 * 										when the height of container is larger than the 
 * 										height of content and will be hidden otherwise.
 * 										if false, the vertical scroll bar will not be hidden
 * 										irrespectively on the width of content.
 * 										The default value is true.
 * 
 *      @oaram {callback} onScroll      Will be evoked every time the scrollable is scrolled.
 *                                      You can use the following properties inside the callback:
 *                                          event.detail.left - distance from the left border of the scrollable to the left border of the visible area
 *                                          event.detail.top - distance from the top border of the scrollable to the top border of the visible area
 *                                          event.detail.right - distance from the right border of the scrollable to the right border of the visible area
 *                                          event.detail.bottom - distance from the bottom border of the scrollable to the bottom border of the visible area
 * 
 *      @param {string} cssSuffix       The suffix to be attached to the end of the item
 */
export default class Scrollable extends React.Component{

    constructor(props){
        super(props);
        this.scrollContainer = React.createRef();
        this.handleScroll = this.handleScroll.bind(this);
    }

    /** Scrolls the container to a point (x, y)
     * 
     *      @param {number} x   Position of the horizontal scroll bar
     *      @param {number} y   Position of the vertical scroll bar
     *      @return {undefined}
     * 
     * If x or y is higher that the scroll area dimensions, the component
     * will be scrolled at the very end. So, if you want to scroll them at
     * the very end, use Infinity as their values.
     */
    scroll(x, y){
        let scrollElement = this.scrollContainer.current;
        if (x === Infinity){
            scrollElement.scrollLeft = scrollElement.scrollWidth;
        } else {
            scrollElement.scrollLeft = x;
        }
        if (y === Infinity){
            scrollElement.scrollTop = scrollElement.scrollHeight;
        } else {
            scrollElement.scrollTop = y;
        }
    }

    /** The scroll handler. This function accepts events directly from the scrollbars
     *  and calls the props' onScroll function.
     */
    handleScroll(event){
        if (this.props.onScroll){
            let scrollElement = this.scrollContainer.current;
            event.detail = {
                left: scrollElement.scrollLeft,
                top: scrollElement.scrollTop,
                right: scrollElement.scrollWidth - scrollElement.scrollLeft - scrollElement.clientWidth,
                bottom: scrollElement.scrollHeight - scrollElement.scrollTop - scrollElement.clientHeight,
            }
            this.props.onScroll(event);
        }
    }

	render(){
		let overflowX = this.props.overflowX === undefined ? false : this.props.overflowX;
		let overflowY = this.props.overflowY === undefined ? true : this.props.overflowY;
		let overflowXClass = overflowX ? ` ${styles.overflow_x}` : '';
		let overflowYClass = overflowY ? ` ${styles.overflow_y}` : '';
        let cssSuffix = this.props.cssSuffix ? ' ' + this.props.cssSuffix.trim() : '';

		return(<div className={`scrollable ${styles.scrollable}${overflowXClass}${overflowYClass}${cssSuffix}`}
                onScroll={this.handleScroll} ref={this.scrollContainer}>
			{this.props.children}
		</div>);
	}

    getSnapshotBeforeUpdate(prevProps, prevState){
        return {
            x: this.scrollContainer.current.scrollLeft,
            y: this.scrollContainer.current.scrollTop,
        }
    }

    componentDidUpdate(prevProps, prevState, snapshot){
        this.scrollContainer.current.scrollLeft = snapshot.x;
        this.scrollContainer.current.scrollTop = snapshot.y;
    }

}