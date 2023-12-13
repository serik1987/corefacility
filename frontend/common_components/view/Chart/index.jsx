import * as React from 'react';

import {NotImplementedError} from 'corefacility-base/exceptions/model';
import {wait} from 'corefacility-base/utils';

import style from './style.module.css';


/**
 * 	The base class for all charts. Charts are ways for graphical draw of some information.
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {any}		data 						The input data that shall be graphically represented
 * 	@param {boolean}	noRepaint					true - the chart will not be rendered after repaint,
 * 													false - the chart will be rendered after repaint.
 * 	@param {boolean}	visible						true - the chart will be visible (default value),
 * 													false - the chart will be hidden
 * 	@param {boolean}	followResize				true - run callbacks at the canvas resize (default value),
 * 													false - don't run callbacks at the canvas resize
 * 													Set this prop to true is there are multiple charts in the parent
 * 													component and the internal chart resizer work improperly. In this
 * 													case you must develop an external chart resizer.
 * 	--------------------------------------------------------------------------------------------------------------------
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	--------------------------------------------------------------------------------------------------------------------
 */
export default class Chart extends React.Component{

	MINIMUM_CANVAS_WIDTH = 10;
	MINIMUM_CANVAS_HEIGHT = 10;
	MINIMUNM_RESPONSE_TIME = 200;

	/** true if the component shall visualize the canvas borders, false otherwise */
	_debugMode = false;

	/** '2d' for 2D charts, 'webgl' for 3D charts */
	_drawMode = '2d';

	/** Width of the canvas, px. To be used by the _paintFigures */
	_canvasWidth = null;

	/** Height of the canvas, px. To be used by _paintFigures */
	_canvasHeight = null;

	/** the CSS styles for the container. This option is valid only during the execution of paintFigures(...) method */
	_containerStyle = null;

	constructor(props){
		super(props);

		this.__canvasRef = React.createRef();
		this.__containerRef = React.createRef();
		this.__resizeObserver = null;
		this._canvasWidth = null;
		this._canvasHeight = null;
		this.__resizeRequired = false;
		this.__inactive = false;

		this.state = {
			_rendering: false,
		}
	}

	/**
	 * 	Provides the first stage of the chart rendering: puts the <div> element at chart location and the <canvas>
	 * 	element inside this <div> element.
	 * 
	 * 	This method doesn't draw the chart itself inside the <canvas> element. Refer to the repaint() method for
	 * 	such purpose.
	 */
	render(){
		let additionalClasses = "";
		if (this._debugMode){
			additionalClasses += " " + style.debug_mode;
		}

		return (
			<div className={`${style.container} chart${additionalClasses}`} ref={this.__containerRef}>
				{this.visible && <canvas ref={this.__canvasRef}></canvas>}
			</div>
		);
	}

	componentDidMount(){
		this.__resizeObserver = new ResizeObserver(entries => this.resize());
		this.__resizeObserver.observe(this.container);
		if (!this.followResize){
			this.repaint();
		}
	}

	componentDidUpdate(prevProps, prevState){
		if (!this.props.noRepaint){
			let isResize = this.state.visible && !prevState.visible;
			this.repaint(isResize);
		}
	}

	componentWillUnmount(){
		this.__resizeObserver.disconnect();
	}

	/**
	 * 	Every canvas that is a member of the Chart component is placed inside the <div> element. This element is
	 * 	called "the container element" and is returned by this property.
	 */
	get container(){
		return this.__containerRef.current;
	}

	/**
	 * 	Returns HTMLElement that corresponds to the HTML canvas where the figures shall be drawn.
	 */
	get canvas(){
		return this.__canvasRef.current;
	}

	/**
	 * 	true if the canvas is visible, false othersize
	 */
	get visible(){
		return this.props.visible ?? true;
	}

	/**
	 * 	true if the canvas size shall be changed when the parent element changes its size, false otherwise
	 */
	get followResize(){
		return this.props.followResize ?? true;
	}

	/**
	 * 	Resizes the chart when one of the parent elements has been resized.
	 */
	resize(){
		if (this.followResize && !this.__inactive){
			this.repaint();
		}
	}

	/**
	 *  Changes the canvas sizes and repaints them.
	 * 	The method uses measureAspectRatio and paintFigures methods that provide details about the canvas sizing and
	 * 	which figures are drawn. So, implement these methods in child classes, don't implement the current method.
	 *	Please, mind that the method is asynchronous even though the waiting time is still small - about 1 ms.
	 * 	@async
	 * 	@param {boolean} updateSizes 		true - the canvas will be resized as well as repainted,
	 * 										false - the canvas will be just repainted, not resized.
	 * 	@param {Number} minimumResponseTime the minimum response time before the canvas clearing and the canvas painting
	 * 										null means use default value
	 * 										0 means don't wait
	 */
	async repaint(updateSizes = true, minimumResponseTime = null){
		if (this.canvas === null){
			return;
		}
		if (updateSizes){
			this.canvas.width = this.MINIMUM_CANVAS_WIDTH;
			this.canvas.height = this.MINIMUM_CANVAS_HEIGHT;
			this.__inactive = true;
			if (this._debugMode){
				console.log("The inactive state is ON");
			}
			if (minimumResponseTime === null){
				minimumResponseTime = this.MINIMUM_RESPONSE_TIME
			}
			if (minimumResponseTime > 0){
				await wait(minimumResponseTime);
			}
			this._setAspectRatio(this.measureAspectRatio());
		}
		let g = this.canvas.getContext(this._drawMode);
		g.clearRect(0, 0, this._canvasWidth, this._canvasHeight);
		this._containerStyle = window.getComputedStyle(this.container);
		g.font = this._containerStyle.font;
		this.paintFigures(g);
		this.__inactive = false;
		if (this._debugMode){
			console.log("The active state is OFF");
		}
	}

	/**
	 * 	Measures the aspect ratio that the canvas shall have.
	 * 
	 * 	@return the ratio of canvas width to the canvas height.
	 */
	measureAspectRatio(){
		throw new NotImplementedError("Chart.measureAspectRatio");
	}

	/**
	 *  Paints figures on the canvas. The method assumes that the canvas sizes are properly set and the canvas has
	 * 	been cleared.
	 * 
	 * 	@param {context} g  the rendering context. Rendering context is an object that allows you to paint figures
	 * 						on the canvas. Refer to Javascript help for more information.
	 */
	paintFigures(g){
		throw new NotImplementedError("Chart.paintFigures");
	}


	/**
	 * Resizes the <canvas> element in such a way as the ratio of its width to its height equals to a value given
	 * as a function argument.
	 * @param {Number|null} ratio the <canvas> width / <canvas> height ratio or null if the canvas must occupy the full
	 *    area of its parent container.
	 */
	_setAspectRatio(ratio){

		this._canvasWidth = 0;
		this._canvasHeight = 0;
		let parentWidth = this.container.clientWidth;
		let parentHeight = this.container.clientHeight;

		if (ratio === null){
			this._canvasWidth = parentWidth;
			this._canvasHeight = parentHeight;
		} else {
			if (ratio <= parentWidth / parentHeight){
				this._canvasHeight = parentHeight;
				this._canvasWidth = parseInt(this._canvasHeight * ratio);
			} else {
				this._canvasWidth = parentWidth;
				this._canvasHeight = parseInt(this._canvasWidth / ratio);
			}
		}

		this.canvas.width = this._canvasWidth;
		this.canvas.height = this._canvasHeight;
	}

}