import GraphicList from './GraphicList';
import RoiAddTool from './drawer-tools/RoiAddTool';
import RoiEditTool from './drawer-tools/RoiEditTool';
import RoiRemoveTool from './drawer-tools/RoiRemoveTool';
import CloseAppTool from './drawer-tools/CloseAppTool';


/**
 * 	Allows the user to interactively manage the list of rectangular ROIs.
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
 * 	@param {Array} 			itemList 					List of all items to display
 * 	@param {callback} 		onItemAdd 					Triggers when the user tries to add new item. Asynchronous
 * 	@param {callback} 		onItemChange 				Triggers when the user tries to change the item. Asynchronous
 * 	@param {callback} 		onItemRemove				Triggers when the user tries to remove the item. Asynchronous
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
export default class RectangularRoiGraphicList extends GraphicList{

	ROI_LINE_WIDTH = 3;
	ROI_STROKE_WIDTH = 1;
	ROI_LINE_COLOR = {
		amplitude: "#ff0000",
		phase: "#000000"
	};
	ROI_STROKE_COLOR = "#ffffff";
	ROI_SHADOW_BLUR = 3;

	constructor(props){
		super(props);

		this.tools = [
			...this.tools,
			new RoiAddTool(),
			new RoiEditTool(),
			new RoiRemoveTool(),
			new CloseAppTool(`/data/${this.props.functionalMap.id}/`),
		];
	}

	repaintItems(){
		for (this._mapType of ['amplitude', 'phase']){
			this._context.save();

			let rectangle = this._getMapRectangle(this._mapType);
			[this._clipLeft, this._clipTop, this._clipWidth, this._clipHeight] = rectangle;
			this._context.beginPath();
			this._context.rect(...rectangle);
			this._context.clip();

			/* Drawing the ROI line */
			this._context.strokeStyle = this.ROI_LINE_COLOR[this._mapType];
			this._context.lineWidth = this.ROI_LINE_WIDTH;
			this._roiShift = this.ROI_STROKE_WIDTH;
			this.repaintItemsPrimitive();

			this._context.strokeStyle = this.ROI_STROKE_COLOR;
			this._context.lineWidth = this.ROI_STROKE_WIDTH;
			this._context.shadowBlur = this.ROI_SHADOW_BLUR;
			this._roiShift = this.ROI_LINE_WIDTH + this.ROI_STROKE_WIDTH;
			this.repaintItemsPrimitive();

			this._roiShift = 0;
			this._context.shadowBlur = 0;
			this.repaintItemsPrimitive();

			this._context.restore();
		}
	}

	repaintItemsPrimitive(){
		this._context.beginPath();
		super.repaintItems();
		this._context.stroke();
	}

	/**
	 * 	Repaints a single item
	 * 	@param {RectangularRoi}		roi 					An item to repaint
	 * 	@param {boolean} 			isCurrent 				The item is currently selected by a given tool
	 */
	repaintItem(roi, isCurrent){
		if (this.state.currentTool && this.state.currentTool.current && !isCurrent){
			return;
		}

		let left = this.getCanvasX(roi.left, this._mapType);
		let top = this.getCanvasY(roi.top, this._mapType);
		let right = this.getCanvasX(roi.right, this._mapType);
		let bottom = this.getCanvasY(roi.bottom, this._mapType);

		if (left < this._clipLeft + this._clipWidth && right > this._clipLeft &&
			top < this._clipTop + this._clipHeight && bottom > this._clipTop){
			this._context.rect(
				left - this._context.lineWidth / 2 - this._roiShift,
				top - this._context.lineWidth / 2 - this._roiShift,
				right - left + this._context.lineWidth + 2 * this._roiShift,
				bottom - top + this._context.lineWidth + 2 * this._roiShift,
			);
		}
	}

}