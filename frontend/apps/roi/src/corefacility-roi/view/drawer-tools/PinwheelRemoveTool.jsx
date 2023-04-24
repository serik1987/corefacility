import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as RemoveIcon} from 'corefacility-base/shared-view/icons/delete.svg';

import PinwheelCaptureTool from './PinwheelCaptureTool';


/**
 * 	Allows the user to interactively remove the pinwheel
 */
export default class PinwheelRemoveTool extends PinwheelCaptureTool{

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Remove the pinwheel center");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <RemoveIcon/>;
	}

	/**
	 * 	Applies the pinwheel action made by the user.
	 * 	@param {object} 		selectionArea 			information about mouse position and the parent area
	 */
	apply(selectionArea){
		selectionArea.parent.handleItemRemove(this._selectedPinwheel)
			.finally(() => {
				this._selectedPinwheel = this._capturedPinwheel = null;
			});
	}

}