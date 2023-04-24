import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as EditIcon} from 'corefacility-base/shared-view/icons/edit.svg';

import PinwheelCaptureTool from './PinwheelCaptureTool';

/**
 * 	Allows the user to change the pinwheel position
 */
export default class PinwheelEditTool extends PinwheelCaptureTool{

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Change pinwheel position");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <EditIcon/>;
	}

	/**
	 * 	Triggers when the user hovers mouse over the selection area.
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 */
	mouseMove(selectionArea){
		super.mouseMove(selectionArea);
		if (this._dragging && this._selectedPinwheel){
			this.changePinwheelPosition(selectionArea);
			selectionArea.parent.repaint();
		}
	}

	/**
	 * 	Modifies the pinwheel position
	 * 	@param {object} 		selectionArea 			Information about the pinwheel area selected
	 */
	changePinwheelPosition(selectionArea){
		this._selectedPinwheel.x += selectionArea.sourceX - this._startSourceX;
		this._selectedPinwheel.y += selectionArea.sourceY - this._startSourceY;
		this._startSourceX = selectionArea.sourceX;
		this._startSourceY = selectionArea.sourceY;
	}

	/**
	 * Applies the pinwheel action made by the user.
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 */
	apply(selectionArea){
		if (this._selectedPinwheel.state !== 'changed'){
			this._selectedPinwheel = this._capturedPinwheel = null;
			selectionArea.parent.repaint();
			return;
		}
		selectionArea.parent.handleItemChange(this._selectedPinwheel)
			.finally(() => {
				this._selectedPinwheel = this._capturedPinwheel = null;
			});
	}

}