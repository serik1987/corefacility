import {NotImplementedError} from 'corefacility-base/exceptions/model';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';


/**
 * 	This is a base tool for all facilities where the user have to capture a pinwheel
 */
export default class PinwheelCaptureTool extends BaseTool{

	CAPTURE_AREA_SQR = 10 * 10;

	constructor(props){
		super(props);
		this._capturedPinwheel = null;
		this._selectedPinwheel = null;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		if (this._selectedPinwheel){
			return 'none';
		} else if (this._capturedPinwheel){
			return 'pointer';
		} else {
			return 'default';
		}
	}

	/**
	 * 	Currently selected pinwheel
	 */
	get current(){
		return this._selectedPinwheel;
	}

	/**
	 * 	Triggers when the user presses the mouse button.
	 * 	@param {object} 		selectionArea 			information about the mouse position and the parent area
	 */
	mouseDown(selectionArea){
		super.mouseDown(selectionArea);
		if (this._capturedPinwheel){
			this._selectedPinwheel = this._capturedPinwheel;
			selectionArea.parent.repaint();
		}
	}

	/**
	 * 	Triggers when the user hovers mouse over the selection area.
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 */
	mouseMove(selectionArea){
		super.mouseMove(selectionArea);
		if (!this._dragging) {
			this._capturedPinwheel = this.capturePinwheel(selectionArea);
		}
	}

	/**
	 *	Triggers when the user releases the mouse button.
	 */
	mouseUp(selectionArea){
		super.mouseUp(selectionArea);
		if (this._selectedPinwheel){
			this.apply(selectionArea);
		}
	}

	/**
	 * 	Applies the pinwheel action made by the user.
	 * 	@abstract
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 */
	apply(selectionArea){
		throw new NotImplementedError('apply');
	}

	/**
	 * 	Indicates whether the user hovers mouse over the pinwheel center.
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 * 	@return {Pinwheel|null} 						Pinwheel captured or null if no pinwheel was captured.
	 */
	capturePinwheel(selectionArea){
		/*
		 *	Designations: sqr - square, min - minimum
		 */
		let mouseX = selectionArea.destinationX;
		let mouseY = selectionArea.destinationY;
		let pinwheelX, pinwheelY, pinwheelDistanceSqr;

		let pinwheel = null;
		let pinwheelDistanceSqrMin = null;

		for (let pinwheelLocal of selectionArea.parent.state.itemList){
			pinwheelX = selectionArea.parent.getCanvasX(pinwheelLocal.x, 'relative');
			pinwheelY = selectionArea.parent.getCanvasY(pinwheelLocal.y, 'relative');
			pinwheelDistanceSqr = (mouseX - pinwheelX) * (mouseX - pinwheelX) +
				(mouseY - pinwheelY) * (mouseY - pinwheelY);

			if (pinwheelDistanceSqr < this.CAPTURE_AREA_SQR &&
				(pinwheelDistanceSqrMin === null || pinwheelDistanceSqrMin > pinwheelDistanceSqr)){
				pinwheel = pinwheelLocal;
				pinwheelDistanceSqrMin = pinwheelDistanceSqr;
			}
		}

		return pinwheel;
	}

}