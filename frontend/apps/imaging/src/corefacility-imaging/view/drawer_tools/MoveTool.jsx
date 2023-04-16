import {translate as t} from 'corefacility-base/utils';
import {ReactComponent as MoveToolIcon} from 'corefacility-base/shared-view/icons/pan_tool.svg';

import BaseTool from './BaseTool';


export default class MoveTool extends BaseTool{

	constructor(props){
		super(props);
		this._originalLeft = undefined;
		this._originalTop = undefined;
	}

	get cursorCss(){
		return 'move';
	}


	get icon(){
		return <MoveToolIcon/>;
	}

	get tooltip(){
		return t("Move");
	}

	/**
	 * 	Triggered when the user clicks and holds the left mouse button
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseDown(selectionArea){
		super.mouseDown(selectionArea);
	}

	/**
	 * 	Triggered when the user moves the mouse over the functional map.
	 * 	@param {object} 	selectionArea 		contains the parent FunctionalMapDrawer together with mouse coordinates
	 */
	mouseMove(selectionArea){
		if (this._dragging){
			let deltaX = selectionArea.sourceX - this._startSourceX;
			let deltaY = selectionArea.sourceY - this._startSourceY;
			let newX = selectionArea.parent.left - deltaX;
			let newY = selectionArea.parent.top - deltaY;

			let visibleAreaPart = 1 - 1 / selectionArea.parent.state.scale;
			let newXMax = Math.round(selectionArea.parent.props.functionalMap.resolution_x * visibleAreaPart);
			let newYMax = Math.round(selectionArea.parent.props.functionalMap.resolution_y * visibleAreaPart);		

			if (newX >= 0 && newX < newXMax && newY >= 0 && newY < newYMax){
				selectionArea.parent.left = newX;
				selectionArea.parent.top = newY;
				selectionArea.parent.repaint();
			} else {
				this._startSourceX = selectionArea.sourceX;
				this._startSourceY = selectionArea.sourceY;
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
		this._originalLeft = this._originalTop = undefined;
	}
}