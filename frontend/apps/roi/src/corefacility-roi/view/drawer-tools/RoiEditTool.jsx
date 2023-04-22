import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';


/**
 * 	Allows the user to edit ROI
 */
export default class RoiEditTool extends BaseTool{

	CAPTURE_AREA = 10;

	constructor(){
		super();
		this.CAPTURE_AREA_SQR = this.CAPTURE_AREA * this.CAPTURE_AREA;
		this._capturedRoi = null;
		this._capturedSide = null;
		this._selectedRoi = null;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Edit an existent ROI");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <EditIcon/>;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		switch (this._capturedSide){
		case 'left':
			return 'w-resize';
		case 'top-left':
			return 'nw-resize';
		case 'top':
			return 'n-resize';
		case 'top-right':
			return 'ne-resize';
		case 'right':
			return 'e-resize';
		case 'bottom-right':
			return 'se-resize';
		case 'bottom':
			return 's-resize';
		case 'bottom-left':
			return 'sw-resize';
		default:
			return 'crosshair';
		}
	}

	/**
	 * 	Currently selected ROI
	 */
	get current(){
		return this._selectedRoi;
	}

	/**
	 * 	Triggered when the user clicks and holds the left mouse button
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseDown(selectionArea){
		super.mouseDown(selectionArea);
		this._selectedRoi = this._capturedRoi;
		selectionArea.parent.repaint();
	}

	/**
	 * 	Triggered when the user moves the mouse over the functional map.
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseMove(selectionArea){
		super.mouseMove(selectionArea);

		if (this._dragging && this._selectedRoi){
			this.updateCapturedSide(selectionArea);
			this.editSelectedRoi(selectionArea);
			selectionArea.parent.repaint();
		} else {
			let capturedDetails = this.captureCorners(selectionArea);
			if (capturedDetails === null){
				capturedDetails = this.captureSides(selectionArea);
			}
			if (capturedDetails === null){
				this._capturedRoi = null;
				this._capturedSide = null;
			} else {
				this._capturedRoi = capturedDetails.roi;
				this._capturedSide = capturedDetails.side;
			}
		}
	}

	/**
	 * 	Triggers when the user releases the mouse button or leaves the functional map area.
	 * 	@param {object|null} 	selectionArea	contains the parent FunctionalMapDrawer together with mouse coordinates
	 * 											null when the user suddenly leaves the map area
	 */
	mouseUp(selectionArea){
		super.mouseUp(selectionArea);
		if (selectionArea && this._selectedRoi){
			selectionArea.parent.handleItemChange(this._selectedRoi)
				.finally(() => {
					this._selectedRoi = this._capturedRoi = this._capturedSide = null;
				});
		}
	}

	/**
	 * 	Detects whether the user moves the mouse over corners of some ROI
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent map drawer
	 * 	@return {object} 								information about the ROI and the captured corner
	 */
	captureCorners(selectionArea){
		/* To increase productivity we use the following designations in variable names:
				Sqr - square
				Dist - distance to the current mouse pointer
		*/
		let roiDistance;
		let leftDistSqr, topDistSqr, rightDistSqr, bottomDistSqr;
		let topLeftDistSqr, topRightDistSqr, bottomLeftDistSqr, bottomRightDistSqr;
		let minCornerDistSqr;
		let closestRoi = null;
		let closestCorner = null;
		let minDistanceValue = null;
		for (let roi of selectionArea.parent.state.itemList){
			roiDistance = this.getDistanceToRoiSides(selectionArea, roi);
			leftDistSqr = roiDistance.left * roiDistance.left;
			rightDistSqr = roiDistance.right * roiDistance.right;
			topDistSqr = roiDistance.top * roiDistance.top;
			bottomDistSqr = roiDistance.bottom * roiDistance.bottom;
			topLeftDistSqr = leftDistSqr + topDistSqr;
			topRightDistSqr = rightDistSqr + topDistSqr;
			bottomLeftDistSqr = leftDistSqr + bottomDistSqr;
			bottomRightDistSqr = rightDistSqr + bottomDistSqr;
			minCornerDistSqr = Math.min(topLeftDistSqr, topRightDistSqr, bottomLeftDistSqr, bottomRightDistSqr);
			if (minCornerDistSqr < this.CAPTURE_AREA_SQR &&
					(minDistanceValue === null || minDistanceValue > minCornerDistSqr)){
				closestRoi = roi;
				minDistanceValue = minCornerDistSqr;
				switch (minCornerDistSqr){
				case topLeftDistSqr:
					closestCorner = 'top-left';
					break;
				case topRightDistSqr:
					closestCorner = 'top-right';
					break;
				case bottomLeftDistSqr:
					closestCorner = 'bottom-left';
					break;
				case bottomRightDistSqr:
					closestCorner = 'bottom-right';
					break;
				default:
					throw new Error("No idea about the corner.");
				}
			}
		}

		if (closestRoi === null){
			return null;
		} else {
			return {roi: closestRoi, side: closestCorner};
		}
	}

	/**
	 * 	Detects whether the user moves the mouse over the borders of some ROI
	 * 	@param {object} 		selectionArea 			Information about mouse position and the parent map drawer
	 * 	@return {object} 								Information about the ROI and the captured corner
	 */
	captureSides(selectionArea){
		let roiDistance;
		let minSideDistanceLocal;
		let closestSideLocal;
		let closestSideIsVertical, closestSideIsHorizontal;
		let sourceXIsInsideRoi, sourceYIsInsideRoi;
		let sideIsCaptured;

		let closestRoi = null;
		let closestSide = null;
		let minSideDistance = null;
		for (let roi of selectionArea.parent.state.itemList){
			roiDistance = this.getDistanceToRoiSides(selectionArea, roi);
			minSideDistanceLocal = Math.min(roiDistance.left, roiDistance.right, roiDistance.top, roiDistance.bottom);
			if (minSideDistanceLocal > this.CAPTURE_AREA){
				continue;
			}

			switch (minSideDistanceLocal){
			case roiDistance.left:
				closestSideLocal = 'left';
				closestSideIsVertical = true;
				closestSideIsHorizontal = false;
				break;
			case roiDistance.right:
				closestSideLocal = 'right';
				closestSideIsVertical = true;
				closestSideIsHorizontal = false;
				break;
			case roiDistance.top:
				closestSideLocal = 'top';
				closestSideIsVertical = false;
				closestSideIsHorizontal = true;
				break;
			case roiDistance.bottom:
				closestSideLocal = 'bottom';
				closestSideIsVertical = false;
				closestSideIsHorizontal = true;
				break;
			default:
				throw new Error("No idea about the side.");
			}
			sourceXIsInsideRoi = selectionArea.sourceX >= roi.left && selectionArea.sourceX <= roi.right;
			sourceYIsInsideRoi = selectionArea.sourceY >= roi.top && selectionArea.sourceY <= roi.bottom;
			sideIsCaptured = closestSideIsVertical && sourceYIsInsideRoi ||
				closestSideIsHorizontal && sourceXIsInsideRoi;
			if (!sideIsCaptured){
				continue;
			}

			if (minSideDistance === null || minSideDistance > minSideDistanceLocal){
				closestRoi = roi;
				closestSide = closestSideLocal;
				minSideDistance = minSideDistanceLocal;
			}
		}

		if (closestRoi === null){
			return null;
		} else {
			return {roi: closestRoi, side: closestSide};
		}
	}

	/**
	 * 	Changes the ROI borders when the user grabs and moves them
	 * 	@param {object} 		selectionArea 			Information about mouse position and the parent drawer
	 */
	updateCapturedSide(selectionArea){
		if (this._capturedSide === 'left'){
			if (selectionArea.sourceY < this._selectedRoi.top){
				this._capturedSide = 'top-left';
				this._startSourceY = selectionArea.sourceY;
			}
			if (selectionArea.sourceY > this._selectedRoi.bottom){
				this._capturedSide = 'bottom-left';
				this._startSourceY = selectionArea.sourceY;
			}
		}
		if (this._capturedSide === 'top'){
			if (selectionArea.sourceX < this._selectedRoi.left){
				this._capturedSide = 'top-left';
				this._startSourceX = selectionArea.sourceX;
			}
			if (selectionArea.sourceX > this._selectedRoi.right){
				this._capturedSide = 'top-right';
				this._startSourceX = selectionArea.sourceX;
			}
		}
		if (this._capturedSide === 'right'){
			if (selectionArea.sourceY < this._selectedRoi.top){
				this._capturedSide = 'top-right';
				this._startSourceY = selectionArea.sourceY;
			}
			if (selectionArea.sourceY > this._selectedRoi.bottom){
				this._capturedSide = 'bottom-right';
				this._startSourceY = selectionArea.sourceY;
			}
		}
		if (this._capturedSide === 'bottom'){
			if (selectionArea.sourceX < this._selectedRoi.left){
				this._capturedSide = 'bottom-left';
				this._startSourceX = selectionArea.sourceX;
			}
			if (selectionArea.sourceX > this._selectedRoi.right){
				this._capturedSide = 'bottom-right';
				this._startSourceX = selectionArea.sourceX;
			}
		}
	}

	/**
	 * 	Modifies the ROI change mode the the user hovers mouse over the ROI corners
	 * 	@param {object} 		selectionArea			Information about mouse position and the map drawer
	 */
	editSelectedRoi(selectionArea){
		if (this._capturedSide.search('left') !== -1){
			let newValue = this._selectedRoi.left + selectionArea.sourceX - this._startSourceX;
			if (newValue >= 0 && newValue < this._selectedRoi.right){
				this._selectedRoi.left = newValue;
				this._startSourceX = selectionArea.sourceX;
			}
		}
		if (this._capturedSide.search('top') !== -1){
			let newValue = this._selectedRoi.top + selectionArea.sourceY - this._startSourceY;
			if (newValue >= 0 && newValue < this._selectedRoi.bottom){
				this._selectedRoi.top = newValue;
				this._startSourceY = selectionArea.sourceY;
			}
		}
		if (this._capturedSide.search('right') !== -1){
			let newValue = this._selectedRoi.right + selectionArea.sourceX - this._startSourceX;
			if (newValue > this._selectedRoi.left && newValue < window.application.functionalMap.resolution_x){
				this._selectedRoi.right = newValue;
				this._startSourceX = selectionArea.sourceX;
			}
		}
		if (this._capturedSide.search('bottom') !== -1){
			let newValue = this._selectedRoi.bottom + selectionArea.sourceY - this._startSourceY;
			if (newValue > this._selectedRoi.top && newValue < window.application.functionalMap.resolution_y){
				this._selectedRoi.bottom = newValue;
				this._startSourceY = selectionArea.sourceY;
			}
		}
	}

	/**
	 * 	Returns the distance from the current mouse position to the sides of a ROI
	 * 	@param {object}			selectionArea 			Information about mouse position and the ROI
	 * 	@param {RectangularRoi} roi 					ROI which information shall be revealed
	 * 	@return {object} 								Information about the distance to the borders of this ROI
	 */
	getDistanceToRoiSides(selectionArea, roi){
		let mouseX = selectionArea.destinationX;
		let mouseY = selectionArea.destinationY;

		let roiLeft = selectionArea.parent.getCanvasX(roi.left, 'relative');
		let roiRight = selectionArea.parent.getCanvasX(roi.right, 'relative');
		let roiTop = selectionArea.parent.getCanvasY(roi.top, 'relative');
		let roiBottom = selectionArea.parent.getCanvasY(roi.bottom, 'relative');

		return {
			left: Math.abs(mouseX - roiLeft),
			right: Math.abs(mouseX - roiRight),
			top: Math.abs(mouseY - roiTop),
			bottom: Math.abs(mouseY - roiBottom),
		}
	}


}