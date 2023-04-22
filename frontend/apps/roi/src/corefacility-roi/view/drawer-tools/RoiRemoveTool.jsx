import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as DeleteIcon} from 'corefacility-base/shared-view/icons/delete.svg';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';


/**
 * 	Handles mouse coordinates the the user tries to remove the ROI
 */
export default class RoiRemoveTool extends BaseTool{

	CAPTURE_AREA = 10;

	constructor(){
		super();
		this._capturedRoi = null;
		this._selectedRoi = null;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Remove the ROI");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <DeleteIcon/>;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		if (this._capturedRoi){
			return 'pointer';
		} else {
			return 'default';
		}
	}

	/**
	 * 	Returns the currently selected ROI
	 */
	get current(){
		return this._selectedRoi;
	}

	/**
	 * 	Triggers when the user holds the mouse over the ROI.
	 * 	@param {object} 		selectionArea 			Information about the mouse position and the parent drawer
	 */
	mouseDown(selectionArea){
		super.mouseDown(selectionArea);

		if (this._capturedRoi){
			this._selectedRoi = this._capturedRoi;
			selectionArea.parent.repaint();
		}
	}

	/**
	 * 	Triggers when the user hovers the mouse over the functional map
	 * 	@param {object}			selectionArea 			Information about mouse position and the parent drawer
	 */
	mouseMove(selectionArea){
		super.mouseMove(selectionArea);

		if (!this._dragging) {
			let roi = this.captureRoi(selectionArea);
			if (roi){
				this._capturedRoi = roi;
			} else {
				this._capturedRoi = null;
			}
		}
	}

	/**
	 *  Triggers when the user releases the mouse button
	 * 	@param {object} 		selectionArea 			Information about the area selected by the ROI.
	 */
	mouseUp(selectionArea){
		super.mouseUp(selectionArea);

		if (this._selectedRoi){
			let capturedRoi = this.captureRoi(selectionArea);
			let promise;
			if (capturedRoi && capturedRoi.id === this._selectedRoi.id){
				promise = selectionArea.parent.handleItemRemove(this._selectedRoi);
			} else {
				promise = Promise.resolve();
			}
			promise.finally(() => {
				this._selectedRoi = null;
			});
		}
	}

	/**
	 * 	Detects a ROI that the user hovers on
	 * 	@param {object} 		selectionArea 			Information about mouse position and the parent drawer
	 * 	@return {RectangularRoi} 						The ROI detected or false if no ROI detected
	 */
	captureRoi(selectionArea){
		let mouseX = selectionArea.destinationX;
		let mouseY = selectionArea.destinationY;
		let roiLeft, roiRight, roiTop, roiBottom;
		let leftDistance, rightDistance, topDistance, bottomDistance;
		let allDistances, minDistanceLocal;
		
		let capturedRoi = false;
		let minDistance = null;

		for (let roi of selectionArea.parent.state.itemList){
			roiLeft = selectionArea.parent.getCanvasX(roi.left, 'relative');
			roiRight = selectionArea.parent.getCanvasX(roi.right, 'relative');
			roiTop = selectionArea.parent.getCanvasY(roi.top, 'relative');
			roiBottom = selectionArea.parent.getCanvasY(roi.bottom, 'relative');
			if (mouseY >= roiTop - this.CAPTURE_AREA && mouseY <= roiBottom + this.CAPTURE_AREA){
				leftDistance = Math.abs(roiLeft - mouseX);
				rightDistance = Math.abs(roiRight - mouseX);
			} else {
				leftDistance = rightDistance = undefined;
			}
			if (mouseX >= roiLeft - this.CAPTURE_AREA && mouseX <= roiRight + this.CAPTURE_AREA){
				topDistance = Math.abs(roiTop - mouseY);
				bottomDistance = Math.abs(roiBottom - mouseY);
			} else {
				topDistance = bottomDistance = undefined;
			}
			allDistances = [leftDistance, topDistance, rightDistance, bottomDistance]
				.filter(distance => distance !== undefined);
			minDistanceLocal = Math.min(...allDistances);

			if (allDistances.length === 4 && minDistanceLocal <= this.CAPTURE_AREA &&
					(minDistance === null || minDistance > minDistanceLocal)){
				capturedRoi = roi;
				minDistance = minDistanceLocal;
			}
		}

		return capturedRoi;
	}

}
