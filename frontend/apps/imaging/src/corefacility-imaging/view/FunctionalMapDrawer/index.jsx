import {createRef} from 'react';

import {translate as t} from 'corefacility-base/utils';
import Loader from 'corefacility-base/view/Loader';
import Icon from 'corefacility-base/shared-view/components/Icon';
import {ReactComponent as ZoomInIcon} from  'corefacility-base/shared-view/icons/zoom_in.svg';
import {ReactComponent as ZoomOutIcon} from 'corefacility-base/shared-view/icons/zoom_out.svg';
import {ReactComponent as PointerIcon} from 'corefacility-base/shared-view/icons/arrow_selection_tool.svg';

import MoveTool from '../drawer_tools/MoveTool';
import style from './style.module.css';


/**
 * 	Shows functional maps, allows to scale and translate them, provides additional features
 * 
 * 	Props:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {FunctionalMap}	functionalMap 				The functional map to be downloaded.
 * 	@param {callback} 		onFetchStart 				Tells the parent component that the FunctionalMapDrawer starts
 * 														the map downloading. The callback requires no arguments.
 * 	@param {callback} 		onFetchSuccess 				Tells the parent component that the FunctionalMapDrawer
 * 														finishes the map downloading. The callback requires no arguments
 * 	@param {callback} 		onFetchFailure 				Tells the parent component that the FunctionalMapDrawer
 * 														was failed to download the map. Arguments:
 * 		@param {Error}			error 						A Javascript exception thrown during the map downloading.
 * 	@param {string}			cssSuffix 					Additional CSS clsaases to apply
 * 	@param {boolean} 		inactive 					All buttons and controls of this drawer are inactive
 * 
 * 	State:
 * 	--------------------------------------------------------------------------------------------------------------------
 * 	@param {BaseTool} 		tool 						Currently selected tool
 * 	@param {Number} 		minValue 					Minimum amplitude
 * 	@param {Number} 		maxValue 					Maximum amplitude
 * 	@param {Number} 		colorBarResolution 			dimensions of the phase axis color bar, px
 * 	@param {Uint8ClampedArray} 	colorBarImage			bitmap for the phase axis color bar
 * 	@param {Number} 		scale 						Currently selected scale.
 */
export default class FunctionalMapDrawer extends Loader{

	/* Map downloading parameters */
	FUNCTIONAL_MAP_IDENTIFICATION = 0x464d4150; /* The first four bytes of the response file. They need to ensure that
													we deal exactly with the functional map, not with Django, Python or
													hosting provider, Roscomnadzor and many other messages.
												*/

	/* Map draw parameters */
	MINIMUM_MAP_SIZE = 100; /* An exception will be risen for maps smaller than this size */
	INITIAL_COLOR_BAR_WIDTH = 50;
	MINIMUM_SCALE_BAR_WIDTH = 20;
	AMPLITUDE_COLOR_BAR_MINIMUM_TICK_DISTANCE = 30;
	AMPLITUDE_COLOR_BAR_GRADIENT_WIDTH = 20;
	MAP_TITLE_HEIGHT = 20;
	SCALE_BAR_HEIGHT = 20;
	CANVAS_MARGIN = 20; /* Distance between canvas and the next bottom element */
	DEFAULT_TEXT_HEIGHT = 12;
	SCALE_ELEMENT_HEIGHT = 10;
	SUBPLOT_GAP = 10; /* Distance between two subplots */
	PHASE_COLOR_BAR_TICK_WIDTH = 10;
	SCALE_BAR_TEXT_POSITION = 10; /* Position of the text relatively to the scale bar top */
	AXES_GAP = 5; /* Distance between subplot and the scale bar, between subplot and the color bar */
	SCALE_BAR_THICKNESS = 5;
	TEXT_PADDING = 5;
	AMPLITUDE_COLOR_BAR_TICK_WIDTH = 4;

	/* Rect parameter index */
	LEFT = 0;
	TOP = 1;
	WIDTH = 2;
	HEIGHT = 3;
	COLOR_DEPTH = 4;

	/* Misc draw parameters */
	DEFAULT_FONT = '12px Arial';
	DEFAULT_FILL_STYLE = 'rgb(60, 64, 67)';

	/* Zooming parameters */
	MIN_SCALE = 1;
	SCALE_STEP = 0.5;
	MAX_SCALE = 10;

	/* Mouse parameters */
	MOTION_PROMPT = t("Move the cursor to a point on the map to view its coordinates");
	NO_BUTTONS_ID = 0;
	LEFT_BUTTON_ID = 1;

	constructor(props){
		super(props);
		this._canvasRect = null;
		this._amplitudeMapRectangle = null;
		this._phaseMapRectangle = null;
		this.handleMouseDown = this.handleMouseDown.bind(this);
		this.handleMouseMove = this.handleMouseMove.bind(this);
		this.handleMouseUp = this.handleMouseUp.bind(this);
		this.handleCancelSelection = this.handleCancelSelection.bind(this);
		this._containerRef = createRef();
		this._statusBarRef = createRef();
		this._context = null;
		this._mouseButtonPressed = false;

		this._left = 0;
		this._top = 0;

		this.state = {
			currentTool: null,
			minValue: null,
			maxValue: null,
			colorBarResolution: null,
			colorBarImage: null,
			scale: 1,
		}

		this.tools = [
			new MoveTool(),
		];
	}

	/**
	 * 	DOM node of the root element
	 */
	get container(){
		return this._containerRef.current;
	}

	/**
	 * 	DOM node of the status bar
	 */
	get statusBar(){
		return this._statusBarRef.current;
	}

	/**
	 * 	DOM node of the canvas where we will draw maps and color bars.
	 */
	get canvasElement(){
		return this.container.getElementsByTagName('canvas')[0]; /* There is only one canvas */
	}

	/**
	 * 	Returns abscissa of the very left map pixels to show
	 */
	get left(){
		return this._left;
	}

	/**
	 * 	Sets abscissa of the very left map pixels to show
	 */
	set left(newValue){
		if (newValue >= 0 && newValue < this.props.functionalMap.resolution_x){
			this._left = newValue;
		} else {
			throw new Error("Bad value of the map left property");
		}
	}

	/**
	 * 	Returns ordinate of the very top pixels to show
	 */
	get top(){
		return this._top;
	}

	/**
	 * 	Sets ordinate of the very top map pixels to show
	 */
	set top(newValue){
		if (newValue >= 0 && newValue < this.props.functionalMap.resolution_y){
			this._top = newValue;
		} else {
			throw new Error("Bad value of the map top property");
		}
	}

	/**
	 * 	Reports the start of the map fetching
	 */
	reportFetchStart(){
		if (this.props.onFetchStart){
			this.props.onFetchStart();
		}
	}

	/**
	 *	Reports the success of the map fetching
	 */
	reportFetchSuccess(){
		if (this.props.onFetchSuccess){
			this.props.onFetchSuccess();
		}
	}

	/**
	 * 	Reports the fetch failure
	 * 	@param {Error} error 		The error message to trigger
	 */
	reportFetchFailure(error){
		if (this.props.onFetchFailure){
			this.props.onFetchFailure(error);
		}
	}

	/**
	 * 	Reloads the map
	 * 	@async
	 */
	async reload(){
		if (!this.canvasElement.getContext){
			return this.reportFetchFailure(new Error("The web browser doesn't support canvas"));
		}
		try{
			this.reportFetchStart();
			if (this.props.functionalMap){
				let mapData = await this.props.functionalMap.download('bin');
				this.__buffer = await mapData.arrayBuffer();
				this.__view = new DataView(this.__buffer);
				this.__viewOffset = 0;

				let identification = this._readValue(Uint32Array);
				let mapWidth = this._readValue(Uint32Array);
				let mapHeight = this._readValue(Uint32Array);
				let mapSizeBytes = mapWidth * mapHeight * this.COLOR_DEPTH;
				if (identification !== this.FUNCTIONAL_MAP_IDENTIFICATION ||
					mapWidth !== this.props.functionalMap.resolution_x ||
					mapHeight !== this.props.functionalMap.resolution_y){
					throw new Error(t("Corrupted functional map data received from the Web server"));
				}
				let minValue = this._readValue(Float64Array);
				let maxValue = this._readValue(Float64Array);

				let colorBarResolution = this._readValue(Uint32Array);
				let colorBarImage = this._readImage(colorBarResolution * colorBarResolution * this.COLOR_DEPTH);
				let amplitudeMapData = this._readImage(mapSizeBytes);
				let phaseMapData = this._readImage(mapSizeBytes);

				this.setState({
					minValue: minValue,
					maxValue: maxValue,
					colorBarResolution: colorBarResolution,
					colorBarImage: colorBarImage,
					scale: 1,
					left: 0,
					top: 0,
				});

				this.canvasElement.offscreenCanvas = document.createElement('canvas');
				this.canvasElement.offscreenCanvas.width = 2 * mapWidth;
				this.canvasElement.offscreenCanvas.height = mapHeight;
				let offscreenCanvasContext = this.canvasElement.offscreenCanvas.getContext('2d');
				let canvasImageData = offscreenCanvasContext.createImageData(mapWidth, mapHeight);
				canvasImageData.data.set(amplitudeMapData);
				offscreenCanvasContext.putImageData(canvasImageData, 0, 0);
				canvasImageData.data.set(phaseMapData);
				offscreenCanvasContext.putImageData(canvasImageData, mapWidth, 0);
			}
			this.reportFetchSuccess();
		} catch (error){
			this.reportFetchFailure(error);
		}
	}

	/**
	 * 	Reads a single value from the binary output response saved as BigEndian. The value will be read from the
	 * 	current position of the file.
	 * 
	 * 	@param {class} ArrayType 		The Javascript typed array class that is used to identify the value type
	 */
	_readValue(ArrayType){
		let byteLength = ArrayType.BYTES_PER_ELEMENT;
		let methodName = 'get' + ArrayType.name.replace('Array', '');
		let result = this.__view[methodName](this.__viewOffset);
		this.__viewOffset += byteLength;
		return result;
	}

	/**
	 * 	Reads the Uint8ClampedArray from the binary output response. The value will be read from the current position
	 * 	of the file.
	 * 
	 * 	@param {Number} nbytes 			Total number of bytes (not pixels!) in the array.
	 */
	_readImage(nbytes){
		let imageArray = new Uint8ClampedArray(this.__buffer, this.__viewOffset, nbytes);
		this.__viewOffset += nbytes;
		return imageArray;
	}

	/**
	 * 	Provides a full redraw of the canvas
	 */
	repaint(){
		if (!this.props.functionalMap ||
				!this.props.functionalMap.resolution_x || !this.props.functionalMap.resolution_y){
			throw new Error("The FunctionalMapDrawer is not suitable for maps that has not been uploaded yet");
		}

		if (!this.canvasElement.getContext){
			this.reportFetchFailure(new Error("The Web browser doesn't support the canvas"));
			return;
		}
		this._context = this.canvasElement.getContext('2d');

		let toolbarTopPosition = this.container
			.getElementsByClassName(style.toolbar)[0]
			.getBoundingClientRect()
			.top;

		let statusBarBottomPosition = this.container
			.getElementsByClassName(style.status_bar)[0]
			.getBoundingClientRect()
			.bottom;

		let barHeight = statusBarBottomPosition - toolbarTopPosition + this.CANVAS_MARGIN;
		let availableWidth = this.container.clientWidth;
		let availableHeight = this.container.clientHeight - barHeight;

		let dimensions = this.calculateSizes(availableWidth, availableHeight);
		this.drawMapTitle(dimensions.amplitudeMapTitle, t("Amplitude map"));
		this.drawMap(dimensions.amplitudeMapSrc, dimensions.amplitudeMap);
		this.drawAmplitudeColorBar(dimensions.amplitudeColorBar, dimensions.amplitudeColorBarProperties);
		this.drawScaleBar(dimensions.amplitudeScaleBar, dimensions.scaleBarProperties);
		this.drawMapTitle(dimensions.phaseMapTitle, t("Phase map"));
		this.drawMap(dimensions.phaseMapSrc, dimensions.phaseMap);
		this.drawPhaseColorBar(dimensions.phaseColorBar, dimensions.phaseColorBarProperties);
		this.drawScaleBar(dimensions.phaseScaleBar, dimensions.scaleBarProperties);
	}

	/**
	 * 	Calculates the sizes for redraw.
	 * 
	 * 	@param {Number} 	availableWidth 			Maximum width that the canvas can occupy
	 * 	@param {Number} 	availableHeight 		Maximum height that the canvas can occupy
	 * 	@return {object} 							Different properties related to sizes of maps, color bars, titles
	 * 												etc.
	 */
	calculateSizes(availableWidth, availableHeight){
		let colorBarWidth = this.INITIAL_COLOR_BAR_WIDTH;
		let oldColorBarWidth = null;
		let mapResolution = null; /* number of pixels in real map per each pixel in visible map */
		let mapWidth = null;
		let mapHeight = null;
		let subplotWidth = null;
		let subplotHeight = null;
		let canvasWidth = null;
		let canvasHeight = null;
		let amplitudeColorBarProperties = null;
		let phaseColorBarProperties = null;
		let scaleBarProperties = null;
		this._amplitudeMapRectangle = null;
		this._phaseMapRectangle = null;

		this._context.font = this.DEFAULT_FONT;
		this._context.textAlign = 'left';

		while (colorBarWidth !== oldColorBarWidth){
			oldColorBarWidth = colorBarWidth;
			let availableSubplotWidth = (availableWidth - this.SUBPLOT_GAP) / 2;
			let availableMapWidth = availableSubplotWidth - colorBarWidth - this.AXES_GAP;
			let availableMapHeight = availableHeight
				- this.SCALE_BAR_HEIGHT
				- 2 * this.AXES_GAP
				- this.MAP_TITLE_HEIGHT;
			let availableMapResolutionX = availableMapWidth / this.props.functionalMap.resolution_x;
			let availableMapResolutionY = availableMapHeight / this.props.functionalMap.resolution_y;

			mapResolution = Math.min(availableMapResolutionX, availableMapResolutionY);
			mapWidth = Math.round(mapResolution * this.props.functionalMap.resolution_x);
			mapHeight = Math.round(mapResolution * this.props.functionalMap.resolution_y);
			amplitudeColorBarProperties = this.measureAmplitudeColorBar(mapHeight);
			phaseColorBarProperties = this.measurePhaseColorBar(mapHeight);
			scaleBarProperties = this.measureScaleBar(mapWidth);
			subplotWidth = mapWidth + this.AXES_GAP + colorBarWidth;
			subplotHeight = mapHeight + 2 * this.AXES_GAP + this.SCALE_BAR_HEIGHT + this.MAP_TITLE_HEIGHT;
			canvasWidth = 2 * subplotWidth + this.SUBPLOT_GAP;
			canvasHeight = subplotHeight;

			colorBarWidth = Math.ceil(Math.max(
				colorBarWidth,
				amplitudeColorBarProperties.totalWidth,
				phaseColorBarProperties.totalWidth,
			));
		}

		this.canvasElement.width = canvasWidth;
		this.canvasElement.height = canvasHeight;
		if (mapWidth < this.MINIMUM_MAP_SIZE){
			this.reportFetchFailure(new Error("Too low screen resolution"));
			return;
		}
		this._canvasRect = this.canvasElement.getBoundingClientRect();

		this._context.font = this.DEFAULT_FONT;
		this._context.textAlign = 'left';
		this._context.imageSmoothingEnabled = false;

		let mapOffsetY = this.MAP_TITLE_HEIGHT + this.AXES_GAP;
		this._amplitudeMapRectangle = [0, mapOffsetY, mapWidth, mapHeight];
		this._phaseMapRectangle = [subplotWidth + this.SUBPLOT_GAP, mapOffsetY, mapWidth, mapHeight];
		this._relativeMapRectangle = [0, 0, mapWidth, mapHeight];

		return {
			mapResolution: mapResolution,
			amplitudeMapTitle: [0, 0, mapWidth, this.MAP_TITLE_HEIGHT],
			amplitudeMapSrc: this.measureMap(0),
			amplitudeMap: this._amplitudeMapRectangle,
			amplitudeColorBar: [subplotWidth - colorBarWidth, mapOffsetY, colorBarWidth, mapHeight],
			amplitudeColorBarProperties: amplitudeColorBarProperties,
			amplitudeScaleBar: [0, canvasHeight - this.SCALE_BAR_HEIGHT, mapWidth, this.SCALE_BAR_HEIGHT],
			phaseMapTitle: [subplotWidth + this.SUBPLOT_GAP, 0, mapWidth, this.MAP_TITLE_HEIGHT],
			phaseMapSrc: this.measureMap(this.props.functionalMap.resolution_x),
			phaseMap: this._phaseMapRectangle,
			phaseColorBar: [canvasWidth - colorBarWidth, mapOffsetY, colorBarWidth, mapHeight],
			phaseColorBarProperties: phaseColorBarProperties,
			phaseScaleBar: [
				subplotWidth + this.SUBPLOT_GAP,
				canvasHeight - this.SCALE_BAR_HEIGHT,
				mapWidth,
				this.SCALE_BAR_HEIGHT
			],
			scaleBarProperties: scaleBarProperties,
		};
	}

	/**
	 * 	Draws the map title
	 * 	
	 * 	@param {Array of Number} 		dimensions 			A rectangle where the text must be drawn.
	 * 	@param {string} 				text 				The text to draw
	 */
	drawMapTitle(dimensions, text){
		let [left, top, width, height] = dimensions;
		this._context.save();

		this._context.font = '18px Arial';
		this._context.textAlign = 'center';
		this._context.textBaseline = 'top';
		this._context.fillStyle = this.DEFAULT_FILL_STYLE;
		this._context.fillText(text, left + 0.5 * width, top, width);

		this._context.restore();
	}

	/**
	 * 	Defines the rectangle from the offline map canvas to be used to draw the map
	 * 	@param {Number} 				globalOffset 		0 for amplitude map, map resolution x for the phase map
	 * 	@return {Array} 									Rectangle in the source map to
	 */
	measureMap(globalOffset){
		let sWidth = this.props.functionalMap.resolution_x;
		let sHeight = this.props.functionalMap.resolution_y;
		let scale = this.state.scale;

		return [this.left + globalOffset, this.top, Math.round(sWidth / scale), Math.round(sHeight / scale)];
	}

	/**
	 * 	Draws amplitude or phase map
	 * 	@param {Array}					sourceDimensions	rectangle area on the source offscreen canvas to put the map
	 * 	@param {Array} 					dimensions 			rectangle area on the target canvas to put the map
	 */
	drawMap(sourceDimensions, dimensions){
		if (this.canvasElement.offscreenCanvas){
			this._context.drawImage(this.canvasElement.offscreenCanvas, ...sourceDimensions, ...dimensions);
		}
	}

	/**
	 * 	Measures geometrical parameters of the amplitude map color bar
	 * 	@param {Number} 				colorBarHeight 		Desired colorbar height, units text are not included here
	 * 	@return {object} 									Various geometrical parameters of the amplitude color bar.
	 */
	measureAmplitudeColorBar(colorBarHeight){
		const MIN_POWER_FIXED = -2;
		const MAX_POWER_FIXED = 1;

		let tickProperties = {
			ticks: [],
		}
		let colorAxisResolution = (colorBarHeight - 1) / (this.state.maxValue - this.state.minValue);
		/* Because minValue is from 0th to 1st pixel; minValue + 1 / colorAxisResolution => from 1st to 2nd pixel; ...
			maxValue => from colorBarHeight-1-th to colorBarHeight'th pixel
		*/
		let tickDistance = Math.pow(10, Math.floor(Math.log10(this.state.maxValue) - 1));
		let tickDistancePx = tickDistance * colorAxisResolution;
		let tickDistanceRule = 1;
			/* Available rules: 
				1 - 1, 2, 3, 4, 5, 6, 7, 8, 10, ... x 10^n, where n is integer
				2 - 2, 4, 6, 8, 10, ... x 10^n, where n is integer
				5 - 5, 10, 50, 100, ... x 10^n, where n is integer
			*/
		let increaseTickDistance = () => {
			switch (tickDistanceRule){
			case 1:
			default:
				tickDistance *= 2.0;
				tickDistancePx *= 2.0;
				tickDistanceRule = 2.0;
				break;
			case 2:
				tickDistance *= 2.5;
				tickDistancePx *= 2.5;
				tickDistanceRule = 5;
				break;
			case 5:
				tickDistance *= 2.0;
				tickDistancePx *= 2.0;
				tickDistanceRule = 1;
				break;
			}
		}
		let decreaseTickDistance = () => {
			switch (tickDistanceRule){
			case 1:
			default:
				tickDistance /= 2.0;
				tickDistancePx /= 2.0;
				tickDistanceRule = 5;
				break;
			case 5:
				tickDistance /= 2.5;
				tickDistancePx /= 2.5;
				tickDistanceRule = 2;
				break;
			case 2:
				tickDistance /= 2.0;
				tickDistancePx /= 2.0;
				tickDistanceRule = 1;
				break;
			}
		}
		if (tickDistancePx < this.AMPLITUDE_COLOR_BAR_MINIMUM_TICK_DISTANCE){
			while (tickDistancePx < this.AMPLITUDE_COLOR_BAR_MINIMUM_TICK_DISTANCE){
				increaseTickDistance();
			}
		} else {
			while (tickDistancePx > this.AMPLITUDE_COLOR_BAR_MINIMUM_TICK_DISTANCE){
				decreaseTickDistance();
			}
			increaseTickDistance();
		}

		let currentTick = 0;
		while (currentTick < this.state.minValue){
			currentTick += tickDistance;
		}
		while (currentTick < this.state.maxValue){
			tickProperties.ticks.push(currentTick);
			currentTick += tickDistance;
		}
		
		tickProperties.ticksPx = tickProperties.ticks.map(tick => tick * colorAxisResolution);
		
		let multiplier = tickDistance / tickDistanceRule;
		let power = Math.log10(multiplier);
		if (power >= 0 && power <= MAX_POWER_FIXED){
			tickProperties.tickLabels = tickProperties.ticks.map(tick => tick.toFixed(0));
			tickProperties.mainLabel = '%';
		} else if (power < 0 && power >= MIN_POWER_FIXED){
			tickProperties.tickLabels = tickProperties.ticks.map(tick => tick.toFixed(-power));
			tickProperties.mainLabel = '%';
		} else {
			tickProperties.tickLabels = tickProperties.ticks.map(tick => (tick / multiplier).toFixed(0));
			tickProperties.mainLabel = `\u{00d7}10^{${power}} %`;
		}

		let textWidth = Math.max(...tickProperties.tickLabels.map(text => this._context.measureText(text).width));
		if (textWidth < 0){
			textWidth = 0;
		}
		tickProperties.totalWidth = 
			this.AMPLITUDE_COLOR_BAR_GRADIENT_WIDTH +
			this.AMPLITUDE_COLOR_BAR_TICK_WIDTH +
			this.TEXT_PADDING +
			textWidth;

		return tickProperties;
	}

	/**
	 * 	Plots the color bar on the amplitude map
	 * 	@param {Array} 			dimensions 				Rectangle where the amplitude map color bar must be plotted
	 * 													(units message is not included here)
	 * 	@param {object} 		tickProperties 			Various geometrical parameters calculated by the
	 * 													measureAmplitudeColorBar method
	 */
	drawAmplitudeColorBar(dimensions, tickProperties){
		let [left, top, width, height] = dimensions;
		let {ticks, ticksPx, tickLabels, mainLabel} = tickProperties;
		let tickLeft = left + this.AMPLITUDE_COLOR_BAR_GRADIENT_WIDTH;
		let tickRight = tickLeft + this.AMPLITUDE_COLOR_BAR_TICK_WIDTH;
		let tickLabelLeft = tickLeft + this.AMPLITUDE_COLOR_BAR_TICK_WIDTH + this.TEXT_PADDING;

		let gradient = this._context.createLinearGradient(left, top + height, left, top + 1);
		gradient.addColorStop(0.0, '#000');
		gradient.addColorStop(1.0, '#fff');
		this._context.fillStyle = gradient;
		this._context.strokeStyle = this.DEFAULT_FILL_STYLE;
		this._context.fillRect(left, top, this.AMPLITUDE_COLOR_BAR_GRADIENT_WIDTH, height);
		this._context.strokeRect(left + 0.5, top + 0.5, this.AMPLITUDE_COLOR_BAR_GRADIENT_WIDTH - 1, height - 1);
		this._context.beginPath();
		for (let index in ticks){
			let tickTop = top + height - Math.round(ticksPx[index]);
			this._context.moveTo(tickLeft, tickTop - 0.5);
			this._context.lineTo(tickRight, tickTop - 0.5);
		}
		this._context.stroke();

		this._context.fillStyle = this.DEFAULT_FILL_STYLE;
		this._context.textBaseline = 'middle';
		this._context.strokeStyle = this.DEFAULT_FILL_STYLE;
		for (let index in ticks){
			let tickTop = top + height - Math.round(ticksPx[index]);
			this._context.fillText(tickLabels[index], tickLabelLeft, tickTop);
		}

		this._context.textBaseline = 'bottom';
		this._context.fillText(mainLabel, left, top - this.TEXT_PADDING);
	}

	/**
	 * 	Calculates various geometrical parameters of the phase color bar
	 * 	@param {Array} 			colorBarHeight 			Desired height of the phase map color bar
	 * 	@return {object} 								Various geometrical parameters of the phase map color bar.
	 */
	measurePhaseColorBar(colorBarHeight){
		let imageDataPosition = this.PHASE_COLOR_BAR_TICK_WIDTH + this.DEFAULT_TEXT_HEIGHT + this.TEXT_PADDING;
		let colorBarResolution = this.state.colorBarResolution;
		if (!colorBarResolution || colorBarResolution < 0){
			return {totalWidth: 0};
		}
		let colorBarCenter = Math.floor(this.state.colorBarResolution / 2);
		let zeroDegreeText = '0\u{00b0}';

		return {
			zeroDegreeText: zeroDegreeText,
			verticalOrientationText: '90\u{00b0}',
			imageDataPosition: imageDataPosition,
			colorBarCenterX: colorBarCenter,
			colorBarCenterY: colorBarCenter + imageDataPosition,
			colorBarRadius: colorBarCenter,
			totalWidth:
				this.state.colorBarResolution +
				this.PHASE_COLOR_BAR_TICK_WIDTH +
				this.TEXT_PADDING +
				this._context.measureText(zeroDegreeText).width,
		};
	}

	/**
	 * 	Draws the phase map color bar.
	 * 	@param {Array} 			dimensions 				A rectangular area of the color bar
	 * 	@param {object} 		properties 				Various geometrical parameters returned by the
	 * 													measurePhaseColorBar method.
	 */
	drawPhaseColorBar(dimensions, properties){
		if (!this.state.colorBarResolution){
			return;
		}
		const [left, top, width, height] = dimensions;
		const {imageDataPosition, colorBarCenterX, colorBarCenterY, colorBarRadius,
			zeroDegreeText, verticalOrientationText} = properties;
		this._context.fillStyle = this.DEFAULT_FILL_STYLE;

		let imageData = this._context.createImageData(this.state.colorBarResolution, this.state.colorBarResolution);
		imageData.data.set(this.state.colorBarImage, 0);
		this._context.putImageData(imageData, left, top + imageDataPosition);

		this._context.save();
		this._context.translate(left + colorBarCenterX, top + colorBarCenterY);
		this._context.textBaseline = 'middle';

		/* Ticks */
		this._context.beginPath();
		this._context.moveTo(-this.PHASE_COLOR_BAR_TICK_WIDTH, 0.5);
		this._context.lineTo(colorBarRadius + this.PHASE_COLOR_BAR_TICK_WIDTH, 0.5);
		this._context.moveTo(0.5, this.PHASE_COLOR_BAR_TICK_WIDTH);
		this._context.lineTo(0.5, -colorBarRadius - this.PHASE_COLOR_BAR_TICK_WIDTH);
		this._context.stroke();

		this._context.fillText(
			zeroDegreeText,
			colorBarRadius + this.PHASE_COLOR_BAR_TICK_WIDTH + this.TEXT_PADDING,
			0.5
		);

		this._context.textBaseline = 'bottom';
		this._context.textAlign = 'center';
		this._context.fillText(
			verticalOrientationText,
			2.5,
			-colorBarRadius - this.PHASE_COLOR_BAR_TICK_WIDTH - this.TEXT_PADDING,
		);

		this._context.restore();
	}

	/**
	 * 	Calculates geometrical parameters of the scale bar
	 * 	@param {Number} 		mapWidth 				Desired width of the scale bar
	 * 	@return {object} 								Various geometrical parameters of the scale bar
	 */
	measureScaleBar(mapWidth){
		let mapWidthUm = this.props.functionalMap.width;
		let mapResolution = this.state.scale * mapWidth / mapWidthUm;
		let mapWidthPower = Math.floor(Math.log10(mapWidthUm));
		let scaleBarWidth = Math.pow(10, mapWidthPower) * mapResolution;
		let oldMapWidthPower, oldScaleBarWidth;
		while (scaleBarWidth > this.MINIMUM_SCALE_BAR_WIDTH){
			oldMapWidthPower = mapWidthPower;
			oldScaleBarWidth = scaleBarWidth;
			mapWidthPower -= 1;
			scaleBarWidth /= 10;

		}
		if (oldMapWidthPower){
			mapWidthPower = oldMapWidthPower;
			scaleBarWidth = oldScaleBarWidth;
		}

		let scaleBarText = Math.pow(10, mapWidthPower);
		if (scaleBarWidth > mapWidth){
			scaleBarText /= 2;
			scaleBarWidth /= 2;
		}
		if (scaleBarText > 100){ /* um */
			scaleBarText = `${scaleBarText / 1000} ${t('mm')}`;
		} else {
			scaleBarText = `${scaleBarText} ${t('um')}`;
		}

		return {
			scaleBarWidth: Math.round(scaleBarWidth),
			scaleBarText: scaleBarText,
		}
	}

	/**
	 * 	Draws the scale bar
	 * 	@param {Array} 			dimensions 				Rectangle where the scale bar must be drawn
	 * 	@return {object} 								Various geometrical parameters returned by measureScaleBar
	 * 													method
	 */
	drawScaleBar(dimensions, scaleBarProperties){
		let [left, top, width, height] = dimensions;
		let {scaleBarWidth, scaleBarText} = scaleBarProperties;
		this._context.save();

		this._context.fillStyle = this.DEFAULT_FILL_STYLE;
		this._context.strokeStyle = this.DEFAULT_FILL_STYLE;

		this._context.lineWidth = this.SCALE_BAR_THICKNESS;
		this._context.lineCap = 'butt';
		this._context.beginPath();
		this._context.moveTo(left, top + 0.5 * this.SCALE_BAR_THICKNESS);
		this._context.lineTo(left + scaleBarWidth, top + 0.5 * this.SCALE_BAR_THICKNESS);
		this._context.stroke();

		this._context.textBaseline = 'hanging';
		this._context.fillText(scaleBarText, left, top + this.SCALE_BAR_TEXT_POSITION, width);

		this._context.restore();
	}

	/**
	 * 	Returns coordinates of a current mouse position
	 * 	@param {SyntheticEvent} event 					The event that triggered this method
	 * 	@return {object} 								Given coordinates on the source functional map ('source') and
	 * 													on the user-visible scaled map copy ('destination')
	 */
	getSelectionArea(event){
		if (!this.props.functionalMap || !this._canvasRect || !this._amplitudeMapRectangle || !this._phaseMapRectangle){
			return undefined;
		}
		let globalX = event.clientX - this._canvasRect.left;
		let globalY = event.clientY - this._canvasRect.top;
		let localX = null;
		let localY = null;
		let destinationWidth = null;
		let destinationHeight = null;

		for (let rectangle of [this._amplitudeMapRectangle, this._phaseMapRectangle]){
			let [left, top, width, height] = rectangle;
			if (globalX >= left && globalX < left + width && globalY >= top && globalY < top + height){
				localX = globalX - left;
				localY = globalY - top;
				destinationWidth = width;
				destinationHeight = height;
				break;
			}
		}

		if (localX && this.state.currentTool){
			this.canvasElement.style.cursor = this.state.currentTool.cursorCss;
		} else {
			this.canvasElement.style.cursor = null;
		}

		if (localX === null){
			this.statusBar.innerText = this.MOTION_PROMPT;
			return null;
		}

		let sourceWidth = this.props.functionalMap.resolution_x / this.state.scale;
		let sourceHeight = this.props.functionalMap.resolution_y / this.state.scale;
		let sourceX = Math.round(this._left + localX * sourceWidth / destinationWidth);
		let sourceY = Math.round(this._top + localY * sourceHeight / destinationHeight);

		this.statusBar.innerText = `X = ${sourceX}; Y = ${sourceY}`;

		return {
			parent: this,
			sourceX: sourceX,
			sourceY: sourceY,
			destinationX: localX,
			destinationY: localY,
			sourceWidth: sourceWidth,
		}
	}

	/**
	 * 	Returns destination coordinates of the functional map draw on the canvas
	 * 	@param {String} 		mapType 				Type of the map.
	 * 	@return {Array} 								Abscissa of the left border, ordinate of the top border,
	 * 													width of the map area, height of the map area
	 */
	_getMapRectangle(mapType){
		let mapRectangle = null;
		switch (mapType){
		case 'amplitude':
			mapRectangle = this._amplitudeMapRectangle;
			break;
		case 'phase':
			mapRectangle = this._phaseMapRectangle;
			break;
		case 'relative':
			mapRectangle = this._relativeMapRectangle;
			break;
		default:
			throw new Error('getCanvasX or getCanvasY requires two arguments: source coordinates and mapType');
		}
		return mapRectangle;
	}

	/**
	 * 	Returns the X coordinate on the canvas related to a given X coordinate on the source map
	 * 	@param {Number} 		mapX 					Abscissa of a point on the source map
	 * 	@param {String} 		mapType 				'amplitude' for amplitude map, 'phase' for phase map
	 * 	@return {Number} 								Abscissa of related point on the canvas
	 */
	getCanvasX(mapX, mapType){
		let [destinationLeft, destinationTop, destinationWidth, destinationHeight] = this._getMapRectangle(mapType);
		let sourceWidth = this.props.functionalMap.resolution_x / this.state.scale;
		return Math.round((mapX - this._left) * destinationWidth / sourceWidth + destinationLeft);
	}

	/**
	 * 	Returns the Y coordinate on the canvas related to a given Y coordinate on the source map
	 * 	@param {Number} 		mapY 					Ordinate of a point on the source map
	 * 	@param {String} 		mapType 				'amplitude' for an amplitude map, 'phase' for a phase map
	 * 	@return {Number} 								Ordinate of related point on the canvas
	 */
	getCanvasY(mapY, mapType){
		let [destinationLeft, destinationTop, destinationWidth, destinationHeight] = this._getMapRectangle(mapType);
		let sourceHeight = this.props.functionalMap.resolution_y / this.state.scale;
		return Math.round((mapY - this._top) * destinationHeight / sourceHeight + destinationTop);
	}

	render(){
		let containerClasses = style.drawer;
		if (this.props.cssSuffix){
			containerClasses += ` ${this.props.cssSuffix}`;
		}

		/* leaving canvas area is the same as putting mouse up */
		return (
			<div className={containerClasses} ref={this._containerRef}>
				<canvas
					style={{marginBottom: `${this.CANVAS_MARGIN}px`}}
					onMouseDown={this.handleMouseDown}
					onMouseMove={this.handleMouseMove}
					onMouseUp={this.handleMouseUp}
					onMouseLeave={this.handleMouseUp}
				/>
				<div className={style.toolbar}>
					<Icon
						onClick={event => this.handleZoom(this.SCALE_STEP)}
						inactive={this.props.isLoading}
						disabled={this.state.scale >= this.MAX_SCALE}
						tooltip={t("Zoom in")}
						src={<ZoomInIcon/>}
					/>
					<Icon
						onClick={event => this.handleZoom(-this.SCALE_STEP)}
						inactive={this.props.isLoading}
						disabled={this.state.scale <= this.MIN_SCALE}
						tooltip={t("Zoom out")}
						src={<ZoomOutIcon/>}
					/>
					<Icon
						onClick={this.handleCancelSelection}
						inactive={this.props.isLoading}
						tooltip={t("Cancel tool selection")}
						src={<PointerIcon/>}
					/>
					{this.tools.map(tool => {
						return <Icon
							onClick={event => this.handleToolSelection(tool)}
							inactive={this.props.isLoading}
							toggled={tool === this.state.currentTool}
							tooltip={tool.tooltip}
							src={tool.icon}
						/>;
					})}
				</div>
				<div className={style.status_bar} ref={this._statusBarRef}>{this.MOTION_PROMPT}</div>
			</div>
		);
	}

	componentDidMount(){
		super.componentDidMount();
		this.__mapResizeObserver = new ResizeObserver(entries => this.repaint());
		this.__mapResizeObserver.observe(this.container);
	}

	componentDidUpdate(prevProps, prevState){
		if (this.props.functionalMap.id !== prevProps.functionalMap.id){
			this.reload();
		} else {
			this.repaint();
		}
	}

	componentWillUnmount(){
		this.__mapResizeObserver.disconnect();
	}

	/**
	 * 	Triggers when the user tries to zoom in or zoom out the map
	 * 	@param {Number} 		zoomDirection 			Amount that the zoom must be change to
	 */
	handleZoom(zoomDirection){
		let newScale =  this.state.scale + zoomDirection;
		if (newScale < 1){
			return;
		}
		let maxPositionFactor = 1 - 1 / newScale;
		let maxLeft = Math.round(this.props.functionalMap.resolution_x * maxPositionFactor);
		let maxTop = Math.round(this.props.functionalMap.resolution_y * maxPositionFactor);
		if (this._left < 0){
			this._left = 0;
		}
		if (this._left > maxLeft){
			this._left = maxLeft;
		}
		if (this._top < 0){
			this._top = 0;
		}
		if (this._top > maxTop){
			this._top = maxTop;
		}

		this.setState({
			scale: newScale,
		});
	}

	/**
	 * 	Triggers when the user clicks on a given tool
	 * 	@param 	{BaseTool} tool 			The tool selected by the user
	 */
	handleToolSelection(tool){
		let selectionResult = tool.selectTool();
		if (selectionResult !== true){
			this.setState({currentTool: tool});
		}
	}

	/**
	 * 	Triggers when the user clicks on 'Cancel all tools' button
	 * 	@param {SyntheticEvent} event
	 */
	handleCancelSelection(event){
		this.setState({currentTool: null});
	}

	/**
	 * 	Triggers when the user holds the mouse button on the canvas
	 * 	@param {SyntheticEvent} event
	 */
	handleMouseDown(event){
		if (event.buttons !== this.NO_BUTTONS_ID && event.buttons !== this.LEFT_BUTTON_ID){
			return;
		}
		this._mouseButtonPressed = true;
		let selectionArea = this.getSelectionArea(event);
		if (this.state.currentTool && selectionArea){
			this.state.currentTool.mouseDown(selectionArea);
		}
	}

	/**
	 * 	Triggers when the user moves the button over the canvas
	 * 	@param {SyntheticEvent} event
	 */
	handleMouseMove(event){
		let selectionArea = this.getSelectionArea(event);
		if (this.state.currentTool && selectionArea === null && this._mouseButtonPressed){
			this._mouseButtonPressed = false;
			this.state.currentTool.mouseUp(null);
		}
		if (this.state.currentTool && selectionArea){
			this.state.currentTool.mouseMove(selectionArea);
		}
	}

	/**
	 * 	Triggers when the user releases the mouse button on the canvas
	 * 	@param {SyntheticEvent} event
	 */
	handleMouseUp(event){
		if (!this._mouseButtonPressed){
			return;
		}
		this._mouseButtonPressed = false;
		let selectionArea = this.getSelectionArea(event);
		if (this.state.currentTool && selectionArea){
			this.state.currentTool.mouseUp(selectionArea);
		}
	}

}