import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as AddIcon} from 'corefacility-base/shared-view/icons/add.svg';
import BaseTool from 'corefacility-imaging/view/drawer_tools/BaseTool';

import Pinwheel from 'corefacility-roi/model/Pinwheel';


/**
 * 	Provides facility for adding new pinwheel center
 */
export default class PinwheelAddTool extends BaseTool{

	constructor(props){
		super(props);
		this._currentPinwheel = null;
	}

	/**
	 * 	Tooltip for an icon
	 */
	get tooltip(){
		return t("Add new pimwheel center");
	}

	/**
	 * 	Icon of a tool to be displayed on the toolbar below.
	 */
	get icon(){
		return <AddIcon/>;
	}

	/**
	 * 	When the cursor moves over the functional map, the canvas CSS property cursor will be set to this value
	 */
	get cursorCss(){
		return 'none';
	}

	/**
	 * 	Returns the current pinwheel that must also be displayed.
	 */
	get current(){
		return this._currentPinwheel;
	}

	/**
	 * 	Triggers when the user moves the mouse over the map
	 * 	@param {object} 		selectionArea 			Information about mouse position and the parent drawer.
	 */
	mouseMove(selectionArea){
		if (this._currentPinwheel === null){
			this._currentPinwheel = new Pinwheel(
				{x: selectionArea.sourceX, y: selectionArea.sourceY},
				window.application.functionalMap
			);
		} else if (this._currentPinwheel.state === 'creating'){
			this._currentPinwheel.x = selectionArea.sourceX;
			this._currentPinwheel.y = selectionArea.sourceY;
		}
		selectionArea.parent.repaint();
	}

	/**
	 *	Triggers when the user releases the mouse buttons
	 * 	@param {object} 		selectionArea 			Information about mouse position and the parent drawer.
	 */
	mouseUp(selectionArea){
		selectionArea.parent.handleItemAdd(this._currentPinwheel)
			.finally(() => {
				this._currentPinwheel = null;
			});
	}

}
